from enum import Enum

from .base_handler import BaseHandler
from ..chunked_endpoint import ChunkedEndpoint


class CMDType(int, Enum):
    CAPABILITIES_REQUEST = 0x01
    CAPABILITIES_RESPONSE = 0x02
    LOGS_START = 0x03
    LOGS_START_ACK = 0x04
    LOGS_STOP = 0x05
    LOGS_STOP_ACK = 0x06
    LOGS_DATA = 0x07
    UNKNOWN_8 = 0x08
    UNKNOWN_9 = 0x09


class LogsClient(BaseHandler):
    endpoint = ChunkedEndpoint.LOGS
    encrypted = False
    logs_type = None

    def __init__(self, *args, **kwargs):
        self.sessions = set()
        super().__init__(*args, **kwargs)

    async def request_capabilities(self):
        await self.write(
            bytes([CMDType.CAPABILITIES_REQUEST]),
        )

    async def start(self):
        while self.logs_type is None:
            raise Exception("No logs type specified, run request_capabilities first")

        await self.write(
            bytes([CMDType.LOGS_START]) + self.logs_type.encode("utf-8") + b"\0",
        )

    async def stop(self, session_id: int):
        self.sessions.remove(session_id)
        await self.write(
            bytes([CMDType.LOGS_STOP]) + b"\0" + session_id.to_bytes(1, "little"),
        )


@LogsClient.handler(CMDType.UNKNOWN_8)
async def unknown_8_handler(self: LogsClient, payload: bytes):
    self.logger.debug("Got unknown 8, replying with unknown 9")
    await self.write(bytes([CMDType.UNKNOWN_9]))


@LogsClient.handler(CMDType.LOGS_START_ACK)
async def logs_start_ack_handler(self: LogsClient, payload: bytes):
    if payload[0] != 1:
        raise Exception("Start logging failed")
    session_id = payload[1]
    self.sessions.add(session_id)
    self.logger.info("Start logging: %i", session_id)


@LogsClient.handler(CMDType.LOGS_STOP_ACK)
async def logs_stop_ack_handler(self: LogsClient, payload: bytes):
    assert payload[0] == 1
    self.logger.info("Stop logging")


@LogsClient.handler(CMDType.LOGS_DATA)
async def logs_data_handler(self: LogsClient, payload: bytes):
    index = payload[1]
    session_id = payload[0]

    app_id, timestamp, data = payload.split(b"\0")
    self.logger.info("Log entry - {} [{}] - {}", timestamp, app_id, data)


@LogsClient.handler(CMDType.CAPABILITIES_RESPONSE)
async def capabilities_response_handler(self: LogsClient, payload: bytes):
    version = payload[0]
    var1 = payload[1]
    var2 = payload[2]
    assert [version, var1, var2] == [1, 1, 0]
    self.logs_type = payload[3:].rstrip(b"\0").decode()
    self.logger.info(f"Logs type: {self.logs_type}")

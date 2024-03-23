import logging
from enum import Enum

from chunked_endpoint import ChunkedEndpoint
from .base_handler import BaseHandler


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

    async def __call__(self, payload: bytes):
        cmd = CMDType(payload[0])
        print(cmd, payload[1:])

    async def start(self):
        await self.write(
            bytes([CMDType.LOGS_START]) + b"utf-8\0",
        )

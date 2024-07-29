import struct
from enum import Enum

from .base_handler import BaseHandler
from ..chunked_endpoint import ChunkedEndpoint


class StepsCmd(int, Enum):
    GET = 0x03
    REPLY = 0x04
    ENABLE_REALTIME = 0x05
    ENABLE_REALTIME_ACK = 0x06
    REALTIME_NOTIFICATION = 0x07


class StepsClient(BaseHandler):
    endpoint = ChunkedEndpoint.STEPS
    encrypted = False

    async def start(self):
        await self.write(
            bytes([StepsCmd.ENABLE_REALTIME]),
        )

    async def get_steps(self):
        await self.write(
            bytes([StepsCmd.GET]),
        )


@StepsClient.handler(StepsCmd.REPLY)
async def reply_handler(self: StepsClient, payload: bytes):
    _, _, steps, meters, calories = struct.unpack("<BB3I", payload)
    self.logger.info(f"steps: {steps}, meters: {meters}, calories: {calories}")


@StepsClient.handler(StepsCmd.ENABLE_REALTIME_ACK)
async def enable_realtime_ack_handler(self: StepsClient, payload: bytes):
    self.logger.info(
        "Band acknowledged realtime steps, status = %i, enabled = %i",
        payload[1],
        payload[2],
    )


@StepsClient.handler(StepsCmd.REALTIME_NOTIFICATION)
async def realtime_notification_handler(self: StepsClient, payload: bytes):
    data = struct.unpack("<Biii", payload)
    self.logger.info(f"Realtime steps: {data}")

import logging
import struct
from enum import Enum

from chunked_endpoint import ChunkedEndpoint
from .base_handler import BaseHandler


class StepsCmd(int, Enum):
    GET = 0x03
    REPLY = 0x04
    ENABLE_REALTIME = 0x05
    ENABLE_REALTIME_ACK = 0x06
    REALTIME_NOTIFICATION = 0x07


class StepsClient(BaseHandler):
    endpoint = ChunkedEndpoint.STEPS

    async def __call__(self, payload: bytes):
        cmd = StepsCmd(payload[0])

        if cmd == StepsCmd.REPLY:
            steps = int.from_bytes(payload[1:], "little")
            self.logger.info(f"Steps: {steps}")
        elif cmd == StepsCmd.ENABLE_REALTIME_ACK:
            logging.info(
                "Band acknowledged realtime steps, status = %i, enabled = %i",
                payload[1],
                payload[2],
            )
        elif cmd == StepsCmd.REALTIME_NOTIFICATION:
            self.handle_realtime_steps(payload[1:])

    async def start(self):
        await self.write(
            bytes([StepsCmd.ENABLE_REALTIME]),
        )

    async def get_steps(self):
        await self.write(StepsCmd.GET.to_bytes(1, "little"))

    def handle_realtime_steps(self, payload: bytes):
        data = struct.unpack("<Biii", payload)
        self.logger.info(f"Realtime steps: {data}")

from enum import Enum

from chunked_endpoint import ChunkedEndpoint
from .base_handler import BaseHandler


class HeartRateRealtimeMode(int, Enum):
    STOP = 0x00
    START = 0x01
    CONTINUE = 0x02


class HeartRateCmd(int, Enum):
    REALTIME_SET = 0x04
    REALTIME_ACK = 0x05
    SLEEP = 0x06


class HeartRateStatus(int, Enum):
    FALL_ASLEEP = 0x01
    WAKE_UP = 0x00


class HeartRateClient(BaseHandler):
    endpoint = ChunkedEndpoint.HEARTRATE

    async def __call__(self, payload: bytes):
        cmd = HeartRateCmd(payload[0])

        self.logger.info(cmd, payload[1:])

        if cmd == HeartRateCmd.REALTIME_ACK:
            status = HeartRateStatus(payload[1])
            if status == HeartRateStatus.WAKE_UP:
                self.logger.info("Woke up")
            elif status == HeartRateStatus.FALL_ASLEEP:
                self.logger.info("Fall asleep")

    async def start(self):
        await self.write(
            bytes([HeartRateCmd.REALTIME_SET, HeartRateRealtimeMode.START]),
        )

    async def stop(self):
        await self.write(
            bytes([HeartRateCmd.REALTIME_SET, HeartRateRealtimeMode.STOP]),
        )

    async def sleep(self):
        await self.write(
            bytes([HeartRateCmd.SLEEP]),
        )

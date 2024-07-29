from enum import Enum

from .base_handler import BaseHandler
from ..chunked_endpoint import ChunkedEndpoint


class HeartRateCmd(int, Enum):
    REALTIME_SET = 0x04
    REALTIME_ACK = 0x05
    SLEEP = 0x06


class HeartRateRealtimeMode(int, Enum):
    STOP = 0x00
    START = 0x01
    CONTINUE = 0x02


class SleepStatus(int, Enum):
    FALL_ASLEEP = 0x01
    WAKE_UP = 0x00


class HeartRateClient(BaseHandler):
    endpoint = ChunkedEndpoint.HEARTRATE
    encrypted = False

    async def start(self):
        await self.write(
            bytes([HeartRateCmd.REALTIME_SET, HeartRateRealtimeMode.START]),
        )

    async def stop(self):
        await self.write(
            bytes([HeartRateCmd.REALTIME_SET, HeartRateRealtimeMode.STOP]),
        )

    async def test(self):
        await self.write(
            bytes([0x03]),
        )


@HeartRateClient.handler(HeartRateCmd.REALTIME_ACK)
async def realtime_ack_handler(self: HeartRateClient, payload: bytes):
    self.logger.info("Band acknowledged realtime heart rate: ", payload[1])


@HeartRateClient.handler(HeartRateCmd.SLEEP)
async def sleep_handler(self: HeartRateClient, payload: bytes):
    status = SleepStatus(payload[1])
    if status == SleepStatus.WAKE_UP:
        self.logger.info("Woke up")
    elif status == SleepStatus.FALL_ASLEEP:
        self.logger.info("Fall asleep")

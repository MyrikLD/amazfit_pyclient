import struct
from dataclasses import dataclass
from datetime import datetime, timedelta

from ..data_fetch import CsvDataFetch, FetchType


@dataclass(frozen=True)
class ActivitySample:
    timestamp: datetime
    kind: int
    intensity: int
    steps: int
    heart_rate: int
    retain: int
    sleep: int
    deep_sleep: int
    rem_sleep: int

    @classmethod
    def parse(cls, timestamp, data: bytes):
        return cls(timestamp, *struct.unpack("8B", data))


class FetchActivity(CsvDataFetch):
    sample_type = ActivitySample

    async def start(self, since: datetime):
        await super().start(FetchType.ACTIVITY, since)

    def get_samples(self):
        def _iter(_buf):
            while data := _buf.read(8):
                yield data

        for n, sample in enumerate(_iter(self.buffer)):
            yield self.sample_type.parse(
                self.start_timestamp + timedelta(minutes=1 * n), sample
            )

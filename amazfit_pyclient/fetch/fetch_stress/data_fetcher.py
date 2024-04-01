from dataclasses import dataclass
from datetime import datetime, timedelta

from ..data_fetch import CsvDataFetch, FetchType


@dataclass(frozen=True)
class StressSample:
    timestamp: datetime
    stress: int

    @classmethod
    def parse(cls, timestamp, data: int):
        return cls(timestamp, data)


class FetchStress(CsvDataFetch):
    sample_type = StressSample

    async def start(self, since: datetime):
        await super().start(FetchType.STRESS_AUTOMATIC, since)

    def get_samples(self):
        for n, sample in enumerate(self.buffer.getvalue()):
            if sample != 0xFF:
                yield self.sample_type.parse(
                    self.start_timestamp + timedelta(minutes=1 * n), sample
                )

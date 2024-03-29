from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path

from .utils import parse_samples, save_csv
from ..data_fetch import DataFetch, FetchType


class FetchActivity(DataFetch):
    async def start(self, since: datetime):
        await super().start(FetchType.ACTIVITY, since)

    async def on_transaction_complete(self):
        path = Path(
            f"{self.fetch_type.name.lower()}.{self.start_timestamp.isoformat()}.csv"
        )

        fieldnames = [
            "datetime",
            "kind",
            "intensity",
            "steps",
            "heart_rate",
            "unknown1",
            "sleep",
            "deep_sleep",
            "rem_sleep",
        ]

        with save_csv(path, fieldnames) as writer:
            for sample in self.get_samples():
                writer.writerow(sample)

        print(f"Saved to {path}")

    def get_samples(self):
        for n, sample in enumerate(parse_samples(self.buffer)):
            yield {
                "datetime": (self.start_timestamp + timedelta(minutes=1 * n)),
                **asdict(sample),
            }

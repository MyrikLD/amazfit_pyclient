from dataclasses import asdict
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

from fetch.data_fetch import DataFetch, FetchType
from .utils import parse_samples, save_csv


class FetchActivity(DataFetch):
    async def start(self, since: datetime):
        await super().start(FetchType.ACTIVITY, since)

    @staticmethod
    async def on_transaction_complete(
        fetch_type: FetchType, start_timestamp: datetime, buffer: BytesIO
    ):
        path = Path(f"{fetch_type.name.lower()}.{start_timestamp.isoformat()}.csv")

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
            for n, sample in enumerate(parse_samples(buffer)):
                writer.writerow(
                    {
                        "datetime": (
                            start_timestamp + timedelta(minutes=1 * n)
                        ).isoformat(),
                        **asdict(sample),
                    }
                )

        print(f"Saved to {path}")

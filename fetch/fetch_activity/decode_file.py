from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path

from fetch.fetch_activity.utils import parse_samples, save_csv


def main():
    filename = Path("activity.2024-03-26T12:04:00.bin")
    t, dt = filename.stem.split(".")
    start_timestamp = datetime.fromisoformat(dt)

    path = Path(f"{t}.{start_timestamp.isoformat()}.csv")

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

    with open(filename, "rb") as fi:
        with save_csv(path, fieldnames) as writer:
            for n, sample in enumerate(parse_samples(fi)):
                writer.writerow(
                    {
                        "datetime": (
                            start_timestamp + timedelta(minutes=1 * n)
                        ).isoformat(),
                        **asdict(sample),
                    }
                )


if __name__ == "__main__":
    main()

import csv
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def save_csv(path: Path, fieldnames: list[str]) -> Iterator[csv.DictWriter]:
    with open(path, "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        yield writer

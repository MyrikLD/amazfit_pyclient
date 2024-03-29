import csv
import struct
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterator


@dataclass
class Sample:
    kind: int
    intensity: int
    steps: int
    heart_rate: int
    unknown1: int
    sleep: int
    deep_sleep: int
    rem_sleep: int


def parse_samples(f: BinaryIO) -> Iterator[Sample]:
    while data := f.read(8):
        sample = Sample(*struct.unpack("3Bb4B", data))
        yield sample


@contextmanager
def save_csv(path: Path, fieldnames: list[str]) -> Iterator[csv.DictWriter]:
    with open(path, "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        yield writer



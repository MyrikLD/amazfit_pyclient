import struct
from datetime import datetime, timedelta, timezone
from enum import Enum


class TimeUnit(int, Enum):
    MINUTES = 0x01
    SECONDS = 0x02


class TimeUtils:
    @staticmethod
    def short_time_bytes(timestamp: datetime) -> bytes:
        return (
            timestamp.year.to_bytes(2, "little")
            + timestamp.month.to_bytes(1, "little")
            + timestamp.day.to_bytes(1, "little")
            + timestamp.hour.to_bytes(1, "little")
            + timestamp.minute.to_bytes(1, "little")
        )

    @staticmethod
    def time_bytes(timestamp: datetime) -> bytes:
        return (
            timestamp.year.to_bytes(2, "little")
            + timestamp.month.to_bytes(1, "little")
            + timestamp.day.to_bytes(1, "little")
            + timestamp.hour.to_bytes(1, "little")
            + timestamp.minute.to_bytes(1, "little")
            + timestamp.second.to_bytes(1, "little")
            + timestamp.date().isoweekday().to_bytes(1, "little")
            + b"\0"
        )

    @classmethod
    def bytes_time(cls, data: bytes) -> datetime:
        fmt = "<H6b"
        size = struct.calcsize(fmt)
        assert len(data) == size, f"Expected {size} bytes, got {len(data)}"
        year, month, day, hour, minute, second, tz_ = struct.unpack(fmt, data)
        tz = cls.bytes_tz(tz_)
        dt = datetime(year, month, day, hour, minute, second, tzinfo=tz)

        return dt

    @classmethod
    def short_bytes_time(cls, data: bytes) -> datetime:
        fmt = "<H5b"
        size = struct.calcsize(fmt)
        assert len(data) == size, f"Expected {size} bytes, got {len(data)}"
        year, month, day, hour, minute, second = struct.unpack(fmt, data)
        return datetime(year, month, day, hour, minute, second)

    @staticmethod
    def bytes_tz(data: bytes) -> timezone:
        if isinstance(data, bytes):
            data = int.from_bytes(data)
        tz = timezone(timedelta(seconds=data * 15 * 60))
        return tz


def get_time_bytes(timestamp: datetime, precision: TimeUnit) -> bytes:
    if precision == TimeUnit.SECONDS:
        data = TimeUtils.time_bytes(timestamp)
    elif precision == TimeUnit.MINUTES:
        data = TimeUtils.short_time_bytes(timestamp)
    else:
        raise ValueError

    if timestamp.tzinfo is None:
        tz = timedelta(seconds=0)
    else:
        tz = timestamp.utcoffset()

    tail = int(tz.total_seconds() // (60 * 15))

    return data + tail.to_bytes(2, "big")

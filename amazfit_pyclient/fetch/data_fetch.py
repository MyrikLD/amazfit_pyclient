import asyncio
import struct
from dataclasses import asdict, fields
from datetime import datetime
from enum import Enum
from io import BytesIO
from logging import getLogger
from pathlib import Path
from typing import Iterator, Type
from uuid import UUID

from bleak import BleakClient, BleakGATTCharacteristic

from .utils import get_time_bytes, save_csv, TimeUnit, TimeUtils


class FetchType(int, Enum):
    ACTIVITY = 0x01
    MANUAL_HEART_RATE = 0x02
    SPORTS_SUMMARIES = 0x38
    SPORTS_DETAILS = 0x3D
    DEBUG_LOGS = 0x07
    PAI = 0x0D
    STRESS_MANUAL = 0x12
    STRESS_AUTOMATIC = 0x13
    SPO2_NORMAL = 0x25
    SPO2_SLEEP = 0x26
    STATISTICS = 0x2C
    TEMPERATURE = 0x2E
    SLEEP_RESPIRATORY_RATE = 0x38
    RESTING_HEART_RATE = 0x3A
    MAX_HEART_RATE = 0x3D


class DataCMD(int, Enum):
    ACTIVITY_DATA_START_DATE = 0x01
    FETCH_DATA = 0x02
    ACK_ACTIVITY_DATA = 0x03


class ActivityDataCMD(int, Enum):
    START_DATE = 1
    FETCH_DATA = 2
    ACK_ACTIVITY_DATA = 3


class DataFetch:
    CHARACTERISTIC_ACTIVITY_METADATA = UUID("00000004-0000-3512-2118-0009af100700")
    CHARACTERISTIC_ACTIVITY_DATA = UUID("00000005-0000-3512-2118-0009af100700")
    buffer: BytesIO
    counter: int
    global_counter: int
    expected_data_length: int
    start_timestamp: datetime
    fetch_type: FetchType
    in_progress: asyncio.Lock

    def __init__(self, client: BleakClient):
        self.client = client
        self.in_progress = asyncio.Lock()
        self.log = getLogger(__name__)

    async def handle_activity_data(
        self, char: BleakGATTCharacteristic, data: bytearray
    ):
        data = bytes(data)
        counter = data[0]
        assert counter == (
            self.counter
        ), f"Unexpected counter: {counter} != {self.counter + 1}"

        self.counter = self.counter + 1
        if self.counter == 256:
            self.global_counter += self.counter
            self.counter = 0
            self.log.debug(f"Received {self.global_counter} packets")

        self.buffer.write(data[1:])

    async def handle_activity_metadata(
        self, char: BleakGATTCharacteristic, data: bytearray
    ):
        assert data[0] == 0x10, f"Failed to start date: {hex(data[0])}"
        cmd = ActivityDataCMD(data[1])
        data = bytes(data[2:])
        try:
            if cmd == ActivityDataCMD.START_DATE:
                await self.handle_start_date_response(data)
            elif cmd == ActivityDataCMD.FETCH_DATA:
                await self.handle_fetch_data_response(data)
        except Exception as e:
            self.in_progress.release()
            raise

    async def handle_start_date_response(self, data: bytes):
        (
            status,
            self.expected_data_length,
            start_timestamp,
            unknown,
        ) = struct.unpack("<BI8sB", data)
        assert status == 0x01, f"Failed to start date: {hex(status)}"
        self.start_timestamp = TimeUtils.bytes_time(start_timestamp)

        self.log.info(
            f"Start date: {self.start_timestamp}, expected data length: {self.expected_data_length}, {hex(unknown)=}"
        )
        await self.client.write_gatt_char(
            self.CHARACTERISTIC_ACTIVITY_METADATA, bytes([DataCMD.FETCH_DATA])
        )

    async def handle_fetch_data_response(self, data: bytes):
        status = data[0]
        data = data[1:]
        assert status == 0x01, f"Failed to fetch data: {hex(status)}: {data}"
        print(f"{data}")
        self.buffer.seek(0)
        self.in_progress.release()

        await self.on_transaction_complete()

        await self.data_ack(True)

    @property
    def path(self):
        return Path(
            f"{self.fetch_type.name.lower()}.{self.start_timestamp.isoformat()}.bin"
        )

    async def on_transaction_complete(self):
        path = self.path

        path = path.with_suffix(".bin")
        with open(path, "wb") as f:
            f.write(self.buffer.getvalue())

        print(f"Saved to {path}")

    async def data_ack(self, keep_data_on_device: bool):
        ack_byte = 0x09 if keep_data_on_device else 0x01
        ack_bytes = bytes([DataCMD.ACK_ACTIVITY_DATA, ack_byte])
        await self.client.write_gatt_char(
            self.CHARACTERISTIC_ACTIVITY_METADATA, ack_bytes
        )

    async def start(self, fetch_type: FetchType, since: datetime):
        self.buffer = BytesIO()
        self.counter = 0
        self.global_counter = 0
        self.fetch_type = fetch_type
        await self.in_progress.acquire()

        await self.client.start_notify(
            self.CHARACTERISTIC_ACTIVITY_METADATA,
            self.handle_activity_metadata,
        )

        await self.client.start_notify(
            self.CHARACTERISTIC_ACTIVITY_DATA,
            self.handle_activity_data,
        )

        await self.client.write_gatt_char(
            self.CHARACTERISTIC_ACTIVITY_METADATA,
            bytes([DataCMD.ACTIVITY_DATA_START_DATE, fetch_type])
            + get_time_bytes(since, TimeUnit.MINUTES),
        )


class CsvDataFetch(DataFetch):
    sample_type: Type

    @property
    def path(self):
        return Path(
            f"{self.fetch_type.name.lower()}.{self.start_timestamp.isoformat()}.csv"
        )

    async def on_transaction_complete(self):
        path = self.path
        _fields = [i.name for i in fields(self.sample_type)]

        with save_csv(path, _fields) as writer:
            for sample in self.get_samples():
                writer.writerow(asdict(sample))

        print(f"Saved to {path}")

    def get_samples(self) -> Iterator:
        raise NotImplementedError()

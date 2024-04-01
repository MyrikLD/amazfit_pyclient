import struct
from datetime import datetime
from enum import Enum
from typing import Tuple

from .base_handler import BaseHandler
from ..chunked_endpoint import ChunkedEndpoint
from amazfit_pyclient.fetch.utils import TimeUtils


class BatteryCmd(int, Enum):
    GET_STATE = 0x01
    STATE_ACK = 0x02
    GET_STATUS = 0x03
    FULL_INFO_ACK = 0x04


class BatteryStatus(int, Enum):
    NORMAL = 0
    CHARGING = 1


class BatteryClient(BaseHandler):
    endpoint = ChunkedEndpoint.BATTERY
    encrypted = False

    async def request_state(self):
        await self.write(
            bytes([BatteryCmd.GET_STATE]),
        )

    async def request_status(self):
        await self.write(
            bytes([BatteryCmd.GET_STATUS]),
        )

    def decode_payload(
        self,
        data: bytes,
    ) -> Tuple[int, BatteryStatus, datetime, int]:
        (
            unknown,
            proc,
            _status,
            _unknown_date,
            _last_charge_start,
            last_charge_proc,
        ) = struct.unpack("3B8s8sB", data)
        assert unknown == 0x0F
        assert proc <= 100
        assert last_charge_proc <= 100
        status = BatteryStatus(_status)
        unknown_date = TimeUtils.bytes_time(_unknown_date)
        last_charge_start = TimeUtils.bytes_time(_last_charge_start)

        self.logger.debug(f"{unknown_date=}")

        return proc, status, last_charge_start, last_charge_proc


@BatteryClient.handler(BatteryCmd.FULL_INFO_ACK)
async def get_full_info_handler(self: BatteryClient, payload: bytes):
    (
        proc,
        status,
        last_charge_start,
        last_charge_proc,
    ) = self.decode_payload(payload)
    print(
        "proc = %i, status = %s, last_charge_start = %s, last_charge_proc = %i"
        % (proc, status, last_charge_start, last_charge_proc)
    )


@BatteryClient.handler(BatteryCmd.STATE_ACK)
async def get_info_handler(self: BatteryClient, payload: bytes):
    print(f"Battery status: {int.from_bytes(payload)}")

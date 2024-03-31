from enum import Enum
from io import BytesIO

from .base_handler import BaseHandler
from ..chunked_endpoint import ChunkedEndpoint
from amazfit_pyclient.fetch.utils import TimeUtils


class BatteryCmd(int, Enum):
    GET_FULL_INFO = 0x04


class BatteryStatus(int, Enum):
    NORMAL = 0
    CHARGING = 1


class BatteryClient(BaseHandler):
    endpoint = ChunkedEndpoint.BATTERY
    encrypted = False


@BatteryClient.handler(BatteryCmd.GET_FULL_INFO)
async def get_full_info_handler(self: BatteryClient, payload: bytes):
    data = BytesIO(payload)
    unknown, proc, _status = data.read(3)
    assert payload[0] == 0x0F
    assert proc <= 100
    status = BatteryStatus(_status)
    last_full_charge = TimeUtils.short_bytes_time(data.read(7))
    ch = int.from_bytes(data.read(1))
    assert ch == 4
    last_charge_start = TimeUtils.short_bytes_time(data.read(7))
    ch = int.from_bytes(data.read(1))
    assert ch == 4
    last_charge_proc = int.from_bytes(data.read(1))
    print(
        "proc = %i, status = %s, last_full_charge = %s, last_charge_start = %s, last_charge_proc = %i"
        % (proc, status, last_full_charge, last_charge_start, last_charge_proc)
    )

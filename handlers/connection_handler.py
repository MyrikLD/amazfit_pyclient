from enum import Enum

from chunked_endpoint import ChunkedEndpoint
from .base_handler import BaseHandler


class ConnectionCmd(int, Enum):
    MTU_REQUEST = 0x01
    MTU_RESPONSE = 0x02
    PING_REQUEST = 0x03
    PING_RESPONSE = 0x04


class ConnectionClient(BaseHandler):
    endpoint = ChunkedEndpoint.CONNECT

    async def __call__(self, payload: bytes):
        cmd = ConnectionCmd(payload[0])
        if cmd == ConnectionCmd.PING_REQUEST:
            await self.write(ConnectionCmd.PING_RESPONSE.to_bytes(1, "little"))
        elif cmd == ConnectionCmd.MTU_RESPONSE:
            mtu = int.from_bytes(payload[1:], "little")
            self.logger.info(f"MTU: {mtu}")
            self.encoder.m_mtu = mtu

    async def ping(self):
        await self.write(ConnectionCmd.PING_REQUEST.to_bytes(1, "little"))

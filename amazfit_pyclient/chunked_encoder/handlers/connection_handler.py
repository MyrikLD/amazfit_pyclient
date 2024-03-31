from enum import Enum

from .base_handler import BaseHandler
from ..chunked_endpoint import ChunkedEndpoint


class ConnectionCmd(int, Enum):
    MTU_REQUEST = 0x01
    MTU_RESPONSE = 0x02
    PING_REQUEST = 0x03
    PING_RESPONSE = 0x04


class ConnectionClient(BaseHandler):
    endpoint = ChunkedEndpoint.CONNECT
    encrypted = False

    async def ping(self):
        await self.write(ConnectionCmd.PING_REQUEST.to_bytes(1, "little"))

    async def get_mtu(self):
        await self.write(ConnectionCmd.MTU_REQUEST.to_bytes(1, "little"))


@ConnectionClient.handler(ConnectionCmd.PING_REQUEST)
async def ping_response_handler(self: ConnectionClient, payload: bytes):
    await self.write(ConnectionCmd.PING_RESPONSE.to_bytes(1, "little"))


@ConnectionClient.handler(ConnectionCmd.MTU_RESPONSE)
async def mtu_response_handler(self: ConnectionClient, payload: bytes):
    mtu = int.from_bytes(payload, "little")
    self.logger.info(f"MTU: {mtu}")
    self.encoder.m_mtu = mtu

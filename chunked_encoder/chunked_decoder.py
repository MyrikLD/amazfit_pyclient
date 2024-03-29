import logging
import struct
from typing import Awaitable, Callable, Optional, TYPE_CHECKING

from bleak import BleakClient, BleakGATTCharacteristic

from .aes import decrypt_aes
from .chunked_endpoint import ChunkedEndpoint, HeaderFlags

if TYPE_CHECKING:
    from handlers.base_handler import BaseHandler


class ChunkedDecoder:
    current_handle: Optional[int] = None
    current_type = 0
    full_length = 0
    last_count = 0

    reassembly_buffer: bytes = b""
    __shared_session_key: Optional[bytes] = None

    callbacks: dict[ChunkedEndpoint, Callable[[bytes], Awaitable[None]]]

    def __init__(
        self,
        client: BleakClient,
    ):
        self.client = client

        service = client.services.get_service("0000fee0-0000-1000-8000-00805f9b34fb")
        self.char = service.get_characteristic("00000017-0000-3512-2118-0009af100700")

        self.callbacks = {}

        self.logger = logging.getLogger(self.__class__.__qualname__)

    async def callback(self, sender: BleakGATTCharacteristic, data: bytearray):
        assert sender == self.char
        await self.decode(data)

    async def start_notify(self):
        await self.client.start_notify(self.char.handle, self.callback)

    def set_encryption_parameters(self, final_shared_session_aes: bytes):
        self.__shared_session_key = final_shared_session_aes

    def add_handler(
        self,
        callback: "BaseHandler",
    ):
        assert callback.endpoint not in self.callbacks
        self.callbacks[callback.endpoint] = callback

    async def decode(self, data: bytes):
        chunked, _flags, _, handle, self.last_count = struct.unpack("BBBBB", data[:5])
        data = data[5:]

        if chunked != 0x03:
            self.logger.warning("Ignoring non-chunked payload")
            return False, 0

        flags = HeaderFlags(_flags)

        if self.current_handle is not None and self.current_handle != handle:
            self.logger.warning(
                "ignoring handle %s, expected %s", handle, self.current_handle
            )
            return False, 0

        if flags.first_chunk:
            self.full_length = int.from_bytes(data[:4], "little")
            data = data[4:]
            if flags.encrypted:
                encrypted_length = self.full_length + 8
                overflow = encrypted_length % 16
                if overflow > 0:
                    encrypted_length += 16 - overflow

                self.full_length = encrypted_length

            self.reassembly_buffer = b""
            self.current_type = int.from_bytes(data[:2], "little")
            data = data[2:]
            self.current_handle = handle

        self.reassembly_buffer += data

        if flags.last_chunk:
            assert len(self.reassembly_buffer) == self.full_length
            if flags.encrypted:
                if self.__shared_session_key is None:
                    self.logger.warning(
                        "Got encrypted message, but there's no shared session key"
                    )
                    self.current_handle = None
                    self.current_type = 0
                    return False, 0

                message_key = bytes(
                    [self.__shared_session_key[i] ^ handle for i in range(16)]
                )

                try:
                    buf = decrypt_aes(self.reassembly_buffer, message_key)
                except Exception as e:
                    self.logger.warning("error decrypting: %s", e)
                    self.current_handle = None
                    self.current_type = 0
                    return False, 0

                # todo: decode head
                head = buf[self.full_length :]
                buf = buf[: self.full_length]
            else:
                buf = self.reassembly_buffer

            self.reassembly_buffer = b""

            if self.current_type in list(ChunkedEndpoint):
                t_name = ChunkedEndpoint(self.current_type).name
            else:
                t_name = hex(self.current_type)

            self.logger.debug(
                "%s data %s: %s",
                "Decrypted" if flags.encrypted else "Plaintext",
                t_name,
                buf,
            )

            if self.current_type not in self.callbacks:
                self.logger.warning("No callback for event type: %s", t_name)
            else:
                try:
                    await self.callbacks[self.current_type](buf)
                except Exception as e:
                    self.logger.exception("Failed to handle payload: %s", e)

            if flags.needs_ack:
                ack_payload = struct.pack(
                    "<5B", 0x04, 0x00, self.current_handle, 0x01, self.last_count
                )
                await self.client.write_gatt_char(self.char, ack_payload)

            self.current_type = 0
            self.current_handle = None

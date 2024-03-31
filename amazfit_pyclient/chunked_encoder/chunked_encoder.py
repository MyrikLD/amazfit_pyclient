import logging
import zlib
from typing import Optional

from bleak import BleakClient

from .aes import encrypt_aes
from .chunked_endpoint import HeaderFlags


class ChunkedEncoder:
    shared_session_key: Optional[bytes] = None
    write_handle = 0
    encrypted_sequence_nr = 0
    m_mtu = 23

    def __init__(self, client: BleakClient):
        self.client = client

        self.char = client.services.get_characteristic(
            "00000016-0000-3512-2118-0009af100700"
        )

        self.logger = logging.getLogger(self.__class__.__qualname__)

    def set_encryption_parameters(
        self, encrypted_sequence_number: int, final_shared_session_aes: bytes
    ):
        self.shared_session_key = final_shared_session_aes
        self.encrypted_sequence_nr = encrypted_sequence_number

    def encrypt(self, payload: bytes):
        messagekey = bytes(i ^ self.write_handle for i in self.shared_session_key)
        assert len(messagekey) == 16

        encrypted_length = len(payload) + 8
        overflow = encrypted_length % 16
        if overflow:
            encrypted_length += 16 - overflow

        encryptable_payload = payload + self.encrypted_sequence_nr.to_bytes(4, "little")

        checksum = zlib.crc32(encryptable_payload)
        encryptable_payload += checksum.to_bytes(4, "little")

        payload = encrypt_aes(
            encryptable_payload + b"\0" * (encrypted_length - len(encryptable_payload)),
            messagekey,
        )
        self.encrypted_sequence_nr += 1

        return payload

    def encode(
        self,
        endpoint: int,
        payload: bytes,
        extended_flags: bool = False,
        encrypt: bool = False,
    ):
        if encrypt and self.shared_session_key is None:
            self.logger.error("Can't encrypt without the shared session key")
            return

        self.write_handle += 1

        count = 0
        header_size = 11

        if encrypt:
            try:
                payload = self.encrypt(payload)
            except Exception as e:
                self.logger.error("Could not encrypt data: %s", e)
                return

        while payload:
            max_chunklength = self.m_mtu - 3 - header_size
            copybytes = min(len(payload), max_chunklength)

            flags = HeaderFlags(0)
            if encrypt:
                flags |= HeaderFlags.encrypted
            if count == 0:
                flags |= HeaderFlags.first_chunk
            if len(payload) <= max_chunklength:
                flags |= HeaderFlags.last_chunk

            header = b"\x03"
            header += flags.to_bytes(1, "little")
            if extended_flags:
                header += b"\x00"
            header += self.write_handle.to_bytes(1, "little")
            header += count.to_bytes(1, "little")
            if count == 0:
                header += len(payload).to_bytes(4, "little")
                header += endpoint.to_bytes(2, "little")

            chunk = header + payload[:copybytes]

            assert len(chunk) == header_size + copybytes
            yield chunk

            payload = payload[copybytes:]

            header_size = 4 + extended_flags

            count += 1

    async def write(
        self,
        t: int,
        payload: bytes,
        extended_flags: bool = False,
        encrypt: bool = False,
    ):
        for i in self.encode(t, payload, extended_flags, encrypt):
            await self.client.write_gatt_char(self.char, i)

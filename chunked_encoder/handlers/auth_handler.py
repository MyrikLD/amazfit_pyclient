import asyncio
import struct
from enum import Enum

from cryptography.hazmat.primitives.asymmetric import ec

from .base_handler import BaseHandler
from ..aes import encrypt_aes
from ..chunked_decoder import ChunkedDecoder
from ..chunked_encoder import ChunkedEncoder
from ..chunked_endpoint import ChunkedEndpoint

SUCCESS = 0x01


curve = ec.SECT163R2()
exchange_algorithm = ec.ECDH()  # Elliptic curve Diffie-Hellman algorithm


privateEC = ec.generate_private_key(curve)
publicEC = privateEC.public_key()


class AuthCmd(int, Enum):
    RESPONSE = 0x10


class ChunkedEndpointAuth(int, Enum):
    STAGE_1 = 0x04
    STAGE_2 = 0x05


class AuthHandler(BaseHandler):
    endpoint = ChunkedEndpoint.AUTH

    def __init__(
        self,
        key: str,
        encoder: ChunkedEncoder,
        decoder: ChunkedDecoder,
    ):
        super().__init__(encoder=encoder, decoder=decoder)
        if key.startswith("0x"):
            key = key[2:]
        self.priv_key = bytes.fromhex(key)
        self.ready = asyncio.Event()

    async def send_response(self, remote_random, secret_key, final_shared_session_aes):
        encrypted_random1 = encrypt_aes(remote_random, secret_key)
        encrypted_random2 = encrypt_aes(remote_random, final_shared_session_aes)
        assert len(encrypted_random1) == 16
        assert len(encrypted_random2) == 16

        await self.encoder.write(
            self.endpoint,
            ChunkedEndpointAuth.STAGE_2.to_bytes(1, "little")
            + encrypted_random1
            + encrypted_random2,
            extended_flags=True,
            encrypt=False,
        )

    async def autenticate(self):
        await self.encoder.write(
            self.endpoint,
            struct.pack(
                "<4B48B",
                *(
                    [ChunkedEndpointAuth.STAGE_1, 0x02, 0x00, 0x02]
                    + list(
                        publicEC.public_numbers().x.to_bytes(24, "little")
                        + publicEC.public_numbers().y.to_bytes(24, "little")
                    )
                ),
            ),
            True,
        )
        self.logger.info("Waiting for auth")
        await self.ready.wait()


@AuthHandler.handler(AuthCmd.RESPONSE)
async def response_handler(self: AuthHandler, payload: bytes):
    stage = ChunkedEndpointAuth(payload[0])
    stages = {
        ChunkedEndpointAuth.STAGE_1: stage_1_handler,
        ChunkedEndpointAuth.STAGE_2: stage_2_handler,
    }
    await stages[stage](self, payload[1:])


async def stage_1_handler(self: AuthHandler, payload: bytes):
    status = payload[0]

    assert status == 1

    payload = payload[1:]

    self.logger.info("Got remote random + public key")
    remote_random = payload[:16]
    _remote_public_ec = payload[16:64]

    remote_public_ec = ec.EllipticCurvePublicNumbers(
        int.from_bytes(_remote_public_ec[0:24], byteorder="little"),
        int.from_bytes(_remote_public_ec[24:48], byteorder="little"),
        curve,
    ).public_key()
    shared_ec = int.from_bytes(
        privateEC.exchange(exchange_algorithm, remote_public_ec)
    ).to_bytes(24, "little")
    encrypted_sequence_number = int.from_bytes(shared_ec[:4], "big")

    final_shared_session_aes = bytes(
        shared_ec[i + 8] ^ self.priv_key[i] for i in range(16)
    )

    self.logger.info(f"Shared Session AES: {final_shared_session_aes.hex()}")

    self.encoder.set_encryption_parameters(
        encrypted_sequence_number, final_shared_session_aes
    )
    self.decoder.set_encryption_parameters(final_shared_session_aes)

    await self.send_response(remote_random, self.priv_key, final_shared_session_aes)


async def stage_2_handler(self: AuthHandler, payload: bytes):
    if payload[0] == SUCCESS:
        self.logger.info("Auth Success")
        self.ready.set()
    else:
        self.logger.error("AUTH FAILED")

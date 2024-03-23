import logging
from typing import Protocol

from chanked_encoder import ChunkedEncoder
from chanked_decoder import ChunkedDecoder
from chunked_endpoint import ChunkedEndpoint


class BaseHandler(Protocol):
    endpoint: ChunkedEndpoint
    encrypted = True

    def __init__(
        self,
        encoder: ChunkedEncoder,
        decoder: ChunkedDecoder,
    ):
        self.encoder = encoder
        self.decoder = decoder
        self.logger = logging.getLogger(self.__class__.__qualname__)

    async def __call__(self, payload: bytes):
        raise NotImplementedError()

    async def write(self, payload: bytes):
        await self.encoder.write(
            self.endpoint, payload, encrypt=self.encrypted, extended_flags=True
        )

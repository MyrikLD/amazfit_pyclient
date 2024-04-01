import logging
from typing import Awaitable, Callable, Protocol

from ..chunked_decoder import ChunkedDecoder
from ..chunked_encoder import ChunkedEncoder
from ..chunked_endpoint import ChunkedEndpoint


class BaseHandler(Protocol):
    endpoint: ChunkedEndpoint
    encrypted: bool
    handlers: dict[int, Callable[["BaseHandler", bytes], Awaitable[None]]]

    def __init__(
        self,
        encoder: ChunkedEncoder,
        decoder: ChunkedDecoder,
    ):
        self.encoder = encoder
        self.decoder = decoder
        decoder.add_handler(self)
        self.logger = logging.getLogger(self.__class__.__qualname__)

    async def __call__(self, payload: bytes):
        handler = self.handlers.get(payload[0])
        if not handler:
            self.logger.error(f"Handler not found: {payload[0]} -> {payload[1:]}")
            return

        await handler(self, payload[1:])

    async def write(self, payload: bytes):
        await self.encoder.write(
            self.endpoint, payload, encrypt=self.encrypted, extended_flags=True
        )

    @classmethod
    def handler(cls, cmd: int):
        if not hasattr(cls, "handlers"):
            cls.handlers = {}

        def decorator(func: Callable[[cls, bytes], Awaitable[None]]):
            cls.handlers[cmd] = func

            return func

        return decorator

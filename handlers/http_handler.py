from enum import Enum

import httpx

from chunked_endpoint import ChunkedEndpoint
from .base_handler import BaseHandler
from .utils.weather_server import WeatherServer


class CMDType(int, Enum):
    REQUEST = 0x01
    RESPONSE = 0x02


class ResponseCode(int, Enum):
    SUCCESS = 0x01
    NO_INTERNET = 0x02


def list_to_dict(lst):
    res_dict = {}
    for i in range(0, len(lst), 2):
        res_dict[lst[i]] = lst[i + 1]
    return res_dict


class HttpClient(BaseHandler):
    endpoint = ChunkedEndpoint.HTTP


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.weather = WeatherServer()

    async def __call__(self, payload: bytes):
        t, request_id = payload[0], payload[1]

        assert t == CMDType.REQUEST

        data = payload[2:]

        head, metadata = data.split(b"\0\0\0\0", 1)

        _method, _url, headers_data = head.split(b"\0", 2)
        len_headers = int(headers_data[0])

        method = _method.decode("utf-8")
        url = _url.decode("utf-8")

        headers = list_to_dict(headers_data[1:].split(b"\0"))

        assert len_headers == len(headers)

        async with httpx.AsyncClient() as client:
            response = self.weather.get(url)
            # response = await client.request(method, url, headers=headers)
            self.logger.info(
                f"{method} {url}[{response.status_code}] -> {response.content}"
            )
            if response.is_success:
                await self.reply_http_success(
                    request_id, response.status_code, response.content
                )
            else:
                await self.reply_http_fail(request_id)

    async def reply_http_success(self, request_id: int, status: int, content: bytes):
        buf = bytes(
            [
                CMDType.RESPONSE,
                request_id,
                ResponseCode.SUCCESS,
                status,
            ]
        ) + len(content).to_bytes(4, "little")

        await self.write(buf + content)

    async def reply_http_fail(self, request_id: int):
        buf = (
            bytes(
                [
                    CMDType.RESPONSE,
                    request_id,
                    ResponseCode.NO_INTERNET,
                ]
            )
            + int(0).to_bytes(4, "little")
        )

        await self.write(buf)

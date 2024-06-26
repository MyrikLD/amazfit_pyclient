from unittest.mock import AsyncMock, Mock, patch

import pytest

from amazfit_pyclient.chunked_encoder import ChunkedEncoder
from amazfit_pyclient.chunked_encoder.handlers import HttpClient


@pytest.mark.asyncio
async def test_weather():
    client = Mock()
    client.write_gatt_char = AsyncMock()
    a = ChunkedEncoder(client)
    client = HttpClient(a, AsyncMock())

    with patch.object(ChunkedEncoder, "write") as encoder_mock:
        await client.request(102, "GET", "https://localhost/weather/current")
    encoder_mock.assert_called_once_with(
        1,
        b'\x02f\x01\xc8\xb4\x01\x00\x00{"currentWeatherModel":{"humidity":{"unit":"%","value":"33"},"pressure":{"unit":"mb","value":"0"},"pubTime":"2024-03-26T13:20:47+0100","temperature":{"unit":"\xe2\x84\x83","value":"33"},"uvIndex":"0","visibility":{"unit":"km","value":"0"},"weather":"1","wind":{"direction":{"unit":"\xc2\xb0","value":"133"},"speed":{"unit":"km/h","value":"33"}}},"aqiModel":{"aqi":null,"co":null,"no2":null,"o3":null,"pm10":null,"pm25":null,"pubTime":null,"so2":null}}',
        encrypt=True,
        extended_flags=True,
    )

    # a = WeatherServer()
    # r = a.get("/weather/current")
    # print(r.content)

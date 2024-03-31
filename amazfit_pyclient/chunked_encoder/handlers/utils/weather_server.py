import json
from dataclasses import dataclass
from enum import Enum

from yarl import URL


class WeatherCode(int, Enum):
    SUNNY = 0
    SOME_CLOUDS = 1
    CLOUDY = 2
    RAIN_WITH_SUN = 3
    THUNDERSTORM = 4
    HAIL = 5
    SLEET = 6
    LIGHT_RAIN = 7
    MODERATE_RAIN = 8
    HEAVY_RAIN = 9
    RAINSTORM = 10
    HEAVY_RAINSTORM = 11
    EXTRAORDINARY_RAINSTORM = 12
    SNOW_SHOWER_WITH_SOME_SUN = 13
    LIGHT_SNOW = 14
    MODERATE_SNOW = 15
    HEAVY_SNOW = 16
    SNOWSTORM = 17
    FOG = 18
    FREEZING_RAIN = 19
    SANDSTORM = 20
    LIGHT_TO_MODERATE_RAIN = 21
    MODERATE_TO_HEAVY_RAIN = 22
    HEAVY_RAIN_TO_RAINSTORM = 23
    RAINSTORM_TO_HEAVY_RAIN = 24
    HEAVY_TO_SEVERE_STORM = 25
    LIGHT_TO_MODERATE_SNOW = 26
    MODERATE_TO_HEAVY_SNOW = 27
    HEAVY_SNOW_TO_SNOWSTORM = 28
    DUST = 29
    SAND_BLOWING = 30
    STRONG_SANDSTORM = 31
    DENSE_FOG = 32
    SNOW = 33


@dataclass
class FakeResponse:
    status_code: int = 200
    content: bytes = b""

    @classmethod
    def json(cls, data: dict):
        return cls(
            status_code=200,
            content=json.dumps(data, ensure_ascii=False)
            .replace(" ", "")
            .encode("utf-8"),
        )

    @property
    def is_success(self):
        return 100 < self.status_code < 300


class WeatherServer:
    def get(self, url: str):
        _url = URL(url)
        if _url.path == "/weather/current":
            return self.current()
        return FakeResponse(status_code=404)

    def current(self):
        """
        humidity = new UnitValue(Unit.PERCENTAGE, weatherSpec.currentHumidity)
        pressure = new UnitValue(Unit.PRESSURE_MB, Math.round(weatherSpec.pressure))
        pubTime = new Date(weatherSpec.timestamp * 1000L)
        temperature = new UnitValue(Unit.TEMPERATURE_C, weatherSpec.currentTemp - 273)
        uvIndex = String.valueOf(Math.round(weatherSpec.uvIndex))
        visibility = new UnitValue(Unit.KM, Math.round(weatherSpec.visibility / 1000))
        weather = String.valueOf(mapToZeppOsWeatherCode(weatherSpec.currentConditionCode))
        wind = new Wind(weatherSpec.windDirection, Math.round(weatherSpec.windSpeed))
        """

        return FakeResponse.json(
            {
                "currentWeatherModel": {
                    "humidity": {"unit": "%", "value": "33"},
                    "pressure": {"unit": "mb", "value": "0"},
                    "pubTime": "2024-03-26T13:20:47+0100",
                    "temperature": {"unit": "℃", "value": "33"},
                    "uvIndex": "0",
                    "visibility": {"unit": "km", "value": "0"},
                    "weather": "1",
                    "wind": {
                        "direction": {"unit": "°", "value": "133"},
                        "speed": {"unit": "km/h", "value": "33"},
                    },
                },
                "aqiModel": {
                    "aqi": None,
                    "co": None,
                    "no2": None,
                    "o3": None,
                    "pm10": None,
                    "pm25": None,
                    "pubTime": None,
                    "so2": None,
                },
            }
        )

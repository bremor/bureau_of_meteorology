import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from homeassistant.components.sensor import SensorEntityDescription

from custom_components.bureau_of_meteorology.PyBoM.collector import Collector
from custom_components.bureau_of_meteorology.PyBoM.helpers import (
    flatten_dict,
    geohash_encode,
)
from custom_components.bureau_of_meteorology.sensor import (
    ForecastSensor,
    ObservationSensor,
    calculate_dew_point,
)
from custom_components.bureau_of_meteorology.weather import WeatherDaily, WeatherHourly


@pytest.mark.parametrize(
    ("latitude", "longitude", "precision", "expected"),
    [
        (-12.463763, 130.844398, 7, "qvv117j"),
        (-12.463302612304688, 130.84510803222656, 7, "qvv117n"),
        (0, 0, 6, "7zzzzz"),
    ],
)
def test_geohash_encode_known_values(latitude, longitude, precision, expected):
    assert geohash_encode(latitude, longitude, precision) == expected


def test_flatten_dict_mutates_in_place_and_keeps_none_values():
    payload = {"amount": {"min": 2, "max": 5}, "chance": 40}
    result = flatten_dict(["amount"], payload)

    assert result is payload
    assert payload == {"chance": 40, "amount_min": 2, "amount_max": 5}

    payload_with_none = {"amount": None, "chance": 40}
    flatten_dict(["amount"], payload_with_none)

    assert payload_with_none == {"amount": None, "chance": 40}


@pytest.mark.parametrize(
    ("temperature", "humidity", "expected"),
    [
        (25, 50, 13.8),
        (30, 80, 26.2),
        (20, 60, 12.0),
    ],
)
def test_calculate_dew_point_matches_tetens_formula(temperature, humidity, expected):
    assert calculate_dew_point(temperature, humidity) == expected


@pytest.mark.asyncio
async def test_weather_daily_forecast_builds_expected_dicts():
    collector = Collector(-12.463763, 130.844398)
    collector.locations_data = {"data": {"timezone": "Australia/Darwin"}}
    collector.daily_forecasts_data = {
        "data": [
            {
                "date": "2024-01-01T00:00:00+00:00",
                "temp_max": 31,
                "temp_min": 24,
                "icon_descriptor": "sunny",
                "rain_amount_max": 5,
                "rain_chance": 60,
            }
        ]
    }

    weather = WeatherDaily(
        {
            "collector": collector,
            "coordinator": SimpleNamespace(
                async_add_listener=lambda *_args, **_kwargs: None
            ),
        },
        "Home",
    )
    forecasts = await weather.async_forecast_daily()

    assert forecasts == [
        {
            "datetime": "2024-01-01T09:30:00",
            "native_temperature": 31,
            "condition": "sunny",
            "templow": 24,
            "native_precipitation": 5,
            "precipitation_probability": 60,
        }
    ]


@pytest.mark.asyncio
async def test_weather_hourly_forecast_builds_expected_dicts():
    collector = Collector(-12.463763, 130.844398)
    collector.locations_data = {"data": {"timezone": "Australia/Darwin"}}
    collector.hourly_forecasts_data = {
        "data": [
            {
                "time": "2024-01-01T12:00:00+00:00",
                "temp": 29,
                "icon_descriptor": "cloudy",
                "rain_amount_max": 2,
                "rain_chance": 30,
                "wind_direction": 150,
                "wind_speed_kilometre": 18,
                "wind_gust_speed_kilometre": 28,
                "relative_humidity": 55,
                "uv": 4,
            }
        ]
    }

    weather = WeatherHourly(
        {
            "collector": collector,
            "coordinator": SimpleNamespace(
                async_add_listener=lambda *_args, **_kwargs: None
            ),
        },
        "Home",
    )
    forecasts = await weather.async_forecast_hourly()

    assert forecasts == [
        {
            "datetime": "2024-01-01T21:30:00",
            "native_temperature": 29,
            "condition": "cloudy",
            "native_precipitation": 2,
            "precipitation_probability": 30,
            "wind_bearing": 150,
            "native_wind_speed": 18,
            "wind_gust_speed": 28,
            "humidity": 55,
            "uv_index": 4,
        }
    ]


def test_observation_sensor_state_and_attributes_for_temperature_and_dew_point():
    collector = Collector(-12.463763, 130.844398)
    collector.locations_data = {"data": {"timezone": "Australia/Darwin"}}
    collector.observations_data = {
        "data": {
            "temp": 25,
            "humidity": 75,
            "max_temp": {"value": 30, "time": "2024-01-01T00:30:00+00:00"},
            "min_temp": {"value": 18, "time": "2024-01-01T00:30:00+00:00"},
            "station": {"id": "abc"},
        },
        "metadata": {"source": "test"},
    }
    hass_data = {
        "collector": collector,
        "coordinator": SimpleNamespace(
            async_add_listener=lambda *_args, **_kwargs: None
        ),
    }

    temp_sensor = ObservationSensor(
        hass_data, "Home", "temp", SensorEntityDescription(key="temp")
    )
    dew_sensor = ObservationSensor(
        hass_data, "Home", "dew_point", SensorEntityDescription(key="dew_point")
    )
    max_sensor = ObservationSensor(
        hass_data, "Home", "max_temp", SensorEntityDescription(key="max_temp")
    )

    assert temp_sensor.state == 25
    assert dew_sensor.state == 20.3
    assert max_sensor.state == 30
    assert (
        max_sensor.extra_state_attributes["time_observed"]
        == "2024-01-01T10:00:00+09:30"
    )
    assert max_sensor.extra_state_attributes["id"] == "abc"


def test_forecast_sensor_uv_forecast_state_uses_localised_time_and_titlecase():
    collector = Collector(-12.463763, 130.844398)
    collector.locations_data = {"data": {"timezone": "Australia/Darwin"}}
    collector.daily_forecasts_data = {
        "data": [
            {
                "uv_category": "veryhigh",
                "uv_start_time": "2024-01-01T00:00:00Z",
                "uv_end_time": "2024-01-01T03:00:00Z",
                "uv_max_index": 7,
            }
        ],
        "metadata": {},
    }
    hass_data = {
        "collector": collector,
        "coordinator": SimpleNamespace(
            async_add_listener=lambda *_args, **_kwargs: None
        ),
    }
    sensor = ForecastSensor(
        hass_data,
        "Home",
        0,
        "uv_forecast",
        SensorEntityDescription(key="uv_forecast"),
    )

    assert "Sun protection recommended from" in sensor.state
    assert "Very High" in sensor.state
    assert "UV Index predicted to reach 7" in sensor.state


@pytest.mark.asyncio
async def test_format_daily_forecast_data_flattens_and_normalizes_current_day():
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": "sunny",
                "rain": {"amount": {"min": 2, "max": 5}, "chance": 60},
                "uv": {"category": "high"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"is_night": True},
            },
            {
                "icon_descriptor": "sunny",
                "rain": {"amount": {"min": 0, "max": None}, "chance": 10},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:01"},
            },
        ]
    }

    await collector.format_daily_forecast_data()

    today = collector.daily_forecasts_data["data"][0]
    later = collector.daily_forecasts_data["data"][1]

    assert today["icon_descriptor"] == "clear"
    assert today["mdi_icon"] == "mdi:weather-night"
    assert today["rain_chance"] == 60
    assert today["rain_amount_min"] == 2
    assert today["rain_amount_max"] == 5
    assert today["rain_amount_range"] == "2–5"
    assert today["uv_category"] == "high"
    assert today["astronomical_sunrise_time"] == "06:00"
    assert today["now_is_night"] is True

    assert later["icon_descriptor"] == "sunny"
    assert later["mdi_icon"] == "mdi:weather-sunny"
    assert later["rain_amount_min"] == 0
    assert later["rain_amount_max"] == 0
    assert later["rain_amount_range"] == 0
    assert later["uv_category"] == "low"


@pytest.mark.asyncio
async def test_format_hourly_forecast_data_normalizes_each_item_and_formats_rain_ranges():
    collector = Collector(-12.463763, 130.844398)
    collector.hourly_forecasts_data = {
        "data": [
            {
                "icon_descriptor": "mostly_sunny",
                "is_night": True,
                "rain": {"amount": {"min": 1, "max": 3}, "chance": 80},
                "wind": {"speed_kilometre": 10},
            },
            {
                "icon_descriptor": "clear",
                "is_night": False,
                "rain": {"amount": {"min": 4, "max": None}, "chance": 20},
                "wind": {"speed_knot": 8},
            },
        ]
    }

    await collector.format_hourly_forecast_data()

    first = collector.hourly_forecasts_data["data"][0]
    second = collector.hourly_forecasts_data["data"][1]

    assert first["icon_descriptor"] == "clear"
    assert first["mdi_icon"] == "mdi:weather-night"
    assert first["rain_amount_min"] == 1
    assert first["rain_amount_max"] == 3
    assert first["rain_amount_range"] == "1 to 3"
    assert first["rain_chance"] == 80
    assert first["wind_speed_kilometre"] == 10

    assert second["icon_descriptor"] == "sunny"
    assert second["mdi_icon"] == "mdi:weather-sunny"
    assert second["rain_amount_min"] == 4
    assert second["rain_amount_max"] == 4
    assert second["rain_amount_range"] == 4
    assert second["rain_chance"] == 20
    assert second["wind_speed_knot"] == 8

import asyncio
from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from homeassistant.components.sensor import SensorEntityDescription

from custom_components.bureau_of_meteorology.PyBoM.collector import (
    Collector,
    _get_current_hourly_row,
)
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


def test_observation_sensor_attributes_ignore_null_station_data():
    collector = Collector(-12.463763, 130.844398)
    collector.locations_data = {"data": {"timezone": "Australia/Darwin"}}
    collector.observations_data = {
        "data": {
            "temp": 25,
            "station": None,
        },
        "metadata": {"source": "test"},
    }
    hass_data = {
        "collector": collector,
        "coordinator": SimpleNamespace(
            async_add_listener=lambda *_args, **_kwargs: None
        ),
    }

    sensor = ObservationSensor(
        hass_data, "Home", "temp", SensorEntityDescription(key="temp")
    )

    assert sensor.extra_state_attributes == {
        "source": "test",
        "attribution": "Data provided by the Australian Bureau of Meteorology",
    }


@pytest.mark.asyncio
async def test_sensor_registers_coordinator_listener_once(monkeypatch):
    collector = Collector(-12.463763, 130.844398)
    listeners = []

    def async_add_listener(callback):
        listeners.append(callback)
        return lambda: None

    hass_data = {
        "collector": collector,
        "coordinator": SimpleNamespace(async_add_listener=async_add_listener),
    }
    sensor = ObservationSensor(
        hass_data, "Home", "temp", SensorEntityDescription(key="temp")
    )

    monkeypatch.setattr(sensor, "_update_callback", lambda: None)

    await sensor.async_added_to_hass()

    assert len(listeners) == 1


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


@pytest.mark.asyncio
async def test_format_daily_forecast_handles_null_icon_with_hourly_fallback():
    collector = Collector(-12.463763, 130.844398)
    collector.hourly_forecasts_data = {
        "data": [{"icon_descriptor": "shower", "short_text": "Passing shower."}]
    }
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": None,
                "short_text": None,
                "rain": {"amount": {"min": 0, "max": 1}, "chance": 40},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"is_night": True},
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["icon_descriptor"] == "shower"
    assert today["short_text"] == "Passing shower."
    assert today["mdi_icon"] == "mdi:weather-rainy"


@pytest.mark.asyncio
async def test_format_daily_forecast_selects_current_hour_by_timestamp():
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    past = (now - timedelta(hours=2)).isoformat()
    current = now.isoformat()
    future = (now + timedelta(hours=2)).isoformat()

    collector = Collector(-12.463763, 130.844398)
    collector.hourly_forecasts_data = {
        "data": [
            {"time": past, "icon_descriptor": "cloudy", "short_text": "Past cloudy."},
            {"time": current, "icon_descriptor": "shower", "short_text": "Current shower."},
            {"time": future, "icon_descriptor": "rain", "short_text": "Future rain."},
        ]
    }
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": None,
                "short_text": None,
                "rain": {"amount": {"min": 0, "max": 1}, "chance": 40},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"is_night": True},
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["icon_descriptor"] == "shower"
    assert today["short_text"] == "Current shower."
    assert today["mdi_icon"] == "mdi:weather-rainy"


@pytest.mark.asyncio
async def test_format_daily_forecast_handles_null_icon_without_hourly_fallback():
    collector = Collector(-12.463763, 130.844398)
    collector.hourly_forecasts_data = {"data": []}
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": None,
                "short_text": None,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"is_night": True},
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["icon_descriptor"] is None
    assert today["short_text"] is None
    assert today["mdi_icon"] is None


@pytest.mark.asyncio
async def test_format_hourly_forecast_data_handles_null_icon_safely():
    collector = Collector(-12.463763, 130.844398)
    collector.hourly_forecasts_data = {
        "data": [
            {
                "icon_descriptor": None,
                "is_night": True,
                "rain": {"amount": {"min": 0, "max": 1}},
                "wind": {"speed_kilometre": 10},
            },
            {
                "icon_descriptor": "unrecognized_code",
                "is_night": False,
                "rain": {"amount": {"min": 0, "max": 1}},
                "wind": {"speed_kilometre": 10},
            },
        ]
    }
    await collector.format_hourly_forecast_data()
    first = collector.hourly_forecasts_data["data"][0]
    second = collector.hourly_forecasts_data["data"][1]
    assert first["icon_descriptor"] is None
    assert first["mdi_icon"] is None
    assert second["icon_descriptor"] == "unrecognized_code"
    assert second["mdi_icon"] is None


@pytest.mark.asyncio
async def test_format_daily_forecast_retains_daytime_temp_min_via_now_temp_later():
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": "sunny",
                "temp_min": None,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"is_night": True, "temp_later": 12},
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["temp_min"] == 12


@pytest.mark.asyncio
async def test_format_daily_forecast_retains_temp_min_from_now_sliding_window_evening():
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": "sunny",
                "temp_min": None,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {
                    "is_night": True,
                    "now_label": "Overnight min",
                    "later_label": "Tomorrow's max",
                    "temp_now": 14,
                    "temp_later": 29,
                },
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["temp_min"] == 14


@pytest.mark.asyncio
async def test_format_daily_forecast_retains_temp_min_from_now_sliding_window_daytime():
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": "sunny",
                "temp_min": None,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {
                    "is_night": False,
                    "now_label": "Max",
                    "later_label": "Overnight min",
                    "temp_now": 29,
                    "temp_later": 15,
                },
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["temp_min"] == 15


@pytest.mark.asyncio
async def test_format_daily_forecast_retains_temp_min_from_now_sliding_window_morning_fallback():
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": "sunny",
                "temp_min": None,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {
                    "is_night": False,
                    "now_label": "Min",
                    "later_label": "Max",
                    "temp_now": 13,
                    "temp_later": 25,
                },
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["temp_min"] == 13


def test_get_current_hourly_row_handles_null_empty_and_malformed_structures():
    """Verify null-safety for all forms of missing or non-list hourly forecast data."""
    assert _get_current_hourly_row(None) is None
    assert _get_current_hourly_row({}) is None
    assert _get_current_hourly_row({"data": None}) is None
    assert _get_current_hourly_row({"data": []}) is None
    assert _get_current_hourly_row({"data": "not-a-list"}) is None
    assert _get_current_hourly_row({"data": [None, 123, "string"]}) is None


def test_get_current_hourly_row_matches_time_window_and_timezone_conversions():
    """Verify row selection when now falls within stamp <= now < stamp + 1 hour."""
    t0 = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(hours=1)
    t2 = t0 + timedelta(hours=2)

    hourly_data = {
        "data": [
            {"time": t0.isoformat(), "hour_id": 0},
            {"time": t1.isoformat(), "hour_id": 1},
            {"time": t2.isoformat(), "hour_id": 2},
        ]
    }

    # At exact boundary (13:00:00 UTC) -> should match hour_id 1
    exact_boundary = t1
    match = _get_current_hourly_row(hourly_data, now=exact_boundary)
    assert match is not None and match["hour_id"] == 1

    # Mid-hour (13:45:00 UTC) -> should match hour_id 1
    mid_hour = t1 + timedelta(minutes=45)
    match = _get_current_hourly_row(hourly_data, now=mid_hour)
    assert match is not None and match["hour_id"] == 1

    # End of hour (13:59:59 UTC) -> should match hour_id 1
    end_hour = t1 + timedelta(minutes=59, seconds=59)
    match = _get_current_hourly_row(hourly_data, now=end_hour)
    assert match is not None and match["hour_id"] == 1

    # Timezone conversion: stamp in AWST (+08:00), now in UTC
    awst_tz = timezone(timedelta(hours=8))
    t1_awst = t1.astimezone(awst_tz)
    hourly_data_awst = {
        "data": [
            {"time": t1_awst.isoformat(), "hour_id": "awst_hour"},
        ]
    }
    match = _get_current_hourly_row(hourly_data_awst, now=mid_hour)
    assert match is not None and match["hour_id"] == "awst_hour"

    # Naive datetimes (tzinfo is None on both stamp and now)
    t_naive = datetime(2026, 11, 14, 15, 0, 0)
    hourly_data_naive = {
        "data": [
            {"time": t_naive.isoformat(), "hour_id": "naive_hour"},
        ]
    }
    match = _get_current_hourly_row(hourly_data_naive, now=t_naive + timedelta(minutes=20))
    assert match is not None and match["hour_id"] == "naive_hour"


def test_get_current_hourly_row_picks_nearest_row_when_out_of_bounds():
    """Verify selection of nearest available row when current time is out of exact bounds."""
    t0 = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)
    hourly_data = {
        "data": [
            {"time": t0.isoformat(), "hour_id": "first"},
            {"time": (t0 + timedelta(hours=1)).isoformat(), "hour_id": "second"},
        ]
    }
    # Time in the past: closer to t0 -> picks "first"
    past_now = t0 - timedelta(hours=2)
    assert _get_current_hourly_row(hourly_data, now=past_now)["hour_id"] == "first"

    # Time in the future: closer to t0+1h -> picks "second"
    future_now = t0 + timedelta(hours=5)
    assert _get_current_hourly_row(hourly_data, now=future_now)["hour_id"] == "second"


def test_get_current_hourly_row_falls_back_to_first_row_when_timestamps_unparseable():
    """Verify fallback to rows[0] when all timestamps are malformed or missing."""
    t0 = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)
    malformed_data = {
        "data": [
            {"time": "invalid-timestamp", "hour_id": "malformed_first"},
            {"time": None, "hour_id": "malformed_second"},
        ]
    }
    assert _get_current_hourly_row(malformed_data, now=t0)["hour_id"] == "malformed_first"


@pytest.mark.asyncio
async def test_format_daily_forecast_hourly_fallback_overrides_sunny_and_mostly_sunny_at_night():
    """Verify PR 345: if hourly fallback supplies sunny/mostly_sunny at night, it converts to clear."""
    collector = Collector(-12.463763, 130.844398)
    collector.hourly_forecasts_data = {
        "data": [{"icon_descriptor": "sunny", "short_text": "Clear night sky."}]
    }
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": None,
                "short_text": None,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"is_night": True},
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["icon_descriptor"] == "clear"
    assert today["mdi_icon"] == "mdi:weather-night"
    assert today["short_text"] == "Clear night sky."

    # Also test mostly_sunny -> clear
    collector.hourly_forecasts_data = {
        "data": [{"icon_descriptor": "mostly_sunny", "short_text": "Mostly clear."}]
    }
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": None,
                "short_text": None,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"is_night": True},
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["icon_descriptor"] == "clear"
    assert today["mdi_icon"] == "mdi:weather-night"


@pytest.mark.asyncio
async def test_format_daily_forecast_hourly_fallback_preserves_existing_short_text():
    """Verify that hourly fallback never overwrites pre-existing short_text."""
    collector = Collector(-12.463763, 130.844398)
    collector.hourly_forecasts_data = {
        "data": [{"icon_descriptor": "rain", "short_text": "Heavy rain."}]
    }
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": None,
                "short_text": "BOM original daily forecast text.",
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"is_night": True},
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    # icon was pulled from hourly
    assert today["icon_descriptor"] == "rain"
    assert today["mdi_icon"] == "mdi:weather-pouring"
    # but short_text was preserved!
    assert today["short_text"] == "BOM original daily forecast text."


@pytest.mark.asyncio
async def test_format_daily_forecast_handles_unrecognized_icon_descriptor_safely():
    """Verify that unrecognized icon_descriptor returns mdi_icon=None without KeyError."""
    collector = Collector(-12.463763, 130.844398)
    collector.hourly_forecasts_data = {
        "data": [{"icon_descriptor": "unknown_future_bom_code"}]
    }
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": None,
                "short_text": None,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"is_night": False},
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["icon_descriptor"] == "unknown_future_bom_code"
    assert today["mdi_icon"] is None


@pytest.mark.asyncio
async def test_format_daily_forecast_rain_amount_none_fallback():
    """Verify rain_amount_max fallback when None sets amount_max and amount_range to amount_min."""
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": "sunny",
                "rain": {"amount": {"min": 0, "max": None}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": None,
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["rain_amount_min"] == 0
    assert today["rain_amount_max"] == 0
    assert today["rain_amount_range"] == 0


@pytest.mark.asyncio
async def test_format_daily_forecast_daytime_clear_converts_to_sunny():
    """Verify that during daytime (is_night=False), clear icon_descriptor is converted to sunny."""
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": "clear",
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"is_night": False},
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    assert today["icon_descriptor"] == "sunny"
    assert today["mdi_icon"] == "mdi:weather-sunny"


@pytest.mark.asyncio
async def test_format_hourly_forecast_data_returns_early_when_missing():
    """Verify format_hourly_forecast_data returns gracefully when data is empty or missing."""
    collector = Collector(-12.463763, 130.844398)
    collector.hourly_forecasts_data = None
    await collector.format_hourly_forecast_data()
    assert collector.hourly_forecasts_data is None

    collector.hourly_forecasts_data = {}
    await collector.format_hourly_forecast_data()
    assert collector.hourly_forecasts_data == {}


@pytest.mark.asyncio
async def test_format_daily_forecast_falls_back_is_night_from_hourly_when_missing():
    """Verify is_night falls back to current hourly row when now_is_night is missing from Day 0."""
    collector = Collector(-12.463763, 130.844398)
    collector.hourly_forecasts_data = {
        "data": [
            {
                "is_night": True,
                "icon_descriptor": "sunny",
                "short_text": "Clear starry night.",
            }
        ]
    }
    collector.daily_forecasts_data = {
        "data": [
            {
                "icon_descriptor": None,
                "short_text": None,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {"temp_now": 16},  # No now_is_night
            }
        ]
    }
    await collector.format_daily_forecast_data()
    today = collector.daily_forecasts_data["data"][0]
    # Hourly row had is_night=True, so "sunny" was converted to "clear"
    assert today["icon_descriptor"] == "clear"
    assert today["mdi_icon"] == "mdi:weather-night"


def test_flatten_dict_is_idempotent_and_safe_when_keys_missing():
    """Verify flatten_dict does not raise KeyError when keys are absent or already popped."""
    payload = {"amount": {"min": 2, "max": 5}}
    flatten_dict(["amount"], payload)
    assert payload == {"amount_min": 2, "amount_max": 5}

    # Second call on already flattened dict should not raise KeyError
    flatten_dict(["amount", "nonexistent_key"], payload)
    assert payload == {"amount_min": 2, "amount_max": 5}





def _make_daily_forecast_payload(temp_min=None, temp_max=25, now=None):
    """Helper to generate an unflattened daily forecast payload."""
    row = {
        "icon_descriptor": "sunny",
        "temp_min": temp_min,
        "temp_max": temp_max,
        "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
        "uv": {"category": "low"},
        "astronomical": {"sunrise_time": "06:00"},
    }
    if now is not None:
        row["now"] = dict(now)
    return {"data": [row]}


@pytest.mark.asyncio
async def test_format_daily_forecast_preserves_existing_temp_min():
    """Verify pre-existing temp_min (e.g. 18 or 0 C) is never overridden by now window."""
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=18,
        now={
            "is_night": True,
            "now_label": "Overnight min",
            "later_label": "Tomorrow's max",
            "temp_now": 14,
            "temp_later": 29,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] == 18

    # Also verify freezing 0 C is preserved and not treated as None/falsy
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=0,
        now={
            "is_night": True,
            "now_label": "Overnight min",
            "later_label": "Tomorrow's max",
            "temp_now": 14,
            "temp_later": 29,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] == 0


@pytest.mark.asyncio
async def test_format_daily_forecast_handles_freezing_and_subzero_temperatures():
    """Verify 0 C and sub-zero temperatures (e.g. alpine regions) are correctly assigned."""
    collector = Collector(-12.463763, 130.844398)
    # 0 C overnight min in now_temp_now
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": True,
            "now_label": "Overnight min",
            "later_label": "Tomorrow's max",
            "temp_now": 0,
            "temp_later": 16,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] == 0

    # Sub-zero (-4 C) overnight min in now_temp_now
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": True,
            "now_label": "Overnight min",
            "later_label": "Tomorrow's max",
            "temp_now": -4,
            "temp_later": 16,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] == -4

    # Sub-zero (-2 C) overnight min in now_temp_later during daytime
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": False,
            "now_label": "Max",
            "later_label": "Overnight min",
            "temp_now": 12,
            "temp_later": -2,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] == -2


@pytest.mark.asyncio
async def test_format_daily_forecast_handles_float_temperatures():
    """Verify float temperatures (e.g. 14.5 C) are preserved correctly."""
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": True,
            "now_label": "Overnight min",
            "later_label": "Tomorrow's max",
            "temp_now": 14.5,
            "temp_later": 29.2,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] == 14.5


@pytest.mark.asyncio
async def test_format_daily_forecast_sliding_window_label_variations():
    """Verify case-insensitivity and phrasing variations matching 'min'."""
    collector = Collector(-12.463763, 130.844398)
    # Uppercase 'MIN'
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": False,
            "now_label": "MIN",
            "later_label": "MAX",
            "temp_now": 11,
            "temp_later": 24,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] == 11

    # Later label uppercase 'OVERNIGHT MIN'
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": False,
            "now_label": "Max",
            "later_label": "OVERNIGHT MIN",
            "temp_now": 28,
            "temp_later": 16,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] == 16


@pytest.mark.asyncio
async def test_format_daily_forecast_sliding_window_ignores_max_only_labels():
    """Verify that if neither label contains 'min', temp_min is NOT set to a max temperature."""
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": False,
            "now_label": "Max",
            "later_label": "Tomorrow's max",
            "temp_now": 28,
            "temp_later": 30,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] is None


@pytest.mark.asyncio
async def test_format_daily_forecast_sliding_window_missing_temp_in_min_slot():
    """Verify that if the min slot label is present but temp is None, temp_min stays None."""
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": True,
            "now_label": "Overnight min",
            "later_label": "Tomorrow's max",
            "temp_now": None,
            "temp_later": 29,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] is None


@pytest.mark.asyncio
async def test_format_daily_forecast_multi_day_isolation():
    """Verify that sliding now window only affects Day 0 and leaves Day 1..N untouched."""
    collector = Collector(-12.463763, 130.844398)
    collector.daily_forecasts_data = {
        "data": [
            {
                "date": "2026-11-14T00:00:00Z",
                "icon_descriptor": "sunny",
                "temp_min": None,
                "temp_max": 27,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 0},
                "uv": {"category": "low"},
                "astronomical": {"sunrise_time": "06:00"},
                "now": {
                    "is_night": True,
                    "now_label": "Overnight min",
                    "later_label": "Tomorrow's max",
                    "temp_now": 15,
                    "temp_later": 29,
                },
            },
            {
                "date": "2026-11-15T00:00:00Z",
                "icon_descriptor": "shower",
                "temp_min": 17,
                "temp_max": 28,
                "rain": {"amount": {"min": 1, "max": 5}, "chance": 60},
                "uv": {"category": "veryhigh"},
                "astronomical": {"sunrise_time": "06:00"},
            },
            {
                "date": "2026-11-16T00:00:00Z",
                "icon_descriptor": "mostly_sunny",
                "temp_min": 0,
                "temp_max": 18,
                "rain": {"amount": {"min": 0, "max": 0}, "chance": 10},
                "uv": {"category": "high"},
                "astronomical": {"sunrise_time": "06:00"},
            },
        ]
    }
    await collector.format_daily_forecast_data()
    days = collector.daily_forecasts_data["data"]
    assert days[0]["temp_min"] == 15
    assert days[0]["temp_max"] == 27
    assert days[1]["temp_min"] == 17
    assert days[1]["temp_max"] == 28
    assert days[2]["temp_min"] == 0
    assert days[2]["temp_max"] == 18


@pytest.mark.asyncio
async def test_format_daily_forecast_empty_or_missing_labels_fallback():
    """Verify fallback behavior when now/later labels are absent or empty string."""
    collector = Collector(-12.463763, 130.844398)
    # Both labels None, temp_later present
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": True,
            "now_label": None,
            "later_label": None,
            "temp_now": 12,
            "temp_later": 16,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] == 16

    # Both labels empty strings, only temp_now present
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": True,
            "now_label": "",
            "later_label": "",
            "temp_now": 12,
            "temp_later": None,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] == 12

    # Both labels empty strings, neither temp present
    collector.daily_forecasts_data = _make_daily_forecast_payload(
        temp_min=None,
        now={
            "is_night": True,
            "now_label": "",
            "later_label": "",
            "temp_now": None,
            "temp_later": None,
        },
    )
    await collector.format_daily_forecast_data()
    assert collector.daily_forecasts_data["data"][0]["temp_min"] is None



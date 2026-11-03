"""Refresh failures must not publish retained weather data as current."""

from copy import deepcopy
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock

import aiohttp
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from custom_components.bureau_of_meteorology.PyBoM import collector as collector_module  # noqa: E402
from custom_components.bureau_of_meteorology.PyBoM.collector import Collector  # noqa: E402
from custom_components.bureau_of_meteorology.weather import WeatherDaily  # noqa: E402


class Response:
    def __init__(self, payload=None, status=200, error=None):
        self.payload = payload
        self.status = status
        self.error = error

    async def __aenter__(self):
        if self.error is not None:
            raise self.error
        return self

    async def __aexit__(self, *_args):
        return False

    async def json(self):
        return deepcopy(self.payload)


class Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    def get(self, _url):
        self.calls += 1
        return next(self.responses)


def successful_responses():
    return [
        Response({"data": {"wind": None, "gust": None, "temp": 21}}),
        Response({"data": []}),
        Response({"data": []}),
        Response({"data": []}),
    ]


@pytest.fixture
def collector(monkeypatch):
    monkeypatch.setattr(collector_module.asyncio, "sleep", AsyncMock())
    instance = Collector(-31.95, 115.86)
    instance.locations_data = {"data": {"timezone": "Australia/Perth"}}
    return instance


@pytest.mark.asyncio
async def test_http_failure_stays_failed_after_later_endpoints_succeed(
    collector, monkeypatch
):
    session = Session(
        [Response(status=503) for _ in range(3)] + successful_responses()[1:]
    )
    monkeypatch.setattr(
        collector_module.aiohttp, "ClientSession", lambda **_kw: session
    )

    await collector.async_update()

    assert session.calls == 6
    assert collector.last_update_success is False
    assert collector.daily_forecasts_data == {"data": []}


@pytest.mark.asyncio
async def test_transport_failure_with_cache_is_failed_and_does_not_refresh_age(
    collector, monkeypatch
):
    retained = {"data": {"wind": None, "gust": None, "temp": 19}}
    collector._cache["observations"] = {"data": retained, "timestamp": 1}
    session = Session(
        [Response(error=aiohttp.ClientConnectionError("offline")) for _ in range(3)]
        + successful_responses()[1:]
    )
    monkeypatch.setattr(
        collector_module.aiohttp, "ClientSession", lambda **_kw: session
    )

    await collector.async_update()

    assert collector.last_update_success is False
    assert collector.observations_data["data"]["temp"] == 19
    assert collector._cache["observations"]["timestamp"] == 1


@pytest.mark.asyncio
async def test_transport_failure_without_cache_is_failed(collector, monkeypatch):
    session = Session(
        [Response(error=aiohttp.ClientConnectionError("offline")) for _ in range(3)]
        + successful_responses()[1:]
    )
    monkeypatch.setattr(
        collector_module.aiohttp, "ClientSession", lambda **_kw: session
    )

    await collector.async_update()

    assert collector.last_update_success is False
    assert collector.observations_data is None


@pytest.mark.asyncio
async def test_formatter_error_is_failed(collector, monkeypatch):
    session = Session(successful_responses())
    monkeypatch.setattr(
        collector_module.aiohttp, "ClientSession", lambda **_kw: session
    )
    monkeypatch.setattr(
        collector,
        "format_daily_forecast_data",
        AsyncMock(side_effect=ValueError("bad payload")),
    )

    await collector.async_update()

    assert collector.last_update_success is False


@pytest.mark.asyncio
async def test_throttled_failure_stays_failed_and_successful_refresh_recovers(
    collector, monkeypatch
):
    weather = WeatherDaily(
        {"collector": collector, "coordinator": SimpleNamespace(last_update_success=True)},
        "Home",
    )
    failed_session = Session(
        [Response(status=503) for _ in range(3)] + successful_responses()[1:]
    )
    monkeypatch.setattr(
        collector_module.aiohttp, "ClientSession", lambda **_kw: failed_session
    )
    await collector.async_update()
    assert collector.last_update_success is False
    assert weather.available is False

    good_session = Session(successful_responses())
    monkeypatch.setattr(
        collector_module.aiohttp, "ClientSession", lambda **_kw: good_session
    )
    await collector.async_update()
    assert good_session.calls == 0
    assert collector.last_update_success is False
    assert weather.available is False

    await collector.async_update(no_throttle=True)
    assert good_session.calls == 4
    assert collector.last_update_success is True
    assert collector.observations_data["data"]["temp"] == 21
    assert weather.available is True


@pytest.mark.asyncio
async def test_initial_state_is_unavailable_and_successful_retry_recovers(
    collector, monkeypatch
):
    assert collector.last_update_success is False
    responses = successful_responses()
    session = Session([Response(status=503)] + responses)
    monkeypatch.setattr(
        collector_module.aiohttp, "ClientSession", lambda **_kw: session
    )

    await collector.async_update()

    assert session.calls == 5
    assert collector.last_update_success is True

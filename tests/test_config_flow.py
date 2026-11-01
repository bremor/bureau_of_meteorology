import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.data_entry_flow import FlowResultType

from custom_components.bureau_of_meteorology.config_flow import ConfigFlow
from custom_components.bureau_of_meteorology.const import (
    CONF_FORECASTS_BASENAME,
    CONF_FORECASTS_CREATE,
    CONF_FORECASTS_DAYS,
    CONF_FORECASTS_MONITORED,
    CONF_OBSERVATIONS_BASENAME,
    CONF_OBSERVATIONS_CREATE,
    CONF_OBSERVATIONS_MONITORED,
    CONF_WARNINGS_BASENAME,
    CONF_WARNINGS_CREATE,
    CONF_WEATHER_NAME,
)


@pytest.fixture
def entry_data():
    return {
        CONF_LATITUDE: -34.9,
        CONF_LONGITUDE: 138.6,
        CONF_WEATHER_NAME: "Home",
        CONF_OBSERVATIONS_CREATE: True,
        CONF_FORECASTS_CREATE: True,
        CONF_WARNINGS_CREATE: True,
        CONF_OBSERVATIONS_BASENAME: "Station",
        CONF_OBSERVATIONS_MONITORED: ["temp"],
        CONF_FORECASTS_BASENAME: "Forecast",
        CONF_FORECASTS_MONITORED: ["temp_max"],
        CONF_FORECASTS_DAYS: 5,
        CONF_WARNINGS_BASENAME: "Warnings",
    }


def make_flow(data, options):
    entry = SimpleNamespace(data=data, options=options)
    flow = ConfigFlow.async_get_options_flow(entry)
    flow.hass = SimpleNamespace(config=SimpleNamespace(latitude=-35.0, longitude=139.0))
    flow.collector = SimpleNamespace(
        locations_data={"data": {"name": "Location"}},
        observations_data={"data": {"station": {"name": "Weather station"}}},
        get_locations_data=AsyncMock(),
        async_update=AsyncMock(),
    )
    return flow


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ["data", "options", "fallback"])
@pytest.mark.parametrize(
    ("step", "keys"),
    [
        ("init", [CONF_LATITUDE, CONF_LONGITUDE]),
        ("weather_name", [CONF_WEATHER_NAME]),
        (
            "sensors_create",
            [CONF_OBSERVATIONS_CREATE, CONF_FORECASTS_CREATE, CONF_WARNINGS_CREATE],
        ),
        (
            "observations_monitored",
            [CONF_OBSERVATIONS_BASENAME, CONF_OBSERVATIONS_MONITORED],
        ),
        (
            "forecasts_monitored",
            [CONF_FORECASTS_BASENAME, CONF_FORECASTS_MONITORED, CONF_FORECASTS_DAYS],
        ),
        ("warnings_basename", [CONF_WARNINGS_BASENAME]),
    ],
)
async def test_options_forms_use_entry_defaults(entry_data, source, step, keys):
    options = {
        **entry_data,
        CONF_LATITUDE: -33.8,
        CONF_LONGITUDE: 151.2,
        CONF_WEATHER_NAME: "Updated home",
        CONF_OBSERVATIONS_CREATE: False,
        CONF_FORECASTS_CREATE: False,
        CONF_WARNINGS_CREATE: False,
        CONF_OBSERVATIONS_BASENAME: "Updated station",
        CONF_OBSERVATIONS_MONITORED: ["humidity"],
        CONF_FORECASTS_BASENAME: "Updated forecast",
        CONF_FORECASTS_MONITORED: ["temp_min"],
        CONF_FORECASTS_DAYS: 3,
        CONF_WARNINGS_BASENAME: "Updated warnings",
    }
    fallback = {
        CONF_LATITUDE: -35.0,
        CONF_LONGITUDE: 139.0,
        CONF_WEATHER_NAME: "Location",
        CONF_OBSERVATIONS_CREATE: True,
        CONF_FORECASTS_CREATE: True,
        CONF_WARNINGS_CREATE: True,
        CONF_OBSERVATIONS_BASENAME: "Weather station",
        CONF_OBSERVATIONS_MONITORED: None,
        CONF_FORECASTS_BASENAME: "Location",
        CONF_FORECASTS_MONITORED: None,
        CONF_FORECASTS_DAYS: 0,
        CONF_WARNINGS_BASENAME: "Location",
    }
    flow = make_flow(
        {} if source == "fallback" else entry_data,
        options if source == "options" else {},
    )

    result = await getattr(flow, f"async_step_{step}")()

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == step
    expected = {"data": entry_data, "options": options, "fallback": fallback}[source]
    defaults = {key.schema: key.default() for key in result["data_schema"].schema}
    assert defaults == {key: expected[key] for key in keys}


@pytest.mark.asyncio
async def test_options_flow_completes_without_changing_entry_data(
    entry_data, monkeypatch
):
    original_data = entry_data.copy()
    flow = make_flow(entry_data, {})
    collector = flow.collector
    monkeypatch.setattr(
        "custom_components.bureau_of_meteorology.config_flow.Collector",
        lambda *_args: collector,
    )
    submitted = {}

    for step, keys in [
        ("init", [CONF_LATITUDE, CONF_LONGITUDE]),
        ("weather_name", [CONF_WEATHER_NAME]),
        (
            "sensors_create",
            [CONF_OBSERVATIONS_CREATE, CONF_FORECASTS_CREATE, CONF_WARNINGS_CREATE],
        ),
        (
            "observations_monitored",
            [CONF_OBSERVATIONS_BASENAME, CONF_OBSERVATIONS_MONITORED],
        ),
        (
            "forecasts_monitored",
            [CONF_FORECASTS_BASENAME, CONF_FORECASTS_MONITORED, CONF_FORECASTS_DAYS],
        ),
        ("warnings_basename", [CONF_WARNINGS_BASENAME]),
    ]:
        user_input = {key: entry_data[key] for key in keys}
        submitted.update(user_input)
        result = await getattr(flow, f"async_step_{step}")(user_input)
        assert not result.get("errors")

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == submitted
    assert entry_data == original_data
    collector.get_locations_data.assert_awaited_once()
    collector.async_update.assert_awaited_once()

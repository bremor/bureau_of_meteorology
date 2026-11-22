"""Config entry setup must be retried when BOM cannot be reached."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components import bureau_of_meteorology as integration
from custom_components.bureau_of_meteorology.const import COLLECTOR, DOMAIN
from custom_components.bureau_of_meteorology.PyBoM import collector as collector_module


class OfflineSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    def get(self, _url):
        raise aiohttp.ClientConnectionError("offline")


class FakeCoordinator:
    def __init__(self, hass, collector):
        self.hass = hass
        self.collector = collector
        self.async_refresh = AsyncMock()


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setattr(collector_module.asyncio, "sleep", AsyncMock())
    monkeypatch.setattr(integration, "BomDataUpdateCoordinator", FakeCoordinator)
    hass = SimpleNamespace(
        data={},
        config_entries=SimpleNamespace(async_forward_entry_setups=AsyncMock()),
    )
    entry = SimpleNamespace(
        entry_id="entry",
        data={CONF_LATITUDE: -37.81, CONF_LONGITUDE: 144.96},
        add_update_listener=MagicMock(),
    )
    return hass, entry


@pytest.mark.asyncio
async def test_setup_entry_raises_not_ready_when_bom_unreachable(
    setup_env, monkeypatch
):
    hass, entry = setup_env
    monkeypatch.setattr(
        collector_module.aiohttp, "ClientSession", lambda **_kw: OfflineSession()
    )

    with pytest.raises(ConfigEntryNotReady):
        await integration.async_setup_entry(hass, entry)

    hass.config_entries.async_forward_entry_setups.assert_not_awaited()
    assert entry.entry_id not in hass.data.get(DOMAIN, {})


@pytest.mark.asyncio
async def test_setup_entry_forwards_platforms_when_location_data_loaded(
    setup_env, monkeypatch
):
    hass, entry = setup_env

    async def fake_update(self):
        self.locations_data = {"data": {"timezone": "Australia/Melbourne"}}

    monkeypatch.setattr(collector_module.Collector, "async_update", fake_update)

    assert await integration.async_setup_entry(hass, entry) is True

    hass.config_entries.async_forward_entry_setups.assert_awaited_once()
    assert hass.data[DOMAIN][entry.entry_id][COLLECTOR].locations_data is not None

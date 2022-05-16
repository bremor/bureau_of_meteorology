"""The BOM integration."""
import asyncio
import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import debounce
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .PyBoM.collector import Collector
from .const import (CONF_WEATHER_NAME,
                    CONF_FORECASTS_BASENAME,
                    DOMAIN, COLLECTOR, COORDINATOR)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "weather"]

DEFAULT_SCAN_INTERVAL = datetime.timedelta(minutes=10)
DEBOUNCE_TIME = 60  # in seconds

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the BOM component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:

        new = {**config_entry.data}
        if CONF_FORECASTS_BASENAME in new:
            new[CONF_WEATHER_NAME] = config_entry.data[CONF_FORECASTS_BASENAME]

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BOM from a config entry."""
    collector = Collector(
        entry.data[CONF_LATITUDE],
        entry.data[CONF_LONGITUDE]
    )

    await collector.async_update()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"BOM observation {collector.locations_data['data']['name']}",
        update_method=collector.async_update,
        update_interval=DEFAULT_SCAN_INTERVAL,
        request_refresh_debouncer=debounce.Debouncer(
            hass, _LOGGER, cooldown=DEBOUNCE_TIME, immediate=True
        )
    )

    await coordinator.async_refresh()

    hass_data = hass.data.setdefault(DOMAIN, {})
    hass_data[entry.entry_id] = {
        COLLECTOR: collector,
        COORDINATOR: coordinator,
    }

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

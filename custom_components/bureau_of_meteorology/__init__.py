"""The BOM integration."""
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant

from .PyBoM.collector import Collector
from .const import DOMAIN

PLATFORMS = ["sensor", "weather"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the BOM component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BOM from a config entry."""
    collector = Collector(
        entry.data[CONF_LATITUDE],
        entry.data[CONF_LONGITUDE]
    )

    await collector.get_location_name()
    await collector.get_observations_data()
    await collector.get_daily_forecasts_data()

    hass.data[DOMAIN][entry.entry_id] = collector

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

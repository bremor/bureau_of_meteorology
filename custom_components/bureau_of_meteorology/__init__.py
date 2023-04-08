"""The BOM integration."""
import asyncio
import datetime
import logging

from aiohttp.client_exceptions import ClientConnectorError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import debounce
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    COLLECTOR,
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
    COORDINATOR,
    DOMAIN,
    UPDATE_LISTENER,
)
from .PyBoM.collector import Collector

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "weather"]

DEFAULT_SCAN_INTERVAL = datetime.timedelta(minutes=5)
DEBOUNCE_TIME = 60  # in seconds


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the BOM component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
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
    collector = Collector(entry.data[CONF_LATITUDE], entry.data[CONF_LONGITUDE])

    try:
        await collector.async_update()
    except ClientConnectorError as ex:
        raise ConfigEntryNotReady from ex

    coordinator = BomDataUpdateCoordinator(hass=hass, collector=collector)
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

    update_listener = entry.add_update_listener(async_update_options)
    hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER] = update_listener

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle config entry updates."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Remove unconfigured entities and unload the config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    entity_registry = er.async_get(hass)
    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    entities_to_keep = []

    # if observations are enabled, keep the configured observation sensors
    if entry.options.get(CONF_OBSERVATIONS_CREATE) is True:
        for observation in entry.options.get(CONF_OBSERVATIONS_MONITORED):
            entities_to_keep.append(
                f"sensor.{str(entry.options.get(CONF_OBSERVATIONS_BASENAME)).lower()}_{str(observation).lower()}"
            )

    # if forecasts are enabled, keep the configured forecast sensors
    if entry.options.get(CONF_FORECASTS_CREATE) is True:
        for day in range(0, entry.options.get(CONF_FORECASTS_DAYS, 0) + 1):
            for forecast in entry.options.get(CONF_FORECASTS_MONITORED):
                if forecast in [
                    "now_now_label",
                    "now_temp_now",
                    "now_later_label",
                    "now_temp_later",
                ]:
                    if day == 0:
                        entities_to_keep.append(
                            f"sensor.{str(entry.options.get(CONF_FORECASTS_BASENAME)).lower()}_{str(forecast).lower()}"
                        )
                    else:
                        entities_to_keep.append(
                            f"sensor.{str(entry.options.get(CONF_FORECASTS_BASENAME)).lower()}_{str(day)}_{str(forecast).lower()}"
                        )

    # if warnings are enabled, keep the warnings sensor
    if entry.options.get(CONF_WARNINGS_CREATE) is True:
        basename = entry.options.get(CONF_WARNINGS_BASENAME)
        if basename is None:
            basename = entry.options.get(CONF_FORECASTS_BASENAME)
            if basename:
                entities_to_keep.append(f"sensor.{str(basename).lower()}_warnings")

    # if the weather entity basename has not changed, keep the weather entities
    weather_name = entry.options.get(
        CONF_WEATHER_NAME, entry.data.get(CONF_WEATHER_NAME, "Home")
    )
    entities_to_keep.append(f"weather.{str(weather_name).lower()}")
    entities_to_keep.append(f"weather.{str(weather_name).lower()}_hourly")

    _LOGGER.debug("Keeping %s", entities_to_keep)

    # remove any sensors that are not configured
    for entity in entities:
        if entity.entity_id not in entities_to_keep:
            entity_registry.async_remove(entity_id=entity.entity_id)
            _LOGGER.debug("Removing %s from entity registry", entity.entity_id)

    if unload_ok:
        update_listener = hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER]
        update_listener()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class BomDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Bureau of Meteorology."""

    def __init__(self, hass: HomeAssistant, collector: Collector) -> None:
        """Initialise the data update coordinator."""
        self.collector = collector
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_method=self.collector.async_update,
            update_interval=DEFAULT_SCAN_INTERVAL,
            request_refresh_debouncer=debounce.Debouncer(
                hass, _LOGGER, cooldown=DEBOUNCE_TIME, immediate=True
            ),
        )

        self.entity_registry_updated_unsub = self.hass.bus.async_listen(
            er.EVENT_ENTITY_REGISTRY_UPDATED, self.entity_registry_updated
        )

    @callback
    def entity_registry_updated(self, event):
        """Handle entity registry update events."""
        if event.data["action"] == "remove":
            self.remove_empty_devices()

    def remove_empty_devices(self):
        """Remove devices with no entities."""
        entity_registry = er.async_get(self.hass)
        device_registry = dr.async_get(self.hass)
        device_list = dr.async_entries_for_config_entry(
            device_registry, self.config_entry.entry_id
        )

        for device_entry in device_list:
            entities = er.async_entries_for_device(
                entity_registry, device_entry.id, include_disabled_entities=True
            )

            if not entities:
                _LOGGER.debug("Removing orphaned device: %s", device_entry.name)
                device_registry.async_update_device(
                    device_entry.id, remove_config_entry_id=self.config_entry.entry_id
                )

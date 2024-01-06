"""Platform for sensor integration."""
from __future__ import annotations

import logging
from datetime import datetime, tzinfo

import iso8601
import pytz
from homeassistant.components.weather import Forecast, WeatherEntity, WeatherEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pytz import timezone

from . import BomDataUpdateCoordinator
from .const import (
    ATTRIBUTION,
    COLLECTOR,
    CONF_WEATHER_NAME,
    COORDINATOR,
    DOMAIN,
    MAP_CONDITION,
    SHORT_ATTRIBUTION,
    MODEL_NAME,
)
from .PyBoM.collector import Collector

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    hass_data = hass.data[DOMAIN][config_entry.entry_id]

    new_entities = []

    location_name = config_entry.options.get(
        CONF_WEATHER_NAME, config_entry.data.get(CONF_WEATHER_NAME, "Home")
    )

    new_entities.append(WeatherDaily(hass_data, location_name))
    new_entities.append(WeatherHourly(hass_data, location_name))

    if new_entities:
        async_add_entities(new_entities, update_before_add=False)


class WeatherBase(WeatherEntity):
    """Base representation of a BOM weather entity."""

    def __init__(self, hass_data, location_name) -> None:
        """Initialize the sensor."""
        self.collector: Collector = hass_data[COLLECTOR]
        self.coordinator: BomDataUpdateCoordinator = hass_data[COORDINATOR]
        self.location_name: str = location_name
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self.location_name)},
            manufacturer=SHORT_ATTRIBUTION,
            model=MODEL_NAME,
            name=self.location_name,
        )

    async def async_added_to_hass(self) -> None:
        """Set up a listener and load data."""
        self.async_on_remove(self.coordinator.async_add_listener(self._update_callback))
        self._update_callback()

    async def async_forecast_daily(self) -> list[Forecast]:
        tzinfo = pytz.timezone(self.collector.locations_data["data"]["timezone"])
        return [
            Forecast(
                datetime=iso8601.parse_date(data["date"]).astimezone(tzinfo).isoformat(),
                native_temperature=data["temp_max"],
                condition=MAP_CONDITION[data["icon_descriptor"]],
                templow=data["temp_min"],
                native_precipitation=data["rain_amount_max"],
                precipitation_probability=data["rain_chance"],
            )
            for data in self.collector.daily_forecasts_data["data"]
        ]

    async def async_forecast_hourly(self) -> list[Forecast]:
        tzinfo = pytz.timezone(self.collector.locations_data["data"]["timezone"])
        return [
            Forecast(
                datetime=iso8601.parse_date(data["time"]).astimezone(tzinfo).isoformat(),
                native_temperature=data["temp"],
                condition=MAP_CONDITION[data["icon_descriptor"]],
                native_precipitation=data["rain_amount_max"],
                precipitation_probability=data["rain_chance"],
                wind_bearing=data["wind_direction"],
                native_wind_speed=data["wind_speed_kilometre"],
                wind_gust_speed=data["wind_gust_speed_kilometre"],
                humidity=data["relative_humidity"],
                uv=data["uv"],
            )
            for data in self.collector.hourly_forecasts_data["data"]
        ]

    @property
    def supported_features(self) -> WeatherEntityFeature:
      """Determine supported features based on available data sets reported by WeatherKit."""
      return WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY

    @callback
    def _update_callback(self) -> None:
        """Load data from integration."""
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False

    @property
    def native_temperature(self):
        """Return the platform temperature."""
        return self.collector.observations_data["data"]["temp"]

    @property
    def icon(self):
        """Return the icon."""
        return self.collector.daily_forecasts_data["data"][0]["mdi_icon"]

    @property
    def native_temperature_unit(self):
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def humidity(self):
        """Return the humidity."""
        return self.collector.observations_data["data"]["humidity"]

    @property
    def native_wind_speed(self):
        """Return the wind speed."""
        return self.collector.observations_data["data"]["wind_speed_kilometre"]

    @property
    def native_wind_speed_unit(self):
        """Return the unit of measurement for wind speed."""
        return UnitOfSpeed.KILOMETERS_PER_HOUR

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        return self.collector.observations_data["data"]["wind_direction"]

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def condition(self):
        """Return the current condition."""
        return MAP_CONDITION[
            self.collector.daily_forecasts_data["data"][0]["icon_descriptor"]
        ]

    async def async_update(self):
        await self.coordinator.async_update()


class WeatherDaily(WeatherBase):
    """Representation of a BOM weather entity."""

    def __init__(self, hass_data, location_name):
        """Initialize the sensor."""
        super().__init__(hass_data, location_name)

    async def async_forecast_hourly(self) -> list[Forecast]:
        # Don't implement this feature for this entity
        raise NotImplementedError

    @property
    def supported_features(self):
      return WeatherEntityFeature.FORECAST_DAILY

    @property
    def name(self):
        """Return the name."""
        return self.location_name

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return self.location_name


class WeatherHourly(WeatherBase):
    """Representation of a BOM hourly weather entity."""

    def __init__(self, hass_data, location_name):
        """Initialize the sensor."""
        super().__init__(hass_data, location_name)

    async def async_forecast_daily(self) -> list[Forecast]:
        # Don't implement this feature for this entity
        raise NotImplementedError

    @property
    def supported_features(self):
      return WeatherEntityFeature.FORECAST_HOURLY

    @property
    def name(self):
        """Return the name."""
        return self.location_name + " Hourly"

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return self.location_name + "_hourly"

"""Platform for sensor integration."""
import logging

from homeassistant.components.weather import WeatherEntity
from homeassistant.const import (
    TEMP_CELSIUS, SPEED_KILOMETERS_PER_HOUR,
)
from homeassistant.core import callback

from .const import (
    ATTRIBUTION, COLLECTOR, CONF_WEATHER_NAME, COORDINATOR, DOMAIN,
    MAP_CONDITION,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    hass_data = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []

    if CONF_WEATHER_NAME in config_entry.data:
        location_name = config_entry.data[CONF_WEATHER_NAME]
    elif hasattr(hass_data[COLLECTOR], "location_name"):
        location_name = hass_data[COLLECTOR].location_name
    else:
        location_name = "home"

    new_devices.append(WeatherDaily(hass_data, location_name))
    new_devices.append(WeatherHourly(hass_data, location_name))

    if new_devices:
        async_add_devices(new_devices)


class WeatherBase(WeatherEntity):
    """Base representation of a BOM weather entity."""

    def __init__(self, hass_data, location_name):
        """Initialize the sensor."""
        self.collector = hass_data[COLLECTOR]
        self.coordinator = hass_data[COORDINATOR]
        self.location_name = location_name

    async def async_added_to_hass(self) -> None:
        """Set up a listener and load data."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self._update_callback)
        )
        self.async_on_remove(
            self.coordinator.async_add_listener(self._update_callback)
        )
        self._update_callback()

    @callback
    def _update_callback(self) -> None:
        """Load data from integration."""
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False

    @property
    def temperature(self):
        """Return the platform temperature."""
        return self.collector.observations_data["data"]["temp"]

    @property
    def icon(self):
        """Return the icon."""
        return self.collector.daily_forecasts_data["data"][0]["mdi_icon"]

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def humidity(self):
        """Return the humidity."""
        return self.collector.observations_data["data"]["humidity"]

    @property
    def wind_speed(self):
        """Return the wind speed."""
        return self.collector.observations_data["data"]["wind_speed_kilometre"]

    @property
    def wind_speed_unit(self):
        """Return the unit of measurement for wind speed."""
        return SPEED_KILOMETERS_PER_HOUR

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
        return MAP_CONDITION[self.collector.daily_forecasts_data["data"][0]["icon_descriptor"]]

    async def async_update(self):
        await self.coordinator.async_update()

class WeatherDaily(WeatherBase):
    """Representation of a BOM weather entity."""

    def __init__(self, hass_data, location_name):
        """Initialize the sensor."""
        super().__init__(hass_data, location_name)

    @property
    def name(self):
        """Return the name."""
        return self.location_name

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return self.location_name

    @property
    def forecast(self):
        """Return the forecast."""
        forecasts = []
        days = len(self.collector.daily_forecasts_data["data"])
        for day in range(0, days):
            forecast = {
                "datetime": self.collector.daily_forecasts_data["data"][day]["date"],
                "temperature": self.collector.daily_forecasts_data["data"][day]["temp_max"],
                "condition": MAP_CONDITION[self.collector.daily_forecasts_data["data"][day]["icon_descriptor"]],
                "templow": self.collector.daily_forecasts_data["data"][day]["temp_min"],
                "precipitation": self.collector.daily_forecasts_data["data"][day]["rain_amount_max"],
                "precipitation_probability":  self.collector.daily_forecasts_data["data"][day]["rain_chance"],
            }
            forecasts.append(forecast)
        return forecasts


class WeatherHourly(WeatherBase):
    """Representation of a BOM hourly weather entity."""

    def __init__(self, hass_data, location_name):
        """Initialize the sensor."""
        super().__init__(hass_data, location_name)

    @property
    def name(self):
        """Return the name."""
        return self.location_name + " Hourly"

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return self.location_name + "_hourly"

    @property
    def forecast(self):
        """Return the forecast."""
        forecasts = []
        hours = len(self.collector.hourly_forecasts_data["data"])
        for hour in range(0, hours):
            forecast = {
                "datetime": self.collector.hourly_forecasts_data["data"][hour]["time"],
                "temperature": self.collector.hourly_forecasts_data["data"][hour]["temp"],
                "condition": MAP_CONDITION[self.collector.hourly_forecasts_data["data"][hour]["icon_descriptor"]],
                "precipitation": self.collector.hourly_forecasts_data["data"][hour]["rain_amount_max"],
                "precipitation_probability":  self.collector.hourly_forecasts_data["data"][hour]["rain_chance"],
                "wind_bearing":  self.collector.hourly_forecasts_data["data"][hour]["wind_direction"],
                "wind_speed":  self.collector.hourly_forecasts_data["data"][hour]["wind_speed_kilometre"],
            }
            forecasts.append(forecast)
        return forecasts
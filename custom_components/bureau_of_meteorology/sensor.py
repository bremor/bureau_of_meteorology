"""Platform for sensor integration."""
import logging

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_DATE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
    LENGTH_MILLIMETERS,
    PERCENTAGE,
    TEMP_CELSIUS,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from .const import (ATTRIBUTION,
                    COLLECTOR,
                    CONF_FORECASTS_BASENAME,
                    CONF_FORECASTS_CREATE,
                    CONF_FORECASTS_DAYS,
                    CONF_FORECASTS_MONITORED,
                    CONF_OBSERVATIONS_BASENAME,
                    CONF_OBSERVATIONS_CREATE,
                    CONF_OBSERVATIONS_MONITORED,
                    COORDINATOR,
                    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_NAMES = {
    "temp": [TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE],
    "temp_feels_like": [TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE],
    "rain_since_9am": [LENGTH_MILLIMETERS, None],
    "humidity": [PERCENTAGE, DEVICE_CLASS_HUMIDITY],
    "wind_speed_kilometre": ["km/h", None],
    "wind_speed_knot": ["kts", None],
    "wind_direction": [None, None],
    "gust_speed_kilometre": ["km/h", None],
    "gust_speed_knot": ["kts", None],
    "temp_max": [TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE],
    "temp_min": [TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE],
    "extended_text": [None, None],
    "icon_descriptor": [None, None],
    "mdi_icon": [None, None],
    "short_text": [None, None],
    "uv_category": [None, None],
    "uv_max_index": ["UV", None],
    "uv_start_time": ["UV", DEVICE_CLASS_TIMESTAMP],
    "uv_end_time": ["UV", DEVICE_CLASS_TIMESTAMP],
    "rain_amount_min": [LENGTH_MILLIMETERS, None],
    "rain_amount_max": [LENGTH_MILLIMETERS, None],
    "rain_amount_range": [LENGTH_MILLIMETERS, None],
    "rain_chance": [PERCENTAGE, None],
    "fire_danger": [None, None],
}


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    hass_data = hass.data[DOMAIN][config_entry.entry_id]
    collector = hass_data[COLLECTOR]

    forecast_region = collector.daily_forecasts_data["metadata"]["forecast_region"]
    new_devices = []

    if config_entry.data[CONF_OBSERVATIONS_CREATE] == True:
       for observation in collector.observations_data["data"]:
           if observation in SENSOR_NAMES and observation in config_entry.data[CONF_OBSERVATIONS_MONITORED]:
               new_devices.append(ObservationSensor(hass_data, config_entry.data[CONF_OBSERVATIONS_BASENAME], observation))

    if config_entry.data[CONF_FORECASTS_CREATE] == True:
        days = config_entry.data[CONF_FORECASTS_DAYS]
        for day in range(0, days+1):
            for forecast in config_entry.data[CONF_FORECASTS_MONITORED]:
                new_devices.append(ForecastSensor(hass_data, config_entry.data[CONF_FORECASTS_BASENAME], day, forecast))

    if new_devices:
        async_add_devices(new_devices)


class SensorBase(Entity):
    """Base representation of a BOM Sensor."""

    def __init__(self, hass_data, location_name, sensor_name):
        """Initialize the sensor."""
        self.collector = hass_data[COLLECTOR]
        self.coordinator = hass_data[COORDINATOR]
        self.location_name = location_name
        self.sensor_name = sensor_name
        self.current_state = None

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
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False

    @property
    def device_class(self):
        """Return the name of the sensor."""
        return SENSOR_NAMES[self.sensor_name][1]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_NAMES[self.sensor_name][0]

    async def async_update(self):
        """Refresh the data on the collector object."""
        await self.collector.async_update()

class ObservationSensor(SensorBase):
    """Representation of a BOM Observation Sensor."""

    def __init__(self, hass_data, location_name, sensor_name):
        """Initialize the sensor."""
        super().__init__(hass_data, location_name, sensor_name)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.sensor_name}"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = self.collector.observations_data["metadata"]
        attr.update(self.collector.observations_data["data"]["station"])
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        new_state = self.collector.observations_data["data"][self.sensor_name]
        if new_state is None:
            return self.current_state
        else:
            self.current_state = new_state
            return self.current_state

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {self.sensor_name.replace('_', ' ').title()}"


class ForecastSensor(SensorBase):
    """Representation of a BOM Forecast Sensor."""

    def __init__(self, hass_data, location_name, day, sensor_name):
        """Initialize the sensor."""
        self.day = day
        super().__init__(hass_data, location_name, sensor_name)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.day}_{self.sensor_name}"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = self.collector.daily_forecasts_data["metadata"]
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION

        # If there is no data for this day, do not add attributes for this day.
        if self.day < len(self.collector.daily_forecasts_data["data"]):
            attr[ATTR_DATE] = self.collector.daily_forecasts_data["data"][self.day]["date"]

        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        # If there is no data for this day, return state as 'None'.
        if self.day < len(self.collector.daily_forecasts_data["data"]):

            new_state = self.collector.daily_forecasts_data["data"][self.day][self.sensor_name]
            if type(new_state) == str and len(new_state) > 251:
                    self.current_state = new_state[:251] + '...'
            else:
                self.current_state = new_state

            return self.current_state

        else:
            return None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {self.sensor_name.replace('_', ' ').title()} {self.day}"

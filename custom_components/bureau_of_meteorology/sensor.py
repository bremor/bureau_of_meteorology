"""Platform for sensor integration."""
import logging

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
    LENGTH_MILLIMETERS,
    PERCENTAGE,
    TEMP_CELSIUS,
)
from homeassistant.helpers.entity import Entity
from .const import (ATTRIBUTION,
                    CONF_FORECASTS_BASENAME,
                    CONF_FORECASTS_CREATE,
                    CONF_FORECASTS_DAYS,
                    CONF_FORECASTS_MONITORED,
                    CONF_OBSERVATIONS_BASENAME,
                    CONF_OBSERVATIONS_CREATE,
                    CONF_OBSERVATIONS_MONITORED,
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
    collector = hass.data[DOMAIN][config_entry.entry_id]

    forecast_region = collector.daily_forecasts_data["metadata"]["forecast_region"]
    new_devices = []

    if config_entry.data[CONF_OBSERVATIONS_CREATE] == True:
       for observation in collector.observations_data["data"]:
           if observation in SENSOR_NAMES and observation in config_entry.data[CONF_OBSERVATIONS_MONITORED]:
               new_devices.append(ObservationSensor(collector, config_entry.data[CONF_OBSERVATIONS_BASENAME], observation))

    if config_entry.data[CONF_FORECASTS_CREATE] == True:
        days = config_entry.data[CONF_FORECASTS_DAYS]
        for day in range(0, days+1):
            for forecast in config_entry.data[CONF_FORECASTS_MONITORED]:
                new_devices.append(ForecastSensor(collector, collector.location_name, day, forecast))

    if new_devices:
        async_add_devices(new_devices)


class SensorBase(Entity):
    """Base representation of a BOM Sensor."""

    def __init__(self, collector, location_name, sensor_name):
        """Initialize the sensor."""
        self.collector = collector
        self.location_name = location_name
        self.sensor_name = sensor_name
        self.current_state = None

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

    def __init__(self, collector, location_name, sensor_name):
        """Initialize the sensor."""
        super().__init__(collector, location_name, sensor_name)

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

    def __init__(self, collector, location_name, day, sensor_name):
        """Initialize the sensor."""
        self.day = day
        super().__init__(collector, location_name, sensor_name)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.day}_{self.sensor_name}"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = self.collector.daily_forecasts_data["metadata"]
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.day < len(self.collector.daily_forecasts_data["data"]):
            new_state = self.collector.daily_forecasts_data["data"][self.day][self.sensor_name]
            if new_state is None:
                return self.current_state
            else:
                self.current_state = new_state
                return (new_state[:251] + '...') if type(new_state) == str and len(
                        new_state) > 251 else new_state
        else:
            return None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {self.sensor_name.replace('_', ' ').title()} {self.day}"

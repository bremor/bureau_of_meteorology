"""Platform for sensor integration."""
import logging

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
    #LENGTH_MILLIMETERS,
    #PERCENTAGE,
    TEMP_CELSIUS,
)
from homeassistant.helpers.entity import Entity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

OBSERVATIONS = {
    "temp": ["Temperature", TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE],
    "temp_feels_like": ["Temperature Feels Like", TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE],
    "rain_since_9am": ["Rain Since 9am", "mm", None],
    "humidity": ["Humidity", "%", DEVICE_CLASS_HUMIDITY],
    "wind_speed_kilometre": ["Wind Speed", "km/h", None],
    "wind_speed_knot": ["Wind Speed Knots", "kts", None],
    "wind_direction": ["Wind Direction", None, None],
    "gust_speed_kilometre": ["Gust Speed", "km/h", None],
    "gust_speed_knot": ["Gust Speed Knots", "kts", None],
}

DAILY_FORECAST = {
    "temp_max": ["Max", TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE],
    "temp_min": ["Min", TEMP_CELSIUS, DEVICE_CLASS_TEMPERATURE],
    "extended_text": ["Extended Text", None, None],
    "icon_descriptor": ["Icon", None, None],
    "short_text": ["Short Text", None, None],
    "uv_category": ["UV Category", None, None],
    "uv_max_index": ["UV Max Index", "UV", None],
    "uv_start_time": ["UV Start Time", "UV", DEVICE_CLASS_TIMESTAMP],
    "uv_end_time": ["UV End Time", "UV", DEVICE_CLASS_TIMESTAMP],
    "rain_amount_min": ["Rain Amount Min", "mm", None],
    "rain_amount_max": ["Rain Amount Max", "mm", None],
    "rain_amount_range": ["Rain Amount Range", "mm", None],
    "rain_chance": ["Rain Chance", "%", None],
    "fire_danger": ["Fire Danger", None, None],
}

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    collector = hass.data[DOMAIN][config_entry.entry_id]

    await collector.get_observations_data()
    await collector.get_daily_forecasts_data()
    await collector.get_location_name()

    station_name = collector.observations_data["data"]["station"]["name"]
    forecast_region = collector.daily_forecasts_data["metadata"]["forecast_region"]
    new_devices = []

    for observation in collector.observations_data["data"]:
        if observation in OBSERVATIONS:
            new_devices.append(ObservationSensor(collector, station_name, observation))

    for day in range(0,6):
        for forecast in collector.daily_forecasts_data["data"][day]:
            if forecast in DAILY_FORECAST:
                new_devices.append(ForecastSensor(collector, collector.location_name, day, forecast))
        new_devices.append(ForecastSensor(collector, collector.location_name, day, "rain_amount_range"))

    if new_devices:
        async_add_devices(new_devices)


class ObservationSensor(Entity):
    """Base representation of a BOM Observation Sensor."""

    def __init__(self, collector, station_name, observation):
        """Initialize the sensor."""
        self.collector = collector
        self.station_name = station_name
        self.observation = observation

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.station_name}_{self.observation}"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = self.collector.observations_data["metadata"]
        attr.update(self.collector.observations_data["data"]["station"])
        attr[ATTR_ATTRIBUTION] = "Data provided by the Australian Bureau of Meteorology"
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.collector.observations_data["data"][self.observation]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return OBSERVATIONS[self.observation][1]

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.station_name} {OBSERVATIONS[self.observation][0]}"

    @property
    def device_class(self):
        """Return the name of the sensor."""
        return OBSERVATIONS[self.observation][2]

    async def async_update(self):
        """Refresh the data on the collector object."""
        await self.collector.async_update()


class ForecastSensor(Entity):
    """Base representation of a BOM Forecast Sensor."""

    def __init__(self, collector, location_name, day, forecast):
        """Initialize the sensor."""
        self.collector = collector
        self.location_name = location_name
        self.day = day
        self.forecast = forecast

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.day}_{self.forecast}"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = self.collector.daily_forecasts_data["metadata"]
        attr[ATTR_ATTRIBUTION] = "Data provided by the Australian Bureau of Meteorology"
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.forecast == "rain_amount_range":
            if self.collector.daily_forecasts_data["data"][self.day]["rain_amount_max"] is not None:
                state = "{} to {}".format(
                    self.collector.daily_forecasts_data["data"][self.day]["rain_amount_min"],
                    self.collector.daily_forecasts_data["data"][self.day]["rain_amount_max"]
                )
            else:
                state = self.collector.daily_forecasts_data["data"][self.day]["rain_amount_min"]
        else:
            state = self.collector.daily_forecasts_data["data"][self.day][self.forecast]
        return (state[:251] + '...') if type(state) == str and len(
                state) > 251 else state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the sensor."""
        return DAILY_FORECAST[self.forecast][1]

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {DAILY_FORECAST[self.forecast][0]} {self.day}"

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return DAILY_FORECAST[self.forecast][2]

    async def async_update(self):
        """Refresh the data on the collector object."""
        await self.collector.async_update()

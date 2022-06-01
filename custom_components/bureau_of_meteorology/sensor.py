"""Platform for sensor integration."""
import logging

from homeassistant.const import (
    ATTR_ATTRIBUTION, ATTR_DATE, ATTR_STATE,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

from .const import (
    ATTRIBUTION, COLLECTOR, CONF_FORECASTS_BASENAME, CONF_FORECASTS_CREATE,
    CONF_FORECASTS_DAYS, CONF_FORECASTS_MONITORED, CONF_OBSERVATIONS_BASENAME,
    CONF_OBSERVATIONS_CREATE, CONF_OBSERVATIONS_MONITORED,
    CONF_WARNINGS_CREATE, CONF_WARNINGS_BASENAME,
    COORDINATOR, DOMAIN, SENSOR_NAMES,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    hass_data = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []

    if config_entry.data[CONF_OBSERVATIONS_CREATE] == True:
        for observation in config_entry.data[CONF_OBSERVATIONS_MONITORED]:
            new_devices.append(ObservationSensor(hass_data, config_entry.data[CONF_OBSERVATIONS_BASENAME], observation))

    if config_entry.data[CONF_FORECASTS_CREATE] == True:
        days = config_entry.data[CONF_FORECASTS_DAYS]
        for day in range(0, days+1):
            for forecast in config_entry.data[CONF_FORECASTS_MONITORED]:
                if forecast in ["now_now_label", "now_temp_now", "now_later_label", "now_temp_later"]:
                    if day == 0:
                        new_devices.append(NowLaterSensor(hass_data, config_entry.data[CONF_FORECASTS_BASENAME], forecast))
                else:
                    new_devices.append(ForecastSensor(hass_data, config_entry.data[CONF_FORECASTS_BASENAME], day, forecast))

    if config_entry.data.get(CONF_WARNINGS_CREATE, True) == True:
        basename = config_entry.data.get(CONF_WARNINGS_BASENAME, None)
        if basename is None:
            basename = config_entry.data.get(CONF_FORECASTS_BASENAME, None)
        if basename:
            new_devices.append(WarningsSensor(hass_data, basename, "warnings"))

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
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = self.collector.observations_data["metadata"]
        attr.update(self.collector.observations_data["data"]["station"])
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.sensor_name in self.collector.observations_data["data"]:
            if self.collector.observations_data["data"][self.sensor_name] is not None:
                self.current_state = self.collector.observations_data["data"][self.sensor_name]
            else:
                self.current_state = 'unavailable'
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
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = []

        # If there is no data for this day, do not add attributes for this day.
        if self.day < len(self.collector.daily_forecasts_data["data"]):
            attr = self.collector.daily_forecasts_data["metadata"]
            attr[ATTR_ATTRIBUTION] = ATTRIBUTION
            attr[ATTR_DATE] = self.collector.daily_forecasts_data["data"][self.day]["date"]
            if self.sensor_name.startswith('extended'):
                attr[ATTR_STATE] = self.collector.daily_forecasts_data["data"][self.day]["extended_text"]

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


class WarningsSensor(SensorBase):
    """Representation of a BOM Warnings Sensor."""

    def __init__(self, hass_data, location_name, sensor_name):
        """Initialize the sensor."""
        super().__init__(hass_data, location_name, sensor_name)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.sensor_name}"

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = self.collector.warnings_data["metadata"]
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        attr["warnings"] = self.collector.warnings_data["data"]
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        # If there is no data for this day, return state as 'None'.
        return len(self.collector.warnings_data["data"])

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {self.sensor_name.replace('_', ' ').title()}"


class NowLaterSensor(SensorBase):
    """Representation of a BOM Forecast Sensor."""

    def __init__(self, hass_data, location_name, sensor_name):
        """Initialize the sensor."""
        super().__init__(hass_data, location_name, sensor_name)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.sensor_name}"

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = self.collector.daily_forecasts_data["metadata"]
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        self.current_state = self.collector.daily_forecasts_data["data"][0][self.sensor_name]
        return self.current_state

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {self.sensor_name.replace('_', ' ').title()}"

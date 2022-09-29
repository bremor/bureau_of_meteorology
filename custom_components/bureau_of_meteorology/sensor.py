"""Platform for sensor integration."""
import logging
from datetime import datetime, tzinfo
from typing import Any

import iso8601
import pytz
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_DATE,
    ATTR_STATE,
    DEVICE_CLASS_TIMESTAMP,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo, Entity, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pytz import timezone

from . import BomDataUpdateCoordinator
from .const import (
    ATTRIBUTION,
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
    COORDINATOR,
    DOMAIN,
    SENSOR_NAMES,
    SHORT_ATTRIBUTION,
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
    create_observations = config_entry.options.get(
        CONF_OBSERVATIONS_CREATE, config_entry.data.get(CONF_OBSERVATIONS_CREATE)
    )
    create_forecasts = config_entry.options.get(
        CONF_FORECASTS_CREATE, config_entry.data.get(CONF_FORECASTS_CREATE)
    )
    create_warnings = config_entry.options.get(
        CONF_WARNINGS_CREATE, config_entry.data.get(CONF_WARNINGS_CREATE)
    )

    if create_observations is True:
        observation_basename = config_entry.options.get(
            CONF_OBSERVATIONS_BASENAME,
            config_entry.data.get(CONF_OBSERVATIONS_BASENAME),
        )
        observations = config_entry.options.get(
            CONF_OBSERVATIONS_MONITORED,
            config_entry.data.get(CONF_OBSERVATIONS_MONITORED, None),
        )

        for observation in observations:
            new_entities.append(
                ObservationSensor(
                    hass_data,
                    observation_basename,
                    observation,
                )
            )

    if create_forecasts is True:
        forecast_basename = config_entry.options.get(
            CONF_FORECASTS_BASENAME, config_entry.data.get(CONF_FORECASTS_BASENAME)
        )
        forecast_days = config_entry.options.get(
            CONF_FORECASTS_DAYS, config_entry.data.get(CONF_FORECASTS_DAYS)
        )
        forecasts_monitored = config_entry.options.get(
            CONF_FORECASTS_MONITORED, config_entry.data.get(CONF_FORECASTS_MONITORED)
        )

        for day in range(0, forecast_days + 1):
            for forecast in forecasts_monitored:
                if forecast in [
                    "now_now_label",
                    "now_temp_now",
                    "now_later_label",
                    "now_temp_later",
                ]:
                    if day == 0:
                        new_entities.append(
                            NowLaterSensor(
                                hass_data,
                                forecast_basename,
                                forecast,
                            )
                        )
                else:
                    new_entities.append(
                        ForecastSensor(
                            hass_data,
                            forecast_basename,
                            day,
                            forecast,
                        )
                    )

    if create_warnings is True:
        warnings_basename = config_entry.options.get(
            CONF_WARNINGS_BASENAME,
            config_entry.data.get(
                CONF_WARNINGS_BASENAME,
                config_entry.options.get(
                    CONF_FORECASTS_BASENAME,
                    config_entry.data.get(CONF_FORECASTS_BASENAME, None),
                ),
            ),
        )

        if warnings_basename is not None:
            new_entities.append(
                WarningsSensor(hass_data, warnings_basename, "warnings")
            )

    if new_entities:
        async_add_entities(new_entities, update_before_add=False)


class SensorBase(Entity):
    """Base representation of a BOM Sensor."""

    def __init__(self, hass_data, location_name, sensor_name) -> None:
        """Initialize the sensor."""
        self.collector: Collector = hass_data[COLLECTOR]
        self.coordinator: BomDataUpdateCoordinator = hass_data[COORDINATOR]
        self.location_name: str = location_name
        self.sensor_name: str = sensor_name
        self.current_state: Any = None

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{self.location_name}")},
            manufacturer=SHORT_ATTRIBUTION,
            name=self.location_name,
        )

    async def async_added_to_hass(self) -> None:
        """Set up a listener and load data."""
        self.async_on_remove(self.coordinator.async_add_listener(self._update_callback))
        self.async_on_remove(self.coordinator.async_add_listener(self._update_callback))
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

    def __init__(self, hass_data, location_name, sensor_name) -> None:
        """Initialize the sensor."""
        super().__init__(hass_data, location_name, sensor_name)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.sensor_name}"

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {}

        tzinfo = pytz.timezone(self.collector.locations_data["data"]["timezone"])
        for key in self.collector.observations_data["metadata"]:
            try:
                attr[key] = iso8601.parse_date(self.collector.observations_data["metadata"][key]).astimezone(tzinfo).isoformat()
            except iso8601.ParseError:
                attr[key] = self.collector.observations_data["metadata"][key]

        attr.update(self.collector.observations_data["data"]["station"])
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        if self.sensor_name == "max_temp" or self.sensor_name == "min_temp":
            attr["time_observed"] = iso8601.parse_date(self.collector.observations_data["data"][self.sensor_name]["time"]).astimezone(tzinfo).isoformat()
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.sensor_name in self.collector.observations_data["data"]:
            if self.collector.observations_data["data"][self.sensor_name] is not None:
                if self.sensor_name == "max_temp" or self.sensor_name == "min_temp":
                    self.current_state = self.collector.observations_data["data"][self.sensor_name]["value"]
                else:
                    self.current_state = self.collector.observations_data["data"][self.sensor_name]
            else:
                self.current_state = "unavailable"
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
        attr = {}

        # If there is no data for this day, do not add attributes for this day.
        if self.day < len(self.collector.daily_forecasts_data["data"]):
            tzinfo = pytz.timezone(self.collector.locations_data["data"]["timezone"])
            for key in self.collector.daily_forecasts_data["metadata"]:
                try:
                    attr[key] = iso8601.parse_date(self.collector.daily_forecasts_data["metadata"][key]).astimezone(tzinfo).isoformat()
                except iso8601.ParseError:
                    attr[key] = self.collector.daily_forecasts_data["metadata"][key]
            attr[ATTR_ATTRIBUTION] = ATTRIBUTION
            attr[ATTR_DATE] = iso8601.parse_date(self.collector.daily_forecasts_data["data"][self.day]["date"]).astimezone(tzinfo).isoformat()
            if (self.sensor_name == "fire_danger") and (self.current_state != None):
                if self.collector.daily_forecasts_data["data"][self.day]["fire_danger_category"]["default_colour"]:
                    attr["color_fill"] = self.collector.daily_forecasts_data["data"][self.day]["fire_danger_category"]["default_colour"]
                    attr["color_text"] =  "#ffffff" if (self.collector.daily_forecasts_data["data"][self.day]["fire_danger_category"]["text"] == "Catastrophic") else "#000000"
            if self.sensor_name.startswith("extended"):
                attr[ATTR_STATE] = self.collector.daily_forecasts_data["data"][self.day]["extended_text"]
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        # If there is no data for this day, return state as 'None'.
        if self.day < len(self.collector.daily_forecasts_data["data"]):
            if self.device_class == DEVICE_CLASS_TIMESTAMP:
                tzinfo = pytz.timezone(
                    self.collector.locations_data["data"]["timezone"]
                )
                try:
                    return iso8601.parse_date(self.collector.daily_forecasts_data["data"][self.day][self.sensor_name]).astimezone(tzinfo).isoformat()
                except iso8601.ParseError:
                    return self.collector.daily_forecasts_data["data"][self.day][self.sensor_name]
            if self.sensor_name == "uv_forecast":
                if (self.collector.daily_forecasts_data["data"][self.day]["uv_category"] is None):
                    return None
                if (self.collector.daily_forecasts_data["data"][self.day]["uv_start_time"] is None):
                    return (
                        f"Sun protection not required, UV Index predicted to reach "
                        f'{self.collector.daily_forecasts_data["data"][self.day]["uv_max_index"]} '
                        f'[{self.collector.daily_forecasts_data["data"][self.day]["uv_category"].replace("veryhigh", "very high").title()}]'
                    )
                else:
                    utc = pytz.utc
                    local = timezone(self.collector.locations_data["data"]["timezone"])
                    start_time = utc.localize(datetime.strptime(self.collector.daily_forecasts_data["data"][self.day]["uv_start_time"], "%Y-%m-%dT%H:%M:%SZ")).astimezone(local)
                    end_time = utc.localize(datetime.strptime(self.collector.daily_forecasts_data["data"][self.day]["uv_end_time"], "%Y-%m-%dT%H:%M:%SZ")).astimezone(local)
                    return (
                        f'Sun protection recommended from {start_time.strftime("%-I:%M%p").lower()} to '
                        f'{end_time.strftime("%-I:%M%p").lower()}, UV Index predicted to reach '
                        f'{self.collector.daily_forecasts_data["data"][self.day]["uv_max_index"]} '
                        f'[{self.collector.daily_forecasts_data["data"][self.day]["uv_category"].replace("veryhigh", "very high").title()}]'
                    )
            new_state = self.collector.daily_forecasts_data["data"][self.day][self.sensor_name]
            if type(new_state) == str and len(new_state) > 251:
                self.current_state = new_state[:251] + "..."
            else:
                self.current_state = new_state
            if (self.sensor_name == "uv_category") and (self.current_state != None):
                self.current_state = self.current_state.replace("veryhigh", "very high").title()
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
        self.current_state = self.collector.daily_forecasts_data["data"][0][
            self.sensor_name
        ]
        return self.current_state

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {self.sensor_name.replace('_', ' ').title()}"

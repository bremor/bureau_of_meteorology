"""Platform for sensor integration."""

import logging
from datetime import datetime, timezone
from typing import Any

import iso8601
import zoneinfo
import math  # Required for calculated observations (e.g dew point)
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_DATE,
    ATTR_STATE,
)
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
    SHORT_ATTRIBUTION,
    MODEL_NAME,
    OBSERVATION_SENSOR_TYPES,
    FORECAST_SENSOR_TYPES,
    WARNING_SENSOR_TYPES,
    ATTR_API_NON_NOW_LABEL,
    ATTR_API_NON_TEMP_NOW,
    ATTR_API_NOW_LATER_LABEL,
    ATTR_API_NOW_TEMP_LATER,
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
                    [
                        description
                        for description in OBSERVATION_SENSOR_TYPES
                        if description.key == observation
                    ][0],
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
                    ATTR_API_NON_NOW_LABEL,
                    ATTR_API_NON_TEMP_NOW,
                    ATTR_API_NOW_LATER_LABEL,
                    ATTR_API_NOW_TEMP_LATER,
                ]:
                    if day == 0:
                        new_entities.append(
                            NowLaterSensor(
                                hass_data,
                                forecast_basename,
                                forecast,
                                [
                                    description
                                    for description in FORECAST_SENSOR_TYPES
                                    if description.key == forecast
                                ][0],
                            )
                        )
                else:
                    new_entities.append(
                        ForecastSensor(
                            hass_data,
                            forecast_basename,
                            day,
                            forecast,
                            [
                                description
                                for description in FORECAST_SENSOR_TYPES
                                if description.key == forecast
                            ][0],
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
                WarningsSensor(
                    hass_data,
                    warnings_basename,
                    "warnings",
                    [
                        description
                        for description in WARNING_SENSOR_TYPES
                        if description.key == "warnings"
                    ][0],
                )
            )

    if new_entities:
        async_add_entities(new_entities, update_before_add=False)


class SensorBase(CoordinatorEntity[BomDataUpdateCoordinator], SensorEntity):
    """Base representation of a BOM Sensor."""

    def __init__(
        self,
        hass_data,
        location_name,
        sensor_name,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(hass_data[COORDINATOR])
        self.collector: Collector = hass_data[COLLECTOR]
        self.coordinator: BomDataUpdateCoordinator = hass_data[COORDINATOR]
        self.location_name: str = location_name
        self.sensor_name: str = sensor_name
        self.current_state: Any = None
        self.entity_description = description

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{self.location_name}")},
            manufacturer=SHORT_ATTRIBUTION,
            model=MODEL_NAME,
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

    async def async_update(self):
        """Refresh the data on the collector object."""
        await self.collector.async_update()

    def _location_data(self) -> dict[str, Any]:
        """Return location payload data with a non-optional type."""
        return (self.collector.locations_data or {}).get("data", {})

    def _observations_data(self) -> dict[str, Any]:
        """Return observation payload data with a non-optional type."""
        return (self.collector.observations_data or {}).get("data", {})

    def _observations_metadata(self) -> dict[str, Any]:
        """Return observation payload metadata with a non-optional type."""
        return (self.collector.observations_data or {}).get("metadata", {})

    def _daily_forecasts(self) -> list[dict[str, Any]]:
        """Return daily forecast list with a non-optional type."""
        return (self.collector.daily_forecasts_data or {}).get("data", [])

    def _daily_forecasts_metadata(self) -> dict[str, Any]:
        """Return daily forecast metadata with a non-optional type."""
        return (self.collector.daily_forecasts_data or {}).get("metadata", {})

    def _warnings_data(self) -> dict[str, Any]:
        """Return warnings payload with a non-optional type."""
        return self.collector.warnings_data or {"metadata": {}, "data": []}


class ObservationSensor(SensorBase):
    """Representation of a BOM Observation Sensor."""

    def __init__(
        self,
        hass_data,
        location_name,
        sensor_name,
        description: SensorEntityDescription,
    ):
        """Initialize the sensor."""
        super().__init__(hass_data, location_name, sensor_name, description)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.sensor_name}"

    @property
    def native_value(self):
        """Return the state of the device."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {}

        location_data = self._location_data()
        observations_data = self._observations_data()
        observations_metadata = self._observations_metadata()
        tzinfo = zoneinfo.ZoneInfo(location_data.get("timezone", "UTC"))
        for key in observations_metadata:
            try:
                attr[key] = (
                    iso8601.parse_date(observations_metadata[key])
                    .astimezone(tzinfo)
                    .isoformat()
                )
            except iso8601.ParseError:
                attr[key] = observations_metadata[key]

        attr.update(observations_data.get("station", {}))
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION

        # Only proceed for max_temp or min_temp
        if self.sensor_name not in ("max_temp", "min_temp"):
            return attr

        # Get data safely
        data = observations_data
        if not data:
            return attr

        # Get sensor data safely
        sensor_data = data.get(self.sensor_name)
        if not sensor_data:
            return attr

        # Get time safely
        time_str = sensor_data.get("time")
        if not time_str:
            return attr

        # We have all required data, now add the time_observed attribute
        attr["time_observed"] = (
            iso8601.parse_date(time_str).astimezone(tzinfo).isoformat()
        )
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        observations_data = self._observations_data()
        if self.sensor_name == "dew_point":
            temperature = observations_data.get("temp")
            humidity = observations_data.get("humidity")
            if temperature is not None and humidity is not None:
                return calculate_dew_point(temperature, humidity)
            else:
                return None
        else:
            if self.sensor_name in observations_data:
                if observations_data[self.sensor_name] is not None:
                    if self.sensor_name == "max_temp" or self.sensor_name == "min_temp":
                        return observations_data[self.sensor_name]["value"]
                    else:
                        return observations_data[self.sensor_name]
            else:
                return "unavailable"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {self.sensor_name.replace('_', ' ').title()}"


class ForecastSensor(SensorBase):
    """Representation of a BOM Forecast Sensor."""

    def __init__(
        self,
        hass_data,
        location_name,
        day,
        sensor_name,
        description: SensorEntityDescription,
    ):
        """Initialize the sensor."""
        self.day = day
        super().__init__(hass_data, location_name, sensor_name, description)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.day}_{self.sensor_name}"

    @property
    def native_value(self):
        """Return the state of the device."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {}
        forecasts_data = self._daily_forecasts()
        forecasts_metadata = self._daily_forecasts_metadata()

        # If there is no data for this day, do not add attributes for this day.
        if self.day < len(forecasts_data):
            tzinfo = zoneinfo.ZoneInfo(self._location_data().get("timezone", "UTC"))
            for key in forecasts_metadata:
                try:
                    attr[key] = (
                        iso8601.parse_date(forecasts_metadata[key])
                        .astimezone(tzinfo)
                        .isoformat()
                    )
                except iso8601.ParseError:
                    attr[key] = forecasts_metadata[key]
            attr[ATTR_ATTRIBUTION] = ATTRIBUTION
            attr[ATTR_DATE] = (
                iso8601.parse_date(forecasts_data[self.day]["date"])
                .astimezone(tzinfo)
                .isoformat()
            )
            if (self.sensor_name == "fire_danger") and (self.current_state is not None):
                if forecasts_data[self.day]["fire_danger_category"]["default_colour"]:
                    attr["color_fill"] = forecasts_data[self.day][
                        "fire_danger_category"
                    ]["default_colour"]
                    attr["color_text"] = (
                        "#ffffff"
                        if forecasts_data[self.day]["fire_danger_category"]["text"]
                        == "Catastrophic"
                        else "#000000"
                    )
            if self.sensor_name.startswith("extended"):
                attr[ATTR_STATE] = forecasts_data[self.day]["extended_text"]
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        forecasts_data = self._daily_forecasts()
        # If there is no data for this day, return state as 'None'.
        if self.day < len(forecasts_data):
            if self.device_class == SensorDeviceClass.TIMESTAMP:
                tzinfo = zoneinfo.ZoneInfo(self._location_data().get("timezone", "UTC"))
                try:
                    return (
                        iso8601.parse_date(forecasts_data[self.day][self.sensor_name])
                        .astimezone(tzinfo)
                        .isoformat()
                    )
                except iso8601.ParseError:
                    return forecasts_data[self.day][self.sensor_name]
            if self.sensor_name == "uv_forecast":
                if forecasts_data[self.day]["uv_category"] is None:
                    return None
                if forecasts_data[self.day]["uv_start_time"] is None:
                    return (
                        f"Sun protection not required, UV Index predicted to reach "
                        f"{forecasts_data[self.day]['uv_max_index']} "
                        f"[{forecasts_data[self.day]['uv_category'].replace('veryhigh', 'very high').title()}]"
                    )
                else:
                    utc = timezone.utc
                    local = zoneinfo.ZoneInfo(
                        self._location_data().get("timezone", "UTC")
                    )
                    start_time = (
                        datetime.strptime(
                            forecasts_data[self.day]["uv_start_time"],
                            "%Y-%m-%dT%H:%M:%SZ",
                        )
                        .replace(tzinfo=utc)
                        .astimezone(local)
                    )
                    end_time = (
                        datetime.strptime(
                            forecasts_data[self.day]["uv_end_time"],
                            "%Y-%m-%dT%H:%M:%SZ",
                        )
                        .replace(tzinfo=utc)
                        .astimezone(local)
                    )
                    return (
                        f"Sun protection recommended from {start_time.strftime('%-I:%M%p').lower()} to "
                        f"{end_time.strftime('%-I:%M%p').lower()}, UV Index predicted to reach "
                        f"{forecasts_data[self.day]['uv_max_index']} "
                        f"[{forecasts_data[self.day]['uv_category'].replace('veryhigh', 'very high').title()}]"
                    )
            new_state = forecasts_data[self.day][self.sensor_name]
            if isinstance(new_state, str) and len(new_state) > 251:
                self.current_state = new_state[:251] + "..."
            else:
                self.current_state = new_state
            if (self.sensor_name == "uv_category") and (self.current_state is not None):
                self.current_state = self.current_state.replace(
                    "veryhigh", "very high"
                ).title()
            return self.current_state
        else:
            return None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {self.sensor_name.replace('_', ' ').title()} {self.day}"


class WarningsSensor(SensorBase):
    """Representation of a BOM Warnings Sensor."""

    def __init__(
        self,
        hass_data,
        location_name,
        sensor_name,
        description: SensorEntityDescription,
    ):
        """Initialize the sensor."""
        super().__init__(hass_data, location_name, sensor_name, description)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.sensor_name}"

    @property
    def native_value(self):
        """Return the state of the device."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        warnings_data = self._warnings_data()
        attr = warnings_data["metadata"]
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        attr["warnings"] = warnings_data["data"]
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        # If there is no data for this day, return state as 'None'.
        return len(self._warnings_data()["data"])

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {self.sensor_name.replace('_', ' ').title()}"


class NowLaterSensor(SensorBase):
    """Representation of a BOM Forecast Sensor."""

    def __init__(
        self,
        hass_data,
        location_name,
        sensor_name,
        description: SensorEntityDescription,
    ):
        """Initialize the sensor."""
        super().__init__(hass_data, location_name, sensor_name, description)

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"{self.location_name}_{self.sensor_name}"

    @property
    def native_value(self):
        """Return the state of the device."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = self._daily_forecasts_metadata()
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    @property
    def state(self):
        """Return the state of the sensor."""
        forecasts_data = self._daily_forecasts()
        if not forecasts_data:
            return None
        self.current_state = forecasts_data[0][self.sensor_name]
        return self.current_state

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.location_name} {self.sensor_name.replace('_', ' ').title()}"


def calculate_dew_point(temperature, humidity):
    """Calculate dew point using temperature and humidity observations"""
    a, b = 17.27, 237.7  # Tetens equation constants
    saturation_factor = ((a * temperature) / (b + temperature)) + math.log(
        humidity / 100.0
    )
    dew_point = (b * saturation_factor) / (a - saturation_factor)
    return round(dew_point, 1)

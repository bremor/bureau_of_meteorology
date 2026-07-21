"""Config flow for BOM."""

import math
import logging

import aiohttp
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback

from .const import (
    CONF_FORECAST_LOCATION_GEOHASH,
    CONF_FORECASTS_BASENAME,
    CONF_FORECASTS_CREATE,
    CONF_FORECASTS_DAYS,
    CONF_FORECASTS_MONITORED,
    CONF_OBSERVATION_LOCATION_GEOHASH,
    CONF_OBSERVATIONS_BASENAME,
    CONF_OBSERVATIONS_CREATE,
    CONF_OBSERVATIONS_MONITORED,
    CONF_PLACE_ID,
    CONF_WARNINGS_BASENAME,
    CONF_WARNINGS_CREATE,
    CONF_WEATHER_NAME,
    DOMAIN,
    OBSERVATION_SENSOR_TYPES,
    FORECAST_SENSOR_TYPES,
)
from .PyBoM.collector import Collector
from .PyBoM.helpers import geohash_encode

_LOGGER = logging.getLogger(__name__)

SEARCH_OFFSETS = (0.0, 0.02, -0.02)
DEFAULT_TOP_LOCATION_CHOICES = 3
PLACE_AUTOCOMPLETE_URL = (
    "https://api.bom.gov.au/apikey/v1/locations/places/autocomplete"
)
WEATHER_BOM_LOCATION_URL = "https://api.weather.bom.gov.au/v1/locations/"


def _distance_meters(lat_a, lon_a, lat_b, lon_b):
    """Return approximate distance in meters using equirectangular projection."""
    earth_radius = 6371000
    pi_over_180 = math.pi / 180
    x = (lon_b - lon_a) * pi_over_180 * math.cos((lat_a + lat_b) * pi_over_180 / 2)
    y = (lat_b - lat_a) * pi_over_180
    return (x * x + y * y) ** 0.5 * earth_radius


def _collector_forecast_geohash7(collector: Collector | None) -> str:
    """Return the collector forecast geohash or a safe fallback."""
    if collector is None:
        return ""
    return collector.forecast_geohash7


def _collector_location_name(collector: Collector | None) -> str:
    """Return the collector location name or a safe fallback."""
    if collector is None:
        return "Location"
    return ((collector.locations_data or {}).get("data") or {}).get("name", "Location")


def _collector_observation_station_name(collector: Collector | None) -> str:
    """Return the collector observation station name or a safe fallback."""
    if collector is None:
        return "Observation"
    return (
        ((collector.observations_data or {}).get("data") or {})
        .get("station", {})
        .get("name", "Observation")
    )


async def _get_top_location_choices(
    latitude, longitude, limit=DEFAULT_TOP_LOCATION_CHOICES
):
    """Return the closest canonical BoM places for the given coordinates."""
    headers = {"User-Agent": "MakeThisAPIOpenSource/1.0.0"}
    by_geohash = {}

    async with aiohttp.ClientSession(headers=headers) as session:
        for lat_offset in SEARCH_OFFSETS:
            for lon_offset in SEARCH_OFFSETS:
                query_lat = latitude + lat_offset
                query_lon = longitude + lon_offset
                url = (
                    "https://api.weather.bom.gov.au/v1/locations"
                    f"?search={query_lat:.6f},{query_lon:.6f}"
                )
                try:
                    async with session.get(url) as response:
                        if response.status != 200:
                            continue
                        payload = await response.json()
                except aiohttp.ClientError:
                    continue

                for location in payload.get("data", []):
                    geohash = location.get("geohash")
                    if geohash and geohash not in by_geohash:
                        by_geohash[geohash] = location

        detailed_locations = []
        for geohash in by_geohash:
            detail_url = f"https://api.weather.bom.gov.au/v1/locations/{geohash}"
            try:
                async with session.get(detail_url) as response:
                    if response.status != 200:
                        continue
                    payload = await response.json()
            except aiohttp.ClientError:
                continue

            location = payload.get("data")
            if not location:
                continue

            lat = location.get("latitude")
            lon = location.get("longitude")
            if lat is None or lon is None:
                continue

            distance = _distance_meters(latitude, longitude, lat, lon)
            detailed_locations.append((distance, location))

    sorted_locations = sorted(detailed_locations, key=lambda item: item[0])
    if not sorted_locations:
        return []

    unique_places = []
    seen_names = set()
    for _, location in sorted_locations:
        key = (location.get("name"), location.get("state"))
        if key in seen_names:
            continue
        seen_names.add(key)
        unique_places.append(location)
        if len(unique_places) >= limit * 3:
            break

    choices = []
    seen_place_ids = set()

    async with aiohttp.ClientSession(headers=headers) as session:
        for location in unique_places:
            name = location.get("name")
            state = location.get("state")
            if not name or not state:
                continue

            autocomplete_params = {
                "name": f"{name} {state}",
                "limit": "5",
                "website-sort": "true",
                "include-states": "true",
                "include-districts": "true",
            }

            try:
                async with session.get(
                    PLACE_AUTOCOMPLETE_URL,
                    params=autocomplete_params,
                    headers={
                        **headers,
                        "Origin": "https://www.bom.gov.au",
                        "Referer": "https://www.bom.gov.au/",
                    },
                ) as response:
                    if response.status != 200:
                        continue
                    payload = await response.json()
            except aiohttp.ClientError:
                continue

            candidates = payload.get("candidates", [])
            place = next(
                (
                    candidate
                    for candidate in candidates
                    if candidate.get("type") == "place"
                    and candidate.get("name") == name
                    and candidate.get("state") == state
                ),
                None,
            )
            if place is None:
                place = next(
                    (
                        candidate
                        for candidate in candidates
                        if candidate.get("type") == "place"
                    ),
                    None,
                )
            if place is None:
                continue

            place_id = place.get("id")
            if not place_id or place_id in seen_place_ids:
                continue
            seen_place_ids.add(place_id)

            coordinate = place.get("coordinate", {})
            place_latitude = coordinate.get("latitude")
            place_longitude = coordinate.get("longitude")
            if place_latitude is None or place_longitude is None:
                continue

            distance = _distance_meters(
                latitude,
                longitude,
                place_latitude,
                place_longitude,
            )
            forecast_geohash = geohash_encode(
                place_latitude,
                place_longitude,
                precision=7,
            )
            observation_geohash = forecast_geohash
            has_observations = False
            station_name = None

            for geohash in dict.fromkeys([forecast_geohash, forecast_geohash[:6]]):
                try:
                    async with session.get(
                        f"{WEATHER_BOM_LOCATION_URL}{geohash}/observations"
                    ) as response:
                        if response.status != 200:
                            continue
                        payload = await response.json()
                except aiohttp.ClientError:
                    continue

                data = payload.get("data")
                if isinstance(data, dict) and data.get("temp") is not None:
                    observation_geohash = geohash
                    has_observations = True
                    station_name = (data.get("station") or {}).get("name")
                    break

            forecast_label = (
                f"{place.get('name')}, {place.get('state')} "
                f"(Place {place_id}, {int(round(distance))}m)"
            )
            if has_observations and station_name:
                observation_label = (
                    f"{place.get('name')}, {place.get('state')} via {station_name}"
                )
            else:
                observation_label = (
                    f"{place.get('name')}, {place.get('state')} "
                    f"via nearest fallback station"
                )
            choices.append(
                {
                    "forecast_geohash": forecast_geohash,
                    "observation_geohash": observation_geohash,
                    "forecast_label": forecast_label,
                    "observation_label": observation_label,
                    "label": forecast_label,
                    "has_observations": has_observations,
                    "place_id": place_id,
                    "station_name": station_name,
                }
            )

            if len(choices) >= limit:
                break

    return choices


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BOM."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialise the config flow."""
        self.data = {}
        self.collector = None
        self._location_choices = []

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return BomOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        data_schema = vol.Schema(
            {
                vol.Required(CONF_LATITUDE, default=self.hass.config.latitude): float,
                vol.Required(CONF_LONGITUDE, default=self.hass.config.longitude): float,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                # Create the collector object with the given long. and lat.
                self.collector = Collector(
                    user_input[CONF_LATITUDE],
                    user_input[CONF_LONGITUDE],
                )

                # Save the user input into self.data so it's retained
                self.data = user_input

                # Check if location is valid
                await self.collector.get_locations_data()
                if self.collector.locations_data is None:
                    _LOGGER.debug("Unsupported Lat/Lon")
                    errors["base"] = "bad_location"
                else:
                    self._location_choices = await _get_top_location_choices(
                        user_input[CONF_LATITUDE],
                        user_input[CONF_LONGITUDE],
                    )

                    # Move onto the source selection step.
                    return await self.async_step_location_source()

            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_location_source(self, user_input=None):
        """Select the BoM location source from the closest options."""
        if not self._location_choices:
            fallback_geohash = _collector_forecast_geohash7(self.collector)
            fallback_name = _collector_location_name(self.collector)
            fallback_label = f"{fallback_name} [{fallback_geohash}]"
            self._location_choices = [
                {
                    "forecast_geohash": fallback_geohash,
                    "observation_geohash": fallback_geohash[:6],
                    "forecast_label": fallback_label,
                    "observation_label": f"{fallback_name} via nearest fallback station",
                    "label": fallback_label,
                    "has_observations": False,
                }
            ]

        forecast_choice_map = {
            choice["forecast_geohash"]: choice["forecast_label"]
            for choice in self._location_choices
        }
        observation_choice_map = {
            choice["observation_geohash"]: choice["observation_label"]
            for choice in self._location_choices
        }
        default_forecast_geohash = self._location_choices[0]["forecast_geohash"]
        default_observation_geohash = next(
            (
                choice["observation_geohash"]
                for choice in self._location_choices
                if choice["has_observations"]
            ),
            self._location_choices[0]["observation_geohash"],
        )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_FORECAST_LOCATION_GEOHASH,
                    default=self.data.get(
                        CONF_FORECAST_LOCATION_GEOHASH,
                        default_forecast_geohash,
                    ),
                ): vol.In(forecast_choice_map),
                vol.Required(
                    CONF_OBSERVATION_LOCATION_GEOHASH,
                    default=self.data.get(
                        CONF_OBSERVATION_LOCATION_GEOHASH,
                        default_observation_geohash,
                    ),
                ): vol.In(observation_choice_map),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)
                forecast_geohash = self.data[CONF_FORECAST_LOCATION_GEOHASH]
                selected_choice = next(
                    (
                        choice
                        for choice in self._location_choices
                        if choice["forecast_geohash"]
                        == self.data[CONF_FORECAST_LOCATION_GEOHASH]
                    ),
                    None,
                )
                if selected_choice and selected_choice.get("place_id"):
                    self.data[CONF_PLACE_ID] = selected_choice["place_id"]

                self.collector = Collector(
                    self.data[CONF_LATITUDE],
                    self.data[CONF_LONGITUDE],
                    forecast_geohash,
                    self.data[CONF_OBSERVATION_LOCATION_GEOHASH],
                    self.data.get(CONF_PLACE_ID),
                )
                await self.collector.get_locations_data()
                await self.collector.async_update()

                return await self.async_step_weather_name()

            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="location_source", data_schema=data_schema, errors=errors
        )

    async def async_step_weather_name(self, user_input=None):
        """Handle the locations step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_WEATHER_NAME,
                    default=_collector_location_name(self.collector),
                ): str,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                # Save the user input into self.data so it's retained
                self.data.update(user_input)

                return await self.async_step_sensors_create()

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="weather_name", data_schema=data_schema, errors=errors
        )

    async def async_step_sensors_create(self, user_input=None):
        """Handle the observations step."""
        data_schema = vol.Schema(
            {
                vol.Required(CONF_OBSERVATIONS_CREATE, default=True): bool,
                vol.Required(CONF_FORECASTS_CREATE, default=True): bool,
                vol.Required(CONF_WARNINGS_CREATE, default=True): bool,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                # Save the user input into self.data so it's retained
                self.data.update(user_input)

                # Move onto the next step of the config flow
                if self.data[CONF_OBSERVATIONS_CREATE]:
                    return await self.async_step_observations_monitored()
                elif self.data[CONF_FORECASTS_CREATE]:
                    return await self.async_step_forecasts_monitored()
                elif self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                else:
                    return self.async_create_entry(
                        title=_collector_location_name(self.collector),
                        data=self.data,
                    )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="sensors_create", data_schema=data_schema, errors=errors
        )

    async def async_step_observations_monitored(self, user_input=None):
        """Handle the observations monitored step."""
        monitored = {}
        for sensor in OBSERVATION_SENSOR_TYPES:
            monitored[sensor.key] = sensor.name

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_OBSERVATIONS_BASENAME,
                    default=_collector_observation_station_name(self.collector),
                ): str,
                vol.Required(CONF_OBSERVATIONS_MONITORED): cv.multi_select(monitored),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)

                # Move onto the next step of the config flow
                if self.data[CONF_FORECASTS_CREATE]:
                    return await self.async_step_forecasts_monitored()
                elif self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                else:
                    return self.async_create_entry(
                        title=_collector_location_name(self.collector),
                        data=self.data,
                    )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="observations_monitored", data_schema=data_schema, errors=errors
        )

    async def async_step_forecasts_monitored(self, user_input=None):
        """Handle the forecasts monitored step."""
        monitored = {}
        for sensor in FORECAST_SENSOR_TYPES:
            monitored[sensor.key] = sensor.name

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_FORECASTS_BASENAME,
                    default=_collector_location_name(self.collector),
                ): str,
                vol.Required(CONF_FORECASTS_MONITORED): cv.multi_select(monitored),
                vol.Required(CONF_FORECASTS_DAYS): vol.All(
                    vol.Coerce(int), vol.Range(0, 7)
                ),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)

                if self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                return self.async_create_entry(
                    title=_collector_location_name(self.collector), data=self.data
                )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="forecasts_monitored", data_schema=data_schema, errors=errors
        )

    async def async_step_warnings_basename(self, user_input=None):
        """Handle the forecasts monitored step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_WARNINGS_BASENAME,
                    default=_collector_location_name(self.collector),
                ): str,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)
                return self.async_create_entry(
                    title=_collector_location_name(self.collector), data=self.data
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="warnings_basename", data_schema=data_schema, errors=errors
        )


class BomOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialise the options flow."""
        super().__init__()
        self.data = {}
        self.collector = None
        self._location_choices = []

    async def async_step_init(self, user_input=None):
        """Handle the initial step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_LATITUDE,
                    default=self.config_entry.options.get(
                        CONF_LATITUDE,
                        self.config_entry.data.get(
                            CONF_LATITUDE, self.hass.config.latitude
                        ),
                    ),
                ): float,
                vol.Required(
                    CONF_LONGITUDE,
                    default=self.config_entry.options.get(
                        CONF_LONGITUDE,
                        self.config_entry.data.get(
                            CONF_LONGITUDE, self.hass.config.longitude
                        ),
                    ),
                ): float,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                # Create the collector object with the given long. and lat.
                self.collector = Collector(
                    user_input[CONF_LATITUDE],
                    user_input[CONF_LONGITUDE],
                )

                # Save the user input into self.data so it's retained
                self.data = user_input

                # Check if location is valid
                await self.collector.get_locations_data()
                if self.collector.locations_data is None:
                    _LOGGER.debug("Unsupported Lat/Lon")
                    errors["base"] = "bad_location"
                else:
                    self._location_choices = await _get_top_location_choices(
                        user_input[CONF_LATITUDE],
                        user_input[CONF_LONGITUDE],
                    )

                    return await self.async_step_location_source()

            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="init", data_schema=data_schema, errors=errors
        )

    async def async_step_location_source(self, user_input=None):
        """Select the BoM location source from the closest options."""
        if not self._location_choices:
            fallback_geohash = self.config_entry.options.get(
                CONF_FORECAST_LOCATION_GEOHASH,
                self.config_entry.data.get(
                    CONF_FORECAST_LOCATION_GEOHASH,
                    _collector_forecast_geohash7(self.collector),
                ),
            )
            fallback_name = _collector_location_name(self.collector)
            fallback_label = f"{fallback_name} [{fallback_geohash}]"
            self._location_choices = [
                {
                    "forecast_geohash": fallback_geohash,
                    "observation_geohash": fallback_geohash[:6],
                    "forecast_label": fallback_label,
                    "observation_label": f"{fallback_name} via nearest fallback station",
                    "label": fallback_label,
                    "has_observations": False,
                }
            ]

        forecast_choice_map = {
            choice["forecast_geohash"]: choice["forecast_label"]
            for choice in self._location_choices
        }
        observation_choice_map = {
            choice["observation_geohash"]: choice["observation_label"]
            for choice in self._location_choices
        }

        default_forecast_geohash = self.config_entry.options.get(
            CONF_FORECAST_LOCATION_GEOHASH,
            self.config_entry.data.get(
                CONF_FORECAST_LOCATION_GEOHASH,
                self._location_choices[0]["forecast_geohash"],
            ),
        )
        if default_forecast_geohash not in forecast_choice_map:
            default_forecast_geohash = self._location_choices[0]["forecast_geohash"]

        default_observation_geohash = self.config_entry.options.get(
            CONF_OBSERVATION_LOCATION_GEOHASH,
            self.config_entry.data.get(
                CONF_OBSERVATION_LOCATION_GEOHASH,
                default_forecast_geohash,
            ),
        )
        if default_observation_geohash not in observation_choice_map:
            default_observation_geohash = next(
                (
                    choice["observation_geohash"]
                    for choice in self._location_choices
                    if choice["has_observations"]
                ),
                self._location_choices[0]["observation_geohash"],
            )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_FORECAST_LOCATION_GEOHASH,
                    default=self.data.get(
                        CONF_FORECAST_LOCATION_GEOHASH,
                        default_forecast_geohash,
                    ),
                ): vol.In(forecast_choice_map),
                vol.Required(
                    CONF_OBSERVATION_LOCATION_GEOHASH,
                    default=self.data.get(
                        CONF_OBSERVATION_LOCATION_GEOHASH,
                        default_observation_geohash,
                    ),
                ): vol.In(observation_choice_map),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)
                forecast_geohash = self.data[CONF_FORECAST_LOCATION_GEOHASH]
                selected_choice = next(
                    (
                        choice
                        for choice in self._location_choices
                        if choice["forecast_geohash"]
                        == self.data[CONF_FORECAST_LOCATION_GEOHASH]
                    ),
                    None,
                )
                if selected_choice and selected_choice.get("place_id"):
                    self.data[CONF_PLACE_ID] = selected_choice["place_id"]

                self.collector = Collector(
                    self.data[CONF_LATITUDE],
                    self.data[CONF_LONGITUDE],
                    forecast_geohash,
                    self.data[CONF_OBSERVATION_LOCATION_GEOHASH],
                    self.data.get(CONF_PLACE_ID),
                )
                await self.collector.get_locations_data()
                await self.collector.async_update()

                return await self.async_step_weather_name()

            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="location_source", data_schema=data_schema, errors=errors
        )

    async def async_step_weather_name(self, user_input=None):
        """Handle the locations step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_WEATHER_NAME,
                    default=self.config_entry.options.get(
                        CONF_WEATHER_NAME,
                        self.config_entry.data.get(
                            CONF_WEATHER_NAME,
                            _collector_location_name(self.collector),
                        ),
                    ),
                ): str,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                # Save the user input into self.data so it's retained
                self.data.update(user_input)

                return await self.async_step_sensors_create()

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="weather_name", data_schema=data_schema, errors=errors
        )

    async def async_step_sensors_create(self, user_input=None):
        """Handle the observations step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_OBSERVATIONS_CREATE,
                    default=self.config_entry.options.get(
                        CONF_OBSERVATIONS_CREATE,
                        self.config_entry.data.get(CONF_OBSERVATIONS_CREATE, True),
                    ),
                ): bool,
                vol.Required(
                    CONF_FORECASTS_CREATE,
                    default=self.config_entry.options.get(
                        CONF_FORECASTS_CREATE,
                        self.config_entry.data.get(CONF_FORECASTS_CREATE, True),
                    ),
                ): bool,
                vol.Required(
                    CONF_WARNINGS_CREATE,
                    default=self.config_entry.options.get(
                        CONF_WARNINGS_CREATE,
                        self.config_entry.data.get(CONF_WARNINGS_CREATE, True),
                    ),
                ): bool,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                # Save the user input into self.data so it's retained
                self.data.update(user_input)

                # Move onto the next step of the config flow
                if self.data[CONF_OBSERVATIONS_CREATE]:
                    return await self.async_step_observations_monitored()
                elif self.data[CONF_FORECASTS_CREATE]:
                    return await self.async_step_forecasts_monitored()
                elif self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                else:
                    return self.async_create_entry(
                        title=_collector_location_name(self.collector),
                        data=self.data,
                    )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="sensors_create", data_schema=data_schema, errors=errors
        )

    async def async_step_observations_monitored(self, user_input=None):
        """Handle the observations monitored step."""
        monitored = {}
        for sensor in OBSERVATION_SENSOR_TYPES:
            monitored[sensor.key] = sensor.name

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_OBSERVATIONS_BASENAME,
                    default=self.config_entry.options.get(
                        CONF_OBSERVATIONS_BASENAME,
                        self.config_entry.data.get(
                            CONF_OBSERVATIONS_BASENAME,
                            _collector_observation_station_name(self.collector),
                        ),
                    ),
                ): str,
                vol.Required(
                    CONF_OBSERVATIONS_MONITORED,
                    default=self.config_entry.options.get(
                        CONF_OBSERVATIONS_MONITORED,
                        self.config_entry.data.get(CONF_OBSERVATIONS_MONITORED, None),
                    ),
                ): cv.multi_select(monitored),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)

                # Move onto the next step of the config flow
                if self.data[CONF_FORECASTS_CREATE]:
                    return await self.async_step_forecasts_monitored()
                elif self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                else:
                    return self.async_create_entry(
                        title=_collector_location_name(self.collector),
                        data=self.data,
                    )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="observations_monitored", data_schema=data_schema, errors=errors
        )

    async def async_step_forecasts_monitored(self, user_input=None):
        """Handle the forecasts monitored step."""
        monitored = {}
        for sensor in FORECAST_SENSOR_TYPES:
            monitored[sensor.key] = sensor.name

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_FORECASTS_BASENAME,
                    default=self.config_entry.options.get(
                        CONF_FORECASTS_BASENAME,
                        self.config_entry.data.get(
                            CONF_FORECASTS_BASENAME,
                            _collector_location_name(self.collector),
                        ),
                    ),
                ): str,
                vol.Required(
                    CONF_FORECASTS_MONITORED,
                    default=self.config_entry.options.get(
                        CONF_FORECASTS_MONITORED,
                        self.config_entry.data.get(CONF_FORECASTS_MONITORED, None),
                    ),
                ): cv.multi_select(monitored),
                vol.Required(
                    CONF_FORECASTS_DAYS,
                    default=self.config_entry.options.get(
                        CONF_FORECASTS_DAYS,
                        self.config_entry.data.get(CONF_FORECASTS_DAYS, 0),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(0, 7)),
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)

                if self.data[CONF_WARNINGS_CREATE]:
                    return await self.async_step_warnings_basename()
                return self.async_create_entry(
                    title=_collector_location_name(self.collector), data=self.data
                )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="forecasts_monitored", data_schema=data_schema, errors=errors
        )

    async def async_step_warnings_basename(self, user_input=None):
        """Handle the forecasts monitored step."""
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_WARNINGS_BASENAME,
                    default=self.config_entry.options.get(
                        CONF_WARNINGS_BASENAME,
                        self.config_entry.data.get(
                            CONF_WARNINGS_BASENAME,
                            _collector_location_name(self.collector),
                        ),
                    ),
                ): str,
            }
        )

        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)
                return self.async_create_entry(
                    title=_collector_location_name(self.collector), data=self.data
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="warnings_basename", data_schema=data_schema, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""

import logging
import math
import time
import datetime
import asyncio

import aiohttp

from homeassistant.util import Throttle

from .const import (
    MAP_MDI_ICON,
    URL_BASE,
    URL_DAILY,
    URL_HOURLY,
    URL_OBSERVATIONS,
    URL_WARNINGS,
)
from .helpers import (
    flatten_dict,
    geohash_encode,
)

_LOGGER = logging.getLogger(__name__)

# Constants for retry mechanism
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # seconds
MAX_CACHE_AGE = 86400  # 24 hours in seconds

PLACE_DETAILS_URL = "https://api.bom.gov.au/apikey/v1/locations/places/details/place/"
PLACE_AUTOCOMPLETE_FILTER = (
    "nearby_type:bom_stn,elevation:300,capability:SENSOR_TEMPERATURE_DB,"
    "match_coastal_status:true"
)
PLACE_FORECAST_DAILY_URL = "https://api.bom.gov.au/apikey/v1/forecasts/daily/{x}/{y}"
PLACE_FORECAST_HOURLY_URL = "https://api.bom.gov.au/apikey/v1/forecasts/1hourly/{x}/{y}"
PLACE_FORECAST_3HOURLY_URL = (
    "https://api.bom.gov.au/apikey/v1/forecasts/3hourly/{x}/{y}"
)
PLACE_FORECAST_ASTRO_URL = (
    "https://api.bom.gov.au/apikey/v1/forecasts/astro/{lon}/{lat}"
)
PLACE_FORECAST_TEXT_URL = "https://api.bom.gov.au/apikey/v1/forecasts/texts"
PLACE_OBSERVATIONS_URL = "https://api.bom.gov.au/apikey/v1/observations/latest/{station_id}/atm/surf_air?include_qc_results=false"
PLACE_WARNINGS_URL = "https://api.bom.gov.au/apikey/v1/warnings/list?area_type=coordinate&area_code={lon},{lat}"

ICON_CODE_MAP = {
    1: "sunny",
    2: "clear",
    3: "partly_cloudy",
    4: "cloudy",
    6: "haze",
    8: "light_showers",
    9: "windy",
    10: "fog",
    11: "showers",
    12: "rain",
    13: "dust",
    14: "frost",
    15: "snow",
    16: "storms",
    17: "light_showers",
}

COMPASS_DIRECTIONS = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
]


class Collector:
    """Collector for PyBoM."""

    def __init__(
        self,
        latitude,
        longitude,
        forecast_source_geohash=None,
        observation_source_geohash=None,
        place_id=None,
    ):
        """Init collector."""
        self.locations_data = None
        self.observations_data = None
        self.daily_forecasts_data = None
        self.hourly_forecasts_data = None
        self.warnings_data = None
        self.place_id = place_id
        self.latitude = latitude
        self.longitude = longitude
        # BoM API location endpoints use 7-character geohashes.
        if forecast_source_geohash and len(forecast_source_geohash) >= 7:
            self.forecast_geohash7 = forecast_source_geohash[:7]
        else:
            self.forecast_geohash7 = geohash_encode(latitude, longitude, precision=7)
        self.forecast_geohash6 = self.forecast_geohash7[:6]

        if observation_source_geohash and len(observation_source_geohash) >= 7:
            self.observation_geohash7 = observation_source_geohash[:7]
        else:
            self.observation_geohash7 = self.forecast_geohash7
        self.observation_geohash6 = self.observation_geohash7[:6]
        self.selected_observations_geohash = None
        self.selected_forecasts_geohash = None
        self.selected_daily_forecasts_geohash = None
        self.selected_hourly_forecasts_geohash = None
        # Cache storage with timestamps
        self._cache = {
            "locations": {"data": None, "timestamp": 0},
            "observations": {"data": None, "timestamp": 0},
            "daily_forecasts": {"data": None, "timestamp": 0},
            "hourly_forecasts": {"data": None, "timestamp": 0},
            "warnings": {"data": None, "timestamp": 0},
        }

    @staticmethod
    def _uv_category_from_index(uv_index):
        """Map numeric UV to BoM category string."""
        if uv_index is None:
            return None
        if uv_index < 3:
            return "low"
        if uv_index < 6:
            return "moderate"
        if uv_index < 8:
            return "high"
        if uv_index < 11:
            return "veryhigh"
        return "extreme"

    @staticmethod
    def _wind_direction_from_degrees(direction):
        """Return compass direction from degrees."""
        if direction is None:
            return None
        index = int((float(direction) + 11.25) // 22.5) % 16
        return COMPASS_DIRECTIONS[index]

    @staticmethod
    def _rain_range_from_precip(precipitation):
        """Approximate BoM displayed rain range from percentile totals."""
        if not precipitation:
            return (None, None)

        low = precipitation.get("exceeding_75percentchance_total_mm")
        high = precipitation.get("exceeding_25percentchance_total_mm")
        if low is None and high is None:
            return (None, None)

        low_value = None if low is None else max(0, math.floor(low))
        high_value = None if high is None else max(0, round(high))
        if high_value is None:
            high_value = low_value
        if low_value is None:
            low_value = 0 if high_value == 0 else None
        return (low_value, high_value)

    @staticmethod
    def _icon_descriptor_from_code(icon_code):
        """Map numeric icon code to old descriptor strings."""
        return ICON_CODE_MAP.get(icon_code, "cloudy")

    def _map_place_to_locations_data(self, place_details):
        """Convert place details payload to legacy locations structure."""
        place = place_details["place"]
        coordinate = place.get("coordinate", {})
        state = place.get("state", {})
        return {
            "metadata": {
                "response_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            },
            "data": {
                "id": place.get("id"),
                "name": place.get("name"),
                "state": state.get("abbrev") if isinstance(state, dict) else state,
                "timezone": place.get("timezone"),
                "latitude": coordinate.get("latitude"),
                "longitude": coordinate.get("longitude"),
            },
        }

    @staticmethod
    def _speed_mps_to_kmh(speed_mps):
        """Convert m/s to km/h."""
        if speed_mps is None:
            return None
        return round(speed_mps * 3.6)

    @staticmethod
    def _speed_mps_to_knots(speed_mps):
        """Convert m/s to knots."""
        if speed_mps is None:
            return None
        return round(speed_mps * 1.943844)

    def _pick_text_detail(self, daily_text):
        """Choose the richest available area text for a day."""
        weather = daily_text.get("atm", {}).get("surf_air", {}).get("weather", {})
        for key in (
            "locality_text",
            "metropolitan_text",
            "public_district_text",
            "coast_text",
            "region_text",
            "precis_text",
        ):
            if weather.get(key):
                return weather.get(key)
        return None

    @staticmethod
    def _pick_precis_text(daily_text):
        """Pick concise precis text for a day."""
        return (
            daily_text.get("atm", {})
            .get("surf_air", {})
            .get("weather", {})
            .get("precis_text")
        )

    async def _get_place_details(self, session):
        """Fetch canonical place details from the newer BoM API."""
        if not self.place_id:
            return None

        url = f"{PLACE_DETAILS_URL}{self.place_id}"
        params = {
            "filter": PLACE_AUTOCOMPLETE_FILTER,
            "radius": 100000,
            "nearby_limit": 10,
        }
        return await self._fetch_with_retry(
            session,
            f"{url}?filter={params['filter']}&radius={params['radius']}&nearby_limit={params['nearby_limit']}",
            "locations",
        )

    def _should_use_place_observations(self):
        """Use canonical place observations only when observation source wasn't overridden."""
        return self.observation_geohash6 == self.forecast_geohash6

    def _map_place_to_observations_data(self, place_details, observation_payload):
        """Convert place observation payload to legacy observation structure."""
        place = place_details.get("place", {})
        nearest = (place.get("location_hierarchy", {}) or {}).get("nearest", {})
        observation = observation_payload.get("obs", {})
        station = observation_payload.get("stn", {})
        identity = station.get("identity", {})
        wind = observation.get("wind", {})
        temp = observation.get("temp", {})
        precip = observation.get("precip", {})

        return {
            "metadata": {
                "response_timestamp": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                ),
                "issue_time": observation.get("datetime_utc"),
                "observation_time": observation.get("datetime_utc"),
            },
            "data": {
                "temp": None
                if temp.get("dry_bulb_1min_cel") is None
                else round(temp.get("dry_bulb_1min_cel")),
                "temp_feels_like": None
                if temp.get("apparent_1min_cel") is None
                else round(temp.get("apparent_1min_cel"), 1),
                "wind": {
                    "speed_kilometre": self._speed_mps_to_kmh(
                        wind.get("speed_10m_mps") or wind.get("speed_10m_avg_mps")
                    ),
                    "speed_knot": self._speed_mps_to_knots(
                        wind.get("speed_10m_mps") or wind.get("speed_10m_avg_mps")
                    ),
                    "direction": wind.get("dirn_10m_ord")
                    or self._wind_direction_from_degrees(wind.get("dirn_10m_deg_t")),
                },
                "gust": {
                    "speed_kilometre": self._speed_mps_to_kmh(
                        wind.get("gust_speed_10m_mps")
                        or wind.get("gust_speed_10m_max_mps")
                    ),
                    "speed_knot": self._speed_mps_to_knots(
                        wind.get("gust_speed_10m_mps")
                        or wind.get("gust_speed_10m_max_mps")
                    ),
                },
                "max_temp": {
                    "time": temp.get("dry_bulb_max_time_utc"),
                    "value": temp.get("dry_bulb_max_cel"),
                },
                "min_temp": {
                    "time": temp.get("dry_bulb_min_time_utc"),
                    "value": temp.get("dry_bulb_min_cel"),
                },
                "rain_since_9am": precip.get("since_0900lct_total_mm"),
                "humidity": temp.get("rel_hum_percent"),
                "station": {
                    "bom_id": str(identity.get("bom_stn_num") or nearest.get("id")),
                    "name": identity.get("bom_stn_name") or nearest.get("name"),
                    "distance": nearest.get("distance"),
                },
            },
        }

    async def _async_update_place_observations(self, session, place_details):
        """Fetch observations from the newer place/station API."""
        nearest = (
            place_details.get("place", {}).get("location_hierarchy", {}) or {}
        ).get("nearest", {})
        station_id = nearest.get("id")
        if not station_id:
            return False

        data = await self._fetch_with_retry(
            session,
            PLACE_OBSERVATIONS_URL.format(station_id=station_id),
            "observations",
        )
        if not data or not data.get("obs"):
            return False

        self.observations_data = self._map_place_to_observations_data(
            place_details,
            data,
        )
        self.selected_observations_geohash = self.observation_geohash6
        return True

    async def _async_update_place_warnings(self, session, place_details):
        """Fetch warnings from newer coordinate-based warnings API."""
        coordinate = place_details.get("place", {}).get("coordinate", {})
        latitude = coordinate.get("latitude")
        longitude = coordinate.get("longitude")
        if latitude is None or longitude is None:
            return False

        data = await self._fetch_with_retry(
            session,
            PLACE_WARNINGS_URL.format(lon=longitude, lat=latitude),
            "warnings",
        )
        if data is None or "warnings" not in data:
            return False

        self.warnings_data = {
            "metadata": {
                "response_timestamp": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                ),
            },
            "data": data.get("warnings", []),
        }
        return True

    async def _async_update_place_forecasts(self, session, place_details):
        """Fetch daily/hourly forecast data from the newer place/grid APIs."""
        place = place_details["place"]
        forecast_grid = place.get("gridcells", {}).get("forecast", {})
        grid_x = forecast_grid.get("x")
        grid_y = forecast_grid.get("y")
        timezone = place.get("timezone")
        coordinate = place.get("coordinate", {})
        latitude = coordinate.get("latitude")
        longitude = coordinate.get("longitude")

        if grid_x is None or grid_y is None or timezone is None:
            return

        daily_data = await self._fetch_with_retry(
            session,
            PLACE_FORECAST_DAILY_URL.format(x=grid_x, y=grid_y)
            + f"?timezone={timezone}",
            "daily_forecasts",
        )
        hourly_data = await self._fetch_with_retry(
            session,
            PLACE_FORECAST_HOURLY_URL.format(x=grid_x, y=grid_y)
            + f"?timezone={timezone}",
            "hourly_forecasts",
        )
        three_hourly_data = await self._fetch_with_retry(
            session,
            PLACE_FORECAST_3HOURLY_URL.format(x=grid_x, y=grid_y)
            + f"?timezone={timezone}",
            "hourly_forecasts",
        )
        astro_data = await self._fetch_with_retry(
            session,
            PLACE_FORECAST_ASTRO_URL.format(lon=longitude, lat=latitude),
            "daily_forecasts",
        )

        text_aac = "SA_ME001"
        hier = place.get("location_hierarchy", {})
        metros = hier.get("metropolitan", [])
        if metros and metros[0].get("aac"):
            text_aac = metros[0]["aac"]
        precis_aac = (hier.get("precis_fcst", {}) or {}).get("aac")
        text_data = await self._fetch_with_retry(
            session,
            PLACE_FORECAST_TEXT_URL + f"?aac={text_aac}&timezone={timezone}",
            "daily_forecasts",
        )
        precis_text_data = None
        if precis_aac:
            precis_text_data = await self._fetch_with_retry(
                session,
                PLACE_FORECAST_TEXT_URL + f"?aac={precis_aac}&timezone={timezone}",
                "daily_forecasts",
            )

        if daily_data and daily_data.get("fcst", {}).get("daily"):
            astro_by_date = {
                item.get("date_utc"): item.get("astro", {})
                for item in (astro_data or {}).get("fcst", {}).get("daily", [])
            }
            text_by_date = {
                item.get("date_utc"): item
                for item in (text_data or {}).get("fcst", {}).get("daily", [])
            }
            precis_by_date = {
                item.get("date_utc"): item
                for item in (precis_text_data or {}).get("fcst", {}).get("daily", [])
            }

            converted_daily = []
            for index, item in enumerate(daily_data["fcst"]["daily"]):
                surf_air = item.get("atm", {}).get("surf_air", {})
                precip = surf_air.get("precip", {})
                radiation = surf_air.get("radiation", {})
                astro = astro_by_date.get(item.get("date_utc"), {})
                text_item = text_by_date.get(item.get("date_utc"), {})
                precis_item = precis_by_date.get(item.get("date_utc"), {})
                icon_descriptor = self._icon_descriptor_from_code(
                    surf_air.get("weather", {}).get("icon_code")
                )
                uv_max = radiation.get("uv_clear_sky_max_code")
                rain_min, rain_max = self._rain_range_from_precip(precip)

                converted = {
                    "date": item.get("date_utc"),
                    "temp_max": None
                    if surf_air.get("temp_max_cel") is None
                    else round(surf_air.get("temp_max_cel")),
                    "temp_min": None
                    if surf_air.get("temp_min_cel") is None
                    else round(surf_air.get("temp_min_cel")),
                    "icon_descriptor": icon_descriptor,
                    "mdi_icon": MAP_MDI_ICON[icon_descriptor],
                    "short_text": self._pick_precis_text(precis_item)
                    or self._pick_precis_text(text_item),
                    "extended_text": self._pick_text_detail(text_item),
                    "uv_category": self._uv_category_from_index(uv_max),
                    "uv_max_index": None if uv_max is None else round(uv_max),
                    "uv_start_time": radiation.get("uv_period_start"),
                    "uv_end_time": radiation.get("uv_period_end"),
                    "rain_amount_min": rain_min,
                    "rain_amount_max": rain_max,
                    "rain_amount_range": rain_min
                    if rain_min == rain_max
                    else f"{rain_min}–{rain_max}",
                    "rain_chance": None
                    if precip.get("any_probability_percent") is None
                    else round(precip.get("any_probability_percent")),
                    "fire_danger": None,
                    "fire_danger_category": {
                        "text": None,
                        "default_colour": None,
                        "dark_mode_colour": None,
                    },
                    "astronomical_sunrise_time": astro.get("sunrise_utc"),
                    "astronomical_sunset_time": astro.get("sunset_utc"),
                    "now_now_label": None,
                    "now_temp_now": None,
                    "now_later_label": None,
                    "now_temp_later": None,
                }
                if index == 0:
                    converted["now_now_label"] = "Max"
                    converted["now_temp_now"] = converted["temp_max"]
                    converted["now_later_label"] = "Overnight Min"
                    converted["now_temp_later"] = converted["temp_min"]
                converted_daily.append(converted)

            self.daily_forecasts_data = {
                "metadata": {
                    "response_timestamp": (daily_data.get("meta") or {}).get(
                        "issue_time_utc"
                    ),
                    "issue_time": (daily_data.get("meta") or {}).get("issue_time_utc"),
                },
                "data": converted_daily,
            }
            self.selected_forecasts_geohash = self.forecast_geohash7
            self.selected_daily_forecasts_geohash = self.forecast_geohash7

        if hourly_data and hourly_data.get("fcst"):
            three_hourly_buckets = []
            for day in (three_hourly_data or {}).get("fcst", []):
                for bucket in day.get("3hourly", []):
                    three_hourly_buckets.append(bucket)

            converted_hourly = []
            for day in hourly_data.get("fcst", []):
                for item in day.get("1hourly", []):
                    surf_air = item.get("atm", {}).get("surf_air", {})
                    time_utc = item.get("time_utc")
                    bucket = next(
                        (
                            candidate
                            for candidate in three_hourly_buckets
                            if candidate.get("start_time_utc") <= time_utc
                            and candidate.get("end_time_utc") > time_utc
                        ),
                        None,
                    )
                    bucket_air = (bucket or {}).get("atm", {}).get("surf_air", {})
                    bucket_precip = bucket_air.get("precip", {})
                    rain_min, rain_max = self._rain_range_from_precip(bucket_precip)
                    icon_descriptor = self._icon_descriptor_from_code(
                        bucket_air.get("weather", {}).get("icon_code")
                    )
                    wind = surf_air.get("wind", {})
                    converted_hourly.append(
                        {
                            "time": time_utc,
                            "temp": None
                            if surf_air.get("temp_cel") is None
                            else round(surf_air.get("temp_cel"), 1),
                            "icon_descriptor": icon_descriptor,
                            "mdi_icon": MAP_MDI_ICON[icon_descriptor],
                            "rain_amount_min": rain_min,
                            "rain_amount_max": rain_max,
                            "rain_amount_range": rain_min
                            if rain_min == rain_max
                            else f"{rain_min} to {rain_max}",
                            "rain_chance": None
                            if bucket_precip.get("precip_any_probability_percent")
                            is None
                            else round(
                                bucket_precip.get("precip_any_probability_percent")
                            ),
                            "wind_direction": self._wind_direction_from_degrees(
                                wind.get("dirn_10m_deg_t")
                            ),
                            "wind_speed_kilometre": None
                            if wind.get("speed_10m_avg_mps") is None
                            else round(wind.get("speed_10m_avg_mps") * 3.6),
                            "wind_gust_speed_kilometre": None
                            if wind.get("gust_speed_10m_max_mps") is None
                            else round(wind.get("gust_speed_10m_max_mps") * 3.6),
                            "relative_humidity": surf_air.get("hum_relative_percent"),
                            "uv": surf_air.get("radiation", {}).get(
                                "uv_clear_sky_code"
                            ),
                            "is_night": False,
                        }
                    )

            self.hourly_forecasts_data = {
                "metadata": {
                    "response_timestamp": (hourly_data.get("meta") or {}).get(
                        "issue_time_utc"
                    ),
                    "issue_time": (hourly_data.get("meta") or {}).get("issue_time_utc"),
                },
                "data": converted_hourly,
            }
            self.selected_forecasts_geohash = self.forecast_geohash7
            self.selected_hourly_forecasts_geohash = self.forecast_geohash7

    async def _fetch_with_retry(self, session, url, cache_key):
        """Fetch data with retry mechanism and store in cache if successful."""
        for attempt in range(MAX_RETRIES):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Update cache with new data and timestamp
                        self._cache[cache_key]["data"] = data
                        self._cache[cache_key]["timestamp"] = time.time()
                        return data
                    if 400 <= response.status < 500 and response.status != 429:
                        _LOGGER.debug(
                            "BoM API returned %s for %s; skipping retries for this geohash",
                            response.status,
                            url,
                        )
                        return None
                    else:
                        _LOGGER.warning(
                            f"Error requesting API data from {url}: {response.status}"
                        )
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                wait_time = RETRY_DELAY_BASE**attempt
                _LOGGER.warning(
                    f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {err}. "
                    f"Retrying in {wait_time} seconds..."
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(wait_time)
                else:
                    _LOGGER.error(
                        f"Error requesting API data: {err}. "
                        "Using cached data if available."
                    )
                    # Return cached data if available
                    cached = self._cache[cache_key]["data"]
                    if cached is not None:
                        cache_age = time.time() - self._cache[cache_key]["timestamp"]
                        _LOGGER.info(
                            f"Returning cached {cache_key} data from {int(cache_age / 60)} minutes ago"
                        )
                        return cached
                    else:
                        _LOGGER.error(f"No cached {cache_key} data available")
                        return None
        return None

    async def get_locations_data(self):
        """Get JSON location name from BOM API endpoint."""
        headers = {"User-Agent": "MakeThisAPIOpenSource/1.0.0"}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                if self.place_id:
                    data = await self._get_place_details(session)
                    if data and data.get("place"):
                        self.locations_data = self._map_place_to_locations_data(data)
                        return

                data = await self._fetch_with_retry(
                    session, URL_BASE + self.forecast_geohash7, "locations"
                )
                if data:
                    self.locations_data = data
        except Exception as err:
            _LOGGER.error(f"Unexpected error in get_locations_data: {err}")

    async def format_daily_forecast_data(self):
        """Format forecast data."""
        if not self.daily_forecasts_data or "data" not in self.daily_forecasts_data:
            _LOGGER.warning("No daily forecast data to format")
            return

        days = len(self.daily_forecasts_data["data"])
        for day in range(0, days):
            d = self.daily_forecasts_data["data"][day]

            flatten_dict(["amount"], d["rain"])
            flatten_dict(["rain", "uv", "astronomical"], d)

            if day == 0:
                flatten_dict(["now"], d)

                is_night = d.get("now_is_night")
                icon_desc = d.get("icon_descriptor")

                # Override icon_descriptor if it's night and icon is sunny/mostly_sunny
                if is_night and icon_desc in {"sunny", "mostly_sunny"}:
                    d["icon_descriptor"] = "clear"
                # Override icon_descriptor if its clear during the day
                elif not is_night and icon_desc == "clear":
                    d["icon_descriptor"] = "sunny"

            d["mdi_icon"] = MAP_MDI_ICON[d["icon_descriptor"]]

            # If rain amount max is None, set as rain amount min
            if d["rain_amount_max"] is None:
                d["rain_amount_max"] = d["rain_amount_min"]
                d["rain_amount_range"] = d["rain_amount_min"]
            else:
                d["rain_amount_range"] = (
                    f"{d['rain_amount_min']}–{d['rain_amount_max']}"
                )

    async def format_hourly_forecast_data(self):
        """Format forecast data."""
        if not self.hourly_forecasts_data or "data" not in self.hourly_forecasts_data:
            _LOGGER.warning("No hourly forecast data to format")
            return

        hours = len(self.hourly_forecasts_data["data"])
        for hour in range(0, hours):
            d = self.hourly_forecasts_data["data"][hour]

            is_night = d.get("is_night")
            icon_desc = d.get("icon_descriptor")

            # Override icon_descriptor if it's night and icon is sunny/mostly_sunny
            if is_night and icon_desc in {"sunny", "mostly_sunny"}:
                d["icon_descriptor"] = "clear"
            # Override icon_descriptor if its clear during the day
            elif not is_night and icon_desc == "clear":
                d["icon_descriptor"] = "sunny"

            d["mdi_icon"] = MAP_MDI_ICON[d["icon_descriptor"]]

            flatten_dict(["amount"], d["rain"])
            flatten_dict(["rain", "wind"], d)

            # If rain amount max is None, set as rain amount min
            if d["rain_amount_max"] is None:
                d["rain_amount_max"] = d["rain_amount_min"]
                d["rain_amount_range"] = d["rain_amount_min"]
            else:
                d["rain_amount_range"] = (
                    f"{d['rain_amount_min']} to {d['rain_amount_max']}"
                )

    @Throttle(datetime.timedelta(minutes=5))
    async def async_update(self):
        """Refresh the data on the collector object."""
        headers = {"User-Agent": "MakeThisAPIOpenSource/1.0.0"}

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                # Get location data if not already available
                if self.locations_data is None:
                    if self.place_id:
                        place_details = await self._get_place_details(session)
                        if place_details and place_details.get("place"):
                            self.locations_data = self._map_place_to_locations_data(
                                place_details
                            )
                        else:
                            place_details = None
                    else:
                        place_details = None

                    if self.locations_data is None:
                        data = await self._fetch_with_retry(
                            session, URL_BASE + self.forecast_geohash7, "locations"
                        )
                        if data:
                            self.locations_data = data
                else:
                    place_details = None

                # Get observations data. Prefer place nearest station when the
                # observation source hasn't been explicitly overridden.
                place_observations_loaded = False
                if self.place_id and self._should_use_place_observations():
                    if place_details is None:
                        place_details = await self._get_place_details(session)
                    if place_details and place_details.get("place"):
                        place_observations_loaded = (
                            await self._async_update_place_observations(
                                session,
                                place_details,
                            )
                        )

                if not place_observations_loaded:
                    observations_data = None
                    selected_obs_geohash = None
                    for geohash in dict.fromkeys(
                        [self.observation_geohash7, self.observation_geohash6]
                    ):
                        data = await self._fetch_with_retry(
                            session,
                            URL_BASE + geohash + URL_OBSERVATIONS,
                            "observations",
                        )
                        if data and data.get("data") is not None:
                            if data["data"].get("temp") is not None:
                                observations_data = data
                                selected_obs_geohash = geohash
                                break
                            if observations_data is None:
                                observations_data = data
                                selected_obs_geohash = geohash

                    if observations_data:
                        self.observations_data = observations_data
                        self.selected_observations_geohash = selected_obs_geohash

                if self.observations_data:
                    if self.observations_data["data"].get("wind") is not None:
                        flatten_dict(["wind"], self.observations_data["data"])
                    else:
                        self.observations_data["data"]["wind_direction"] = "unavailable"
                        self.observations_data["data"]["wind_speed_kilometre"] = (
                            "unavailable"
                        )
                        self.observations_data["data"]["wind_speed_knot"] = (
                            "unavailable"
                        )
                    if self.observations_data["data"].get("gust") is not None:
                        flatten_dict(["gust"], self.observations_data["data"])
                    else:
                        self.observations_data["data"]["gust_speed_kilometre"] = (
                            "unavailable"
                        )
                        self.observations_data["data"]["gust_speed_knot"] = (
                            "unavailable"
                        )

                if self.place_id:
                    if place_details is None:
                        place_details = await self._get_place_details(session)
                    if place_details and place_details.get("place"):
                        await self._async_update_place_forecasts(session, place_details)

                if self.daily_forecasts_data is None:
                    # Get daily forecast data
                    for geohash in dict.fromkeys(
                        [self.forecast_geohash7, self.forecast_geohash6]
                    ):
                        data = await self._fetch_with_retry(
                            session,
                            URL_BASE + geohash + URL_DAILY,
                            "daily_forecasts",
                        )
                        if data and data.get("data") is not None:
                            self.daily_forecasts_data = data
                            self.selected_forecasts_geohash = geohash
                            self.selected_daily_forecasts_geohash = geohash
                            await self.format_daily_forecast_data()
                            break

                if self.hourly_forecasts_data is None:
                    # Get hourly forecast data
                    for geohash in dict.fromkeys(
                        [self.forecast_geohash7, self.forecast_geohash6]
                    ):
                        data = await self._fetch_with_retry(
                            session,
                            URL_BASE + geohash + URL_HOURLY,
                            "hourly_forecasts",
                        )
                        if data and data.get("data") is not None:
                            self.hourly_forecasts_data = data
                            self.selected_forecasts_geohash = geohash
                            self.selected_hourly_forecasts_geohash = geohash
                            await self.format_hourly_forecast_data()
                            break

                warnings_loaded = False
                if self.place_id:
                    if place_details is None:
                        place_details = await self._get_place_details(session)
                    if place_details and place_details.get("place"):
                        warnings_loaded = await self._async_update_place_warnings(
                            session,
                            place_details,
                        )

                if not warnings_loaded:
                    # Get warnings data
                    for geohash in dict.fromkeys(
                        [self.forecast_geohash7, self.forecast_geohash6]
                    ):
                        data = await self._fetch_with_retry(
                            session,
                            URL_BASE + geohash + URL_WARNINGS,
                            "warnings",
                        )
                        if data and data.get("data") is not None:
                            self.warnings_data = data
                            break

        except Exception as err:
            _LOGGER.error(f"Unexpected error during async_update: {err}")
            # Even if we have an unexpected error, we still have our cached data

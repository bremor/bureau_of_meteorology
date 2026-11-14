"""BOM data 'collector' that downloads the observation data."""
import aiohttp
import asyncio
import copy
import datetime
import time
import logging

from homeassistant.util import Throttle

from .const import (
    MAP_MDI_ICON, URL_BASE, URL_DAILY,
    URL_HOURLY, URL_OBSERVATIONS, URL_WARNINGS
)
from .helpers import (
    flatten_dict, geohash_encode,
)

_LOGGER = logging.getLogger(__name__)

# Constants for retry mechanism
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # seconds
MAX_CACHE_AGE = 86400  # 24 hours in seconds


def _get_current_hourly_row(hourly_data, now=None):
    """Find the hourly forecast row covering the current time, or fallback to the nearest row."""
    if not hourly_data or "data" not in hourly_data or not isinstance(hourly_data["data"], list):
        return None
    rows = [r for r in hourly_data["data"] if isinstance(r, dict)]
    if not rows:
        return None
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)

    parsed_rows = []
    for row in rows:
        time_str = row.get("time")
        if not time_str:
            continue
        try:
            stamp = datetime.datetime.fromisoformat(time_str)
        except (ValueError, TypeError):
            continue

        if stamp.tzinfo is not None:
            target_now = now if now.tzinfo is not None else now.replace(tzinfo=stamp.tzinfo)
        else:
            target_now = now.replace(tzinfo=None) if now.tzinfo is not None else now

        parsed_rows.append((row, stamp, target_now))

        if stamp <= target_now < stamp + datetime.timedelta(hours=1):
            return row

    # If no row covers the exact 1-hour window, choose the row closest in time
    if parsed_rows:
        return min(
            parsed_rows,
            key=lambda item: abs((item[1] - item[2]).total_seconds()),
        )[0]

    return rows[0]


class Collector:
    """Collector for PyBoM."""

    def __init__(self, latitude, longitude):
        """Init collector."""
        self.locations_data = None
        self.observations_data = None
        self.daily_forecasts_data = None
        self.hourly_forecasts_data = None
        self.warnings_data = None
        # Cached payloads may survive a failed refresh. Keep its outcome separate
        # so consumers do not mistake retained data for a successful update.
        self.last_update_success = False
        self.geohash7 = geohash_encode(latitude, longitude)
        self.geohash6 = self.geohash7[:6]
        # Cache storage with timestamps
        self._cache = {
            "locations": {"data": None, "timestamp": 0},
            "observations": {"data": None, "timestamp": 0},
            "daily_forecasts": {"data": None, "timestamp": 0},
            "hourly_forecasts": {"data": None, "timestamp": 0},
            "warnings": {"data": None, "timestamp": 0},
        }

    async def _fetch_with_retry(self, session, url, cache_key):
        """Fetch data with retry mechanism and store in cache if successful."""
        for attempt in range(MAX_RETRIES):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Update cache with new data and timestamp
                        self._cache[cache_key]["data"] = copy.deepcopy(data)
                        self._cache[cache_key]["timestamp"] = time.time()
                        return data
                    else:
                        _LOGGER.warning(
                            f"Error requesting API data from {url}: {response.status}"
                        )
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                wait_time = RETRY_DELAY_BASE ** attempt
                _LOGGER.warning(
                    f"Attempt {attempt+1}/{MAX_RETRIES} failed: {err}. "
                    f"Retrying in {wait_time} seconds..."
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(wait_time)
                else:
                    self.last_update_success = False
                    _LOGGER.error(
                        f"Error requesting API data: {err}. "
                        "Using cached data if available."
                    )
                    # Return cached data if available
                    cached = self._cache[cache_key]["data"]
                    if cached is not None:
                        cache_age = time.time() - self._cache[cache_key]["timestamp"]
                        _LOGGER.info(
                            f"Returning cached {cache_key} data from {int(cache_age/60)} minutes ago"
                        )
                        return copy.deepcopy(cached)
                    else:
                        _LOGGER.error(f"No cached {cache_key} data available")
                        return None
        self.last_update_success = False
        return None
    
    async def get_locations_data(self):
        """Get JSON location name from BOM API endpoint."""
        headers = {"User-Agent": "MakeThisAPIOpenSource/1.0.0"}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                data = await self._fetch_with_retry(
                    session, URL_BASE + self.geohash7, "locations"
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

                hourly_row = _get_current_hourly_row(self.hourly_forecasts_data)

                # Fallback is_night from hourly feed if missing from daily now dictionary
                if is_night is None and hourly_row:
                    is_night = hourly_row.get("is_night")

                # If daily icon is null (e.g. late evening before local midnight rollover),
                # pull descriptor from current hour in the hourly forecast feed if available:
                if icon_desc is None and hourly_row:
                    icon_desc = hourly_row.get("icon_descriptor")
                    d["icon_descriptor"] = icon_desc

                # Override icon_descriptor if it's night and icon is sunny/mostly_sunny
                if is_night and icon_desc in {"sunny", "mostly_sunny"}:
                    d["icon_descriptor"] = "clear"
                # Override icon_descriptor if its clear during the day
                elif not is_night and icon_desc == "clear":
                    d["icon_descriptor"] = "sunny"

                # Retain morning minimum temperature during afternoon/evening using BOM's now sliding window
                if d.get("temp_min") is None:
                    now_label = (d.get("now_now_label") or "").lower()
                    later_label = (d.get("now_later_label") or "").lower()

                    if "min" in now_label and d.get("now_temp_now") is not None:
                        d["temp_min"] = d.get("now_temp_now")
                    elif "min" in later_label and d.get("now_temp_later") is not None:
                        d["temp_min"] = d.get("now_temp_later")
                    elif not now_label and not later_label:
                        if d.get("now_temp_later") is not None:
                            d["temp_min"] = d.get("now_temp_later")
                        elif d.get("now_temp_now") is not None:
                            d["temp_min"] = d.get("now_temp_now")

                # If short_text is null, pull from current hour in hourly forecast feed
                if d.get("short_text") is None and hourly_row:
                    d["short_text"] = hourly_row.get("short_text")

            d["mdi_icon"] = MAP_MDI_ICON.get(d.get("icon_descriptor"))

            # If rain amount max is None, set as rain amount min
            if d["rain_amount_max"] is None:
                d["rain_amount_max"] = d["rain_amount_min"]
                d["rain_amount_range"] = d["rain_amount_min"]
            else:
                d["rain_amount_range"] = f"{d['rain_amount_min']}–{d['rain_amount_max']}"


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

            d["mdi_icon"] = MAP_MDI_ICON.get(d.get("icon_descriptor"))

            flatten_dict(["amount"], d["rain"])
            flatten_dict(["rain", "wind"], d)

            # If rain amount max is None, set as rain amount min
            if d["rain_amount_max"] is None:
                d["rain_amount_max"] = d["rain_amount_min"]
                d["rain_amount_range"] = d["rain_amount_min"]
            else:
                d["rain_amount_range"] = f"{d['rain_amount_min']} to {d['rain_amount_max']}"

    @Throttle(datetime.timedelta(minutes=5))
    async def async_update(self):
        """Refresh the data on the collector object."""
        headers = {"User-Agent": "MakeThisAPIOpenSource/1.0.0"}
        # This is inside Throttle: a skipped call must preserve the last outcome.
        self.last_update_success = True
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                # Get location data if not already available
                if self.locations_data is None:
                    data = await self._fetch_with_retry(
                        session, URL_BASE + self.geohash7, "locations"
                    )
                    if data:
                        self.locations_data = data
                
                # Get observations data
                data = await self._fetch_with_retry(
                    session, URL_BASE + self.geohash6 + URL_OBSERVATIONS, "observations"
                )
                if data:
                    self.observations_data = data
                    if self.observations_data["data"]["wind"] is not None:
                        flatten_dict(["wind"], self.observations_data["data"])
                    else:
                        self.observations_data["data"]["wind_direction"] = "unavailable"
                        self.observations_data["data"]["wind_speed_kilometre"] = "unavailable"
                        self.observations_data["data"]["wind_speed_knot"] = "unavailable"
                    if self.observations_data["data"]["gust"] is not None:
                        flatten_dict(["gust"], self.observations_data["data"])
                    else:
                        self.observations_data["data"]["gust_speed_kilometre"] = "unavailable"
                        self.observations_data["data"]["gust_speed_knot"] = "unavailable"

                # Get hourly forecast data
                data = await self._fetch_with_retry(
                    session, URL_BASE + self.geohash6 + URL_HOURLY, "hourly_forecasts"
                )
                if data:
                    self.hourly_forecasts_data = data
                    await self.format_hourly_forecast_data()

                # Get daily forecast data
                data = await self._fetch_with_retry(
                    session, URL_BASE + self.geohash6 + URL_DAILY, "daily_forecasts"
                )
                if data:
                    self.daily_forecasts_data = data
                    await self.format_daily_forecast_data()

                # Get warnings data
                data = await self._fetch_with_retry(
                    session, URL_BASE + self.geohash6 + URL_WARNINGS, "warnings"
                )
                if data:
                    self.warnings_data = data
                    
        except Exception as err:
            self.last_update_success = False
            _LOGGER.error(f"Unexpected error during async_update: {err}")
            # Even if we have an unexpected error, we still have our cached data

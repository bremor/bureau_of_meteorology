"""BOM data 'collector' that downloads the observation data."""
import aiohttp
import asyncio
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

class Collector:
    """Collector for PyBoM."""

    def __init__(self, latitude, longitude):
        """Init collector."""
        self.locations_data = None
        self.observations_data = None
        self.daily_forecasts_data = None
        self.hourly_forecasts_data = None
        self.warnings_data = None
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
                        self._cache[cache_key]["data"] = data
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

            d["mdi_icon"] = MAP_MDI_ICON[d["icon_descriptor"]]

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

                # Get daily forecast data
                data = await self._fetch_with_retry(
                    session, URL_BASE + self.geohash6 + URL_DAILY, "daily_forecasts"
                )
                if data:
                    self.daily_forecasts_data = data
                    await self.format_daily_forecast_data()

                # Get hourly forecast data
                data = await self._fetch_with_retry(
                    session, URL_BASE + self.geohash6 + URL_HOURLY, "hourly_forecasts"
                )
                if data:
                    self.hourly_forecasts_data = data
                    await self.format_hourly_forecast_data()

                # Get warnings data
                data = await self._fetch_with_retry(
                    session, URL_BASE + self.geohash6 + URL_WARNINGS, "warnings"
                )
                if data:
                    self.warnings_data = data
                    
        except Exception as err:
            _LOGGER.error(f"Unexpected error during async_update: {err}")
            # Even if we have an unexpected error, we still have our cached data

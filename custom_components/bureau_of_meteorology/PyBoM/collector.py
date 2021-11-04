"""BOM data 'collector' that downloads the observation data."""
import aiohttp
import asyncio
import datetime
import logging

from homeassistant.util import Throttle

from .const import (
    MAP_MDI_ICON, MAP_UV, URL_BASE, URL_DAILY_FORECASTS, URL_HOURLY_FORECASTS,
    URL_LOCATIONS, URL_OBSERVATIONS,
)
from .helpers import (
    flatten_dict, geohash_encode,
)

_LOGGER = logging.getLogger(__name__)

class Collector:
    """Collector for PyBoM."""

    def __init__(self, latitude, longitude):
        """Init collector."""
        self.observations_data = None
        self.daily_forecasts_data = None
        self.hourly_forecasts_data = None
        self.geohash = geohash_encode(latitude, longitude)

    async def get_location_name(self):
        """Get JSON location name from BOM API endpoint."""
        url = URL_BASE + URL_LOCATIONS.format(self.geohash)

        async with aiohttp.ClientSession() as session:
            response = await session.get(url)

        if response is not None and response.status == 200:
            locations_data = await response.json()
            self.location_name = locations_data["data"]["name"]
            return True

    async def async_get_observations_data(self):
        """Get JSON observations data from BOM API endpoint."""
        url = URL_OBSERVATIONS.format(self.geohash)
        _LOGGER.debug(f"Observations URL: {url}")

        async with aiohttp.ClientSession() as session:
            response = await session.get(url)

        if response is not None and response.status == 200:
            self.observations_data = await response.json()
            flatten_dict(["wind", "gust"], self.observations_data["data"])
            _LOGGER.debug(f"Observations data: {self.observations_data}")

    async def async_get_daily_forecasts_data(self):
        """Get JSON daily forecasts data from BOM API endpoint."""
        url = URL_BASE + URL_DAILY_FORECASTS.format(self.geohash)
        _LOGGER.debug(f"Forecasts URL: {url}")

        async with aiohttp.ClientSession() as session:
            response = await session.get(url)

        if response is not None and response.status == 200:
            self.daily_forecasts_data = await response.json()
            await self.format_forecast_data()
            _LOGGER.debug(f"Forecasts data: {self.daily_forecasts_data}")

    async def format_forecast_data(self):
        """Format forecast data."""
        days = len(self.daily_forecasts_data["data"])
        for day in range(0, days):

            d = self.daily_forecasts_data["data"][day]

            d["mdi_icon"] = MAP_MDI_ICON[d["icon_descriptor"]]

            flatten_dict(["amount"], d["rain"])
            flatten_dict(["rain", "uv"], d)

            # If rain amount max is None, set as rain amount min
            if d["rain_amount_max"] is None:
                d["rain_amount_max"] = d["rain_amount_min"]
                d["rain_amount_range"] = d["rain_amount_min"]
            else:
                d["rain_amount_range"] = f"{d['rain_amount_min']} to {d['rain_amount_max']}"


    async def async_get_hourly_forecasts_data(self):
        """Get JSON hourly forecasts data from BOM API endpoint."""
        url = URL_BASE + URL_HOURLY_FORECASTS.format(self.geohash)
        _LOGGER.debug(f"Hourly Forecasts URL: {url}")

        async with aiohttp.ClientSession() as session:
            response = await session.get(url)

        if response is not None and response.status == 200:
            self.hourly_forecasts_data = await response.json()
            await self.format_hourly_forecast_data()
            _LOGGER.debug(f"Hourly Forecasts data: {self.hourly_forecasts_data}")

    async def format_hourly_forecast_data(self):
        """Format forecast data."""
        hours = len(self.hourly_forecasts_data["data"])
        for hour in range(0, hours):

            d = self.hourly_forecasts_data["data"][hour]

            d["mdi_icon"] = MAP_MDI_ICON[d["icon_descriptor"]]

            flatten_dict(["amount"], d["rain"])
            flatten_dict(["rain", "wind"], d)

            # If rain amount max is None, set as rain amount min
            if d["rain_amount_max"] is None:
                d["rain_amount_max"] = d["rain_amount_min"]
                d["rain_amount_range"] = d["rain_amount_min"]
            else:
                d["rain_amount_range"] = f"{d['rain_amount_min']} to {d['rain_amount_max']}"


    @Throttle(datetime.timedelta(minutes=10))
    async def async_update(self):
        """Refresh the data on the collector object."""
        await self.async_get_observations_data()
        await self.async_get_daily_forecasts_data()
        await self.async_get_hourly_forecasts_data()

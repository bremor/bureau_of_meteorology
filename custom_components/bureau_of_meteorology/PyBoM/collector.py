"""BOM data 'collector' that downloads the observation data."""
import asyncio
import datetime
import aiohttp
import logging

from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(minutes=10)
DAILY_FORECASTS_URL = "https://api.weather.bom.gov.au/v1/locations/{}/forecasts/daily"
LOCATIONS_URL = "https://api.weather.bom.gov.au/v1/locations/{}"
OBSERVATIONS_URL = "https://api.weather.bom.gov.au/v1/locations/{}/observations"


class Collector:
    """Data collector for BOM integration."""

    def __init__(self, latitude, longitude):
        """Init BOM data collector."""
        self.observations_data = None
        self.daily_forecasts_data = None
        self.geohash = self.geohash_encode(latitude, longitude)
        _LOGGER.debug(f"geohash: {self.geohash}")

    async def get_location_name(self):
        """Get JSON location name from BOM API endpoint."""
        url = LOCATIONS_URL.format(self.geohash)

        async with aiohttp.ClientSession() as session:
            response = await session.get(url)

        if response is not None and response.status == 200:
            locations_data = await response.json()
            self.location_name = locations_data["data"]["name"]

    async def get_observations_data(self):
        """Get JSON observations data from BOM API endpoint."""
        url = OBSERVATIONS_URL.format(self.geohash)

        async with aiohttp.ClientSession() as session:
            response = await session.get(url)

        if response is not None and response.status == 200:
            self.observations_data = await response.json()
            await self.flatten_data()
            return True

    async def get_daily_forecasts_data(self):
        """Get JSON daily forecasts data from BOM API endpoint."""
        url = DAILY_FORECASTS_URL.format(self.geohash)

        async with aiohttp.ClientSession() as session:
            response = await session.get(url)

        if response is not None and response.status == 200:
            self.daily_forecasts_data = await response.json()
            await self.flatten_forecast_data()

    async def flatten_data(self):
        """Flatten out wind and gust data."""
        flattened = {}
        for observation in self.observations_data["data"]:
            if observation == "wind" or observation == "gust":
                for sub_observation in self.observations_data["data"][observation]:
                    flattened[f"{observation}_{sub_observation}"] = self.observations_data["data"][observation][sub_observation]
        self.observations_data["data"].update(flattened)

    async def flatten_forecast_data(self):
        """Flatten out forecast data."""
        flattened = {}
        for day in range(0, 6):
            flattened["uv_category"] = self.daily_forecasts_data["data"][day]["uv"]["category"]
            flattened["uv_max_index"] = self.daily_forecasts_data["data"][day]["uv"]["max_index"]
            flattened["uv_start_time"] = self.daily_forecasts_data["data"][day]["uv"]["start_time"]
            flattened["uv_end_time"] = self.daily_forecasts_data["data"][day]["uv"]["end_time"]
            flattened["rain_amount_min"] = self.daily_forecasts_data["data"][day]["rain"]["amount"]["min"]
            flattened["rain_amount_max"] = self.daily_forecasts_data["data"][day]["rain"]["amount"]["max"]
            flattened["rain_chance"] = self.daily_forecasts_data["data"][day]["rain"]["chance"]
            self.daily_forecasts_data["data"][day].update(flattened)
        
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Refresh the data on the collector object."""
        await self.get_observations_data()
        await self.get_daily_forecasts_data()

    def geohash_encode(self, latitude, longitude, precision=6):
        base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
        lat_interval = (-90.0, 90.0)
        lon_interval = (-180.0, 180.0)
        geohash = []
        bits = [16, 8, 4, 2, 1]
        bit = 0
        ch = 0
        even = True
        while len(geohash) < precision:
            if even:
                mid = (lon_interval[0] + lon_interval[1]) / 2
                if longitude > mid:
                    ch |= bits[bit]
                    lon_interval = (mid, lon_interval[1])
                else:
                    lon_interval = (lon_interval[0], mid)
            else:
                mid = (lat_interval[0] + lat_interval[1]) / 2
                if latitude > mid:
                    ch |= bits[bit]
                    lat_interval = (mid, lat_interval[1])
                else:
                    lat_interval = (lat_interval[0], mid)
            even = not even
            if bit < 4:
                bit += 1
            else:
                geohash += base32[ch]
                bit = 0
                ch = 0
        return ''.join(geohash)

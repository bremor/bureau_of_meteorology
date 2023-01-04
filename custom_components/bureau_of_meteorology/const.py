"""Constants for the BOM integration."""

from typing import Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
)

from homeassistant.const import (
    LENGTH_MILLIMETERS,
    PERCENTAGE,
    TEMP_CELSIUS,
)

ATTRIBUTION: Final = "Data provided by the Australian Bureau of Meteorology"
SHORT_ATTRIBUTION: Final = "Australian Bureau of Meteorology"
COLLECTOR: Final = "collector"
UPDATE_LISTENER: Final = "update_listener"

CONF_WEATHER_NAME: Final = "weather_name"
CONF_FORECASTS_BASENAME: Final = "forecasts_basename"
CONF_FORECASTS_CREATE: Final = "forecasts_create"
CONF_FORECASTS_DAYS: Final = "forecasts_days"
CONF_FORECASTS_MONITORED: Final = "forecasts_monitored"
CONF_OBSERVATIONS_BASENAME: Final = "observations_basename"
CONF_OBSERVATIONS_CREATE: Final = "observations_create"
CONF_OBSERVATIONS_MONITORED: Final = "observations_monitored"
CONF_WARNINGS_CREATE: Final = "warnings_create"
CONF_WARNINGS_BASENAME: Final = "warnings_basename"

COORDINATOR: Final = "coordinator"
DOMAIN: Final = "bureau_of_meteorology"

MAP_CONDITION: Final = {
    "clear": "clear-night",
    "cloudy": "cloudy",
    "cyclone": "exceptional",
    "dust": "fog",
    "dusty": "fog",
    "fog": "fog",
    "frost": "snowy",
    "haze": "fog",
    "hazy": "fog",
    "heavy_shower": "rainy",
    "heavy_showers": "rainy",
    "light_rain": "rainy",
    "light_shower": "rainy",
    "light_showers": "rainy",
    "mostly_sunny": "sunny",
    "partly_cloudy": "partlycloudy",
    "rain": "rainy",
    "shower": "rainy",
    "showers": "rainy",
    "snow": "snowy",
    "storm": "lightning-rainy",
    "storms": "lightning-rainy",
    "sunny": "sunny",
    "tropical_cyclone": "exceptional",
    "wind": "windy",
    "windy": "windy",
    None: None,
}

SENSOR_NAMES: Final = {
    "temp": [TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE],
    "temp_feels_like": [TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE],
    "max_temp": [TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE],
    "min_temp": [TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE],
    "rain_since_9am": [LENGTH_MILLIMETERS, SensorDeviceClass.PRECIPITATION],
    "humidity": [PERCENTAGE, SensorDeviceClass.HUMIDITY],
    "wind_speed_kilometre": ["km/h", SensorDeviceClass.WIND_SPEED],
    "wind_speed_knot": ["kn", SensorDeviceClass.WIND_SPEED],
    "wind_direction": [None, None],
    "gust_speed_kilometre": ["km/h", SensorDeviceClass.WIND_SPEED],
    "gust_speed_knot": ["kn", SensorDeviceClass.WIND_SPEED],
    "temp_max": [TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE],
    "temp_min": [TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE],
    "extended_text": [None, None],
    "icon_descriptor": [None, None],
    "mdi_icon": [None, None],
    "short_text": [None, None],
    "uv_category": [None, None],
    "uv_max_index": ["UV", None],
    "uv_start_time": [None, SensorDeviceClass.TIMESTAMP],
    "uv_end_time": [None, SensorDeviceClass.TIMESTAMP],
    "uv_forecast": [None, None],
    "rain_amount_min": [LENGTH_MILLIMETERS, SensorDeviceClass.PRECIPITATION],
    "rain_amount_max": [LENGTH_MILLIMETERS, SensorDeviceClass.PRECIPITATION],
    "rain_amount_range": [LENGTH_MILLIMETERS, SensorDeviceClass.DISTANCE],
    "rain_chance": [PERCENTAGE, None],
    "fire_danger": [None, None],
    "now_now_label": [None, None],
    "now_temp_now": [TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE],
    "now_later_label": [None, None],
    "now_temp_later": [TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE],
    "astronomical_sunrise_time": [None, SensorDeviceClass.TIMESTAMP],
    "astronomical_sunset_time": [None, SensorDeviceClass.TIMESTAMP],
    "warnings": [None, None],
}

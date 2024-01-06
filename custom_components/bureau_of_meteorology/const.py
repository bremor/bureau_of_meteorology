"""Constants for the BOM integration."""

from typing import Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.const import (
    PERCENTAGE,
    DEGREE,
    UnitOfTemperature,
    UnitOfLength,
    UnitOfSpeed,
)

ATTRIBUTION: Final = "Data provided by the Australian Bureau of Meteorology"
SHORT_ATTRIBUTION: Final = "Australian Bureau of Meteorology"
MODEL_NAME: Final = "Weather Sensor"
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

ATTR_API_TEMP: Final = "temp"
ATTR_API_TEMP_FEELS_LIKE: Final = "temp_feels_like"
ATTR_API_MAX_TEMP: Final = "max_temp"
ATTR_API_MIN_TEMP: Final = "min_temp"
ATTR_API_RAIN_SINCE_9AM: Final = "rain_since_9am"
ATTR_API_HUMIDITY: Final = "humidity"
ATTR_API_WIND_SPEED_KILOMETRE: Final = "wind_speed_kilometre"
ATTR_API_WIND_SPEED_KNOT: Final = "wind_speed_knot"
ATTR_API_WIND_DIRECTION: Final = "wind_direction"
ATTR_API_GUST_SPEED_KILOMETRE: Final = "gust_speed_kilometre"
ATTR_API_GUST_SPEED_KNOT: Final = "gust_speed_knot"

ATTR_API_TEMP_MAX: Final = "temp_max"
ATTR_API_TEMP_MIN: Final = "temp_min"
ATTR_API_EXTENDED_TEXT: Final = "extended_text"
ATTR_API_ICON_DESCRIPTOR: Final = "icon_descriptor"
ATTR_API_MDI_ICON: Final = "mdi_icon"
ATTR_API_SHORT_TEXT: Final = "short_text"
ATTR_API_UV_CATEGORY: Final = "uv_category"
ATTR_API_UV_MAX_INDEX: Final = "uv_max_index"
ATTR_API_UV_START_TIME: Final = "uv_start_time"
ATTR_API_UV_END_TIME: Final = "uv_end_time"
ATTR_API_UV_FORECAST: Final = "uv_forecast"
ATTR_API_RAIN_AMOUNT_MIN: Final = "rain_amount_min"
ATTR_API_RAIN_AMOUNT_MAX: Final = "rain_amount_max"
ATTR_API_RAIN_AMOUNT_RANGE: Final = "rain_amount_range"
ATTR_API_RAIN_CHANCE: Final = "rain_chance"
ATTR_API_FIRE_DANGER: Final = "fire_danger"
ATTR_API_NON_NOW_LABEL: Final = "now_now_label"
ATTR_API_NON_TEMP_NOW: Final = "now_temp_now"
ATTR_API_NOW_LATER_LABEL: Final = "now_later_label"
ATTR_API_NOW_TEMP_LATER: Final = "now_temp_later"
ATTR_API_ASTRONOMICAL_SUNRISE_TIME: Final = "astronomical_sunrise_time"
ATTR_API_ASTRONOMICAL_SUNSET_TIME: Final = "astronomical_sunset_time"
ATTR_API_WARNINGS: Final = "warnings"

OBSERVATION_SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=ATTR_API_TEMP,
        name="Current Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_TEMP_FEELS_LIKE,
        name="Current Feels Like Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_MAX_TEMP,
        name="Todays Observed Maximum Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_MIN_TEMP,
        name="Todays Observed Minimum Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_RAIN_SINCE_9AM,
        name="Rain Since 9am",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=ATTR_API_HUMIDITY,
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_WIND_SPEED_KILOMETRE,
        name="Wind Speed km/h",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_WIND_SPEED_KNOT,
        name="Wind Speed kn",
        native_unit_of_measurement=UnitOfSpeed.KNOTS,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_WIND_DIRECTION,
        name="Wind Direction",
    ),
    SensorEntityDescription(
        key=ATTR_API_GUST_SPEED_KILOMETRE,
        name="Gust Speed km/h",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_API_GUST_SPEED_KNOT,
        name="Gust Speed kn",
        native_unit_of_measurement=UnitOfSpeed.KNOTS,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dew_point",
        name="Dew Point",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

FORECAST_SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=ATTR_API_TEMP_MAX,
        name="Forecast Maximum Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    SensorEntityDescription(
        key=ATTR_API_TEMP_MIN,
        name="Forecast Minimum Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    SensorEntityDescription(
        key=ATTR_API_EXTENDED_TEXT,
        name="Extended Forecast",
    ),
    SensorEntityDescription(
        key=ATTR_API_ICON_DESCRIPTOR,
        name="Icon Descriptor",
    ),
    SensorEntityDescription(
        key=ATTR_API_MDI_ICON,
        name="MDI Icon",
    ),
    SensorEntityDescription(
        key=ATTR_API_SHORT_TEXT,
        name="Short Summary Forecast",
    ),
    SensorEntityDescription(
        key=ATTR_API_UV_CATEGORY,
        name="UV Category",
    ),
    SensorEntityDescription(
        key=ATTR_API_UV_MAX_INDEX,
        name="UV Maximum Index",
    ),
    SensorEntityDescription(
        key=ATTR_API_UV_START_TIME,
        name="UV Protection Start Time",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=ATTR_API_UV_END_TIME,
        name="UV Protection End Time",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=ATTR_API_UV_FORECAST,
        name="UV Forecast Summary",
    ),
    SensorEntityDescription(
        key=ATTR_API_RAIN_AMOUNT_MIN,
        name="Rain Amount Minimum",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
    ),
    SensorEntityDescription(
        key=ATTR_API_RAIN_AMOUNT_MAX,
        name="Rain Amount Maximum",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
    ),
    SensorEntityDescription(
        key=ATTR_API_RAIN_AMOUNT_RANGE,
        name="Rain Amount Range",
    ),
    SensorEntityDescription(
        key=ATTR_API_RAIN_CHANCE,
        name="Rain Probability",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key=ATTR_API_FIRE_DANGER,
        name="Fire Danger",
    ),
    SensorEntityDescription(
        key=ATTR_API_NON_NOW_LABEL,
        name="Now Label",
    ),
    SensorEntityDescription(
        key=ATTR_API_NON_TEMP_NOW,
        name="Now Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    SensorEntityDescription(
        key=ATTR_API_NOW_LATER_LABEL,
        name="Later Label",
    ),
    SensorEntityDescription(
        key=ATTR_API_NOW_TEMP_LATER,
        name="Later Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    SensorEntityDescription(
        key=ATTR_API_ASTRONOMICAL_SUNRISE_TIME,
        name="Sunrise Time",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    SensorEntityDescription(
        key=ATTR_API_ASTRONOMICAL_SUNSET_TIME,
        name="Sunset Time",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
)

WARNING_SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=ATTR_API_WARNINGS,
        name="Warnings",
    ),
)

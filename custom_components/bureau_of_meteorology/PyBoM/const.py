"""Constants for PyBoM."""

MAP_MDI_ICON = {
    "clear": "mdi:weather-night",
    "cloudy": "mdi:weather-cloudy",
    "cyclone": "mdi:weather-hurricane",
    "dust": "mdi:weather-hazy",
    "dusty": "mdi:weather-hazy",
    "fog": "mdi:weather-fog",
    "frost": "mdi:snowflake-melt",
    "haze": "mdi:weather-hazy",
    "hazy": "mdi:weather-hazy",
    "heavy_shower": "mdi:weather-pouring",
    "heavy_showers": "mdi:weather-pouring",
    "light_rain": "mdi:weather-partly-rainy",
    "light_shower": "mdi:weather-light-showers",
    "light_showers": "mdi:weather-light-showers",
    "mostly_sunny": "mdi:weather-sunny",
    "partly_cloudy": "mdi:weather-partly-cloudy",
    "rain": "mdi:weather-pouring",
    "shower": "mdi:weather-rainy",
    "showers": "mdi:weather-rainy",
    "snow": "mdi:weather-snowy",
    "storm": "mdi:weather-lightning-rainy",
    "storms": "mdi:weather-lightning-rainy",
    "sunny": "mdi:weather-sunny",
    "tropical_cyclone": "mdi:weather-hurricane",
    "wind": "mdi:weather-windy",
    "windy": "mdi:weather-windy",
    None: None,
}
MAP_UV = {
    "extreme": "Extreme",
    "veryhigh": "Very High",
    "high": "High",
    "moderate": "Moderate",
    "low": "Low",
    None: None,
}

URL_BASE = "https://api.weather.bom.gov.au/v1/locations/"
URL_DAILY = "/forecasts/daily"
URL_HOURLY = "/forecasts/hourly"
URL_OBSERVATIONS = "/observations"
URL_WARNINGS = "/warnings"

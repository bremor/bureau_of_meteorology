# Bureau of Meteorology API documentation

This folder contains example output of the BoM's non-documented API's. The API's are used by the BoM's mobile app as well as https://weather.bom.gov.au

The are a number of different API's that all return data as json. To select the location the url's include a 7 character geohash.

## Location Search

This is used to fetch the geohash for a given latitude/longitude.

https://api.weather.bom.gov.au/v1/locations?search=-12.463763,130.844398

```json
{
  "metadata": {
    "response_timestamp": "2022-10-07T00:04:27Z",
    "copyright": "This Application Programming Interface (API) is owned by the Bureau of Meteorology (Bureau). You must not use, copy or share it. Please contact us for more information on ways in which you can access our data. Follow this link http://www.bom.gov.au/inside/contacts.shtml to view our contact details."
  },
  "data": [
    {
      "geohash": "qvv117j",
      "id": "Darwin City-qvv117j",
      "name": "Darwin City",
      "postcode": null,
      "state": "NT"
    }
  ]
}
```

## Location Info

This returns a set of information for the given geohash.

https://api.weather.bom.gov.au/v1/locations/{geohash}

```json
{
  "metadata": {
    "response_timestamp": "2022-10-07T00:27:52Z",
    "copyright": "This Application Programming Interface (API) is owned by the Bureau of Meteorology (Bureau). You must not use, copy or share it. Please contact us for more information on ways in which you can access our data. Follow this link http://www.bom.gov.au/inside/contacts.shtml to view our contact details."
  },
  "data": {
    "geohash": "qvv117n",
    "timezone": "Australia/Darwin",
    "latitude": -12.463302612304688,
    "longitude": 130.84510803222656,
    "marine_area_id": "NT_MW007",
    "tidal_point": "NT_TP001",
    "has_wave": true,
    "id": "Darwin City-qvv117n",
    "name": "Darwin City",
    "state": "NT"
  }
}
```

## Observations

This returns the observation from the nearest monitoring station.

https://api.weather.bom.gov.au/v1/locations/{geohas}/observations

```json
{
  "metadata": {
    "response_timestamp": "2022-10-07T00:19:26Z",
    "issue_time": "2022-10-07T00:11:02Z",
    "observation_time": "2022-10-07T00:10:00Z",
    "copyright": "This Application Programming Interface (API) is owned by the Bureau of Meteorology (Bureau). You must not use, copy or share it. Please contact us for more information on ways in which you can access our data. Follow this link http://www.bom.gov.au/inside/contacts.shtml to view our contact details."
  },
  "data": {
    "temp": 30.5,
    "temp_feels_like": 33.6,
    "wind": {
      "speed_kilometre": 11,
      "speed_knot": 6,
      "direction": "SW"
    },
    "gust": {
      "speed_kilometre": 13,
      "speed_knot": 7
    },
    "max_gust": {
      "speed_kilometre": 20,
      "speed_knot": 11,
      "time": "2022-10-06T16:43:00Z"
    },
    "max_temp": {
      "time": "2022-10-07T00:01:00Z",
      "value": 30.7
    },
    "min_temp": {
      "time": "2022-10-06T20:57:00Z",
      "value": 25.5
    },
    "rain_since_9am": 0,
    "humidity": 64,
    "station": {
      "bom_id": "014015",
      "name": "Darwin Airport",
      "distance": 6899
    }
  }
}
```

## Daily forecasts

This returns the daily forecasts for the given geohash.

https://api.weather.bom.gov.au/v1/locations/{geohas}/forecasts/daily

```json
{
  "data": [
    {
      "rain": {
        "amount": {
          "min": 1,
          "max": 4,
          "lower_range": 0,
          "upper_range": 4,
          "units": "mm"
        },
        "chance": 70,
        "precipitation_amount_25_percent_chance": 4,
        "precipitation_amount_50_percent_chance": 1,
        "precipitation_amount_75_percent_chance": 0
      },
      "uv": {
        "category": "extreme",
        "end_time": "2022-10-07T06:50:00Z",
        "max_index": 12,
        "start_time": "2022-10-06T23:20:00Z"
      },
      "astronomical": {
        "sunrise_time": "2022-10-06T20:57:40Z",
        "sunset_time": "2022-10-07T09:13:56Z"
      },
      "date": "2022-10-06T14:30:00Z",
      "temp_max": 34,
      "temp_min": 25,
      "extended_text": "Partly cloudy. Medium chance of showers. The chance of a thunderstorm. Light winds becoming northwesterly 15 to 25 km/h in the middle of the day then tending westerly in the evening.",
      "icon_descriptor": "storm",
      "short_text": "Shower or two. Possible storm.",
      "surf_danger": "High",
      "fire_danger": "High",
      "fire_danger_category": {
        "text": "High",
        "default_colour": "#fedd3a",
        "dark_mode_colour": "#fedd3a"
      },
      "now": {
        "is_night": false,
        "now_label": "Max",
        "later_label": "Overnight Min",
        "temp_now": 34,
        "temp_later": 25
      }
    },
    {
      "rain": {
        "amount": {
          "min": 3,
          "max": 10,
          "lower_range": 0,
          "upper_range": 10,
          "units": "mm"
        },
        "chance": 70,
        "precipitation_amount_25_percent_chance": 10,
        "precipitation_amount_50_percent_chance": 3,
        "precipitation_amount_75_percent_chance": 0
      },
      "uv": {
        "category": "extreme",
        "end_time": "2022-10-08T06:50:00Z",
        "max_index": 13,
        "start_time": "2022-10-07T23:20:00Z"
      },
      "astronomical": {
        "sunrise_time": "2022-10-07T20:57:01Z",
        "sunset_time": "2022-10-08T09:13:59Z"
      },
      "date": "2022-10-07T14:30:00Z",
      "temp_max": 34,
      "temp_min": 25,
      "extended_text": "Partly cloudy. High chance of showers. The chance of a thunderstorm. Light winds becoming northwesterly 15 to 20 km/h in the early afternoon then becoming light in the late afternoon.",
      "icon_descriptor": "storm",
      "short_text": "Shower or two. Possible storm.",
      "surf_danger": null,
      "fire_danger": "Moderate",
      "fire_danger_category": {
        "text": "Moderate",
        "default_colour": "#64bf30",
        "dark_mode_colour": "#64bf30"
      }
    },
    {
      "rain": {
        "amount": {
          "min": 6,
          "max": 15,
          "lower_range": 2,
          "upper_range": 15,
          "units": "mm"
        },
        "chance": 80,
        "precipitation_amount_25_percent_chance": 15,
        "precipitation_amount_50_percent_chance": 6,
        "precipitation_amount_75_percent_chance": 2
      },
      "uv": {
        "category": "extreme",
        "end_time": "2022-10-09T06:50:00Z",
        "max_index": 13,
        "start_time": "2022-10-08T23:10:00Z"
      },
      "astronomical": {
        "sunrise_time": "2022-10-08T20:56:23Z",
        "sunset_time": "2022-10-09T09:14:02Z"
      },
      "date": "2022-10-08T14:30:00Z",
      "temp_max": 34,
      "temp_min": 25,
      "extended_text": "Partly cloudy. High chance of showers. The chance of a thunderstorm. Light winds.",
      "icon_descriptor": "storm",
      "short_text": "Showers. Possible storm.",
      "surf_danger": null,
      "fire_danger": "Moderate",
      "fire_danger_category": {
        "text": "Moderate",
        "default_colour": "#64bf30",
        "dark_mode_colour": "#64bf30"
      }
    },
    {
      "rain": {
        "amount": {
          "min": 1,
          "max": 6,
          "lower_range": 0,
          "upper_range": 6,
          "units": "mm"
        },
        "chance": 70,
        "precipitation_amount_25_percent_chance": 6,
        "precipitation_amount_50_percent_chance": 1,
        "precipitation_amount_75_percent_chance": 0
      },
      "uv": {
        "category": "extreme",
        "end_time": "2022-10-10T06:50:00Z",
        "max_index": 14,
        "start_time": "2022-10-09T23:10:00Z"
      },
      "astronomical": {
        "sunrise_time": "2022-10-09T20:55:46Z",
        "sunset_time": "2022-10-10T09:14:06Z"
      },
      "date": "2022-10-09T14:30:00Z",
      "temp_max": 35,
      "temp_min": 25,
      "extended_text": "Partly cloudy. High chance of showers, most likely in the morning. The chance of a thunderstorm. Light winds becoming northwest to northeasterly 15 to 20 km/h during the afternoon then becoming light during the evening.",
      "icon_descriptor": "storm",
      "short_text": "Shower or two. Possible storm.",
      "surf_danger": null,
      "fire_danger": "High",
      "fire_danger_category": {
        "text": "High",
        "default_colour": "#fedd3a",
        "dark_mode_colour": "#fedd3a"
      }
    },
    {
      "rain": {
        "amount": {
          "min": 2,
          "max": 8,
          "lower_range": 0,
          "upper_range": 8,
          "units": "mm"
        },
        "chance": 70,
        "precipitation_amount_25_percent_chance": 8,
        "precipitation_amount_50_percent_chance": 2,
        "precipitation_amount_75_percent_chance": 0
      },
      "uv": {
        "category": null,
        "end_time": null,
        "max_index": null,
        "start_time": null
      },
      "astronomical": {
        "sunrise_time": "2022-10-10T20:55:09Z",
        "sunset_time": "2022-10-11T09:14:10Z"
      },
      "date": "2022-10-10T14:30:00Z",
      "temp_max": 33,
      "temp_min": 25,
      "extended_text": "Partly cloudy. High chance of showers, most likely during the morning. The chance of a thunderstorm. Light winds becoming west to northwesterly 15 to 20 km/h during the day.",
      "icon_descriptor": "storm",
      "short_text": "Shower or two. Possible storm.",
      "surf_danger": null,
      "fire_danger": null,
      "fire_danger_category": {
        "text": null,
        "default_colour": null,
        "dark_mode_colour": null
      }
    },
    {
      "rain": {
        "amount": {
          "min": 3,
          "max": 8,
          "lower_range": 0,
          "upper_range": 8,
          "units": "mm"
        },
        "chance": 70,
        "precipitation_amount_25_percent_chance": 8,
        "precipitation_amount_50_percent_chance": 3,
        "precipitation_amount_75_percent_chance": 0
      },
      "uv": {
        "category": null,
        "end_time": null,
        "max_index": null,
        "start_time": null
      },
      "astronomical": {
        "sunrise_time": "2022-10-11T20:54:33Z",
        "sunset_time": "2022-10-12T09:14:15Z"
      },
      "date": "2022-10-11T14:30:00Z",
      "temp_max": 33,
      "temp_min": 25,
      "extended_text": "Partly cloudy. High chance of showers, most likely during the morning. The chance of a thunderstorm. Light winds becoming westerly 15 to 20 km/h during the day.",
      "icon_descriptor": "storm",
      "short_text": "Shower or two. Possible storm.",
      "surf_danger": null,
      "fire_danger": null,
      "fire_danger_category": {
        "text": null,
        "default_colour": null,
        "dark_mode_colour": null
      }
    },
    {
      "rain": {
        "amount": {
          "min": 1,
          "max": 4,
          "lower_range": 0,
          "upper_range": 4,
          "units": "mm"
        },
        "chance": 60,
        "precipitation_amount_25_percent_chance": 4,
        "precipitation_amount_50_percent_chance": 1,
        "precipitation_amount_75_percent_chance": 0
      },
      "uv": {
        "category": null,
        "end_time": null,
        "max_index": null,
        "start_time": null
      },
      "astronomical": {
        "sunrise_time": "2022-10-12T20:53:57Z",
        "sunset_time": "2022-10-13T09:14:20Z"
      },
      "date": "2022-10-12T14:30:00Z",
      "temp_max": 33,
      "temp_min": 26,
      "extended_text": "Partly cloudy. Medium chance of showers. The chance of a thunderstorm. Light winds.",
      "icon_descriptor": "storm",
      "short_text": "Shower or two. Possible storm.",
      "surf_danger": null,
      "fire_danger": null,
      "fire_danger_category": {
        "text": null,
        "default_colour": null,
        "dark_mode_colour": null
      }
    }
  ],
  "metadata": {
    "response_timestamp": "2022-10-07T00:25:37Z",
    "issue_time": "2022-10-07T00:00:16Z",
    "next_issue_time": "2022-10-07T06:30:00Z",
    "forecast_region": "Darwin",
    "forecast_type": "precis",
    "copyright": "This Application Programming Interface (API) is owned by the Bureau of Meteorology (Bureau). You must not use, copy or share it. Please contact us for more information on ways in which you can access our data. Follow this link http://www.bom.gov.au/inside/contacts.shtml to view our contact details."
  }
}
```

## Hourly forecasts

This returns the hourly forecasts for the given geohash.

https://api.weather.bom.gov.au/v1/locations/{geohas}/forecasts/hourly

```json
{
  "metadata": {
    "issue_time": "2022-10-07T00:05:13Z",
    "response_timestamp": "2022-10-07T00:41:49Z",
    "copyright": "This Application Programming Interface (API) is owned by the Bureau of Meteorology (Bureau). You must not use, copy or share it. Please contact us for more information on ways in which you can access our data. Follow this link http://www.bom.gov.au/inside/contacts.shtml to view our contact details."
  },
  "data": [
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 0,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "SSE",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 71,
      "uv": 5,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T03:00:00Z",
      "time": "2022-10-07T00:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T01:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 0,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 31,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "SSW",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 66,
      "uv": 5,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T03:00:00Z",
      "time": "2022-10-07T01:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T02:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 0,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 31,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 5,
        "speed_kilometre": 9,
        "direction": "W",
        "gust_speed_knot": 8,
        "gust_speed_kilometre": 15
      },
      "relative_humidity": 65,
      "uv": 5,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T03:00:00Z",
      "time": "2022-10-07T02:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T03:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 31,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 5,
        "speed_kilometre": 9,
        "direction": "NW",
        "gust_speed_knot": 9,
        "gust_speed_kilometre": 17
      },
      "relative_humidity": 66,
      "uv": 12,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-07T06:00:00Z",
      "time": "2022-10-07T03:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T04:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 32,
      "temp_feels_like": 34,
      "wind": {
        "speed_knot": 9,
        "speed_kilometre": 17,
        "direction": "NW",
        "gust_speed_knot": 14,
        "gust_speed_kilometre": 26
      },
      "relative_humidity": 65,
      "uv": 12,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-07T06:00:00Z",
      "time": "2022-10-07T04:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T05:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 33,
      "temp_feels_like": 34,
      "wind": {
        "speed_knot": 9,
        "speed_kilometre": 17,
        "direction": "NW",
        "gust_speed_knot": 13,
        "gust_speed_kilometre": 24
      },
      "relative_humidity": 61,
      "uv": 12,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-07T06:00:00Z",
      "time": "2022-10-07T05:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T06:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 33,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 9,
        "speed_kilometre": 17,
        "direction": "NW",
        "gust_speed_knot": 13,
        "gust_speed_kilometre": 24
      },
      "relative_humidity": 60,
      "uv": 5,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T09:00:00Z",
      "time": "2022-10-07T06:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T07:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 33,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 9,
        "speed_kilometre": 17,
        "direction": "NW",
        "gust_speed_knot": 13,
        "gust_speed_kilometre": 24
      },
      "relative_humidity": 57,
      "uv": 5,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T09:00:00Z",
      "time": "2022-10-07T07:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T08:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 34,
      "temp_feels_like": 36,
      "wind": {
        "speed_knot": 8,
        "speed_kilometre": 15,
        "direction": "NW",
        "gust_speed_knot": 12,
        "gust_speed_kilometre": 22
      },
      "relative_humidity": 55,
      "uv": 5,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T09:00:00Z",
      "time": "2022-10-07T08:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T09:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 33,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 8,
        "speed_kilometre": 15,
        "direction": "NW",
        "gust_speed_knot": 12,
        "gust_speed_kilometre": 22
      },
      "relative_humidity": 58,
      "uv": 0,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T12:00:00Z",
      "time": "2022-10-07T09:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T10:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 31,
      "temp_feels_like": 32,
      "wind": {
        "speed_knot": 7,
        "speed_kilometre": 13,
        "direction": "WNW",
        "gust_speed_knot": 11,
        "gust_speed_kilometre": 20
      },
      "relative_humidity": 66,
      "uv": 0,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T12:00:00Z",
      "time": "2022-10-07T10:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T11:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 30,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "W",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 70,
      "uv": 0,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T12:00:00Z",
      "time": "2022-10-07T11:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T12:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "W",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 72,
      "uv": 0,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T15:00:00Z",
      "time": "2022-10-07T12:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T13:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 34,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "WNW",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 74,
      "uv": 0,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T15:00:00Z",
      "time": "2022-10-07T13:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T14:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 34,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "WNW",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 77,
      "uv": 0,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-07T15:00:00Z",
      "time": "2022-10-07T14:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T15:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 30,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "WNW",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 77,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-07T18:00:00Z",
      "time": "2022-10-07T15:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T16:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 30,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 28,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "W",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 80,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-07T18:00:00Z",
      "time": "2022-10-07T16:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T17:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 30,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 28,
      "temp_feels_like": 32,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "W",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 82,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-07T18:00:00Z",
      "time": "2022-10-07T17:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T18:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 50,
        "precipitation_amount_10_percent_chance": 3,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 27,
      "temp_feels_like": 32,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "WSW",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 83,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-07T21:00:00Z",
      "time": "2022-10-07T18:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T19:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 50,
        "precipitation_amount_10_percent_chance": 3,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 27,
      "temp_feels_like": 31,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "S",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 86,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-07T21:00:00Z",
      "time": "2022-10-07T19:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T20:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 50,
        "precipitation_amount_10_percent_chance": 3,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 25,
      "temp_feels_like": 30,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "S",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 94,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-07T21:00:00Z",
      "time": "2022-10-07T20:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-07T21:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 26,
      "temp_feels_like": 30,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "S",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 90,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T00:00:00Z",
      "time": "2022-10-07T21:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T22:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 26,
      "temp_feels_like": 31,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "SSE",
        "gust_speed_knot": 5,
        "gust_speed_kilometre": 9
      },
      "relative_humidity": 91,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T00:00:00Z",
      "time": "2022-10-07T22:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-07T23:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 27,
      "temp_feels_like": 32,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "SSE",
        "gust_speed_knot": 5,
        "gust_speed_kilometre": 9
      },
      "relative_humidity": 83,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T00:00:00Z",
      "time": "2022-10-07T23:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T00:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 0,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "SSE",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 74,
      "uv": 5,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-08T03:00:00Z",
      "time": "2022-10-08T00:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T01:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 0,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 30,
      "temp_feels_like": 34,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "NE",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 71,
      "uv": 5,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-08T03:00:00Z",
      "time": "2022-10-08T01:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T02:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 0,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 31,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 5,
        "speed_kilometre": 9,
        "direction": "NNE",
        "gust_speed_knot": 8,
        "gust_speed_kilometre": 15
      },
      "relative_humidity": 68,
      "uv": 5,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-08T03:00:00Z",
      "time": "2022-10-08T02:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T03:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 31,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 5,
        "speed_kilometre": 9,
        "direction": "NNW",
        "gust_speed_knot": 8,
        "gust_speed_kilometre": 15
      },
      "relative_humidity": 67,
      "uv": 13,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T06:00:00Z",
      "time": "2022-10-08T03:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T04:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 32,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 7,
        "speed_kilometre": 13,
        "direction": "NNW",
        "gust_speed_knot": 11,
        "gust_speed_kilometre": 20
      },
      "relative_humidity": 65,
      "uv": 13,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T06:00:00Z",
      "time": "2022-10-08T04:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T05:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 33,
      "temp_feels_like": 36,
      "wind": {
        "speed_knot": 8,
        "speed_kilometre": 15,
        "direction": "NNW",
        "gust_speed_knot": 12,
        "gust_speed_kilometre": 22
      },
      "relative_humidity": 62,
      "uv": 13,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T06:00:00Z",
      "time": "2022-10-08T05:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T06:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 33,
      "temp_feels_like": 36,
      "wind": {
        "speed_knot": 8,
        "speed_kilometre": 15,
        "direction": "NW",
        "gust_speed_knot": 13,
        "gust_speed_kilometre": 24
      },
      "relative_humidity": 61,
      "uv": 5,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T09:00:00Z",
      "time": "2022-10-08T06:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T07:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 34,
      "temp_feels_like": 36,
      "wind": {
        "speed_knot": 9,
        "speed_kilometre": 17,
        "direction": "WNW",
        "gust_speed_knot": 13,
        "gust_speed_kilometre": 24
      },
      "relative_humidity": 58,
      "uv": 5,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T09:00:00Z",
      "time": "2022-10-08T07:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T08:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 34,
      "temp_feels_like": 37,
      "wind": {
        "speed_knot": 7,
        "speed_kilometre": 13,
        "direction": "WNW",
        "gust_speed_knot": 11,
        "gust_speed_kilometre": 20
      },
      "relative_humidity": 58,
      "uv": 5,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T09:00:00Z",
      "time": "2022-10-08T08:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T09:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 33,
      "temp_feels_like": 36,
      "wind": {
        "speed_knot": 7,
        "speed_kilometre": 13,
        "direction": "W",
        "gust_speed_knot": 11,
        "gust_speed_kilometre": 20
      },
      "relative_humidity": 62,
      "uv": 0,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-08T12:00:00Z",
      "time": "2022-10-08T09:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T10:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 31,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "W",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 69,
      "uv": 0,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-08T12:00:00Z",
      "time": "2022-10-08T10:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T11:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 10,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 30,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "W",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 72,
      "uv": 0,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2022-10-08T12:00:00Z",
      "time": "2022-10-08T11:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T12:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 60,
        "precipitation_amount_10_percent_chance": 4,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 30,
      "temp_feels_like": 34,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "W",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 75,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T15:00:00Z",
      "time": "2022-10-08T12:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T13:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 60,
        "precipitation_amount_10_percent_chance": 4,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "WNW",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 78,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T15:00:00Z",
      "time": "2022-10-08T13:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T14:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 60,
        "precipitation_amount_10_percent_chance": 4,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "NNW",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 80,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T15:00:00Z",
      "time": "2022-10-08T14:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T15:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 50,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 28,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "NNE",
        "gust_speed_knot": 5,
        "gust_speed_kilometre": 9
      },
      "relative_humidity": 79,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T18:00:00Z",
      "time": "2022-10-08T15:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T16:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 50,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 28,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "NNE",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 80,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T18:00:00Z",
      "time": "2022-10-08T16:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T17:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 50,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 28,
      "temp_feels_like": 32,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "NE",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 81,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T18:00:00Z",
      "time": "2022-10-08T17:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T18:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 60,
        "precipitation_amount_10_percent_chance": 4,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 28,
      "temp_feels_like": 32,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "NNE",
        "gust_speed_knot": 8,
        "gust_speed_kilometre": 15
      },
      "relative_humidity": 82,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T21:00:00Z",
      "time": "2022-10-08T18:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T19:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 60,
        "precipitation_amount_10_percent_chance": 4,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 27,
      "temp_feels_like": 31,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "E",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 83,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T21:00:00Z",
      "time": "2022-10-08T19:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T20:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 60,
        "precipitation_amount_10_percent_chance": 4,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 26,
      "temp_feels_like": 30,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "E",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 88,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-08T21:00:00Z",
      "time": "2022-10-08T20:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-08T21:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 4,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 26,
      "temp_feels_like": 30,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "SE",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 87,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T00:00:00Z",
      "time": "2022-10-08T21:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T22:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 4,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 25,
      "temp_feels_like": 30,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "ESE",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 92,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T00:00:00Z",
      "time": "2022-10-08T22:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-08T23:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 4,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 26,
      "temp_feels_like": 31,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "ESE",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 90,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T00:00:00Z",
      "time": "2022-10-08T23:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T00:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 27,
      "temp_feels_like": 31,
      "wind": {
        "speed_knot": 5,
        "speed_kilometre": 9,
        "direction": "ESE",
        "gust_speed_knot": 8,
        "gust_speed_kilometre": 15
      },
      "relative_humidity": 83,
      "uv": 5,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T03:00:00Z",
      "time": "2022-10-09T00:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T01:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 32,
      "wind": {
        "speed_knot": 6,
        "speed_kilometre": 11,
        "direction": "NE",
        "gust_speed_knot": 9,
        "gust_speed_kilometre": 17
      },
      "relative_humidity": 72,
      "uv": 5,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T03:00:00Z",
      "time": "2022-10-09T01:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T02:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 30,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 7,
        "speed_kilometre": 13,
        "direction": "NE",
        "gust_speed_knot": 10,
        "gust_speed_kilometre": 19
      },
      "relative_humidity": 68,
      "uv": 5,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T03:00:00Z",
      "time": "2022-10-09T02:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T03:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 31,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 6,
        "speed_kilometre": 11,
        "direction": "NNE",
        "gust_speed_knot": 9,
        "gust_speed_kilometre": 17
      },
      "relative_humidity": 65,
      "uv": 13,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T06:00:00Z",
      "time": "2022-10-09T03:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T04:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 32,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 8,
        "speed_kilometre": 15,
        "direction": "NNE",
        "gust_speed_knot": 13,
        "gust_speed_kilometre": 24
      },
      "relative_humidity": 62,
      "uv": 13,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T06:00:00Z",
      "time": "2022-10-09T04:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T05:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 33,
      "temp_feels_like": 37,
      "wind": {
        "speed_knot": 8,
        "speed_kilometre": 15,
        "direction": "N",
        "gust_speed_knot": 12,
        "gust_speed_kilometre": 22
      },
      "relative_humidity": 57,
      "uv": 13,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T06:00:00Z",
      "time": "2022-10-09T05:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T06:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 33,
      "temp_feels_like": 36,
      "wind": {
        "speed_knot": 8,
        "speed_kilometre": 15,
        "direction": "N",
        "gust_speed_knot": 12,
        "gust_speed_kilometre": 22
      },
      "relative_humidity": 56,
      "uv": 5,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T09:00:00Z",
      "time": "2022-10-09T06:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T07:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 34,
      "temp_feels_like": 37,
      "wind": {
        "speed_knot": 7,
        "speed_kilometre": 13,
        "direction": "N",
        "gust_speed_knot": 11,
        "gust_speed_kilometre": 20
      },
      "relative_humidity": 56,
      "uv": 5,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T09:00:00Z",
      "time": "2022-10-09T07:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T08:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 34,
      "temp_feels_like": 37,
      "wind": {
        "speed_knot": 6,
        "speed_kilometre": 11,
        "direction": "WNW",
        "gust_speed_knot": 10,
        "gust_speed_kilometre": 19
      },
      "relative_humidity": 56,
      "uv": 5,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T09:00:00Z",
      "time": "2022-10-09T08:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T09:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 33,
      "temp_feels_like": 36,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "WSW",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 61,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T12:00:00Z",
      "time": "2022-10-09T09:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T10:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 31,
      "temp_feels_like": 35,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "SW",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 70,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T12:00:00Z",
      "time": "2022-10-09T10:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T11:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 30,
      "temp_feels_like": 34,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "SSW",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 74,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T12:00:00Z",
      "time": "2022-10-09T11:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T12:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 50,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "S",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 75,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T15:00:00Z",
      "time": "2022-10-09T12:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T13:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 50,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 28,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 2,
        "speed_kilometre": 4,
        "direction": "SE",
        "gust_speed_knot": 5,
        "gust_speed_kilometre": 9
      },
      "relative_humidity": 78,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T15:00:00Z",
      "time": "2022-10-09T13:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T14:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 50,
        "precipitation_amount_10_percent_chance": 2,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 27,
      "temp_feels_like": 32,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "ENE",
        "gust_speed_knot": 5,
        "gust_speed_kilometre": 9
      },
      "relative_humidity": 81,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T15:00:00Z",
      "time": "2022-10-09T14:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T15:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 3,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 27,
      "temp_feels_like": 31,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "NE",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 83,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T18:00:00Z",
      "time": "2022-10-09T15:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T16:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 3,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 26,
      "temp_feels_like": 31,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "ENE",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 85,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T18:00:00Z",
      "time": "2022-10-09T16:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T17:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": 1, "units": "mm" },
        "chance": 40,
        "precipitation_amount_10_percent_chance": 3,
        "precipitation_amount_25_percent_chance": 1,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 26,
      "temp_feels_like": 30,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "ENE",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 87,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T18:00:00Z",
      "time": "2022-10-09T17:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T18:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 25,
      "temp_feels_like": 29,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "ENE",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 89,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T21:00:00Z",
      "time": "2022-10-09T18:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T19:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 25,
      "temp_feels_like": 30,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "SE",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 89,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T21:00:00Z",
      "time": "2022-10-09T19:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T20:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 20,
        "precipitation_amount_10_percent_chance": 1,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 25,
      "temp_feels_like": 29,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "SE",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 90,
      "uv": 0,
      "icon_descriptor": "storm",
      "next_three_hourly_forecast_period": "2022-10-09T21:00:00Z",
      "time": "2022-10-09T20:00:00Z",
      "is_night": true,
      "next_forecast_period": "2022-10-09T21:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 5,
        "precipitation_amount_10_percent_chance": 0,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 26,
      "temp_feels_like": 30,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "SE",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 87,
      "uv": 0,
      "icon_descriptor": "sunny",
      "next_three_hourly_forecast_period": "2022-10-10T00:00:00Z",
      "time": "2022-10-09T21:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T22:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 5,
        "precipitation_amount_10_percent_chance": 0,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 26,
      "temp_feels_like": 31,
      "wind": {
        "speed_knot": 3,
        "speed_kilometre": 6,
        "direction": "SE",
        "gust_speed_knot": 6,
        "gust_speed_kilometre": 11
      },
      "relative_humidity": 87,
      "uv": 0,
      "icon_descriptor": "sunny",
      "next_three_hourly_forecast_period": "2022-10-10T00:00:00Z",
      "time": "2022-10-09T22:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-09T23:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 5,
        "precipitation_amount_10_percent_chance": 0,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 28,
      "temp_feels_like": 32,
      "wind": {
        "speed_knot": 4,
        "speed_kilometre": 7,
        "direction": "SE",
        "gust_speed_knot": 7,
        "gust_speed_kilometre": 13
      },
      "relative_humidity": 80,
      "uv": 0,
      "icon_descriptor": "sunny",
      "next_three_hourly_forecast_period": "2022-10-10T00:00:00Z",
      "time": "2022-10-09T23:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-10T00:00:00Z"
    },
    {
      "rain": {
        "amount": { "min": 0, "max": null, "units": "mm" },
        "chance": 5,
        "precipitation_amount_10_percent_chance": 0,
        "precipitation_amount_25_percent_chance": 0,
        "precipitation_amount_50_percent_chance": 0
      },
      "temp": 29,
      "temp_feels_like": 33,
      "wind": {
        "speed_knot": 6,
        "speed_kilometre": 11,
        "direction": "SE",
        "gust_speed_knot": 10,
        "gust_speed_kilometre": 19
      },
      "relative_humidity": 70,
      "uv": 6,
      "icon_descriptor": "sunny",
      "next_three_hourly_forecast_period": "2022-10-10T03:00:00Z",
      "time": "2022-10-10T00:00:00Z",
      "is_night": false,
      "next_forecast_period": "2022-10-10T01:00:00Z"
    }
  ]
}
```

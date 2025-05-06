# Forecast condition
Condition is determined by the `icon_descriptor` entity.

Example:
```
"date": "2025-05-05T16:00:00Z",
      "temp_max": 24,
      "temp_min": 13,
      "extended_text": "Partly cloudy. Light winds becoming southeast to southwesterly 15 to 20 km/h in the early afternoon then tending southeasterly in the evening.",
      "icon_descriptor": "mostly_sunny", <-- Right here
      "short_text": "Partly cloudy.",
      "surf_danger": null,
      "fire_danger": "Moderate",
      "fire_danger_category": {
        "text": "Moderate",
        "default_colour": "#64bf30",
        "dark_mode_colour": "#64bf30"
```

Because the BOM is not uses multiple factors to determine the condition, it appears wrong in home assistant. For example, the `icon_descriptor` could show "sunny" at night time which is not correct.

# Potential fixes
## Add a check to see if the weather is at night
Forecast Daily API call shows a "now" section that gives extra details. 

Example:
```
"now": {
        "is_night": false,
        "now_label": "Max",
        "later_label": "Overnight min",
        "temp_now": 24,
        "temp_later": 13
      }
    },
```

We can probably use `is_night` to overwrite the `icon_descriptor` value if it shows "sunny" at night to "clear-night".

Forecast Hourly API call has a similar situation where we can use the `is_night` entity to overwrite the `icon_descriptor` if it is "sunny" at night.

Example:
```
      "relative_humidity": 69,
      "uv": 1,
      "icon_descriptor": "mostly_sunny",
      "next_three_hourly_forecast_period": "2025-05-06T03:00:00Z",
      "time": "2025-05-06T01:00:00Z",
      "is_night": false,
      "next_forecast_period": "2025-05-06T02:00:00Z"
    },
```

This seems to be the value they are using for the BOM app to determine whether to change the icon from daytime to night. At 6:00PM, it goes from daytime to night on the app as well as the API.

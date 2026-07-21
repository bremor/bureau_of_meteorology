# Bureau of Meteorology API documentation

This integration uses undocumented BoM JSON APIs that back https://weather.bom.gov.au and BoM mobile clients.

All examples below are trimmed response samples for Darwin City, Northern Territory.

## Current API model used by the integration

Primary data is sourced from the newer place/grid/station API family under:

- https://api.bom.gov.au/apikey/v1

### 1) Find candidate places

Endpoint:

- GET /locations/places/autocomplete

Typical query parameters used by the integration:

- name: Darwin City NT
- limit: 5
- website-sort: true
- include-states: true
- include-districts: true

Sample output (trimmed):

```json
{
  "candidates": [
    {
      "id": "o6051889726",
      "coordinate": {
        "longitude": 130.844442,
        "latitude": -12.460834
      },
      "gridcells": {
        "forecast": {
          "x": 316,
          "y": 651
        }
      },
      "name": "Darwin City",
      "state": "NT",
      "timezone": "Australia/Darwin",
      "type": "place"
    }
  ]
}
```

### 2) Resolve canonical place details

Endpoint:

- GET /locations/places/details/place/{place_id}

Example URL values:

- place_id: o6051889726
- filter: nearby_type:bom_stn,elevation:300,capability:SENSOR_TEMPERATURE_DB,match_coastal_status:true
- radius: 100000
- nearby_limit: 10

Sample output (trimmed):

```json
{
  "place": {
    "id": "o6051889726",
    "name": "Darwin City",
    "timezone": "Australia/Darwin",
    "coordinate": {
      "longitude": 130.844442,
      "latitude": -12.460834
    },
    "gridcells": {
      "forecast": {
        "x": 316,
        "y": 651
      }
    },
    "location_hierarchy": {
      "metropolitan": [
        {
          "aac": "NT_ME006",
          "description": "Darwin"
        },
        {
          "aac": "NT_ME001",
          "description": "Darwin Area"
        }
      ],
      "precis_fcst": {
        "aac": "NT_PT001",
        "description": "Darwin"
      },
      "nearest": {
        "id": "14072",
        "name": "Darwin Harbour",
        "type": "bom_stn",
        "distance": 1239.288
      },
      "nearby": [
        {
          "id": "14318",
          "name": "East Point",
          "distance": 5866.6597
        },
        {
          "id": "14015",
          "name": "Darwin Airport",
          "distance": 6640.5645
        }
      ]
    }
  }
}
```

### 3) Forecast data (grid-based)

Endpoints:

- GET /forecasts/daily/{x}/{y}?timezone={timezone}
- GET /forecasts/1hourly/{x}/{y}?timezone={timezone}
- GET /forecasts/3hourly/{x}/{y}?timezone={timezone}
- GET /forecasts/astro/{lon}/{lat}
- GET /forecasts/texts?aac={aac}&timezone={timezone}

Example values for Darwin City:

- x: 316
- y: 651
- timezone: Australia/Darwin
- lon/lat: 130.844442, -12.460834
- text aac (area): NT_ME001

Daily sample output (trimmed):

```json
{
  "meta": {
    "issue_time_utc": "2026-07-21T10:33:26Z",
    "issue_time_next_utc": "2026-07-21T20:00:00Z",
    "local_timezone": "Australia/Darwin"
  },
  "fcst": {
    "daily": [
      {
        "date_utc": "2026-07-21T14:30:00Z",
        "atm": {
          "surf_air": {
            "temp_max_cel": 30.800001,
            "temp_min_cel": 18.0,
            "precip": {
              "any_probability_percent": 2.0,
              "exceeding_50percentchance_total_mm": 0.0
            },
            "weather": {
              "icon_code": 1
            },
            "radiation": {
              "uv_clear_sky_max_code": 8.993267,
              "uv_period_start": "2026-07-22T00:10:00Z",
              "uv_period_end": "2026-07-22T06:30:00Z"
            }
          }
        },
        "astro": {
          "sunrise_utc": null,
          "sunset_utc": null
        }
      }
    ]
  }
}
```

1-hourly sample output (trimmed):

```json
{
  "meta": {
    "issue_time_utc": "2026-07-21T10:50:02Z",
    "local_timezone": "Australia/Darwin"
  },
  "fcst": [
    {
      "date_utc": "2026-07-21T14:30:00Z",
      "1hourly": [
        {
          "time_utc": "2026-07-21T15:00:00Z",
          "atm": {
            "surf_air": {
              "temp_cel": 18.4,
              "temp_apparent_cel": 19.7,
              "hum_relative_percent": 97.5,
              "wind": {
                "dirn_10m_deg_t": 182.3,
                "speed_10m_avg_mps": 2.222,
                "gust_speed_10m_max_mps": 3.601
              },
              "radiation": {
                "uv_clear_sky_code": 0.0
              }
            }
          }
        }
      ]
    }
  ]
}
```

Astro sample output (trimmed):

```json
{
  "meta": {
    "local_timezone": "Australia/Darwin"
  },
  "fcst": {
    "daily": [
      {
        "date_utc": "2026-07-21T14:30:00Z",
        "astro": {
          "sunrise_utc": "2026-07-21T21:38:16Z",
          "sunset_utc": "2026-07-22T09:08:10Z"
        }
      }
    ]
  }
}
```

Forecast text sample output (trimmed):

```json
{
  "meta": {
    "issue_time_utc": "2026-07-21T10:45:26Z",
    "local_timezone": "Australia/Darwin"
  },
  "fcst": {
    "daily": [
      {
        "date_utc": "2026-07-21T14:30:00Z",
        "atm": {
          "surf_air": {
            "radiation": {
              "advice_summary": {
                "metropolitan_text": "Sun protection 9:40am to 4:00pm, UV Index predicted to reach 8 [Very High]"
              }
            },
            "weather": {
              "metropolitan_text": "Sunny. Light winds becoming east to southeasterly 15 to 20 km/h in the morning then becoming light in the middle of the day."
            }
          }
        }
      }
    ]
  }
}
```

### 4) Observations data (station-based)

Endpoint:

- GET /observations/latest/{station_id}/atm/surf_air?include_qc_results=false

Darwin station example used for sample:

- station_id: 14015 (Darwin Airport)

Sample output (trimmed):

```json
{
  "stn": {
    "identity": {
      "bom_stn_num": 14015,
      "bom_stn_name": "Darwin Airport",
      "wmo_stn_id": 94120
    },
    "location": {
      "lat_dec_deg": -12.4239,
      "long_dec_deg": 130.8925,
      "timezone": "Australia/Darwin"
    }
  },
  "obs": {
    "datetime_utc": "2026-07-21T11:00:00Z",
    "temp": {
      "dry_bulb_1min_cel": 23.6,
      "apparent_1min_cel": 26.21,
      "dry_bulb_max_cel": 30.0,
      "dry_bulb_min_cel": 23.5,
      "rel_hum_percent": 80.0
    },
    "wind": {
      "speed_10m_mps": 1.646,
      "dirn_10m_ord": "WSW",
      "gust_speed_10m_max_mps": 8.231
    },
    "precip": {
      "since_0900lct_total_mm": 0.0
    }
  }
}
```

### 5) Warnings data (coordinate-based)

Endpoint:

- GET /warnings/list?area_type=coordinate&area_code={lon},{lat}

Note: coordinates are expected with up to 2 decimal places.

Darwin example request values:

- area_code: 130.84,-12.46

Sample output:

```json
{
  "warnings": []
}
```

## Integration data flow

1. Setup/options resolves top candidate places near configured coordinates.
2. Selected place_id is stored in config data.
3. Forecasts load from place forecast grid (x,y) and text/astro endpoints.
4. Observations use a station endpoint (and may fall back if needed).
5. Warnings load from coordinate warnings endpoint.

## Legacy geohash fallback

Geohash endpoints are no longer the primary model.

They are still retained as a compatibility fallback path when place-based calls are unavailable or when user-selected source behavior requires it.

Legacy endpoint family:

- https://api.weather.bom.gov.au/v1/locations/{geohash}
- .../observations
- .../forecasts/daily
- .../forecasts/hourly
- .../warnings

Legacy location-search sample (Darwin City):

```json
{
  "data": [
    {
      "geohash": "qvv117j",
      "id": "Darwin City-qvv117j",
      "name": "Darwin City",
      "state": "NT"
    }
  ]
}
```

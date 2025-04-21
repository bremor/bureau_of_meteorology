# Bureau of Meteorology Custom Component

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE.md)
![Maintenance](https://img.shields.io/maintenance/yes/2025?style=for-the-badge)

### **This integration only supports locations within Australia.**

This Home Assistant custom component uses the [Bureau of Meteorology (BOM)](http://www.bom.gov.au) as a source for weather information.

## Installation (There are two methods, with HACS or manual)

Install via HACS (default store) or install manually by copying the files in a new 'custom_components/bureau_of_meteorology' directory.

## Configuration

After you have installed the custom component (see above):

1. Goto the `Configuration` -> `Integrations` page.
2. On the bottom right of the page, click on the `+ Add Integration` sign to add an integration.
3. Search for `Bureau of Meteorology`. (If you don't see it, try refreshing your browser page to reload the cache.)
4. Click `Submit` so add the integration.

## Troubleshooting

Please set your logging for the custom_component to debug:

```yaml
logger:
  default: warn
  logs:
    custom_components.bureau_of_meteorology: debug
```

### Notes

1. This integration will not refresh data faster than once every 5 minutes.
2. All feature requests, issues and questions are welcome.

## Release Notes

### 1.3.5 - Fix for null error warnings and small get_forecasts() response improvement
- Fix null forecast errors. Thanks @systemtester
- Fix uv_index response in action.get_forecasts() to confirm with HA documented responses Thanks @systemtester

### 1.3.4 - Fix for 2025.12 HA deprecation warnings
- Fix config_entry deprecation warning. Thanks @systemtester

### 1.3.3 - Fix for more HA breaking changes
- Fix setup block warning. Thanks @Poshy163
- Fix 'timezone' not defined error in UV forecasts. Thanks @dbiczo

### 1.3.2 - Fix for more HA breaking changes
- Fix for Detected blocking call to open inside the event loop by @dbiczo

### 1.3.0 - HA breaking stuff again
- Fix wind direction units. Thanks @djferg.
- Fix breaking changes introduced in 2023.9.
- Add dew sensor. Thanks @djferg.
- Updates for 2024.1 deprecations.

### 1.2.0 - Refactor for breaking changes made by HA
- HA have completely changed how weather forecasts are handled causing a breaking change (thanks to @evilmarty for the work to update the integration).

### 1.1.21 - Fix for BOM breaking change
- A minor bug fix for the previous fix.

### 1.1.20 - Fix for BOM breaking change
- A minor bug fix to make the integration work again after a BOM update.

### 1.1.19 - Updates to keep up with HA
- Minor internal changes to sensors.

### 1.1.18 - Fix observed min/max sensors
- Fix a bug in the configuration of the observed min/max sensors (note that it may be necessary to remove and re-add the instance of the integration to correct).

### 1.1.17 - Adjust rain range format
- On some cards (particularly on mobile devices) with larger numbers the rain range fields where getting to wide to fit. The range fields format has been updated from `25 to 30mm` to `25-30mm` to overcome this problem.

### 1.1.16 - Add more data to hourly forecast
- Add humidity to hourly forecast.
- Add UV to hourly forecast.
- Add wind gust speed to hourly forecast.

### 1.1.15 - Add more sensor data
- Add color attributes to the fire danger sensor.
- Add observation sensors for observed min/max along with timestamp.

### 1.1.14 - Allow reconfiguration
- Allow integration reconfiguration (thanks to @Djelibeybi for the contribution).
- Register entities within a service (thanks to @Djelibeybi for the contribution).
- Adjust UV text to match an update made on the BoM site.
- Fix a problem with the call to the location api not returning a valid location.

### 1.1.13 - Add bad location error message
- Add a meaningful error message when trying to configure using lat/lon that aren't in Australia.

### 1.1.12 - Embed timezone in timestamps
- This embeds the timezone of the location in timestamps, whcih is needed to display timess correctly if you create sensors in a different timezone to where the HA server is located.

### 1.1.11 - Fixes for 2022.7.0
- This is to address an architecture change in 2022.7.0 and will not install on earlier versions of HA.

### 1.1.10 - Add UV Forecast
- Adds new uv_forecast sensors to the daily forecast.
- Make the uv_category sensors more human readable.

### 1.1.9 - Add attribute to extended forecasts
- Add 'state' attribute to extended forecast entities to hold the non-truncated forecast.

### 1.1.8 - Weather Warnings
- Add optional warning sensor.
- Rework card configuration.

### 1.1.7 - Fix upgrading
- 1.1.6 had a problem that when upgrading the weather.xxx entities didn't migrate smoothly.

## 1.1.6 - Allow setting the name of weather entities.
- Add the ability to name the weather entities when forecast is not checked during config.

### 1.1.5 - Fix unit of measurement for wind speed
- The wind speed in the weather object had the wrong value as the unit of measurment was not being set.

### 1.1.4 - Fix weather object not being created
- When the forecast configuration box was unticked the weather object was failing to be created.

### 1.1.2 - Add Sunrise/Sunset sensors
- Added sunrise and sunset sensors in the forecast that provide the sunrise/sunset times for the selected forecast period.

### 1.1.1 - Add Now/Later sensors
- Added now and later sensors in the forecast that provide the next 2 min/max elements.
- Fix sensors disappearing when data is not available from the BoM.

### 1.1.0 - Improve stability
- Updated the way the integration fetches data from BoM to improve stability.

### 1.0.0 - Hourly Forecast Weather Entity and Bug Fixes
- Released a weather entity with hourly forecast.
- Hopefully fixed that bug that occured when BoM had missing data.
- Refactored code to be a bit cleaner.

[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/bremor/bureau_of_meteorology.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/bremor/bureau_of_meteorology.svg?style=for-the-badge
[releases]: https://github.com/bremor/bureau_of_meteorology/releases

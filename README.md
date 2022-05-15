# Bureau of Meteorology Custom Component

This Home Assistant custom component uses the [Bureau of Meteorology (BOM)](http://www.bom.gov.au) as a source for weather information. This grabs data from an undocumented API that is used to provide data to https://weather.bom.gov.au/

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE.md)
![Maintenance](https://img.shields.io/maintenance/yes/2022?style=for-the-badge)

## 1.1.6 - Allow setting the name of weather entities.
- Add the ability to name the weather entities when forecast is not checked during config.

## 1.1.5 - Fix unit of measurement for wind speed
- The wind speed in the weather object had the wrong value as the unit of measurment was not being set.

## 1.1.4 - Fix weather object not being created
- When the forecast configuration box was unticked the weather object was failing to be created.

## 1.1.2 - Add Sunrise/Sunset sensors
- Added sunrise and sunset sensors in the forecast that provide the sunrise/sunset times for the selected forecast period.

## 1.1.1 - Add Now/Later sensors
- Added now and later sensors in the forecast that provide the next 2 min/max elements.
- Fix sensors disappearing when data is not available from the BoM.

## 1.1.0 - Improve stability
- Updated the way the integration fetches data from BoM to improve stability.

## 1.0.0 - Hourly Forecast Weather Entity and Bug Fixes
- Released a weather entity with hourly forecast.
- Hopefully fixed that bug that occured when BoM had missing data.
- Refactored code to be a bit cleaner.

## Installation (There are two methods, with HACS or manual)

Install via HACS (default store) or install manually by copying the files in a new 'custom_components/bonaire_myclimate' directory.

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

## Notes
1. This integration will refresh data no faster than every 10 minutes.
2. All feature requests, issues and questions are welcome.

[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/bremor/bureau_of_meteorology.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/bremor/bureau_of_meteorology.svg?style=for-the-badge
[releases]: https://github.com/bremor/bureau_of_meteorology/releases

# Bureau of Meteorology Custom Component

This Home Assistant custom component uses the [Bureau of Meteorology (BOM)](http://www.bom.gov.au) as a source for weather information. This grabs data from an undocumented API that is used to provide data to https://weather.bom.gov.au/

## 1.0.0 - Hourly Forecast Weather Entity and Bug Fixes
- Released a weather entity with hourly forecast.
- Hopefully fixed that bug that occured when BoM had missing data.
- Refactored code to be a bit cleaner.

## Installation (There are two methods, with HACS or manual)

[![hacs][hacsbadge]][hacs]

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

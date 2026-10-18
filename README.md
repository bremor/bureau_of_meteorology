# Bureau of Meteorology Custom Component

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
![GitHub Release](https://img.shields.io/github/v/release/bremor/bureau_of_meteorology?style=for-the-badge)
![GitHub License](https://img.shields.io/github/license/bremor/bureau_of_meteorology?style=for-the-badge)
![Maintenance](https://img.shields.io/maintenance/yes/2026?style=for-the-badge)

## **This integration only supports locations within Australia.**

This Home Assistant custom component uses the [Bureau of Meteorology (BOM)](http://www.bom.gov.au) as a source for weather information.

## Installation (There are two methods, with HACS or manual)

Install via HACS (default store) or install manually by copying the files in a new 'custom_components/bureau_of_meteorology' directory.

## Configuration

After you have installed the custom component (see above):

1. Goto the `Configuration` -> `Integrations` page.
2. On the bottom right of the page, click on the `+ Add Integration` sign to add an integration.
3. Search for `Bureau of Meteorology`. (If you don't see it, try refreshing your browser page to reload the cache.)
4. Click `Submit` so add the integration.

## API Source Model

The integration uses BoM's legacy geohash API by default. To try the newer place/grid/station APIs (`api.bom.gov.au/apikey/v1`), open the integration settings and enable **Use experimental API**.

When enabled, the experimental API mode:

1. A nearby `place_id` is selected during setup/options.
2. Forecasts come from the place forecast grid (`x`, `y`) and associated text/astro endpoints.
3. Observations come from the nearest station mapped to that place.
4. Warnings come from coordinate-based warning endpoints.

When experimental mode is enabled, the integration falls back to legacy geohash endpoints when place-based data is unavailable. With the option off, it uses the legacy geohash API directly.

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

See [Releases](releases)

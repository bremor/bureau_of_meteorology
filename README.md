[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

The `bureau_of_meteorology` sensor platform uses the [Bureau of Meteorology (BOM)](http://www.bom.gov.au) as a source for weather information.

# Installation (There are two methods, with HACS or manual)

### 1. Easy Mode

1. Add this repo as a custom repository within HACS. This is not currently in the default HACS store, you must add it manually.
2. After adding this as a custom repo, you must also install this integration within HACS.

### 2. Manual

Install it as you would do with any homeassistant custom component:

1. Download `custom_components` folder.
2. Copy the `bureau_of_meteorology` directory within the `custom_components` directory of your homeassistant installation.
The `custom_components` directory resides within your homeassistant configuration directory.
**Note**: if the custom_components directory does not exist, you need to create it.
After a correct installation, your configuration directory should look like the following.

    ```
    └── ...
    └── configuration.yaml
    └── custom_components
        └── bureau_of_meteorology
            └── __init__.py
            └── config_flow.py
            └── const.py
            └── manifest.json
            └── sensor.py
            └── strings.json
            └── PyBoM
                └── collector.py
            └── translations
                └── en.json
    ```

# Configuration
1. Goto the `Configuration` -> `Integrations` page.  
2. On the bottom right of the page, click on the `+` sign to add an integration.
3. Search for `Bureau of Meteorology`. (If you don't see it, try refreshing your browser page to reload the cache.)
4. Enter the required information. (Latitude/Longitude)

# Notes
1. This integration will refresh data no faster than every 10 minutes.

2. All feature requests, issues and questions are welcome.

<a href="https://www.buymeacoffee.com/bremor" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height=40px width=144px></a>

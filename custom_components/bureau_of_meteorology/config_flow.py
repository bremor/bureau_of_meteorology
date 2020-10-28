"""Config flow for BOM."""
import logging

import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN
from .PyBoM.collector import Collector

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BOM."""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        data_schema = vol.Schema({
            vol.Required(CONF_LATITUDE, default=self.hass.config.latitude): float,
            vol.Required(CONF_LONGITUDE, default=self.hass.config.longitude): float,
        })

        errors = {}
        if user_input is not None:
            try:
                collector = Collector(
                    self.hass.config.latitude,
                    self.hass.config.longitude
                )
                await collector.get_location_name()
                result = await collector.get_observations_data()
                if result is None:
                    raise CannotConnect

                #name = collector.observations_data["data"]["station"]["name"]
                #name = collector.locations_data
                return self.async_create_entry(title=collector.location_name, data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""

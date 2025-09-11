from __future__ import annotations
import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN
from .unifi_api import UniFiApi

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Optional("site", default="default"): str,
        vol.Optional("verify_ssl", default=False): bool,
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Проверка соединения с UniFi
            try:
                api = UniFiApi(
                    host=user_input["host"],
                    username=user_input["username"],
                    password=user_input["password"],
                    site=user_input["site"],
                    verify_ssl=user_input["verify_ssl"],
                )
                await api.login()
            except Exception as e:
                errors["base"] = "connection_error"
                _LOGGER.error("Connection error: %s", e)
            else:
                # Проверяем, нет ли уже конфигурации с таким хостом
                await self.async_set_unique_id(user_input["host"])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title="UniFi Presence", data=user_input)

        return self.async_show_form(
            step_id="user", 
            data_schema=DATA_SCHEMA, 
            errors=errors
        )

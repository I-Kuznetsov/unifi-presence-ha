from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class UniFiPresenceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # TODO: здесь можно добавить проверку соединения с UniFi
            return self.async_create_entry(
                title=f"UniFi Presence ({user_input['host']})",
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required("host"): str,
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Optional("site", default="default"): str,
                vol.Optional("verify_ssl", default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    "update_interval", default=self.config_entry.options.get("update_interval", 30)
                ): int
            }
        )
        return self.async_show_form(step_id="init", data_schema=options_schema)

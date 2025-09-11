from __future__ import annotations
import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .unifi_api import UniFiApi

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api = UniFiApi(
        host=entry.data["host"],
        username=entry.data["username"],
        password=entry.data["password"],
        site=entry.data["site"],
        verify_ssl=entry.data.get("verify_ssl", False),
    )

    async def async_update_data():
        return await api.get_clients()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="unifi_presence",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

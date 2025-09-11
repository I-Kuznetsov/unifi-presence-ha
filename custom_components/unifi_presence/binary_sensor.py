from __future__ import annotations
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    async_add_entities(UniFiPresenceSensor(coordinator, client) for client in coordinator.data)

class UniFiPresenceSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, client):
        super().__init__(coordinator)
        self._client = client
        self._attr_unique_id = f"unifi_presence_{client['mac']}"
        self._attr_name = f"UniFi {client.get('1x_identity') or client.get('hostname') or client['mac']}"

    @property
    def is_on(self):
        return self._client.get("is_active", False)

    @property
    def extra_state_attributes(self):
        return {
            "mac": self._client.get("mac"),
            "hostname": self._client.get("hostname"),
            "1x_identity": self._client.get("1x_identity"),
            "last_seen": self._client.get("last_seen"),
        }

    @property
    def available(self):
        return True

    async def async_update(self):
        await self.coordinator.async_request_refresh()
        self._client = next(
            (c for c in self.coordinator.data if c["mac"] == self._client["mac"]),
            self._client,
        )

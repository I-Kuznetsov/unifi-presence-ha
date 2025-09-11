# UniFi Presence for Home Assistant

Интеграция Home Assistant для отображения присутствия пользователей UniFi.

## Возможности
- Автоматически создаёт binary_sensor для клиентов UniFi
- Работает через UniFi Controller API
- Показывает атрибуты: MAC, hostname, identity, last_seen

## Установка через HACS
1. Добавьте этот репозиторий в HACS как custom repository:
   ```
   https://github.com/<your_github>/unifi-presence-ha
   ```
2. Установите компонент UniFi Presence.
3. Перезапустите Home Assistant.
4. Добавьте интеграцию UniFi Presence через интерфейс.

## Ручная установка
1. Скопируйте `custom_components/unifi_presence` в вашу конфигурацию Home Assistant.
2. Перезапустите HA.

## Лицензия
MIT

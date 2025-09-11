# UniFi Presence for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

Интеграция Home Assistant для отображения присутствия пользователей UniFi.  
Создаёт `binary_sensor` для каждого клиента с `1x_identity`, hostname или MAC-адресом.

## ✨ Возможности
- Автоматически обнаруживает клиентов UniFi
- Создаёт `binary_sensor` для каждого клиента
- Статус `on` = клиент активен в сети
- Атрибуты: MAC, hostname, identity, last_seen
- Поддержка настройки через UI (Config Flow)

## 🚀 Установка

### Через HACS
1. В HACS → Интеграции → «Custom repositories» добавьте:
https://github.com/I-Kuznetsov/unifi-presence-ha
Repository type: `Integration`
2. Установите «UniFi Presence».
3. Перезапустите Home Assistant.
4. Добавьте интеграцию «UniFi Presence» через интерфейс.

### Ручная установка
1. Скопируйте папку `custom_components/unifi_presence` в вашу конфигурацию HA.
2. Перезапустите HA.
3. Добавьте интеграцию «UniFi Presence» через UI.

## ⚙️ Настройка
При добавлении интеграции нужно указать:
- **Host**: адрес контроллера UniFi (например, `https://192.168.1.1:8443`)
- **Username**: логин UniFi
- **Password**: пароль UniFi
- **Site**: ID сайта (по умолчанию `default`)
- **Verify SSL**: проверять SSL-сертификат (обычно `false` для self-signed)

## 🖼️ Пример
После установки у вас появятся binary_sensor:

- `binary_sensor.unifi_presence_alex`
- `binary_sensor.unifi_presence_laptop`
- `binary_sensor.unifi_presence_phone`

В UI Home Assistant они будут показывать присутствие в сети.

## 📜 Лицензия
MIT


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

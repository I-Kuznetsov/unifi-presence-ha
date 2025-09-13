# UniFi Presence Tracker

Python script that monitors UniFi network clients and publishes presence status to Home Assistant via MQTT.

## Features

- Detects active clients on UniFi network
- Publishes binary_sensor entities to Home Assistant via MQTT discovery
- Automatic cleanup of stale presence states
- Configurable polling intervals

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

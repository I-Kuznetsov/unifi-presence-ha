# UniFi Presence Tracker

## Description / Описание
**EN:**  
Python script that monitors UniFi network clients and publishes presence status to Home Assistant via MQTT.  

**RU:**  
Python-скрипт, который отслеживает клиентов сети UniFi и публикует статус присутствия в Home Assistant через MQTT.  

---

## Disclaimer / Отказ
**EN:**  
I am not a programmer. This file was made by an AI system. It works. I did not find any alternative ways to get 802.1X identification.  

**RU:**  
Я не программист. Этот файл создан системой ИИ. Он работает. Я не нашёл альтернативных способов получить 802.1X идентификацию.  

---

## Features / Возможности
**EN:**  
- Detects active clients on UniFi network  
- Publishes binary_sensor entities to Home Assistant via MQTT discovery  
- Automatic cleanup of stale presence states  
- Configurable polling intervals  

**RU:**  
- Определяет активных клиентов в сети UniFi  
- Публикует binary_sensor в Home Assistant через MQTT discovery  
- Автоматическая очистка устаревших статусов присутствия  
- Настраиваемые интервалы опроса  

---

## Installation / Установка
**EN:**  
1. Clone this repository  
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt

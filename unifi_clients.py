#!/usr/bin/env python3
"""
unifi_clients.py
Сканирует UniFi-клиентов и публикует presence в MQTT: unifi/presence/<identity>
Поведение:
 - при старте считывает retained состояния на теме unifi/presence/# и выставляет OFF для тех, у кого было ON
 - далее в цикле публикует ON для активных клиентов и OFF для тех, кто ушёл
 - периодически (RECONCILE_INTERVAL) выполняет повторную проверку retained состояний и исправляет "висячие" ON
"""
import requests
import urllib3
import logging
import time
import json
import threading
import paho.mqtt.client as mqtt

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== Настройки ==========
LOG_LEVEL = logging.INFO  # поставьте logging.DEBUG для подробного лога
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# UniFi
UNIFI_HOST = "https://your-unifi-controller:8443"
USERNAME = "your-username"
PASSWORD = "your-password"
SITE = "default"
INTERVAL = 30  # секунд между опросами UniFi

# MQTT
MQTT_HOST = "your-mqtt-broker"
MQTT_PORT = 1883
MQTT_USERNAME = None  # or your username
MQTT_PASSWORD = None  # or your password
DISCOVERY_PREFIX = "homeassistant"
STATE_PREFIX = "unifi/presence"

# Таймауты
STARTUP_MQTT_COLLECT_TIMEOUT = 5.0  # сек - сколько ждать retained сообщений при старте
MAX_SEEN_AGE = 60  # сек - если last_seen старше — считаем клиента неактивным
RECONCILE_INTERVAL = 10 * 60  # сек - каждые N секунд делать полную проверку retained состояний

# =================================

session = requests.Session()
session.verify = False

mqtt_client = mqtt.Client("unifi_presence_script")
if MQTT_USERNAME:
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

_connected_event = threading.Event()


# ---------- MQTT callbacks ----------
def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("MQTT connected (rc=0)")
        _connected_event.set()
    else:
        logger.error("MQTT connect failed, rc=%s", rc)


mqtt_client.on_connect = _on_connect


def mqtt_connect(timeout=10):
    """Подключаемся к брокеру и ждём подтверждения on_connect."""
    logger.info("Connecting to MQTT broker %s:%s ...", MQTT_HOST, MQTT_PORT)
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    mqtt_client.loop_start()
    if not _connected_event.wait(timeout):
        raise Exception("MQTT connect timeout")
    logger.info("MQTT loop started")


def safe_identity_for_topic(identity_raw):
    """Нормализует identity для использования в topic/unique_id."""
    if identity_raw is None:
        return None
    return str(identity_raw).replace(":", "_").replace(" ", "_")


def publish_discovery(identity):
    unique_id = f"unifi_presence_{identity}"
    state_topic = f"{STATE_PREFIX}/{identity}"
    config_topic = f"{DISCOVERY_PREFIX}/binary_sensor/{unique_id}/config"
    payload = {
        "name": f"UniFi Presence {identity}",
        "state_topic": state_topic,
        "payload_on": "ON",
        "payload_off": "OFF",
        "device_class": "presence",
        "unique_id": unique_id,
    }
    mqtt_client.publish(config_topic, json.dumps(payload), retain=True)
    logger.debug("Published discovery %s -> %s", unique_id, config_topic)


def publish_state(identity, state):
    topic = f"{STATE_PREFIX}/{identity}"
    mqtt_client.publish(topic, state, retain=True)
    logger.info("Published state %s for %s", state, identity)


# ---------- UniFi ----------
def login():
    login_url = f"{UNIFI_HOST}/api/login"
    payload = {"username": USERNAME, "password": PASSWORD}
    headers = {"Content-Type": "application/json"}
    logger.info("Logging in to UniFi...")
    resp = session.post(login_url, json=payload, headers=headers, timeout=15)
    if resp.status_code != 200:
        logger.error("Login failed: %s %s", resp.status_code, resp.text)
        raise Exception("Login failed")
    logger.info("UniFi login successful")


def get_clients():
    url = f"{UNIFI_HOST}/api/s/{SITE}/stat/sta"
    resp = session.get(url, timeout=15)
    if resp.status_code != 200:
        logger.error("Failed to get clients: %s %s", resp.status_code, resp.text)
        raise Exception("Failed to get clients")
    data = resp.json()
    return data.get("data", [])


def is_client_active(client):
    last_seen = client.get("last_seen")
    if last_seen:
        now = int(time.time())
        if now - last_seen > MAX_SEEN_AGE:
            return False
    return True


# ---------- Retained state collection ----------
def collect_retained_states(timeout=STARTUP_MQTT_COLLECT_TIMEOUT):
    """
    Подписываемся на STATE_PREFIX/# и собираем retained сообщения.
    Возвращаем dict: identity -> payload (строка).
    """
    retained = {}

    def _on_retained(client, userdata, msg):
        try:
            # рассматривать только retained сообщения
            if not getattr(msg, "retain", False):
                return
            topic = msg.topic
            # topic ожидается как unifi/presence/<identity>
            prefix = STATE_PREFIX + "/"
            if topic.startswith(prefix):
                identity = topic[len(prefix):]
                identity = safe_identity_for_topic(identity)
                payload = msg.payload.decode("utf-8") if msg.payload else ""
                retained[identity] = payload
                logger.debug("Collected retained: %s -> %r", identity, payload)
        except Exception:
            logger.exception("Error in retained message handler")

    # временно назначаем callback только для этой подписки
    sub_filter = STATE_PREFIX + "/#"
    mqtt_client.message_callback_add(sub_filter, _on_retained)
    mqtt_client.subscribe(sub_filter)
    logger.info("Collecting retained states on %s for %.1f sec ...", sub_filter, timeout)
    time.sleep(timeout)
    mqtt_client.unsubscribe(sub_filter)
    mqtt_client.message_callback_remove(sub_filter)
    logger.info("Finished collecting retained states, found %d items", len(retained))
    return retained


# ---------- MAIN ----------
def reconcile_retained_with_unifi(present_identities, known_identities):
    """
    Считываем retained состояния и для каждого retained ON, которого нет в present_identities,
    публикуем OFF.
    """
    try:
        retained = collect_retained_states(timeout=STARTUP_MQTT_COLLECT_TIMEOUT)
        for identity, payload in retained.items():
            if (payload or "").upper() == "ON":
                if identity not in present_identities:
                    logger.info("Reconcile: retained %s is ON but not present -> publishing OFF", identity)
                    publish_state(identity, "OFF")
                    # если надо, добавляем в known (чтобы дальше не публиковать discovery постоянно)
                    known_identities.add(identity)
    except Exception:
        logger.exception("Error during reconcile_retained_with_unifi")


def main():
    # подключение
    login()
    mqtt_connect()

    # 1) На старте: считываем retained состояния и принудительно ставим OFF для всех ON
    try:
        retained_at_start = collect_retained_states(timeout=STARTUP_MQTT_COLLECT_TIMEOUT)
        if retained_at_start:
            logger.info("At startup: found %d retained presence topics", len(retained_at_start))
            for identity, payload in retained_at_start.items():
                if (payload or "").upper() == "ON":
                    logger.info("Startup cleanup: setting %s -> OFF", identity)
                    publish_state(identity, "OFF")
        else:
            logger.info("At startup: no retained presence topics found")
    except Exception:
        logger.exception("Startup retained cleanup failed")

    # known_identities — те, для кого мы уже публиковали discovery
    known_identities = set()
    currently_on = set()

    reconcile_timer = 0

    while True:
        try:
            clients = get_clients()

            present_identities = set()
            for client in clients:
                if not is_client_active(client):
                    # старый/давно не виденный клиент - игнорируем
                    continue
                raw_id = client.get("1x_identity") or client.get("hostname") or client.get("mac")
                if not raw_id:
                    continue
                identity = safe_identity_for_topic(raw_id)
                present_identities.add(identity)

                if identity not in known_identities:
                    publish_discovery(identity)
                    known_identities.add(identity)

                # publish ON если не было
                if identity not in currently_on:
                    publish_state(identity, "ON")
                    currently_on.add(identity)

            # OFF для ушедших
            gone = currently_on - present_identities
            for identity in list(gone):
                logger.info("Client gone: %s -> publishing OFF", identity)
                publish_state(identity, "OFF")
                currently_on.remove(identity)

            # Периодическая полная сверка retained (на случай, если что-то постороннее поставило ON)
            reconcile_timer += INTERVAL
            if reconcile_timer >= RECONCILE_INTERVAL:
                reconcile_retained_with_unifi(present_identities, known_identities)
                reconcile_timer = 0

            time.sleep(INTERVAL)
        except Exception:
            logger.exception("Error in main loop — попытаюсь переподключиться к UniFi и MQTT")
            try:
                time.sleep(5)
                login()
            except Exception:
                logger.exception("Re-login failed, сплю 5 сек")
                time.sleep(5)


if __name__ == "__main__":
    main()

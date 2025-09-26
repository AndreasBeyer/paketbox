import paho.mqtt.client as mqtt
import logging
import time
from config import Config as config

logger = logging.getLogger(__name__)

_client = None  # interne Referenz für den MQTT-Client

def mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Verbunden mit MQTT-Broker")
        client.subscribe(config.MQTT_TOPIC_MESSAGE)
    else:
        logger.warning(f"MQTT-Verbindung fehlgeschlagen, Rückgabecode: {rc}")

def mqtt_disconnect(client, userdata, rc):
    logger.warning("MQTT-Verbindung verloren. Versuche erneut zu verbinden...")
    while True:
        try:
            client.reconnect()
            logger.info("MQTT erfolgreich wieder verbunden.")
            break
        except Exception as e:
            logger.error(f"Reconnect fehlgeschlagen: {e}")
            time.sleep(5)

def mqtt_message(client, userdata, msg):
    logger.info(f"Nachricht empfangen: {msg.topic} {msg.payload.decode()}")

def start_mqtt():
    """Initialisiert und startet die MQTT-Verbindung im Hintergrund."""
    global _client
    _client = mqtt.Client()
    _client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)  # <--- Zugangsdaten setzen
    _client.on_connect = mqtt_connect
    _client.on_disconnect = mqtt_disconnect
    _client.on_message = mqtt_message

    _client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    _client.loop_start()
    logger.info("MQTT-Client gestartet.")

def stop_mqtt():
    """Beendet die MQTT-Verbindung."""
    global _client
    if _client:
        _client.loop_stop()
        _client.disconnect()
        logger.info("MQTT-Client gestoppt.")

def publish_status(message):
    """Sendet eine Statusnachricht über MQTT."""
    if _client:
        _client.publish(config.MQTT_TOPIC_MESSAGE, message)
        logger.info(f"MQTT gesendet: {message}")
    else:
        logger.warning("MQTT-Client nicht verbunden, Nachricht nicht gesendet.")

def publish_paket_zusteller_event(state):
    """Sendet Paket-Zusteller-Event (ON/OFF)."""
    if _client:
        _client.publish(config.MQTT_TOPIC_PAKETZUSTELLER, state)
        logger.info(f"Paket-Zusteller-Event gesendet: {state}")
    else:
        logger.warning("MQTT-Client nicht verbunden, Paket-Zusteller-Event nicht gesendet.")

def publish_briefkasten_event(state):
    """Sendet Briefkasten-Event (ON/OFF)."""
    if _client:
        _client.publish(config.MQTT_TOPIC_BRIEFKASTEN, state)
        logger.info(f"Briefkasten-Event gesendet: {state}")
    else:
        logger.warning("MQTT-Client nicht verbunden, Briefkasten-Event nicht gesendet.")

def publish_briefkasten_entleeren_event(state):
    """Sendet Briefkasten-Entleeren-Event (ON/OFF)."""
    if _client:
        _client.publish(config.MQTT_TOPIC_BRIEFKASTEN_ENTLEEREN, state)
        logger.info(f"Briefkasten-Entleeren-Event gesendet: {state}")
    else:
        logger.warning("MQTT-Client nicht verbunden, Briefkasten-Entleeren-Event nicht gesendet.")

def publish_paketbox_entleeren_event(state):
    """Sendet Paketbox-Entleeren-Event (ON/OFF)."""
    if _client:
        _client.publish(config.MQTT_TOPIC_PAKETBOX_ENTLEEREN, state)
        logger.info(f"Paketbox-Entleeren-Event gesendet: {state}")
    else:
        logger.warning("MQTT-Client nicht verbunden, Paketbox-Entleeren-Event nicht gesendet.")
import paho.mqtt.client as mqtt
import logging
import time

MQTT_BROKER = "server_ip_or_hostname"
MQTT_PORT = 1883
MQTT_TOPIC = "home/raspi/paketbox_text"

logger = logging.getLogger(__name__)

_client = None  # interne Referenz für den MQTT-Client

def mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Verbunden mit MQTT-Broker")
        client.subscribe(MQTT_TOPIC)
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
    _client.on_connect = mqtt_connect
    _client.on_disconnect = mqtt_disconnect
    _client.on_message = mqtt_message

    _client.connect(MQTT_BROKER, MQTT_PORT, 60)
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
        _client.publish(MQTT_TOPIC, message)
        logger.info(f"MQTT gesendet: {message}")
    else:
        logger.warning("MQTT-Client nicht verbunden, Nachricht nicht gesendet.")


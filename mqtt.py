try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    mqtt = None

import logging
import time
from datetime import datetime
from config import Config as config

logger = logging.getLogger(__name__)

_client = None  # interne Referenz für den MQTT-Client

def mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Verbunden mit MQTT-Broker")
        client.subscribe(config.MQTT_TOPIC_MESSAGE)
        client.subscribe(config.MQTT_TOPIC_PAKETBOX_AUTO_LOCK_DOOR)
        logger.info(f"Abonnement: {config.MQTT_TOPIC_MESSAGE}")
        logger.info(f"Abonnement: {config.MQTT_TOPIC_PAKETBOX_AUTO_LOCK_DOOR}")
    else:
        logger.warning(f"MQTT-Verbindung fehlgeschlagen, Rückgabecode: {rc}")

def mqtt_disconnect(client, userdata, rc):
    """Handle MQTT disconnection with limited retry attempts."""
    if not MQTT_AVAILABLE:
        return
        
    logger.warning("MQTT-Verbindung verloren. Versuche erneut zu verbinden...")
    max_retries = 5
    retry_count = 0
    base_delay = 5  # seconds
    
    while retry_count < max_retries:
        try:
            retry_count += 1
            # Exponential backoff with jitter
            delay = min(base_delay * (2 ** (retry_count - 1)), 60)
            logger.info(f"Reconnect-Versuch {retry_count}/{max_retries} in {delay} Sekunden...")
            time.sleep(delay)
            
            client.reconnect()
            logger.info("MQTT erfolgreich wieder verbunden.")
            return
        except Exception as e:
            logger.error(f"Reconnect-Versuch {retry_count} fehlgeschlagen: {e}")
            if retry_count >= max_retries:
                logger.error(f"MQTT-Reconnect nach {max_retries} Versuchen aufgegeben. Manueller Neustart erforderlich.")
                break

def mqtt_message(client, userdata, msg):
    logger.info(f"Nachricht empfangen: {msg.topic} {msg.payload.decode()}")
    
    # Handle auto lock door setting
    if msg.topic == config.MQTT_TOPIC_PAKETBOX_AUTO_LOCK_DOOR:
        payload = msg.payload.decode().lower()
        if payload in ['true', '1', 'on', 'yes']:
            logger.info("Auto-Lock-Door aktiviert via MQTT")
            try:
                from handler import set_auto_lock_door
                set_auto_lock_door(True)
            except Exception as e:
                logger.error(f"Fehler beim Setzen von auto_lock_door: {e}")
        elif payload in ['false', '0', 'off', 'no']:
            logger.info("Auto-Lock-Door deaktiviert via MQTT")
            try:
                from handler import set_auto_lock_door
                set_auto_lock_door(False)
            except Exception as e:
                logger.error(f"Fehler beim Setzen von auto_lock_door: {e}")

def start_mqtt():
    """Initialisiert und startet die MQTT-Verbindung im Hintergrund."""
    global _client
    
    if not MQTT_AVAILABLE:
        logger.warning("MQTT nicht verfügbar - paho-mqtt Bibliothek nicht installiert")
        return False
        
    try:
        _client = mqtt.Client()
        _client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)  # <--- Zugangsdaten setzen
        _client.on_connect = mqtt_connect
        _client.on_disconnect = mqtt_disconnect
        _client.on_message = mqtt_message

        _client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        _client.loop_start()
        logger.info("MQTT-Client gestartet.")
        return True
    except Exception as e:
        logger.error(f"MQTT-Start fehlgeschlagen: {e}")
        return False

def stop_mqtt():
    """Beendet die MQTT-Verbindung."""
    global _client
    if _client:
        _client.loop_stop()
        _client.disconnect()
        logger.info("MQTT-Client gestoppt.")

def publish_status(message):
    """Sendet eine Statusnachricht über MQTT."""
    if not MQTT_AVAILABLE:
        logger.debug(f"MQTT nicht verfügbar - Status ignoriert: {message}")
        return False
        
    if _client:
        try:
            # prepend current date/time to every status message automatically
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # full_message = f"{ts} {message}"
            full_message = f"{message}"
            _client.publish(config.MQTT_TOPIC_MESSAGE, full_message)
            logger.info(f"MQTT gesendet: {full_message}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden der MQTT-Nachricht: {e}")
            return False
    else:
        logger.warning("MQTT-Client nicht verbunden, Nachricht nicht gesendet.")
        return False

def publish_paket_zusteller_event(state):
    """Sendet Paket-Zusteller-Event (ON/OFF)."""
    if not MQTT_AVAILABLE:
        logger.debug(f"MQTT nicht verfügbar - Paket-Zusteller-Event ignoriert: {state}")
        return False
        
    if _client:
        try:
            _client.publish(config.MQTT_TOPIC_PAKETZUSTELLER, state)
            logger.info(f"Paket-Zusteller-Event gesendet: {state}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden des Paket-Zusteller-Events: {e}")
            return False
    else:
        logger.warning("MQTT-Client nicht verbunden, Paket-Zusteller-Event nicht gesendet.")
        return False

def publish_briefkasten_event(state):
    """Sendet Briefkasten-Event (ON/OFF)."""
    if not MQTT_AVAILABLE:
        logger.debug(f"MQTT nicht verfügbar - Briefkasten-Event ignoriert: {state}")
        return False
        
    if _client:
        try:
            _client.publish(config.MQTT_TOPIC_BRIEFKASTEN, state)
            logger.info(f"Briefkasten-Event gesendet: {state}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden des Briefkasten-Events: {e}")
            return False
    else:
        logger.warning("MQTT-Client nicht verbunden, Briefkasten-Event nicht gesendet.")
        return False

def publish_briefkasten_entleeren_event(state):
    """Sendet Briefkasten-Entleeren-Event (ON/OFF)."""
    if not MQTT_AVAILABLE:
        logger.debug(f"MQTT nicht verfügbar - Briefkasten-Entleeren-Event ignoriert: {state}")
        return False
        
    if _client:
        try:
            _client.publish(config.MQTT_TOPIC_BRIEFKASTEN_ENTLEEREN, state)
            logger.info(f"Briefkasten-Entleeren-Event gesendet: {state}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden des Briefkasten-Entleeren-Events: {e}")
            return False
    else:
        logger.warning("MQTT-Client nicht verbunden, Briefkasten-Entleeren-Event nicht gesendet.")
        return False

def publish_paketbox_entleeren_event(state):
    """Sendet Paketbox-Entleeren-Event (ON/OFF)."""
    if not MQTT_AVAILABLE:
        logger.debug(f"MQTT nicht verfügbar - Paketbox-Entleeren-Event ignoriert: {state}")
        return False
        
    if _client:
        try:
            _client.publish(config.MQTT_TOPIC_PAKETBOX_ENTLEEREN, state)
            logger.info(f"Paketbox-Entleeren-Event gesendet: {state}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden des Paketbox-Entleeren-Events: {e}")
            return False
    else:
        logger.warning("MQTT-Client nicht verbunden, Paketbox-Entleeren-Event nicht gesendet.")
        return False
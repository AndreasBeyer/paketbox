# Paketbox control script
# Version 0.6.0
import time
import sys
import logging
from PaketBoxState import DoorState
from config import *
from state import pbox_state, sendMqttErrorState, mqttObject  # Import from central state module
import mqtt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paketbox.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


try:
   import RPi.GPIO as GPIO # type: ignore
except ImportError:
   import sys
   import types
   class MockGPIO:
      BCM = 'BCM'
      OUT = 'OUT'
      IN = 'IN'
      HIGH = 1
      LOW = 0
      RISING = 'RISING'
      FALLING = 'FALLING'
      BOTH = 'BOTH'
      def setmode(self, mode):
         print(f"[MOCK] GPIO setmode({mode})")
      def setup(self, pin, mode):
         print(f"[MOCK] GPIO setup(pin={pin}, mode={mode})")
      def output(self, pin, state):
         print(f"[MOCK] GPIO output(pin={pin}, state={state})")
      def input(self, pin):
        # print(f"[MOCK] GPIO input(pin={pin}) -> LOW")
         return self.LOW
      def add_event_detect(self, pin, edge, callback=None, bouncetime=200):
         print(f"[MOCK] GPIO add_event_detect(pin={pin}, edge={edge}, bouncetime={bouncetime})")
      def cleanup(self):
         print(f"[MOCK] GPIO cleanup()")
   GPIO = MockGPIO()
   

# Import handler after state is defined to avoid circular imports
import handler
# Re-export modules for test compatibility
import time

# Define closure_timer_seconds for test compatibility
closure_timer_seconds = Config.CLOSURE_TIMER_SECONDS
# endregion


def initialize_door_states():
    """Initialize door states based on current GPIO input readings."""
    logger.info("Initialisiere Türzustände basierend auf GPIO-Eingängen...")
    
    statusOld = [0] * len(Config.INPUTS)
    
    # Read current GPIO states
    for i, pin in enumerate(Config.INPUTS):
        statusOld[i] = GPIO.input(pin)
    
    # Set door states based on GPIO readings
    pbox_state.set_left_door(DoorState.OPEN if statusOld[0] == GPIO.HIGH else DoorState.CLOSED)
    pbox_state.set_right_door(DoorState.OPEN if statusOld[2] == GPIO.HIGH else DoorState.CLOSED)
    pbox_state.set_paket_tuer(DoorState.OPEN if statusOld[4] == GPIO.HIGH else DoorState.CLOSED)
    
    logger.info(f"Türzustände initialisiert: {pbox_state}")
    return statusOld


def main():
    """Main application entry point - now synchronous for GPIO compatibility."""

    try:
        # verwende GPIO Nummer statt Board Nummer
        GPIO.setmode(GPIO.BCM)
   
        # Setze alle Inputs
        for pin in Config.INPUTS:
          GPIO.setup(pin, GPIO.IN)
        # Setze alle Outputs auf HIGH (Ruhezustand)
        for output in Config.OUTPUTS:
          GPIO.setup(output, GPIO.OUT)
          GPIO.output(output, GPIO.HIGH)

        global mqttObject
        mqttObject.start_mqtt()
        mqttObject.publish_status(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Paketbox bereit.")
        # Initialize door states based on current GPIO readings
        statusOld = initialize_door_states()
        statusNew = [0] * len(Config.INPUTS)

        logger.info("Init abgeschlossen. Strg+C zum Beenden drücken.")
        handler.ResetDoors()
        global sendMqttErrorState

        while True: 
           time.sleep(1)  # Main loop - check system state
           for i, pin in enumerate(Config.INPUTS):
               statusNew[i] = GPIO.input(pin)
               if statusNew[i] != statusOld[i]:
                   handler.pinChanged(i, statusOld[i], statusNew[i])
                   logger.info(f"GPIO {pin} changed: {statusOld[i]} -> {statusNew[i]}")
                   statusOld[i] = statusNew[i]

           # Monitor for error conditions
           if ( not sendMqttErrorState and pbox_state.is_any_error()):
               logger.warning(f"WARNUNG: System im Fehlerzustand! {pbox_state}")
               mqttObject.publish_status(f"{time.strftime('%Y-%m-%d %H:%M:%S')} FEHLER Paketbox: {pbox_state}")
               sendMqttErrorState = True

    except KeyboardInterrupt:
        logger.info("Beendet mit Strg+C")
    except Exception as e:
        logger.error(f"[Main] Fehler: {e}")
    finally:
        GPIO.cleanup()
        logger.info("GPIO aufgeräumt.")
        mqttObject.stop_mqtt()
        logger.info("MQTT gestoppt.")

# Diese Zeilen sorgen dafür, dass das Skript nur ausgeführt wird,
# wenn es direkt gestartet wird (und nicht importiert).
if __name__ == "__main__":
   main()  # Now synchronous - no asyncio.run() needed

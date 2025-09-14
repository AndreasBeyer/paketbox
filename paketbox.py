# Paketbox control script
# Version 0.4.0
import time
import sys
import logging
from PaketBoxState import PaketBoxState, DoorState
from config import *

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
   

# Initialisiere globalen Zustand
pbox_state = PaketBoxState()

# Import handler after pbox_state is defined to avoid circular imports
import handler

# Re-export functions from handler for backward compatibility
from handler import (
    Klappen_oeffnen, Klappen_schliessen, 
    unlockDoor, lockDoor, setOutputWithRuntime,
    Paket_Tuer_Zusteller_geschlossen, Paket_Tuer_Zusteller_geoeffnet
)

# Re-export modules for test compatibility
import threading
import time

# Define closure_timer_seconds for test compatibility
closure_timer_seconds = Config.CLOSURE_TIMER_SECONDS

# Handler functions for GPIO callbacks (for test compatibility)
def handleLeftFlapClosed(pin):
    """Handler for left flap closed sensor"""
    pbox_state.set_left_door(DoorState.CLOSED)
    logger.info("Entleerungsklappe links ist geschlossen")

def handleLeftFlapOpened(pin):
    """Handler for left flap opened sensor"""
    pbox_state.set_left_door(DoorState.OPEN)
    logger.info("Entleerungsklappe links ist geöffnet")

def handleRightFlapClosed(pin):
    """Handler for right flap closed sensor"""
    pbox_state.set_right_door(DoorState.CLOSED)
    logger.info("Entleerungsklappe rechts ist geschlossen")

def handleRightFlapOpened(pin):
    """Handler for right flap opened sensor"""
    pbox_state.set_right_door(DoorState.OPEN)
    logger.info("Entleerungsklappe rechts ist geöffnet")

def handleDeliveryDoorStatus(pin):
    """Handler for delivery door status changes with debouncing"""
    try:
        # Debouncing: read twice with small delay
        state1 = GPIO.input(pin)
        time.sleep(Config.DEBOUNCE_TIME)
        state2 = GPIO.input(pin)
        
        if state1 != state2:
            logger.debug(f"GPIO {pin} debounce mismatch: {state1} != {state2}")
            return
            
        if state1 == GPIO.HIGH:  # Door opened
            pbox_state.set_paket_tuer(DoorState.OPEN)
            logger.info("Pakettür Zusteller geöffnet")
            logger.info("Türe Paketzusteller wurde geöffnet:")
            handler.Paket_Tuer_Zusteller_geoeffnet()
        else:  # Door closed
            pbox_state.set_paket_tuer(DoorState.CLOSED)
            logger.info("Pakettür Zusteller geschlossen")
            handler.Paket_Tuer_Zusteller_geschlossen()
    except Exception as e:
        logger.error(f"Fehler in handleDeliveryDoorStatus: {e}")

def handleMailboxOpen(pin):
    """Handler for mailbox opening"""
    logger.info("Der Briefkasten wurde geöffnet")

def handlePackageBoxDoorOpen(pin):
    """Handler for package box door opening"""
    logger.info("Die Tür zur Paketentnahme wurde geöffnet")

def handleMailboxDoorOpen(pin):
    """Handler for mailbox door opening"""
    logger.info("Die Türe zum Briefe entnehmen wurde geöffnet")
# endregion


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

        statusOld = [0] * len(Config.INPUTS)
        statusNew = [0] * len(Config.INPUTS)

        for i, pin in enumerate(Config.INPUTS):
           statusOld[i] = GPIO.input(pin)

        pbox_state.set_left_door(DoorState.OPEN if statusOld[0] == GPIO.HIGH else DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.OPEN if statusOld[2] == GPIO.HIGH else DoorState.CLOSED)
        pbox_state.set_paket_tuer(DoorState.OPEN if statusOld[4] == GPIO.HIGH else DoorState.CLOSED)

        logger.info(f"Zustand: {pbox_state}")
        logger.info("Init abgeschlossen. Strg+C zum Beenden drücken.")
        handler.ResetDoors()

        while True: 
           time.sleep(1)  # Main loop - check system state
           for i, pin in enumerate(Config.INPUTS):
               statusNew[i] = GPIO.input(pin)
               if statusNew[i] != statusOld[i]:
                   handler.pinChanged(i, statusOld[i], statusNew[i])
                   logger.info(f"GPIO {pin} changed: {statusOld[i]} -> {statusNew[i]}")
                   statusOld[i] = statusNew[i]

#            # Monitor for error conditions
#            if pbox_state.is_any_error():
#                logger.warning(f"WARNUNG: System im Fehlerzustand! {pbox_state}")
#                time.sleep(Config.ERROR_REPORT_INTERVAL)  # Slow down error reporting
                
    except KeyboardInterrupt:
        logger.info("Beendet mit Strg+C")
    except Exception as e:
        logger.error(f"[Main] Fehler: {e}")
    finally:
        GPIO.cleanup()
        logger.info("GPIO aufgeräumt.")

# Diese Zeilen sorgen dafür, dass das Skript nur ausgeführt wird,
# wenn es direkt gestartet wird (und nicht importiert).
if __name__ == "__main__":
   main()  # Now synchronous - no asyncio.run() needed

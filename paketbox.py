# Paketbox control script
# Version 0.3.4
import time
import threading
import sys
import logging
from datetime import datetime
from interruptHandler import *
from config import *
import config

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

closure_timer_seconds = Config.CLOSURE_TIMER_SECONDS
motor_reverse_signal = Config.MOTOR_REVERSE_SIGNAL

# region State Management
from enum import Enum, auto

class DoorState(Enum):
   CLOSED = auto()
   OPEN = auto()
   ERROR = auto()

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
         print(f"[MOCK] GPIO input(pin={pin}) -> LOW")
         return self.LOW
      def add_event_detect(self, pin, edge, callback=None, bouncetime=200):
         print(f"[MOCK] GPIO add_event_detect(pin={pin}, edge={edge}, bouncetime={bouncetime})")
      def cleanup(self):
         print(f"[MOCK] GPIO cleanup()")
   GPIO = MockGPIO()
class PaketBoxState:
   def __init__(self):
      self._lock = threading.Lock()
      self.left_door = DoorState.CLOSED
      self.right_door = DoorState.CLOSED
      self.paket_tuer = DoorState.CLOSED

   def set_left_door(self, state: DoorState):
      with self._lock:
         self.left_door = state
   def set_right_door(self, state: DoorState):
      with self._lock:
         self.right_door = state
   def set_paket_tuer(self, state: DoorState):
      with self._lock:
         self.paket_tuer = state

   def is_open(self):
       with self._lock:
         return all([
            self.left_door == DoorState.OPEN,
            self.right_door == DoorState.OPEN
         ])
   
   def is_all_closed(self):
      with self._lock:
         return all([
            self.left_door == DoorState.CLOSED,
            self.right_door == DoorState.CLOSED,
            self.paket_tuer == DoorState.CLOSED
         ])

   def is_any_error(self):
      with self._lock:
         return any([
            self.left_door == DoorState.ERROR,
            self.right_door == DoorState.ERROR,
            self.paket_tuer == DoorState.ERROR
         ])

   def __str__(self):
      with self._lock:
         return (f"Links: {self.left_door.name}, Rechts: {self.right_door.name}, "
               f"Pakettür: {self.paket_tuer.name}")

# Initialisiere globalen Zustand
pbox_state = PaketBoxState()
# endregion

def init():
   # verwende GPIO Nummer statt Board Nummer
   GPIO.setmode(GPIO.BCM)

   # Setze als Ausgang
   GPIO.setup(Config.Q1, GPIO.OUT)
   GPIO.output(Config.Q1, GPIO.HIGH)
   GPIO.setup(Config.Q2, GPIO.OUT)
   GPIO.output(Config.Q2, GPIO.HIGH)
   GPIO.setup(Config.Q3, GPIO.OUT)
   GPIO.output(Config.Q3, GPIO.HIGH)
   GPIO.setup(Config.Q4, GPIO.OUT)
   GPIO.output(Config.Q4, GPIO.HIGH)
   GPIO.setup(Config.Q6, GPIO.OUT)
   GPIO.output(Config.Q6, GPIO.HIGH)
   GPIO.setup(Config.Q8, GPIO.OUT)
   GPIO.output(Config.Q8, GPIO.HIGH)

   # Setze als Eingang
   GPIO.setup(Config.I01, GPIO.IN)
   GPIO.setup(Config.I02, GPIO.IN)
   GPIO.setup(Config.I03, GPIO.IN)
   GPIO.setup(Config.I04, GPIO.IN)
   GPIO.setup(Config.I05, GPIO.IN)
   GPIO.setup(Config.I06, GPIO.IN)
   GPIO.setup(Config.I07, GPIO.IN)
   GPIO.setup(Config.I08, GPIO.IN)
   GPIO.setup(Config.I09, GPIO.IN)
   GPIO.setup(Config.I10, GPIO.IN)
   GPIO.setup(Config.I11, GPIO.IN)
   pbox_state.set_left_door(DoorState.OPEN if GPIO.input(Config.I02) == GPIO.HIGH else DoorState.CLOSED)
   pbox_state.set_right_door(DoorState.OPEN if GPIO.input(Config.I04) == GPIO.HIGH else DoorState.CLOSED)
   pbox_state.set_paket_tuer(DoorState.OPEN if GPIO.input(Config.I05) == GPIO.HIGH else DoorState.CLOSED)

   #Interrupt
 #  GPIO.add_event_detect(Config.I01, GPIO.RISING, callback=handleLeftFlapClosed, bouncetime=200) # EndsensorKlappe links geschlossen
 #  GPIO.add_event_detect(Config.I02, GPIO.RISING, callback=handleLeftFlapOpened, bouncetime=200) # Endsensor Klappe links geöffnet
 #  GPIO.add_event_detect(Config.I03, GPIO.RISING, callback=handleRightFlapClosed, bouncetime=200) # Endsensor Klappe rechts geschlossen
 #  GPIO.add_event_detect(Config.I04, GPIO.RISING, callback=handleRightFlapOpened, bouncetime=200) # Endsensor Klappe rechts geöffnet
 #  GPIO.add_event_detect(Config.I05, GPIO.BOTH, callback=handleDeliveryDoorStatus, bouncetime=200) # Paket Tür geöffnet o. geschlossen
 #  GPIO.add_event_detect(Config.I06, GPIO.FALLING, callback=handleMailboxOpen, bouncetime=200) # Briefkasten Zusteller geoffnet
 #  GPIO.add_event_detect(Config.I07, GPIO.FALLING, callback=handleMailboxDoorOpen, bouncetime=200) # Briefkasten Entnahme
 #  GPIO.add_event_detect(Config.I08, GPIO.FALLING, callback=handlePackageBoxDoorClosed, bouncetime=200) # Paketbox Entnahme
 #  GPIO.add_event_detect(Config.I09, GPIO.RISING, callback=handleGartenDoorButton6Press, bouncetime=200) # Tueroeffner 6
 #  GPIO.add_event_detect(Config.I10, GPIO.RISING, callback=handleGardenDoorButton8Press, bouncetime=200) # Tueroeffner 8
 #  GPIO.add_event_detect(Config.I11, GPIO.RISING, callback=handleMotionDetection, bouncetime=200) # Bewegungsmelder Einklemmschutz

def setOutputWithRuntime(runtime, gpio, state):
    """Set GPIO output for specified runtime, then automatically reset to opposite state."""
    try:
      GPIO.output(gpio, state)
      def reset_output():
         opposite_state = GPIO.LOW if state == GPIO.HIGH else GPIO.HIGH
         GPIO.output(gpio, opposite_state)
         logger.debug(f"GPIO {gpio} zurückgeschaltet zu {opposite_state}")
        
      timer = threading.Timer(runtime, reset_output)
      timer.start()
      return timer  # Return timer for potential cancellation
    except Exception as e:
      logger.error(f"Hardwarefehler in setOutputWithRuntime: {e}")
      return None
    
# region Actions

def unlockDoor():
   try:
      GPIO.output(Config.Q8, GPIO.HIGH) # Riegel öffnet Tür. Tür kann wieder geöffnet werden
      logger.info("Türe Paketzusteller wurde entriegelt.")
   except Exception as e:
      logger.error(f"Hardwarefehler in unlockDoor: {e}")

def lockDoor():
   try:
      GPIO.output(Config.Q8, GPIO.LOW) # Riegel schließt Tür. Tür kann nicht mehr geöffnet werden
      logger.info("Türe Paketzusteller wurde verriegelt.")
   except Exception as e:
      logger.error(f"Hardwarefehler in lockDoor: {e}")

def Klappen_schliessen():
    """Close both flaps with proper error handling and state validation."""
    if pbox_state.is_any_error():
        logger.warning("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
        return False
    
    logger.info("Klappen fahren zu")
    # Start closing motors
    timer1 = setOutputWithRuntime(closure_timer_seconds, Config.Q1, GPIO.LOW)
    timer2 = setOutputWithRuntime(closure_timer_seconds, Config.Q3, GPIO.LOW)
    
    if not timer1 or not timer2:
        logger.error("Fehler beim Starten der Motoren!")
        return False
    
    def endlagen_pruefung_closing():
        """Check end positions after closing timeout."""
        if not (pbox_state.left_door == DoorState.CLOSED and pbox_state.right_door == DoorState.CLOSED):
            logger.error(f"Fehler: Klappen nicht geschlossen nach Schließungsversuch!")
            logger.error(f"Status: Links={pbox_state.left_door.name}, Rechts={pbox_state.right_door.name}")
            pbox_state.set_left_door(DoorState.ERROR)
            pbox_state.set_right_door(DoorState.ERROR)
            return False
        else:
            logger.info("Klappen erfolgreich geschlossen.")
            unlockDoor()
            return True

    timer = threading.Timer(closure_timer_seconds + 1, endlagen_pruefung_closing)
    timer.start()
    return True

def Paket_Tuer_Zusteller_geschlossen():
    logger.info("Türe Paketzusteller wurde geschlossen.")
    time.sleep(10)
    lockDoor()
    logger.info("Starte Öffnen der Klappen...")
    Klappen_oeffnen()
    # Audiofile: Box wird geleert, dies dauert 2 Minuten

def Paket_Tuer_Zusteller_geoeffnet():
    if pbox_state.is_open():
         logger.warning(f"Fehler: Tür wurde geöffnet und Klappen waren nicht zu.")
         Klappen_schliessen()

    logger.info("Türe Paketzusteller wurde geöffnet:")

def Klappen_oeffnen():
    """Open both flaps with proper error handling and state validation."""
    if pbox_state.is_any_error():
        logger.warning("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
        return False

    logger.info("Klappen fahren auf")
    # Start opening motors
    timer1 = setOutputWithRuntime(motor_reverse_signal, Config.Q2, GPIO.LOW)
    timer2 = setOutputWithRuntime(motor_reverse_signal, Config.Q4, GPIO.LOW)
    
    if not timer1 or not timer2:
        logger.error("Fehler beim Starten der Motoren!")
        return False
    
    def endlagen_pruefung():
        """Check end positions after opening timeout."""
        if not (pbox_state.left_door == DoorState.OPEN and pbox_state.right_door == DoorState.OPEN):
            logger.error(f"Fehler: Klappen nicht offen nach Öffnungsversuch!")
            logger.error(f"Status: Links={pbox_state.left_door.name}, Rechts={pbox_state.right_door.name}")
            pbox_state.set_left_door(DoorState.ERROR)
            pbox_state.set_right_door(DoorState.ERROR)
            return False
        else:
            logger.info("Klappen erfolgreich geöffnet.")
            logger.info(f"Starte automatisches Schließen der Klappen... Status: {pbox_state}")
            # Auto-close after successful opening
            if (pbox_state.left_door == DoorState.OPEN and pbox_state.right_door == DoorState.OPEN):
               Klappen_schliessen()
            else:
               logger.error(f"Fehler: Klappen nicht beide im OPEN-Zustand!")
            return True

    timer = threading.Timer(closure_timer_seconds + 1, endlagen_pruefung)
    timer.start()
    return True

def ResetDoors():
    """Reset doors to safe closed state."""
    logger.info(f"Current door state: {pbox_state}")
    if pbox_state.is_open():
       logger.info("Resetting doors to closed state...")
       lockDoor()
       return Klappen_schliessen()
    elif pbox_state.is_any_error():
       logger.warning("Doors in error state - manual intervention required!")
       return False
    else:
       logger.info("Doors already in safe state.")
       return True

# endregion

def main():
    """Main application entry point - now synchronous for GPIO compatibility."""
    try:
        init()
        logger.info("Init abgeschlossen. Strg+C zum Beenden drücken.")
        #ResetDoors()
        
        # Main monitoring loop
   # Pinbelegung Eingänge
  #  I01 = 27 #11 Klappe links zu
  #  I02 = 17 #13 Klappe links auf
  #  I03 = 9 #15 Klappe rechts zu
  #  I04 = 22  #21 Klappe rechts auf
  #  I05 = 23 #16 Tür Riegelkontakt + Tür Magentkontakt
  #  I06 = 24 #18 Briefkasten Magnetkontak
  #  I07 = 25 #22 Briefkasten Türe zum leeren
  #  I08 = 12 #32 Paketbox Tür zum leeren
  #  I09 = 8  #24 Türöffner 6 Taster
  #  I10 = 7  #26 Türffner 8 Taster
  #  I11 = 11 #23 Bewegungsmelder
        inputs = [Config.I01, Config.I02, Config.I03, Config.I04, Config.I05, Config.I06, Config.I07, Config.I08, Config.I09, Config.I10, Config.I11]
        inputsClearName = ["Endschalter Klappe links zu", "Endschalter Klappe links auf", " Endschalter Klappe rechts zu", "Endschalter Klappe rechts auf", "Klappe Zusteller Magentkontakt", 
                           "Briefkasten Zusteller Magnetkontak", "Briefkasten Türe zum leeren Magenetkontakt", "Paketbox Tür zum leeren Magenetkontakt", "Türöffner 6 Taster", "Türöffner 8 Taster", "Bewegungsmelder"]
        statusOld = [0] * len(inputs)
        statusNew = [0] * len(inputs)

        # Beispiel: Fülle das Array mit aktuellen GPIO-Werten
        for i, pin in enumerate(inputs):
           statusOld[i] = GPIO.input(pin)
        

        while True:
           time.sleep(1)  # Main loop - check system state
           for i, pin in enumerate(inputs):
               statusNew[i] = GPIO.input(pin)
               if statusNew[i] != statusOld[i]:
                   logger.info(f"GPIO {pin} ({inputsClearName[i]}) changed: {statusOld[i]} -> {statusNew[i]}")
                   statusOld[i] = statusNew[i]



#            time.sleep(1)  # Main loop - check system state
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

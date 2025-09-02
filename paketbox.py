# Paketbox control script
# Version 0.3.2
import time
import threading
import sys
import logging
from datetime import datetime

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

# Configuration constants
class Config:
    CLOSURE_TIMER_SECONDS = 65
    MOTOR_REVERSE_SIGNAL = CLOSURE_TIMER_SECONDS - 1
    DEBOUNCE_TIME = 0.2
    ERROR_REPORT_INTERVAL = 5.0

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
      self.motor_operation_active = False

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

   def set_motor_operation(self, active: bool):
      """Set motor operation flag to suppress non-critical GPIO events during motor operations."""
      with self._lock:
         self.motor_operation_active = active

   def is_motor_operation_active(self):
      """Check if motor operations are currently active."""
      with self._lock:
         return self.motor_operation_active

   def __str__(self):
      with self._lock:
         return (f"Links: {self.left_door.name}, Rechts: {self.right_door.name}, "
               f"Pakettür: {self.paket_tuer.name}")

# Initialisiere globalen Zustand
pbox_state = PaketBoxState()
# endregion

# Pinbelegung der Relais
#  BCM  Stiftpin
Q1 = 5  #29 Klappe links zu
Q2 = 6  #31 Klappe links auf
Q3 = 13 #33 Klappe rechts zu
Q4 = 16 #36 Klappe rechts auf
Q5 = 14 #8
Q6 = 20 #38 Bremse für Tuer
Q7 = 15 #10
Q8 = 26 #37 Riegel Tür

# Pinbelegung Eingänge
I01 = 27 #11 Klappe links zu
I02 = 17 #13 Klappe links auf
I03 = 9 #15 Klappe rechts zu
I04 = 22  #21 Klappe rechts auf
I05 = 23 #16 Tür Riegelkontakt + Tür Magentkontakt
I06 = 24 #18 Briefkasten Magnetkontak
I07 = 25 #22 Briefkasten Türe zum leeren
I08 = 12 #32 Paketbox Tür zum leeren
I09 = 8  #24 Türöffner 6 Taster
I10 = 7  #26 Türffner 8 Taster
I11 = 11 #23 Bewegungsmelder

# 1-wire Temperatursensor
# 1-wire    4  7

# I2S Audiokarte
# LRCLK    19 35
# BITCLR   18 12
# DATA OUT 21 40
# DATA IN  20 38

def init():
   # verwende GPIO Nummer statt Board Nummer
   GPIO.setmode(GPIO.BCM)

   # Setze als Ausgang
   GPIO.setup(Q1, GPIO.OUT)
   GPIO.output(Q1, GPIO.HIGH)
   GPIO.setup(Q2, GPIO.OUT)
   GPIO.output(Q2, GPIO.HIGH)
   GPIO.setup(Q3, GPIO.OUT)
   GPIO.output(Q3, GPIO.HIGH)
   GPIO.setup(Q4, GPIO.OUT)
   GPIO.output(Q4, GPIO.HIGH)
   GPIO.setup(Q6, GPIO.OUT)
   GPIO.output(Q6, GPIO.HIGH)
   GPIO.setup(Q8, GPIO.OUT)
   GPIO.output(Q8, GPIO.HIGH)

   # Setze als Eingang
   GPIO.setup(I01, GPIO.IN)
   GPIO.setup(I02, GPIO.IN)
   GPIO.setup(I03, GPIO.IN)
   GPIO.setup(I04, GPIO.IN)
   GPIO.setup(I05, GPIO.IN)
   GPIO.setup(I06, GPIO.IN)
   GPIO.setup(I07, GPIO.IN)
   GPIO.setup(I08, GPIO.IN)
   GPIO.setup(I09, GPIO.IN)
   GPIO.setup(I10, GPIO.IN)
   GPIO.setup(I11, GPIO.IN)

   # Setze pbox_state entsprechend Hardwarezustand
   pbox_state.set_left_door(DoorState.OPEN if GPIO.input(I02) == GPIO.HIGH else DoorState.CLOSED)
   pbox_state.set_right_door(DoorState.OPEN if GPIO.input(I04) == GPIO.HIGH else DoorState.CLOSED)
   pbox_state.set_paket_tuer(DoorState.OPEN if GPIO.input(I05) == GPIO.HIGH else DoorState.CLOSED)

   #Interrupt
   GPIO.add_event_detect(I01, GPIO.RISING, callback=handleLeftFlapClosed, bouncetime=200) # EndsensorKlappe links geschlossen
   GPIO.add_event_detect(I02, GPIO.RISING, callback=handleLeftFlapOpened, bouncetime=200) # Endsensor Klappe links geöffnet
   GPIO.add_event_detect(I03, GPIO.RISING, callback=handleRightFlapClosed, bouncetime=200) # Endsensor Klappe rechts geschlossen
   GPIO.add_event_detect(I04, GPIO.RISING, callback=handleRightFlapOpened, bouncetime=200) # Endsensor Klappe rechts geöffnet
   GPIO.add_event_detect(I05, GPIO.BOTH, callback=handleDeliveryDoorStatus, bouncetime=200) # Paket Tür geöffnet o. geschlossen
   GPIO.add_event_detect(I06, GPIO.FALLING, callback=handleMailboxOpen, bouncetime=200) # Briefkasten Zusteller geoffnet
   GPIO.add_event_detect(I07, GPIO.FALLING, callback=handleMailboxDoorOpen, bouncetime=200) # Briefkasten Entnahme
   GPIO.add_event_detect(I08, GPIO.FALLING, callback=handlePackageBoxDoorOpen, bouncetime=200) # Paketbox Entnahme
   GPIO.add_event_detect(I09, GPIO.RISING, callback=handleGartenDoorButton6Press, bouncetime=200) # Tueroeffner 6
   GPIO.add_event_detect(I10, GPIO.RISING, callback=handleGardenDoorButton8Press, bouncetime=200) # Tueroeffner 8
   GPIO.add_event_detect(I11, GPIO.RISING, callback=handleMotionDetection, bouncetime=200) # Bewegungsmelder Einklemmschutz

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


# region Callbacks
def handleLeftFlapClosed(channel):
   try:
      time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
      if GPIO.input(channel) == GPIO.HIGH:  # Signal went back to HIGH = false trigger
         return
      pbox_state.set_left_door(DoorState.CLOSED)
      logger.info("Entleerungsklappe links ist geschlossen")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleLeftFlapClosed: {e}")
      pbox_state.set_left_door(DoorState.ERROR)


def handleLeftFlapOpened(channel):
    try:
       time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
       if GPIO.input(channel) == GPIO.HIGH:  # Signal went back to HIGH = false trigger
          return
       pbox_state.set_left_door(DoorState.OPEN)
       logger.info("Entleerungsklappe links ist geöffnet")
    except Exception as e:
       logger.error(f"Hardwarefehler in handleLeftFlapOpened: {e}")
       pbox_state.set_left_door(DoorState.ERROR)


def handleRightFlapClosed(channel):
   try:
      time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
      if GPIO.input(channel) == GPIO.HIGH:  # Signal went back to HIGH = false trigger
         return
      pbox_state.set_right_door(DoorState.CLOSED)
      logger.info("Entleerungsklappe rechts ist geschlossen")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleRightFlapClosed: {e}")
      pbox_state.set_right_door(DoorState.ERROR)

def handleRightFlapOpened(channel):
    try:
       time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
       if GPIO.input(channel) == GPIO.HIGH:  # Signal went back to HIGH = false trigger
            return
       pbox_state.set_right_door(DoorState.OPEN)
       logger.info("Entleerungsklappe rechts ist geöffnet")
    except Exception as e:
       logger.error(f"Hardwarefehler in handleRightFlapOpened: {e}")
       pbox_state.set_right_door(DoorState.ERROR)

def handleDeliveryDoorStatus(channel):
   try:
      current_state = GPIO.input(channel)
      time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
      # Verify state hasn't changed during debounce
      if GPIO.input(channel) != current_state:
         return  # State changed during debounce, ignore
      
      if current_state == GPIO.HIGH:
         pbox_state.set_paket_tuer(DoorState.OPEN)
         logger.info("Pakettür Zusteller geöffnet")
         Paket_Tuer_Zusteller_geoeffnet()
      else:
         pbox_state.set_paket_tuer(DoorState.CLOSED)
         logger.info("Pakettür Zusteller geschlossen")
         Paket_Tuer_Zusteller_geschlossen()
   except Exception as e:
      logger.error(f"Hardwarefehler in handleDeliveryDoorStatus: {e}")
      pbox_state.set_paket_tuer(DoorState.ERROR)

def handleMailboxOpen(channel):
   try:
      time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
      if GPIO.input(channel) == GPIO.HIGH:  # Check if state changed during debounce
         return
      # Suppress spurious events during motor operations (electrical interference)
      if pbox_state.is_motor_operation_active():
         logger.debug("Ignoriere Briefkasten-Öffnung während Motoroperation (Störsignal)")
         return
      logger.info("Der Briefkasten wurde geöffnet")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleMailboxOpen: {e}")

def handlePackageBoxDoorOpen(channel):
   try:
      time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
      if GPIO.input(channel) == GPIO.HIGH:  # Check if state changed during debounce
         return
      # Suppress spurious events during motor operations (electrical interference)
      if pbox_state.is_motor_operation_active():
         logger.debug("Ignoriere Paketentnahme-Tür während Motoroperation (Störsignal)")
         return
      logger.info("Die Tür zur Paketentnahme wurde geöffnet")
   except Exception as e:
      logger.error(f"Hardwarefehler in handlePackageBoxDoorOpen: {e}")

def handleMailboxDoorOpen(channel):
   try:
      time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
      if GPIO.input(channel) == GPIO.HIGH:  # Check if state changed during debounce
         return
      # Suppress spurious events during motor operations (electrical interference)
      if pbox_state.is_motor_operation_active():
         logger.debug("Ignoriere Briefentnahme-Tür während Motoroperation (Störsignal)")
         return
      logger.info("Die Türe zum Briefe entnehmen wurde geöffnet")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleMailboxDoorOpen: {e}")

def handleGartenDoorButton6Press(channel):
   try:
      time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
      if GPIO.input(channel) == GPIO.LOW:  # Check if button released during debounce
         return
      # Suppress spurious events during motor operations (electrical interference)
      if pbox_state.is_motor_operation_active():
         logger.debug("Ignoriere Gartentür-Taster 6 während Motoroperation (Störsignal)")
         return
      logger.info("Der Taster an der Paketbox für Gartentürchen Nr. 6 wurde gedrückt")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleGartenDoorButton6Press: {e}")

def handleGardenDoorButton8Press(channel):
   try:
      time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
      if GPIO.input(channel) == GPIO.LOW:  # Check if button released during debounce
         return
      # Suppress spurious events during motor operations (electrical interference)
      if pbox_state.is_motor_operation_active():
         logger.debug("Ignoriere Gartentür-Taster 8 während Motoroperation (Störsignal)")
         return
      logger.info("Der Taster an der Paketbox für Gartentürchen Nr. 8 wurde gedrückt")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleGardenDoorButton8Press: {e}")

def handleMotionDetection(channel):
   try:
      time.sleep(Config.DEBOUNCE_TIME)  # Debounce delay
      if GPIO.input(channel) == GPIO.LOW:  # Check if motion stopped during debounce
         return
      # Suppress spurious events during motor operations (electrical interference)
      if pbox_state.is_motor_operation_active():
         logger.debug("Ignoriere Bewegungsmelder während Motoroperation (Störsignal)")
         return
      logger.info("Der Bewegungsmelder hat eine Bewegung erkannt.")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleMotionDetection: {e}")

# endregion

# region Actions

def unlockDoor():
   try:
      GPIO.output(Q8, GPIO.HIGH) # Riegel öffnet Tür. Tür kann wieder geöffnet werden
      logger.info("Türe Paketzusteller wurde entriegelt.")
   except Exception as e:
      logger.error(f"Hardwarefehler in unlockDoor: {e}")

def lockDoor():
   try:
      GPIO.output(Q8, GPIO.LOW) # Riegel schließt Tür. Tür kann nicht mehr geöffnet werden
      logger.info("Türe Paketzusteller wurde verriegelt.")
   except Exception as e:
      logger.error(f"Hardwarefehler in lockDoor: {e}")

def Klappen_schliessen():
    """Close both flaps with proper error handling and state validation."""
    if pbox_state.is_any_error():
        logger.warning("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
        return False
    
    logger.info("Klappen fahren zu")
    # Set motor operation flag to suppress spurious GPIO events during motor startup
    pbox_state.set_motor_operation(True)
    
    # Start closing motors
    timer1 = setOutputWithRuntime(closure_timer_seconds, Q1, GPIO.LOW)
    timer2 = setOutputWithRuntime(closure_timer_seconds, Q3, GPIO.LOW)
    
    if not timer1 or not timer2:
        logger.error("Fehler beim Starten der Motoren!")
        pbox_state.set_motor_operation(False)  # Clear flag on error
        return False
    
    # Clear motor operation flag after brief startup period to allow normal GPIO events
    def clear_motor_flag():
        pbox_state.set_motor_operation(False)
    motor_flag_timer = threading.Timer(1.0, clear_motor_flag)  # Clear after 1 second
    motor_flag_timer.start()
    
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
    # Set motor operation flag to suppress spurious GPIO events during motor startup
    pbox_state.set_motor_operation(True)
    
    # Start opening motors
    timer1 = setOutputWithRuntime(motor_reverse_signal, Q2, GPIO.LOW)
    timer2 = setOutputWithRuntime(motor_reverse_signal, Q4, GPIO.LOW)
    
    if not timer1 or not timer2:
        logger.error("Fehler beim Starten der Motoren!")
        pbox_state.set_motor_operation(False)  # Clear flag on error
        return False
    
    # Clear motor operation flag after brief startup period to allow normal GPIO events
    def clear_motor_flag():
        pbox_state.set_motor_operation(False)
    motor_flag_timer = threading.Timer(1.0, clear_motor_flag)  # Clear after 1 second
    motor_flag_timer.start()
    
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
        ResetDoors()
        
        # Main monitoring loop
        while True:
            time.sleep(1)  # Main loop - check system state
            # Monitor for error conditions
            if pbox_state.is_any_error():
                logger.warning(f"WARNUNG: System im Fehlerzustand! {pbox_state}")
                time.sleep(Config.ERROR_REPORT_INTERVAL)  # Slow down error reporting
                
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

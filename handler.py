
import threading
import logging
from PaketBoxState import DoorState
from config import Config
from state import pbox_state  # Import from central state module
import time

# Import GPIO from paketbox to use the same Mock/Real GPIO instance
def get_gpio():
    """Lazy import to avoid circular imports"""
    from paketbox import GPIO
    return GPIO

logger = logging.getLogger(__name__) 



def pinChanged(pin, oldState, newState):
    if oldState == 0 and newState == 1: # rising edge  
        if pin == 4:
            pbox_state.set_paket_tuer(DoorState.OPEN)
            logger.info(f"Paketklappe Zusteller geöffnet.") 
            # Paket_Tuer_Zusteller_geoeffnet()
        elif pin == 5:
            logger.info(f"Briefkasten Zusteller geöffnet.")
        elif pin == 6:
            logger.info(f"Briefkasten Türe zum Leeren geöffnet.")
        elif pin == 7:
            logger.info(f"Paketbox Türe zum Leeren geöffnet.")

    elif oldState == 1 and newState == 0: # falling edge
        if pin == 0:
            pbox_state.set_left_door(DoorState.CLOSED)
            logger.info(f"Packet Klappe links geschlossen/oben.")
        elif pin == 1:
            pbox_state.set_right_door(DoorState.OPEN)
            logger.info(f"Packet Klappe links geöffnet/unten.")
        elif pin == 2:
            pbox_state.set_left_door(DoorState.CLOSED)
            logger.info(f"Packet Klappe recht geschlossen/oben.")
        elif pin == 3:
            pbox_state.set_right_door(DoorState.OPEN)
            logger.info(f"Packet Klappe rechts geöffnet/unten.")
        elif pin == 4:
            pbox_state.set_paket_tuer(DoorState.CLOSED)
            logger.info(f"Paketklappe Zusteller geschlossen.")
            # Paket_Tuer_Zusteller_geschlossen()
        elif pin == 5:
            logger.info(f"Briefkasten Zusteller geschlossen.")
        elif pin == 6:
            logger.info(f"Briefkasten Türe zum Leeren geschlossen.")
        elif pin == 7:
            logger.info(f"Paketbox Türe zum Leeren geschlossen.")
        elif pin == 8:
            logger.info(f"Türöffner Taster 6 gedrückt.")
        elif pin == 9:
            logger.info(f"Türöffner Taster 8 gedrückt.")
        elif pin == 10:
            logger.info(f"Bewegungsmelder hat ausgelöst.")
    else:
        logger.warning(f"pinChanged: oldState == newState keine Änderung erkannt.")


def setOutputWithRuntime(runtime, gpio, state):
    """Set GPIO output for specified runtime, then automatically reset to opposite state."""
    try:
      GPIO = get_gpio()
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
      GPIO = get_gpio()
      GPIO.output(Config.OUTPUTS[7], GPIO.HIGH) # Riegel öffnet Tür. Tür kann wieder geöffnet werden
      logger.info("Türe Paketzusteller wurde entriegelt.")
   except Exception as e:
      logger.error(f"Hardwarefehler in unlockDoor: {e}")

def lockDoor():
   try:
      GPIO = get_gpio()
      GPIO.output(Config.OUTPUTS[7], GPIO.LOW) # Riegel schließt Tür. Tür kann nicht mehr geöffnet werden
      logger.info("Türe Paketzusteller wurde verriegelt.")
   except Exception as e:
      logger.error(f"Hardwarefehler in lockDoor: {e}")

def Klappen_schliessen():
    """Close both flaps with proper error handling and state validation."""
    GPIO = get_gpio()
    
    if pbox_state.is_any_error():
        logger.warning("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
        return False
    
    logger.info("Klappen fahren zu")
    # Start closing motors
    timerLeftFlap = setOutputWithRuntime(Config.CLOSURE_TIMER_SECONDS, Config.OUTPUTS[0], GPIO.LOW)
    timerRightFlap = setOutputWithRuntime(Config.CLOSURE_TIMER_SECONDS, Config.OUTPUTS[2], GPIO.LOW)

    if not timerLeftFlap or not timerRightFlap:
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

    timerCheckClosing = threading.Timer(Config.CLOSURE_TIMER_SECONDS + 1, endlagen_pruefung_closing)
    timerCheckClosing.start()
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
    GPIO = get_gpio()
    
    if pbox_state.is_any_error():
        logger.warning("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
        return False

    logger.info("Klappen fahren auf")
    # Start opening motors
    timer1 = setOutputWithRuntime(Config.MOTOR_REVERSE_SIGNAL, Config.OUTPUTS[1], GPIO.LOW)
    timer2 = setOutputWithRuntime(Config.MOTOR_REVERSE_SIGNAL, Config.OUTPUTS[3], GPIO.LOW)

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

    timer = threading.Timer(Config.CLOSURE_TIMER_SECONDS + 1, endlagen_pruefung)
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

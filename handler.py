
import threading
import logging
from PaketBoxState import DoorState
from config import Config
from state import pbox_state, sendMqttErrorState, mqttObject  # Import from central state module
import time
import mqtt


# Import GPIO from paketbox to use the same Mock/Real GPIO instance
def get_gpio():
    """Lazy import to avoid circular imports"""
    from paketbox import GPIO
    return GPIO

def get_initialize_door_states():
    """Lazy import to avoid circular imports"""
    from paketbox import initialize_door_states
    return initialize_door_states

logger = logging.getLogger(__name__) 

# Global timer for managing flap opening delay
_klappen_oeffnen_timer = None 

def ResetErrorState():
    """Reset all doors from ERROR state to CLOSED state."""
    logger.info("Starte Reset des Fehlerzustands...")
    
    # Check if any door is in error state
    if pbox_state.is_any_error():
        logger.warning("Fehlerzustand erkannt - setze alle Türen auf CLOSED zurück")
                
        # Re-initialize door states based on actual GPIO readings
        initialize_door_states = get_initialize_door_states()
        initialize_door_states()
        global sendMqttErrorState
        sendMqttErrorState = False  # Reset MQTT error state flag
        
        logger.info(f"Fehlerzustand behoben. Aktueller Zustand: {pbox_state}")
    elif isDoorLocked():
        unlockDoor() 
    else:
        logger.info("Kein Fehlerzustand erkannt - keine Aktion erforderlich")
        
    return not pbox_state.is_any_error()

def lichtMueltonneOn():
    GPIO = get_gpio()
    GPIO.output(Config.OUTPUTS[5], GPIO.LOW) # Licht an
    logger.info("Licht Mültonne wurde eingeschaltet.")

def lichtMueltonneOff():
    GPIO = get_gpio()
    GPIO.output(Config.OUTPUTS[5], GPIO.HIGH) # Licht aus
    logger.info("Licht Mültonne wurde ausgeschaltet.")     

def notHaltMotoren():
    GPIO = get_gpio()
    GPIO.output(Config.OUTPUTS[0], GPIO.HIGH) # Alle Motoren stoppen
    GPIO.output(Config.OUTPUTS[1], GPIO.HIGH) 
    GPIO.output(Config.OUTPUTS[2], GPIO.HIGH) 
    GPIO.output(Config.OUTPUTS[3], GPIO.HIGH) 
    GPIO.output(Config.OUTPUTS[7], GPIO.LOW) # Riegel Tür verriegelt
    logger.warning("Nothalt: Alle Motoren gestoppt und Tür verriegelt.")

def isAnyMotorRunning():
    GPIO = get_gpio()
    if not (GPIO.input(Config.OUTPUTS[0]) == GPIO.HIGH and 
                GPIO.input(Config.OUTPUTS[1]) == GPIO.HIGH and 
                GPIO.input(Config.OUTPUTS[2]) == GPIO.HIGH and 
                GPIO.input(Config.OUTPUTS[3]) == GPIO.HIGH):
        return True
    else:
        return False

def setLigthtPaketboxOn():
    GPIO = get_gpio()
    GPIO.output(Config.OUTPUTS[6], GPIO.LOW) # Licht an
    logger.info("Licht Paketbox wurde eingeschaltet.")

def setLigthtPaketboxOff():
    GPIO = get_gpio()
    GPIO.output(Config.OUTPUTS[6], GPIO.HIGH) # Licht aus
    logger.info("Licht Paketbox wurde ausgeschaltet.")

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

def isDoorLocked():
   try:
      GPIO = get_gpio()
      if GPIO.input(Config.OUTPUTS[7]) == GPIO.LOW:
         return True
      else:
         return False
   except Exception as e:
      logger.error(f"Hardwarefehler in isDoorLocked: {e}")
      return None

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
    global _klappen_oeffnen_timer
    logger.info("Türe Paketzusteller wurde geschlossen.")
    
    # Cancel any existing timer
    if _klappen_oeffnen_timer:
        _klappen_oeffnen_timer.cancel()
        logger.info("Vorherigen Klappen-Öffnungs-Timer abgebrochen.")
    
    logger.info("Starte verzögertes Öffnen der Klappen in 10 Sekunden...")
    
    def delayed_klappen_oeffnen():
        global _klappen_oeffnen_timer
        # Check if door is still closed before opening flaps
        if pbox_state.paket_tuer == DoorState.CLOSED:
            logger.info("10 Sekunden vergangen, starte Öffnen der Klappen...")
            lockDoor()
            Klappen_oeffnen()
        else:
            logger.warning("Klappen-Öffnung abgebrochen: Paketzusteller-Tür ist wieder geöffnet!")
        _klappen_oeffnen_timer = None
    
    _klappen_oeffnen_timer = threading.Timer(10.0, delayed_klappen_oeffnen)
    _klappen_oeffnen_timer.start()
    # Audiofile: Box wird geleert, dies dauert 2 Minuten


def Klappen_oeffnen_abbrechen():    
    global _klappen_oeffnen_timer
    if _klappen_oeffnen_timer:
        _klappen_oeffnen_timer.cancel()
        _klappen_oeffnen_timer = None
        logger.info("Klappen-Öffnung wurde abgebrochen.")
        return True
    else:
        logger.info("Kein aktiver Klappen-Öffnungs-Timer zum Abbrechen.")
        return False


def Paket_Tuer_Zusteller_geoeffnet():
    # Cancel flap opening if door is opened during waiting period
    Klappen_oeffnen_abbrechen()
    
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
    if pbox_state.is_any_open():
       logger.info("Resetting doors to closed state...")
       lockDoor()
       return Klappen_schliessen()
    elif pbox_state.is_any_error():
       logger.warning("Doors in error state - manual intervention required!")
       return False
    else:
       logger.info("Doors already in safe state.")
       return True

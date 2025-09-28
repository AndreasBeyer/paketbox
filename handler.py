
import threading
import logging
from PaketBoxState import DoorState, MotorState
from TimerManager import TimerManager
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

# Global timer manager instance
timer_manager = TimerManager() 

def ResetErrorState():
    """Reset all doors and motors from ERROR state to safe state."""
    logger.info("Starte Reset des Fehlerzustands...")
    
    # Check if any door or motor is in error state
    if pbox_state.is_any_error():
        logger.warning("Fehlerzustand erkannt - setze alle Türen und Motoren auf sicheren Zustand zurück")
                
        # Re-initialize door states based on actual GPIO readings
        initialize_door_states = get_initialize_door_states()
        initialize_door_states()
        
        # Reset motor states from ERROR to STOPPED
        if pbox_state.is_any_motor_error():
            logger.info("Setze Motor-Fehlerzustände zurück...")
            from PaketBoxState import MotorState
            pbox_state.set_left_motor(MotorState.STOPPED)
            pbox_state.set_right_motor(MotorState.STOPPED)
            logger.info("Motor-Zustände auf STOPPED zurückgesetzt")
        
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
    
    # Cancel all active motor timers
    timer_manager.cancel_all_timers()
    
    # Set motor states to error due to emergency stop
    pbox_state.set_left_motor(MotorState.ERROR)
    pbox_state.set_right_motor(MotorState.ERROR)
    
    logger.warning("Nothalt: Alle Motoren gestoppt, Timer abgebrochen und Tür verriegelt.")

def isAnyMotorRunning():
    """Check if any motor is currently running using state management."""
    return pbox_state.is_any_motor_running()

def setLigthtPaketboxOn():
    GPIO = get_gpio()
    GPIO.output(Config.OUTPUTS[6], GPIO.LOW) # Licht an
    logger.info("Licht Paketbox wurde eingeschaltet.")

def setLigthtPaketboxOff():
    GPIO = get_gpio()
    GPIO.output(Config.OUTPUTS[6], GPIO.HIGH) # Licht aus
    logger.info("Licht Paketbox wurde ausgeschaltet.")

def setOutputWithRuntime(runtime, gpio, state, timer_id=None):
    """Set GPIO output for specified runtime, then automatically reset to opposite state."""
    try:
      GPIO = get_gpio()
      GPIO.output(gpio, state)
      def reset_output():
         opposite_state = GPIO.LOW if state == GPIO.HIGH else GPIO.HIGH
         GPIO.output(gpio, opposite_state)
         logger.debug(f"GPIO {gpio} zurückgeschaltet zu {opposite_state}")
         # Clear timer reference when completed normally
         if timer_id:
             timer_manager.clear_timer(timer_id)
        
      timer = threading.Timer(runtime, reset_output)
      timer.start()
      
      # Register timer with manager if timer_id provided
      if timer_id:
          timer_manager.add_timer(timer_id, timer)
          
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
    # Set motor states to CLOSING
    pbox_state.set_left_motor(MotorState.CLOSING)
    pbox_state.set_right_motor(MotorState.CLOSING)
    
    # Start closing motors with timer management
    timerLeftFlap = setOutputWithRuntime(Config.CLOSURE_TIMER_SECONDS, Config.OUTPUTS[0], GPIO.LOW, 'left_motor')
    timerRightFlap = setOutputWithRuntime(Config.CLOSURE_TIMER_SECONDS, Config.OUTPUTS[2], GPIO.LOW, 'right_motor')

    if not timerLeftFlap or not timerRightFlap:
        logger.error("Fehler beim Starten der Motoren!")
        # Reset motor states on error
        pbox_state.set_left_motor(MotorState.ERROR)
        pbox_state.set_right_motor(MotorState.ERROR)
        return False
    
    def endlagen_pruefung_closing():
        """Check end positions after closing timeout."""
        # Clear timer reference
        timer_manager.clear_timer('left_check')
        
        if not (pbox_state.left_door == DoorState.CLOSED and pbox_state.right_door == DoorState.CLOSED):
            logger.error(f"Fehler: Klappen nicht geschlossen nach Schließungsversuch!")
            logger.error(f"Status: Links={pbox_state.left_door.name}, Rechts={pbox_state.right_door.name}")
            pbox_state.set_left_door(DoorState.ERROR)
            pbox_state.set_right_door(DoorState.ERROR)
            # Set motor states to ERROR
            pbox_state.set_left_motor(MotorState.ERROR)
            pbox_state.set_right_motor(MotorState.ERROR)
            return False
        else:
            logger.info("Klappen erfolgreich geschlossen.")
            # Set motor states to STOPPED after successful closing
            pbox_state.set_left_motor(MotorState.STOPPED)
            pbox_state.set_right_motor(MotorState.STOPPED)
            unlockDoor()
            return True

    timerCheckClosing = threading.Timer(Config.CLOSURE_TIMER_SECONDS + 1, endlagen_pruefung_closing)
    timerCheckClosing.start()
    timer_manager.add_timer('left_check', timerCheckClosing)
    return True

def Paket_Tuer_Zusteller_geschlossen():
    logger.info("Türe Paketzusteller wurde geschlossen.")
    
    # Cancel any existing timer using timer manager
    timer_manager.cancel_timer('delayed_open')
    logger.info("Vorherigen Klappen-Öffnungs-Timer abgebrochen.")
    
    logger.info("Starte verzögertes Öffnen der Klappen in 10 Sekunden...")
    
    def delayed_klappen_oeffnen():
        # Clear timer reference when executing
        timer_manager.clear_timer('delayed_open')
        
        # Check if door is still closed before opening flaps
        if pbox_state.paket_tuer == DoorState.CLOSED:
            logger.info("10 Sekunden vergangen, starte Öffnen der Klappen...")
            lockDoor()
            Klappen_oeffnen()
        else:
            logger.warning("Klappen-Öffnung abgebrochen: Paketzusteller-Tür ist wieder geöffnet!")
    
    delayed_timer = threading.Timer(10.0, delayed_klappen_oeffnen)
    delayed_timer.start()
    timer_manager.add_timer('delayed_open', delayed_timer)
    # Audiofile: Box wird geleert, dies dauert 2 Minuten


def Klappen_oeffnen_abbrechen():    
    """Cancel delayed flap opening timer using timer manager."""
    if timer_manager.active_timers['delayed_open'] is not None:
        timer_manager.cancel_timer('delayed_open')
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
    # Set motor states to OPENING
    pbox_state.set_left_motor(MotorState.OPENING)
    pbox_state.set_right_motor(MotorState.OPENING)
    
    # Start opening motors with timer management
    timer1 = setOutputWithRuntime(Config.MOTOR_REVERSE_SIGNAL, Config.OUTPUTS[1], GPIO.LOW, 'left_motor')
    timer2 = setOutputWithRuntime(Config.MOTOR_REVERSE_SIGNAL, Config.OUTPUTS[3], GPIO.LOW, 'right_motor')

    if not timer1 or not timer2:
        logger.error("Fehler beim Starten der Motoren!")
        # Reset motor states on error
        pbox_state.set_left_motor(MotorState.ERROR)
        pbox_state.set_right_motor(MotorState.ERROR)
        return False
    
    def endlagen_pruefung():
        """Check end positions after opening timeout."""
        # Clear timer reference
        timer_manager.clear_timer('right_check')
        
        if not (pbox_state.left_door == DoorState.OPEN and pbox_state.right_door == DoorState.OPEN):
            logger.error(f"Fehler: Klappen nicht offen nach Öffnungsversuch!")
            logger.error(f"Status: Links={pbox_state.left_door.name}, Rechts={pbox_state.right_door.name}")
            pbox_state.set_left_door(DoorState.ERROR)
            pbox_state.set_right_door(DoorState.ERROR)
            # Set motor states to ERROR
            pbox_state.set_left_motor(MotorState.ERROR)
            pbox_state.set_right_motor(MotorState.ERROR)
            return False
        else:
            logger.info("Klappen erfolgreich geöffnet.")
            # Set motor states to STOPPED after successful opening
            pbox_state.set_left_motor(MotorState.STOPPED)
            pbox_state.set_right_motor(MotorState.STOPPED)
            logger.info(f"Starte automatisches Schließen der Klappen... Status: {pbox_state}")
            # Auto-close after successful opening
            if (pbox_state.left_door == DoorState.OPEN and pbox_state.right_door == DoorState.OPEN):
               Klappen_schliessen()
            else:
               logger.error(f"Fehler: Klappen nicht beide im OPEN-Zustand!")
            return True

    timer = threading.Timer(Config.CLOSURE_TIMER_SECONDS + 1, endlagen_pruefung)
    timer.start()
    timer_manager.add_timer('right_check', timer)
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

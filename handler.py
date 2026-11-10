
import threading
import logging
from PaketBoxState import DoorState, MotorState
from TimerManager import TimerManager
from config import Config
from state import pbox_state, sendMqttErrorState  # Import from central state module
import state  # use state.mqttObject dynamically to stay in sync
import time
import mqtt
from datetime import datetime


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

failed_motor_releases = set()

# Global light barrier state
light_barrier_triggered = False 

@timer_manager.synchronized
def ResetErrorState():
    """Reset all doors and motors from ERROR state to safe state."""
    logger.info("Starte Reset des Fehlerzustands...")

    if failed_motor_releases and not _cancel_motor_cycle():
        logger.error("Motorfreigabe fehlgeschlagen - Fehlerzustand bleibt aktiv.")
        return False
    
    # Check if any door or motor is in error state
    if pbox_state.is_any_error():
        logger.warning("Fehlerzustand erkannt - setze alle Türen und Motoren auf sicheren Zustand zurück")
                
        # Re-initialize door states based on actual GPIO readings
        initialize_door_states = get_initialize_door_states()
        initialize_door_states()
        
        # Reset motor states from ERROR to STOPPED
        if pbox_state.is_any_motor_error():
            logger.debug("Setze Motor-Fehlerzustände zurück...")
            from PaketBoxState import MotorState
            pbox_state.set_left_motor(MotorState.STOPPED)
            pbox_state.set_right_motor(MotorState.STOPPED)
            logger.debug("Motor-Zustände auf STOPPED zurückgesetzt")
        
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

@timer_manager.synchronized
def notHaltMotoren():
    # Set motor states to error due to emergency stop
    pbox_state.set_left_motor(MotorState.ERROR)
    pbox_state.set_right_motor(MotorState.ERROR)

    timer_manager.cancel_timer('door_open_watchdog')
    released = _cancel_motor_cycle()
    lockDoor()
    
    if released:
        logger.warning("Nothalt: Alle Motoren gestoppt, Timer abgebrochen und Tür verriegelt.")
    else:
        logger.error("Nothalt: Motorfreigabe fehlgeschlagen; Hardware prüfen.")

def isAnyMotorRunning():
    """Check if any motor is currently running using state management."""
    return pbox_state.is_any_motor_running()

def isAnyMotorError():
    """Check if any motor is currently in error state using state management."""
    return pbox_state.is_any_motor_error()

def setLigthtPaketboxOn():
    GPIO = get_gpio()
    GPIO.output(Config.OUTPUTS[6], GPIO.LOW) # Licht an
    logger.info("Licht Paketbox wurde eingeschaltet.")

def setLigthtPaketboxOff():
    GPIO = get_gpio()
    GPIO.output(Config.OUTPUTS[6], GPIO.HIGH) # Licht aus
    logger.info("Licht Paketbox wurde ausgeschaltet.")

@timer_manager.synchronized
def setOutputWithRuntime(runtime, gpio, state, timer_id=None):
    """Set GPIO output for specified runtime, then automatically reset to opposite state."""
    try:
      GPIO = get_gpio()
      GPIO.output(gpio, state)
      def reset_output():
         opposite_state = GPIO.LOW if state == GPIO.HIGH else GPIO.HIGH
         try:
             GPIO.output(gpio, opposite_state)
         except Exception as e:
             if gpio not in Config.OUTPUTS[:4]:
                 raise
             logger.error(f"Motorabschaltung GPIO {gpio} fehlgeschlagen: {e}")
             # Latch the error and invalidate end checks before they can unlock
             # the door or start another movement. The emergency release path
             # retries any outputs that still cannot be switched off.
             notHaltMotoren()
             return
         logger.debug(f"GPIO {gpio} zurückgeschaltet zu {opposite_state}")
      if timer_id:
          return timer_manager.start_timer(timer_id, runtime, reset_output)

      timer = threading.Timer(runtime, reset_output)
      timer.start()
          
      return timer  # Return timer for potential cancellation
    except Exception as e:
      logger.error(f"Hardwarefehler in setOutputWithRuntime: {e}")
      return None

# region Light Barrier Functions

def set_light_barrier_triggered(triggered):
    """Set the light barrier triggered state."""
    global light_barrier_triggered
    light_barrier_triggered = triggered
    state = "ausgelöst" if triggered else "zurückgesetzt"
    logger.warning(f"Lichtschranke {state}.")

def is_light_barrier_triggered():
    """Check if light barrier is currently triggered."""
    return light_barrier_triggered

def reset_light_barrier():
    """Reset light barrier state."""
    global light_barrier_triggered
    light_barrier_triggered = False
    logger.info("Lichtschranke-Status zurückgesetzt.")

# endregion
    
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

def _cancel_motor_cycle():
    """Invalidate the old cycle and release relays before changing direction."""
    for timer_id in ('left_check', 'right_check', 'delayed_open'):
        timer_manager.cancel_timer(timer_id)
    GPIO = get_gpio()
    for output in Config.OUTPUTS[:4]:
        try:
            GPIO.output(output, GPIO.HIGH)
        except Exception as e:
            logger.error(f"Motorfreigabe GPIO {output} fehlgeschlagen: {e}")
            failed_motor_releases.add(output)
        else:
            failed_motor_releases.discard(output)

    if failed_motor_releases:
        pbox_state.set_left_motor(MotorState.ERROR)
        pbox_state.set_right_motor(MotorState.ERROR)

        def retry_release():
            _cancel_motor_cycle()

        if timer_manager.active_timers.get('motor_release_retry') is None:
            try:
                timer_manager.start_timer('motor_release_retry', 1, retry_release)
            except Exception:
                logger.exception("Motorfreigabe-Wiederholung konnte nicht gestartet werden")
        return False

    timer_manager.cancel_timer('motor_release_retry')
    for timer_id in ('left_motor', 'right_motor'):
        timer_manager.cancel_timer(timer_id)
    return True


@timer_manager.synchronized
def Klappen_schliessen():
    """Close both flaps with proper error handling and state validation."""
    GPIO = get_gpio()
    
    # Check if light barrier is triggered - prevent closing if so
    if is_light_barrier_triggered():
        logger.error("NOTHALT: Lichtschranke ausgelöst! Klappen können nicht geschlossen werden.")
        notHaltMotoren()
        return False
    
    if pbox_state.is_any_error():
        logger.warning("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
        return False

    if pbox_state.left_motor == MotorState.CLOSING and pbox_state.right_motor == MotorState.CLOSING:
        logger.info("Klappen schließen bereits; laufender Zyklus bleibt unverändert.")
        return True

    if not _cancel_motor_cycle():
        return False
    
    logger.info("Klappen fahren zu")
    # Set motor states to CLOSING
    pbox_state.set_left_motor(MotorState.CLOSING)
    pbox_state.set_right_motor(MotorState.CLOSING)
    
    # Start closing motors with timer management
    timerLeftFlap = setOutputWithRuntime(Config.MOTOR_REVERSE_SIGNAL_CLOSE, Config.OUTPUTS[0], GPIO.LOW, 'left_motor')
    timerRightFlap = setOutputWithRuntime(Config.MOTOR_REVERSE_SIGNAL_CLOSE, Config.OUTPUTS[2], GPIO.LOW, 'right_motor')

    if not timerLeftFlap or not timerRightFlap:
        logger.error("Fehler beim Starten der Motoren!")
        notHaltMotoren()
        return False
    
    def endlagen_pruefung_closing():
        """Check end positions after closing timeout."""
        # Check if light barrier was triggered during closing
        if is_light_barrier_triggered():
            logger.error("NOTHALT: Lichtschranke während Klappenfahrt ausgelöst!")
            notHaltMotoren()
            return False
        
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

    timer_manager.start_timer('left_check', Config.CLOSURE_TIMER_SECONDS + 1, endlagen_pruefung_closing)
    return True

@timer_manager.synchronized
def Paket_Tuer_Zusteller_geschlossen():
    logger.info("Türe Paketzusteller wurde geschlossen.")
    
    # Cancel 15-Minuten-Überwachung da Tür jetzt geschlossen ist
    timer_manager.cancel_timer('door_open_watchdog')
    logger.info("15-Minuten-Überwachung für geöffnete Paket-Tür abgebrochen.")
    
    # Cancel any existing timer using timer manager
    timer_manager.cancel_timer('delayed_open')
    logger.info("Vorherigen Klappen-Öffnungs-Timer abgebrochen.")
    
    if isAnyMotorRunning() or pbox_state.is_any_error():
        logger.info("Kein neuer Entleerungszyklus: Motorzyklus läuft oder Fehlerzustand aktiv.")
        return

    logger.info(f"Starte verzögertes Öffnen der Klappen in {Config.CLOSURE_DELAY} Sekunden...")
    
    def delayed_klappen_oeffnen():
        if isAnyMotorRunning() or pbox_state.is_any_error():
            logger.info("Klappen-Öffnung übersprungen: Motorzyklus läuft oder Fehlerzustand aktiv.")
            return

        # Check if door is still closed before opening flaps
        if pbox_state.paket_tuer == DoorState.CLOSED:
            logger.info(f"{Config.CLOSURE_DELAY} Sekunden vergangen, starte Öffnen der Klappen...")
            lockDoor()
            Klappen_oeffnen()
        else:
            logger.warning("Klappen-Öffnung abgebrochen: Paketzusteller-Tür ist wieder geöffnet!")
    
    timer_manager.start_timer('delayed_open', Config.CLOSURE_DELAY, delayed_klappen_oeffnen)
    # Audiofile: Box wird geleert, dies dauert 2 Minuten


@timer_manager.synchronized
def Klappen_oeffnen_abbrechen():    
    """Cancel delayed flap opening timer using timer manager."""
    if timer_manager.active_timers['delayed_open'] is not None:
        timer_manager.cancel_timer('delayed_open')
        logger.info("Klappen-Öffnung wurde abgebrochen.")
        return True
    else:
        logger.info("Kein aktiver Klappen-Öffnungs-Timer zum Abbrechen.")
        return False


@timer_manager.synchronized
def Paket_Tuer_Zusteller_geoeffnet():
    # Cancel flap opening if door is opened during waiting period
    Klappen_oeffnen_abbrechen()
    
    if pbox_state.is_any_open() or isAnyMotorRunning():
         logger.warning(f"Fehler: Tür wurde geöffnet und Klappen waren nicht zu.")
         Klappen_schliessen()

    logger.info("Türe Paketzusteller wurde geöffnet")
    
    # Starte 15-Minuten-Überwachung für geöffnete Paket-Tür
    def door_open_watchdog():
        # Check if door is still open after 15 minutes
        if pbox_state.paket_tuer == DoorState.OPEN:
            logger.warning("WARNUNG: Paket-Tür ist seit 15 Minuten geöffnet! Öffne Klappen zur Entleerung...")
            
            # Sende MQTT-Fehlernachricht
            try:
                import mqtt
                if hasattr(mqtt, 'publish_status'):
                    error_message = f"FEHLER: Paket-Tür seit 15 Minuten geöffnet - automatische Entleerung gestartet"
                    mqtt.publish_status(error_message)
                    logger.info(f"MQTT-Fehlernachricht gesendet: {error_message}")
            except Exception as e:
                logger.error(f"Fehler beim Senden der MQTT-Nachricht: {e}")
            
            # Öffne Klappen zur Entleerung
            Klappen_oeffnen()
        else:
            logger.debug("15-Minuten-Timer abgelaufen, aber Paket-Tür ist bereits geschlossen.")
    
    # Starte 15-Minuten-Timer (15 * 60 = 900 Sekunden)
    timer_manager.start_timer('door_open_watchdog', 900.0, door_open_watchdog)
    logger.info("15-Minuten-Überwachung für geöffnete Paket-Tür gestartet.")

@timer_manager.synchronized
def Klappen_oeffnen():
    """Open both flaps with proper error handling and state validation."""
    GPIO = get_gpio()
    
    if pbox_state.is_any_error():
        logger.warning("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
        return False

    if isAnyMotorRunning():
        logger.info("Klappen-Öffnung übersprungen: Motorzyklus läuft bereits.")
        return False

    if not _cancel_motor_cycle():
        return False
    logger.info("Klappen fahren auf")
    # Set motor states to OPENING
    pbox_state.set_left_motor(MotorState.OPENING)
    pbox_state.set_right_motor(MotorState.OPENING)
    
    # Start opening motors with timer management
    timer1 = setOutputWithRuntime(Config.MOTOR_REVERSE_SIGNAL_OPEN, Config.OUTPUTS[1], GPIO.LOW, 'left_motor')
    timer2 = setOutputWithRuntime(Config.MOTOR_REVERSE_SIGNAL_OPEN, Config.OUTPUTS[3], GPIO.LOW, 'right_motor')

    if not timer1 or not timer2:
        logger.error("Fehler beim Starten der Motoren!")
        notHaltMotoren()
        return False
    
    def endlagen_pruefung():
        """Check end positions after opening timeout."""
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
            logger.info(f"Starte automatisches Schließen der Klappen... Status: {pbox_state}")
            Klappen_schliessen()
            return True

    timer_manager.start_timer('right_check', Config.OPENING_TIMER_SECONDS + 1, endlagen_pruefung)
    return True

@timer_manager.synchronized
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

# endregion

# region Auto Lock Door Time Functions

# Global variable to track auto lock door setting
auto_lock_door_enabled = False

def set_auto_lock_door(enabled):
    """Set the auto lock door feature to enabled or disabled."""
    global auto_lock_door_enabled
    auto_lock_door_enabled = enabled
    state = "aktiviert" if enabled else "deaktiviert"
    logger.info(f"Automatische Türverriegelung {state}.")

def is_auto_lock_door_enabled():
    """Return whether auto lock door is enabled."""
    return auto_lock_door_enabled

def is_in_lock_period():
    """Check if current time is within the lock period (TIME_LOCK_DOOR to TIME_UNLOCK_DOOR)."""
    try:
        current_time = datetime.now().time()
        
        # Parse lock and unlock times
        lock_time = datetime.strptime(Config.TIME_LOCK_DOOR, "%H:%M").time()
        unlock_time = datetime.strptime(Config.TIME_UNLOCK_DOOR, "%H:%M").time()
        
        # If lock_time is after unlock_time, it means the lock period spans midnight
        # e.g., 20:00 to 08:00 means locked from 20:00 to 23:59 and 00:00 to 08:00
        if lock_time > unlock_time:
            is_locked = current_time >= lock_time or current_time < unlock_time
        else:
            # Lock period is within the same day
            is_locked = lock_time <= current_time < unlock_time
        
        logger.debug(f"Zeit-Check: Aktuell={current_time.strftime('%H:%M')}, Sperren={lock_time.strftime('%H:%M')}, Entsperren={unlock_time.strftime('%H:%M')}, In Sperrzeit={is_locked}")
        return is_locked
    except Exception as e:
        logger.error(f"Fehler bei Zeit-Überprüfung: {e}")
        return False

@timer_manager.synchronized
def auto_check_and_lock_door():
    """Automatically lock or unlock door based on time and auto_lock_door setting."""
    if not is_auto_lock_door_enabled():
        return
    
    if isAnyMotorRunning() or isAnyMotorError():
        logger.debug("Automatische Verriegelung übersprungen: Motoren laufen gerade oder sind im Fehlerzustand.")
        return

    try:
        should_be_locked = is_in_lock_period()
        is_currently_locked = isDoorLocked()
        
        if should_be_locked and not is_currently_locked:
            logger.info("Automatische Verriegelung: Tür wird verriegelt (Sperrzeit aktiv).")
            lockDoor()
            if state.mqttObject:
                state.mqttObject.publish_status("Türe wurde automatisch verriegelt (Sperrzeit).")
        
        elif not should_be_locked and is_currently_locked:
            logger.info("Automatische Entsperrung: Tür wird entriegelt (Sperrzeit vorbei).")
            unlockDoor()
            if state.mqttObject:
                state.mqttObject.publish_status("Türe wurde automatisch entriegelt (Sperrzeit vorbei).")
    
    except Exception as e:
        logger.error(f"Fehler bei automatischer Türverriegelung: {e}")

# endregion
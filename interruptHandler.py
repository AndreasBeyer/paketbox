
import logging
import time
from paketbox import logger, pbox_state, GPIO, DoorState

def verifyTriggerAndDebounce(channel, level):
   for i in range(0,20):
      time.sleep(0.2)
      if GPIO.input(channel) == level:  # Signal went back to HIGH = false trigger
         return False
   return True 

def handleLeftFlapClosed(channel):
   try:
      if not verifyTriggerAndDebounce(channel, GPIO.HIGH):
         return
      pbox_state.set_left_door(DoorState.CLOSED)
      logger.info("Entleerungsklappe links ist geschlossen")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleLeftFlapClosed: {e}")
      pbox_state.set_left_door(DoorState.ERROR)


def handleLeftFlapOpened(channel):
    try:
      if not verifyTriggerAndDebounce(channel, GPIO.HIGH):
        return
      pbox_state.set_left_door(DoorState.OPEN)
      logger.info("Entleerungsklappe links ist geöffnet")
    except Exception as e:
      logger.error(f"Hardwarefehler in handleLeftFlapOpened: {e}")
      pbox_state.set_left_door(DoorState.ERROR)


def handleRightFlapClosed(channel):
   try:
      if not verifyTriggerAndDebounce(channel, GPIO.HIGH):
         return
      pbox_state.set_right_door(DoorState.CLOSED)
      logger.info("Entleerungsklappe rechts ist geschlossen")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleRightFlapClosed: {e}")
      pbox_state.set_right_door(DoorState.ERROR)

def handleRightFlapOpened(channel):
    try:
      if not verifyTriggerAndDebounce(channel, GPIO.HIGH):
        return
      pbox_state.set_right_door(DoorState.OPEN)
      logger.info("Entleerungsklappe rechts ist geöffnet")
    except Exception as e:
      logger.error(f"Hardwarefehler in handleRightFlapOpened: {e}")
      pbox_state.set_right_door(DoorState.ERROR)


def handleDeliveryDoorStatus(channel):
   try:
      current_state = GPIO.input(channel)
      if not verifyTriggerAndDebounce(channel, ~current_state):
        return

      if current_state == GPIO.HIGH:
         pbox_state.set_paket_tuer(DoorState.OPEN)
         logger.info("Pakettür Zusteller geöffnet")
#         Paket_Tuer_Zusteller_geoeffnet()
      else:
         pbox_state.set_paket_tuer(DoorState.CLOSED)
         logger.info("Pakettür Zusteller geschlossen")
#         Paket_Tuer_Zusteller_geschlossen()
   except Exception as e:
      logger.error(f"Hardwarefehler in handleDeliveryDoorStatus: {e}")
      pbox_state.set_paket_tuer(DoorState.ERROR)

def handleMailboxOpen(channel):
   try:
      if not verifyTriggerAndDebounce(channel, GPIO.HIGH):
         return
      logger.info("Der Briefkasten wurde geöffnet")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleMailboxOpen: {e}")

def handlePackageBoxDoorClosed(channel):
   try:
      if not verifyTriggerAndDebounce(channel, GPIO.HIGH):
         return
      logger.info("Die Tür zur Paketentnahme wurde geschlossen")
   except Exception as e:
      logger.error(f"Hardwarefehler in handlePackageBoxDoorOpen: {e}")

def handleMailboxDoorOpen(channel):
   try:
      if not verifyTriggerAndDebounce(channel, GPIO.HIGH):
         return
      logger.info("Die Türe zum Briefe entnehmen wurde geöffnet")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleMailboxDoorOpen: {e}")

def handleGartenDoorButton6Press(channel):
   try:
      if not verifyTriggerAndDebounce(channel, GPIO.HIGH):
         return
      logger.info("Der Taster an der Paketbox für Gartentürchen Nr. 6 wurde gedrückt")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleGartenDoorButton6Press: {e}")

def handleGardenDoorButton8Press(channel):
   try:
      if not verifyTriggerAndDebounce(channel, GPIO.HIGH):
         return
      logger.info("Der Taster an der Paketbox für Gartentürchen Nr. 8 wurde gedrückt")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleGardenDoorButton8Press: {e}")

def handleMotionDetection(channel):
   try:
      if not verifyTriggerAndDebounce(channel, GPIO.HIGH):
        return
      logger.info("Der Bewegungsmelder hat eine Bewegung erkannt.")
   except Exception as e:
      logger.error(f"Hardwarefehler in handleMotionDetection: {e}")

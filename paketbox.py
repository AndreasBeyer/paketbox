# Paketbox control script
# Version 0.0.5

# region State Management
from enum import Enum, auto

closure_timer_seconds = 10
motor_reverse_signal = 5
class DoorState(Enum):
   CLOSED = auto()
   OPEN = auto()
   ERROR = auto()

try:
   import RPi.GPIO as GPIO
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
import time
import asyncio
import threading
import sys

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

   #Interrupt
   GPIO.add_event_detect(I01, GPIO.RISING, callback=handleLeftFlapClosed, bouncetime=200) # EndsensorKlappe links geschlossen
   GPIO.add_event_detect(I02, GPIO.RISING, callback=handleLeftFLapOpened, bouncetime=200) # Endsensor Klappe links geöffnet
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
    GPIO.output(gpio, state)
    def relaise_ausschalten(state):
         stateREv = ~state
         GPIO.output(gpio, stateREv)
         print("GPIO " + str(gpio) + " zurückschalten zu " + str(stateREv))
    timer = threading.Timer(runtime, relaise_ausschalten, args=(state, ))
    timer.start()


# region Callsbacks
def handleLeftFlapClosed(channel):
   try:
      time.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      pbox_state.set_left_door(DoorState.CLOSED)
      print("Entleerungsklappe links ist geschlossen")
   except Exception as e:
      print(f"Hardwarefehler in handleLeftFlapClosed: {e}")


def handleLeftFLapOpened(channel):
    try:
       time.sleep(0.2)
       if GPIO.input(channel) == GPIO.HIGH:
          return
       pbox_state.set_left_door(DoorState.OPEN)
       print("Entleerungsklappe links ist geöffnet")
    except Exception as e:
       print(f"Hardwarefehler in handleLeftFLapOpened: {e}")


def handleRightFlapClosed(channel):
   try:
      time.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      pbox_state.set_right_door(DoorState.CLOSED)
      print("Entleerungsklappe rechts ist geschlossen")
   except Exception as e:
      print(f"Hardwarefehler in handleRightFlapClosed: {e}")

def handleRightFlapOpened(channel):
    try:
       time.sleep(0.2)
       if GPIO.input(channel) == GPIO.HIGH:
            return # Entprellen
       pbox_state.set_right_door(DoorState.OPEN)
       print("Entleerungsklappe links ist geöffnet")
    except Exception as e:
       print(f"Hardwarefehler in handleRightFlapOpened: {e}")

def handleDeliveryDoorStatus(channel):
   try:
      if GPIO.input(channel):
         time.sleep(0.2)
         if GPIO.input(channel) == GPIO.HIGH:
            return
         pbox_state.set_paket_tuer(DoorState.OPEN)
         Paket_Tuer_Zusteller_geoeffnet()
      else:
         time.sleep(0.2)
         if GPIO.input(channel) == GPIO.HIGH:
            return
         pbox_state.set_paket_tuer(DoorState.CLOSED)
         Paket_Tuer_Zusteller_geschlossen()
   except Exception as e:
      print(f"Hardwarefehler in handleDeliveryDoorStatus: {e}")

def handleMailboxOpen(channel):
   try:
      time.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      print("Der Briefkasten wurde geöffnet")
   except Exception as e:
      print(f"Hardwarefehler in handleMailboxOpen: {e}")

def handlePackageBoxDoorOpen(channel):
   try:
      time.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      print("Die Tür zur Paketentnahme wurde geöffnet")
   except Exception as e:
      print(f"Hardwarefehler in handlePackageBoxDoorOpen: {e}")

def handleMailboxDoorOpen(channel):
   try:
      time.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      print("Die Türe zum Briefe entnehmen wurde geöffnet")
   except Exception as e:
      print(f"Hardwarefehler in handleMailboxDoorOpen: {e}")

def handleGartenDoorButton6Press(channel):
   try:
      time.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      print("Der Taster an der Paketbox für Gartentürchen Nr. 6 wurde gedrückt")
   except Exception as e:
      print(f"Hardwarefehler in handleGartenDoorButton6Press: {e}")

def handleGardenDoorButton8Press(channel):
   try:
      time.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      print("Der Taster an der Paketbox für Gartentürchen Nr. 8 wurde gedrückt")
   except Exception as e:
      print(f"Hardwarefehler in handleGardenDoorButton8Press: {e}")

def handleMotionDetection(channel):
   try:
      time.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      print("Der Bewegungsmelder hat eine Bewegung erkannt.")
   except Exception as e:
      print(f"Hardwarefehler in handleMotionDetection: {e}")

# endregion

# region Actions

def unlockDoor():
   try:
      GPIO.output(Q8, GPIO.HIGH) # Riegel öffnet Tür. Tür kann wieder geöffnet werden
      print("Türe Paketzusteller wurde entriegelt.")
   except Exception as e:
      print(f"Hardwarefehler in unlockDoor: {e}")

def lockDoor():
   try:
      GPIO.output(Q8, GPIO.LOW) # Riegel schließt Tür. Tür kann nicht mehr geöffnet werden
      print("Türe Paketzusteller wurde verriegelt.")
   except Exception as e:
      print(f"Hardwarefehler in lockDoor: {e}")

def Klappen_schliessen():
    if pbox_state.is_any_error():
        print("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
        return
    print("Klappen fahren zu")
    setOutputWithRuntime(closure_timer_seconds, Q1, GPIO.LOW)
    setOutputWithRuntime(closure_timer_seconds, Q3, GPIO.LOW)
    def endlagen_pruefung_closing():
        # if not (pbox_state.left_door == DoorState.OPEN and pbox_state.right_door == DoorState.OPEN):
        if not (pbox_state.left_door == DoorState.CLOSED): # Fake right_door hardware error
            print(f"Fehler: Klappen nicht geschlossen nach Schließungsversuch!")
            pbox_state.set_left_door(DoorState.ERROR)
            pbox_state.set_right_door(DoorState.ERROR)
        else:
            pbox_state.set_right_door(DoorState.CLOSED) # Fake right_door hardware error
            print("Klappen erfolgreich geschlossen.")

    timer = threading.Timer(closure_timer_seconds, endlagen_pruefung_closing)
    timer.start()

def Paket_Tuer_Zusteller_geschlossen():
    print("Türe Paketzusteller wurde geschlossen.")
    time.sleep(10)
    lockDoor()
    print("Starte Öffnen der Klappen...")
    Klappen_oeffnen()
    # Audiofile: Box wird geleert, dies dauert 2 Minuten

def Paket_Tuer_Zusteller_geoeffnet():
    if GPIO.input(I01) == GPIO.HIGH or GPIO.input(I03) == GPIO.HIGH:
        Klappen_schliessen()
        print("Fehler: Tür wurde geöffnet und Klappen waren nicht zu.")
    print("Türe Paketzusteller wurde geöffnet:")

def Klappen_oeffnen():
    if pbox_state.is_any_error():
        print("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
        return
    print("Klappen fahren auf")

    setOutputWithRuntime(motor_reverse_signal, Q2, GPIO.LOW)
    setOutputWithRuntime(motor_reverse_signal, Q4, GPIO.LOW)
    # Endlagenprüfung nach fixer Zeit in einem Timer
    def endlagen_pruefung():
        # if not (pbox_state.left_door == DoorState.OPEN and pbox_state.right_door == DoorState.OPEN):
        if not (pbox_state.left_door == DoorState.OPEN): # Fake right_door hardware error
            print(f"Fehler: Klappen nicht offen nach Öffnungsversuch!")
            pbox_state.set_left_door(DoorState.ERROR)
            pbox_state.set_right_door(DoorState.ERROR)
        else:
            pbox_state.set_right_door(DoorState.OPEN) # Fake right_door hardware error
            print("Klappen erfolgreich geöffnet.")
            def Klappen_wieder_zu():
               if pbox_state.left_door == DoorState.OPEN and pbox_state.right_door == DoorState.OPEN:
                  Klappen_schliessen()
               else:
                   print(f"Fehler: Klappen immer noch im DoorState.OPEN!")
            timer = threading.Timer(closure_timer_seconds, Klappen_wieder_zu)
            timer.start()

    timer = threading.Timer(closure_timer_seconds, endlagen_pruefung)
    timer.start()

# endregion

# Async Main Loop
async def main():
   init()
   print("init abgeschlossen. Strg+C zum Beenden drücken.")
   Klappen_oeffnen()
   def mock_klappen_öffnen():
      pbox_state.set_left_door(DoorState.OPEN)
      pbox_state.set_right_door(DoorState.OPEN) 
   timer = threading.Timer(closure_timer_seconds-2, mock_klappen_öffnen)
   timer.start()

   try:
      while True:
         await asyncio.sleep(1)  # Main loop
         # Hier können weitere async Aufgaben hinzugefügt werden
   except KeyboardInterrupt:
      print("Beendet mit Strg+C")
   except Exception as e:
      print(f"[Main] Fehler: {e}")
   finally:
      GPIO.cleanup()
      print("GPIO aufgeräumt.")

# Diese Zeilen sorgen dafür, dass das Skript nur ausgeführt wird,
# wenn es direkt gestartet wird (und nicht importiert).
# asyncio.run(main()) startet die asynchrone Hauptfunktion.
if __name__ == "__main__":
   asyncio.run(main())


# Threadsicherer globaler Fehlerzustand
import threading
_global_error = False
_global_error_lock = threading.Lock()

def set_global_error(state: bool):
   global _global_error
   with _global_error_lock:
      _global_error = state
   print(f"Globaler Fehlerzustand wurde auf {state} gesetzt.")

def get_global_error() -> bool:
   with _global_error_lock:
      return _global_error

import RPi.GPIO as GPIO
import time
import asyncio

# GPIO.cleanup()

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
    gpio_delayed(runtime, gpio, ~state)

async def gpio_delayed(delay, gpio, state): # delay in Sekunden
   await asyncio.sleep(delay)
   GPIO.output(gpio,state)
   print("GPIO " + gpio + " geschalten zu " + satate)

# region Callsbacks
async def handleLeftFlapClosed(channel):
   await asyncio.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Entleerungsklappe links ist geschlossen")
   # GPIO.output(Q1, GPIO.HIGH) # Antrieb aus Fahrtrichtung zu

async def handleLeftFLapOpened(channel):
    await asyncio.sleep(0.2)
    if GPIO.input(channel) == GPIO.HIGH:
       return
    print("Entleerungsklappe links ist geöffnet")
    # GPIO.output(Q2, GPIO.HIGH) # Antrieb aus Fahrtrichtung auf

async def handleRightFlapClosed(channel):
   await asyncio.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Entleerungsklappe rechts ist geschlossen")
   # GPIO.output(Q3, GPIO.HIGH) # Antrieb aus Fahrtrichtung zu
   # GPIO.output(Q8, GPIO.HIGH) # Riegel öffnet Tür. Tür kann wieder geöffnet werden
 #  print("Tuer wird freigegeben")

async def handleRightFlapOpened(channel):
    await asyncio.sleep(0.2)
    if GPIO.input(channel) == GPIO.HIGH:
         return # Entprellen
    print("Entleerungsklappe links ist geöffnet")
    # GPIO.output(Q4, GPIO.HIGH) # Antrieb aus Fahrtrichtung auf
 #  await asyncio.sleep(0.5)
    await Klappen_schliessen()
 #  print("Klappe wird wieder geschlossen")

async def handleDeliveryDoorStatus(channel):
   if GPIO.input(channel):
      await asyncio.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      await Paket_Tuer_Zusteller_geoeffnet()
   else:
      await asyncio.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      await Paket_Tuer_Zusteller_geschlossen()

async def handleMailboxOpen(channel):
   await asyncio.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Der Briefkasten wurde geöffnet")

async def handlePackageBoxDoorOpen(channel):
   await asyncio.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Die Tür zur Paketentnahme wurde geöffnet")

async def handleMailboxDoorOpen(channel):
   await asyncio.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Die Türe zum Briefe entnehmen wurde geöffnet")

async def handleGartenDoorButton6Press(channel):
   await asyncio.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Der Taster an der Paketbox für Gartentürchen Nr. 6 wurde gedrückt")

async def handleGardenDoorButton8Press(channel):
   await asyncio.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Der Taster an der Paketbox für Gartentürchen Nr. 8 wurde gedrückt")

async def handleMotionDetection(channel):
   await asyncio.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Der Bewegungsmelder hat eine Bewegung erkannt.")

# endregion

async def Klappen_schliessen():
   if get_global_error:
      print("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
      return
   print("Klappen fahren zu")
#   GPIO.output(Q1, GPIO.LOW) # fahre Linke Klappe zu
#   GPIO.output(Q3, GPIO.LOW) # fahre rechte Klappe zu

async def Klappen_oeffnen():
   if get_global_error:
      print("Motorsteuerung gestoppt: Globaler Fehlerzustand aktiv!")
      return
   print("Klappen fahren auf")
#   await setOutputWithRuntime(120, Q2, GPIO.LOW)
#   await setOutputWithRuntime(120, Q4, GPIO.LOW)
#   GPIO.output(Q2, GPIO.LOW) # fahre Linke Klappe auf
#   GPIO.output(Q4, GPIO.LOW) # fahre rechte Klappe auf

async def Paket_Tuer_Zusteller_geschlossen():
   print("Türe Paketzusteller wurde geschlossen.")
   # Audiofile: Die Box wird sich in 10 Sekunden verriegeln. Wenn noch neue Pakete abgegeben werden sollen Türe wieder öffnen.
   GPIO.output(Q8, GPIO.LOW) # Tür verriegelt
   print("Türe Paketzusteller wurde verriegelt.")
   await asyncio.sleep(10)
   GPIO.output(Q8, GPIO.HIGH)
   await Klappen_oeffnen()
   # Audiofile: Box wird geleert, dies dauert 2 Minuten

async def Paket_Tuer_Zusteller_geoeffnet():
   if GPIO.input(I01) == GPIO.HIGH or GPIO.input(I03) == GPIO.HIGH:
      await Klappen_schliessen()
      print("Fehler: Tür wurde geöffnet und Klappen waren nicht zu.")

   # Audiofile: Funktion der Paketbox
   print("Türe Paketzusteller wurde geöffnet:")



# Async Main Loop
async def main():
   init()
   print("init abgeschlossen. Strg+C zum Beenden drücken.")
   try:
      while True:
         await asyncio.sleep(1)  # Main loop
         # Hier können weitere async Aufgaben hinzugefügt werden
   except KeyboardInterrupt:
      print("Beendet mit Strg+C")
   except Exception as e:
      print(f"Fehler: {e}")
   finally:
      GPIO.cleanup()
      print("GPIO aufgeräumt.")

if __name__ == "__main__":
   asyncio.run(main())

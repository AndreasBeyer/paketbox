
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
   GPIO.add_event_detect(I01, GPIO.RISING, callback=Klappe_links_geschlossen, bouncetime=200) # Klappe links geschlossen
   GPIO.add_event_detect(I02, GPIO.RISING, callback=Klappe_links_geoeffnet, bouncetime=200)
   GPIO.add_event_detect(I03, GPIO.RISING, callback=Klappe_rechts_geschlossen, bouncetime=200) # Klappe rechts geschlossen
   GPIO.add_event_detect(I04, GPIO.RISING, callback=Klappe_rechts_geoeffnet, bouncetime=200) # Klappe rechts geöffnet
   GPIO.add_event_detect(I05, GPIO.BOTH, callback=Paket_Tuer_Zusteller, bouncetime=200) # Paket Tür geöffnet o. geschlossen
   GPIO.add_event_detect(I06, GPIO.FALLING, callback=Briefkasten_geoeffnet, bouncetime=200) # Briefkasten Zusteller geoffnet
   GPIO.add_event_detect(I07, GPIO.FALLING, callback=Briefkasten_Tuer_Entnahme_geoeffnet, bouncetime=200) # Briefkasten Entnahme
   GPIO.add_event_detect(I08, GPIO.FALLING, callback=Paketbox_Tuer_Entnahme_geoeffnet, bouncetime=200) # Paketbox Entnahme
   GPIO.add_event_detect(I09, GPIO.RISING, callback=Taster_Tueroeffner_6_gedrueckt, bouncetime=200) # Tueroeffner 6
   GPIO.add_event_detect(I10, GPIO.RISING, callback=Taster_Tueroeffner_8_gedrueckt, bouncetime=200) # Tueroeffner 8
   GPIO.add_event_detect(I11, GPIO.RISING, callback=Bewegungsmelder_Einklemmschutz, bouncetime=200) # Bewegungsmelder Einklemmschutz

def setOutputWithRuntime(runtime, gpio, state):
    GPIO.output(gpio, state)
    gpio_delayed(runtime, gpio, ~state)

async def gpio_delayed(delay, gpio, state): # delay in Sekunden
   await asyncio.sleep(delay)
   GPIO.output(gpio,state)
   print("GPIO " + gpio + " geschalten zu " + satate)

def Klappe_links_geschlossen(channel):
   time.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Entleerungsklappe links ist geschlossen")
   # GPIO.output(Q1, GPIO.HIGH) # Antrieb aus Fahrtrichtung zu

def Klappe_links_geoeffnet(channel):
   time.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
     return
   print("Entleerungsklappe links ist geöffnet")
   # GPIO.output(Q2, GPIO.HIGH) # Antrieb aus Fahrtrichtung auf

def Klappe_rechts_geschlossen(channel):
   time.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Entleerungsklappe rechts ist geschlossen")
   # GPIO.output(Q3, GPIO.HIGH) # Antrieb aus Fahrtrichtung zu
   # GPIO.output(Q8, GPIO.HIGH) # Riegel öffnet Tür. Tür kann wieder geöffnet werden
 #  print("Tuer wird freigegeben")

def Klappe_rechts_geoeffnet(channel):
   time.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return # Entprellen
   print("Entleerungsklappe links ist geöffnet")
   # GPIO.output(Q4, GPIO.HIGH) # Antrieb aus Fahrtrichtung auf
 #  time.sleep(0.5)
   Klappen_schliessen()
 #  print("Klappe wird wieder geschlossen")


def Klappen_schliessen():
   print("Klappen fahren zu")
#   GPIO.output(Q1, GPIO.LOW) # fahre Linke Klappe zu
#   GPIO.output(Q3, GPIO.LOW) # fahre rechte Klappe zu

def Klappen_oeffnen():
   print("Klappen fahren auf")

#   setOutputWithRuntime(120, Q2, GPIO.LOW)
#   setOutputWithRuntime(120, Q4, GPIO.LOW)
#
#   GPIO.output(Q2, GPIO.LOW) # fahre Linke Klappe auf
#   GPIO.output(Q4, GPIO.LOW) # fahre rechte Klappe auf

def Paket_Tuer_Zusteller_geschlossen():
   print("Türe Paketzusteller wurde geschlossen.")
   # Audiofile: Die Box wird sich in 10 Sekunden verriegeln. Wenn noch neue Pakete abgegeben werden sollen Türe wieder öffnen.
   GPIO.output(Q8, GPIO.LOW) # Tür verriegelt
   print("Türe Paketzusteller wurde verriegelt.")
   time.sleep(10)
   GPIO.output(Q8, GPIO.HIGH)
   Klappen_oeffnen()
   # Audiofile: Box wird geleert, dies dauert 2 Minuten

def Paket_Tuer_Zusteller_geoeffnet():
   if GPIO.input(I01) == GPIO.HIGH or GPIO.input(I03) == GPIO.HIGH:
      Klappen_schliessen()
      print("Fehler: Tür wurde geöffnet und Klappen waren nicht zu.")

   # Audiofile: Funktion der Paketbox
   print("Türe Paketzusteller wurde geöffnet:")


def Paket_Tuer_Zusteller(channel):
   if GPIO.input(channel):
      time.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      Paket_Tuer_Zusteller_geoeffnet()
   else:
      time.sleep(0.2)
      if GPIO.input(channel) == GPIO.HIGH:
         return
      Paket_Tuer_Zusteller_geschlossen()

def Briefkasten_geoeffnet(channel):
   time.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Der Briefkasten wurde geöffnet")

def Paketbox_Tuer_Entnahme_geoeffnet(channel):
   time.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Die Tür zur Paketentnahme wurde geöffnet")

def Briefkasten_Tuer_Entnahme_geoeffnet(channel):
   time.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Die Türe zum Briefe entnehmen wurde geöffnet")

def Taster_Tueroeffner_6_gedrueckt(channel):
   time.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Der Taster an der Paketbox für Gartentürchen Nr. 6 wurde gedrückt")

def Taster_Tueroeffner_8_gedrueckt(channel):
   time.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Der Taster an der Paketbox für Gartentürchen Nr. 8 wurde gedrückt")

def Bewegungsmelder_Einklemmschutz(channel):
   time.sleep(0.2)
   if GPIO.input(channel) == GPIO.HIGH:
      return
   print("Der Bewegungsmelder hat eine Bewegung erkannt.")

#async def main():
#    def my_callback():
#        print(f"Callback executed at {time.strftime('%X')}")

#    print(f"Starting timer at {time.strftime('%X')}")
#    await async_timer(2, my_callback)  # Set a 2-second timer
#    print(f"Timer finished at {time.strftime('%X')}")

#if __name__ == "__main__":
#    asyncio.run(main())

# Main
init()
print("init abgeschlossen. Strg+C zum Beenden drücken.")
#setOutputWithRuntime(5,Q2, GPIO.LOW)


try:
    while True:
      time.sleep(1)  # Main loop
#       if laufzeitWaechter == true:
#
#         startZeit = gmtime()
#
#       if (startZeit + 120) <  gmtime():
#          print("laufzeitabgeschlossen")
#
#      if GPIO.input(I01) == GPIO.HIGH and GPIO.input(Q1) == GPIO.LOW: # Kleppe links ist zu und Antrieb fährt
#         GPIO.output(Q1, GPIO.HIGH)
#
#      if GPIO.input(I02) == GPIO.HIGH and GPIO.input(Q2) == GPIO.LOW: # Klappe links ist offen und Antrieb fährt
#         GPIO.output(Q2, GPIO.HIGH)
#
#      if GPIO.input(I03) == GPIO.HIGH and GPIO.input(Q3) == GPIO.LOW: # Klappe rechts ist zu und Antrieb fährt
#         GPIO.output(Q3, GPIO.HIGH)

#      if GPIO.input(I04) == GPIO.HIGH and GPIO.input(Q4) == GPIO.LOW: # Klappe rechts ist offen und Antrieb fährt
#         GPIO.output(Q4, GPIO.HIGH)
#
#      time.sleep(1) # Wartet 1 Sekunden
#      if GPIO.input(I1) == GPIO.HIGH: # Klappe rechts ist offen und Antrieb fährt
#         GPIO.output(Q1, GPIO.HIGH)
#         time.sleep(1) # Wartet 1 Sekunden
#      if GPIO.output(
#         GPIO.output(Q1, GPIO.LOW)




except KeyboardInterrupt:
    # Wenn das Programm mit Ctrl+C beendet wird, setzen Sie die Pins zurück
    GPIO.cleanup()

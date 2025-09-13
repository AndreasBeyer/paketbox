# Configuration constants

class Config:
    CLOSURE_TIMER_SECONDS = 65
    MOTOR_REVERSE_SIGNAL = CLOSURE_TIMER_SECONDS - 1
    DEBOUNCE_TIME = 0.2
    ERROR_REPORT_INTERVAL = 5.0
    
    # Pinbelegung der Relais
    #    BCM  Stiftpin
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

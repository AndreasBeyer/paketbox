# Configuration constants

class Config:
    CLOSURE_TIMER_SECONDS = 65
    MOTOR_REVERSE_SIGNAL = CLOSURE_TIMER_SECONDS - 1
    DEBOUNCE_TIME = 0.2
    ERROR_REPORT_INTERVAL = 5.0
   
    # GPIO pin assignments
    # Using BCM numbering
    inputs = [
            27,  # I01 Klappe links zu
            17,  # I02 Klappe links auf
            9,   # I03 Klappe rechts zu
            22,  # I04 Klappe rechts auf
            23,  # I05 Tür Riegelkontakt + Tür Magentkontakt
            24,  # I06 Briefkasten Magnetkontak
            25,  # I07 Briefkasten Türe zum leeren
            12,  # I08 Paketbox Tür zum leeren
            8,   # I09 Türöffner 6 Taster
            7,   # I10 Türffner 8 Taster
            11   # I11 Bewegungsmelder
        ]
    
    OUTPUTS = [
            5,   # Q1 Klappe links zu
            6,   # Q2 Klappe links auf
            13,  # Q3 Klappe rechts zu
            16,  # Q4 Klappe rechts auf
            14,  # Q5 
            20,  # Q6 Bremse für Tuer
            15,  # Q7 
            26   # Q8 Riegel Tür
        ]


    # 1-wire Temperatursensor
    # 1-wire    4  7

    # I2S Audiokarte
    # LRCLK    19 35
    # BITCLR   18 12
    # DATA OUT 21 40
    # DATA IN  20 38
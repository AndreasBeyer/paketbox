# Configuration constants

class Config:
    CLOSURE_TIMER_SECONDS = 65
    MOTOR_REVERSE_SIGNAL = CLOSURE_TIMER_SECONDS - 1
    DEBOUNCE_TIME = 0.2
    ERROR_REPORT_INTERVAL = 5.0

    MQTT_USER = "dein_benutzername"
    MQTT_PASS = "dein_passwort"
    MQTT_BROKER = "server_ip_or_hostname"
    MQTT_PORT = 1883
    MQTT_TOPIC_MESSAGE = "home/raspi/paketbox_text"
    MQTT_TOPIC_PAKETZUSTELLER = "paketbox/event/paketbox"
    MQTT_TOPIC_BRIEFKASTEN = "paketbox/event/briefkasten"
    MQTT_TOPIC_BRIEFKASTEN_ENTLEEREN = "paketbox/event/briefkastenleeren"
    MQTT_TOPIC_PAKETBOX_ENTLEEREN = "paketbox/event/paketboxleeren"
   
    # GPIO pin assignments
    # Using BCM numbering
    INPUTS = [
            27,  # 0 Klappe links zu
            17,  # 1 Klappe links auf
            9,   # 2 Klappe rechts zu
            22,  # 3 Klappe rechts auf
            23,  # 4 Tür Riegelkontakt + Tür Magentkontakt
            24,  # 5 Briefkasten Magnetkontak
            25,  # 6 Briefkasten Türe zum leeren
            12,  # 7 Paketbox Tür zum leeren
            8,   # 8 Türöffner 6 Taster
            7,   # 9 Türffner 8 Taster
            11   # 10 Bewegungsmelder
        ]
    
    OUTPUTS = [
            5,   # 0 Klappe links zu
            6,   # 1 Klappe links auf
            13,  # 2 Klappe rechts zu
            16,  # 3 Klappe rechts auf
            14,  # 4 
            20,  # 5 Licht Mülltonne
            15,  # 6 Licht Paketbox
            26   # 7 Riegel Tür
        ]


    # 1-wire Temperatursensor
    # 1-wire    4  7

    # I2S Audiokarte
    # LRCLK    19 35
    # BITCLR   18 12
    # DATA OUT 21 40
    # DATA IN  20 38
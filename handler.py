
from venv import logger

def pinChanged(pin, oldState, newState):
    if oldState == 0 and newState == 1: # rising edge  
        if pin == 4:
            logger.info(f"Paketklappe Zusteller geöffnet.") 
        elif pin == 5:
            logger.info(f"Briefkasten Zusteller geöffnet.")
        elif pin == 6:
            logger.info(f"Briefkasten Türe zum Leeren geöffnet.")
        elif pin == 7:
            logger.info(f"Paketbox Türe zum Leeren geöffnet.")

    elif oldState == 1 and newState == 0: # falling edge
        if pin == 0:
            logger.info(f"Packet Klappe links geschlossen/oben.")
        elif pin == 1:
            logger.info(f"Packet Klappe rechts geschlossen/oben.")
        elif pin == 2:
            logger.info(f"Packet Klappe links geöffnet/unten.")
        elif pin == 3:
            logger.info(f"Packet Klappe rechts geöffnet/unten.")
        elif pin == 4:
            logger.info(f"Paketklappe Zusteller geschlossen.") 
        elif pin == 5:
            logger.info(f"Briefkasten Zusteller geschlossen.")
        elif pin == 6:
            logger.info(f"Briefkasten Türe zum Leeren geschlossen.")
        elif pin == 7:
            logger.info(f"Paketbox Türe zum Leeren geschlossen.")
        elif pin == 8:
            logger.info(f"Türöffner Taster 6 gedrückt.")
        elif pin == 9:
            logger.info(f"Türöffner Taster 8 gedrückt.")
        elif pin == 10:
            logger.info(f"Bewegungsmelder hat ausgelöst.")
    else:
        logger.warning(f"pinChanged: oldState == newState keine Änderung erkannt.")


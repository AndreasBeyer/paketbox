# Global state module - single source of truth for pbox_state
from PaketBoxState import PaketBoxState

# Globale Instanz - wird nur einmal erstellt
pbox_state = PaketBoxState()
sendMqttErrorState = False  # To avoid repeated error messages
mqttObject = None  # Will hold the mqtt module reference
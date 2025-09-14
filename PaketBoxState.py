from enum import Enum, auto
import threading


class DoorState(Enum):
   CLOSED = auto()
   OPEN = auto()
   ERROR = auto()


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

   def is_open(self):
       with self._lock:
         return all([
            self.left_door == DoorState.OPEN,
            self.right_door == DoorState.OPEN
         ])

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
         return (f"Klappe links: {self.left_door.name}, Klappe rechts: {self.right_door.name}, "
               f"Pakettür: {self.paket_tuer.name}")
      

# Timer state management for active motor timers
import threading
import logging

logger = logging.getLogger(__name__)


class TimerManager:
    """Central timer management for motor operations"""
    def __init__(self):
        # Predefined timer categories
        self.active_timers = {
            'left_motor': None,
            'right_motor': None,
            'left_check': None,
            'right_check': None,
            'delayed_open': None,
            'door_open_watchdog': None  # 15-Minuten-Überwachung für geöffnete Paket-Tür
        }
        self._lock = threading.Lock()

    def add_timer(self, timer_id: str, timer):
        """Add or replace a timer in the manager"""
        with self._lock:
            # Cancel existing timer if present
            if timer_id in self.active_timers and self.active_timers[timer_id] is not None:
                self.active_timers[timer_id].cancel()
            # Add new timer (create key if doesn't exist)
            self.active_timers[timer_id] = timer

    def cancel_timer(self, timer_id: str):
        """Cancel a specific timer"""
        with self._lock:
            if timer_id in self.active_timers and self.active_timers[timer_id] is not None:
                self.active_timers[timer_id].cancel()
                self.active_timers[timer_id] = None

    def cancel_all_timers(self):
        """Cancel all active timers (emergency stop)"""
        with self._lock:
            cancelled_count = 0
            for timer_id, timer in self.active_timers.items():
                if timer is not None:
                    timer.cancel()
                    cancelled_count += 1
                    logger.info(f"Timer {timer_id} abgebrochen")
            # Reset all timer references
            self.active_timers = {key: None for key in self.active_timers.keys()}
            if cancelled_count > 0:
                logger.info(f"Insgesamt {cancelled_count} Timer abgebrochen")

    def clear_timer(self, timer_id: str):
        """Clear a timer reference (called when timer completes normally)"""
        with self._lock:
            if timer_id in self.active_timers:
                self.active_timers[timer_id] = None
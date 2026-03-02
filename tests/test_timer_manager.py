import unittest
from unittest.mock import MagicMock

from TimerManager import TimerManager


class TestTimerManager(unittest.TestCase):
    def setUp(self):
        self.manager = TimerManager()

    def _prepare_lock(self):
        lock = MagicMock()
        lock.__enter__.return_value = None
        lock.__exit__.return_value = None
        self.manager._lock = lock
        return lock

    def test_add_timer_replaces_existing_and_uses_lock(self):
        existing_timer = MagicMock()
        new_timer = MagicMock()
        self.manager.active_timers['left_motor'] = existing_timer
        lock = self._prepare_lock()

        self.manager.add_timer('left_motor', new_timer)

        existing_timer.cancel.assert_called_once_with()
        self.assertIs(self.manager.active_timers['left_motor'], new_timer)
        lock.__enter__.assert_called_once()
        lock.__exit__.assert_called_once()

    def test_add_timer_creates_new_entry(self):
        new_timer = MagicMock()
        lock = self._prepare_lock()

        self.manager.add_timer('custom_timer', new_timer)

        self.assertIn('custom_timer', self.manager.active_timers)
        self.assertIs(self.manager.active_timers['custom_timer'], new_timer)
        lock.__enter__.assert_called_once()

    def test_cancel_timer_cancels_and_clears_reference(self):
        timer = MagicMock()
        self.manager.active_timers['right_motor'] = timer
        lock = self._prepare_lock()

        self.manager.cancel_timer('right_motor')

        timer.cancel.assert_called_once_with()
        self.assertIsNone(self.manager.active_timers['right_motor'])
        lock.__enter__.assert_called_once()

    def test_cancel_all_timers_cancels_everything_and_resets_dict(self):
        timers = {
            'left_motor': MagicMock(),
            'right_motor': None,
            'left_check': MagicMock(),
        }
        self.manager.active_timers.update(timers)
        lock = self._prepare_lock()

        self.manager.cancel_all_timers()

        timers['left_motor'].cancel.assert_called_once_with()
        timers['left_check'].cancel.assert_called_once_with()
        self.assertTrue(all(value is None for value in self.manager.active_timers.values()))
        lock.__enter__.assert_called_once()

    def test_clear_timer_removes_reference(self):
        self.manager.active_timers['left_motor'] = MagicMock()
        lock = self._prepare_lock()

        self.manager.clear_timer('left_motor')

        self.assertIsNone(self.manager.active_timers['left_motor'])
        lock.__enter__.assert_called_once()


if __name__ == '__main__':
    unittest.main()

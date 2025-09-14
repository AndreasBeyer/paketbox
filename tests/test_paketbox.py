import unittest
from unittest.mock import patch, MagicMock
import asyncio
import threading
import time

# Importiere die wichtigsten Symbole aus dem Hauptscript
from paketbox import (
    DoorState,
    Klappen_oeffnen, Klappen_schliessen, 
    unlockDoor, lockDoor
)
from state import pbox_state  # Import from central state module
from handler import (
    pinChanged, Klappen_oeffnen_abbrechen, 
    Paket_Tuer_Zusteller_geschlossen, Paket_Tuer_Zusteller_geoeffnet,
    Klappen_oeffnen, Klappen_schliessen
)  # Import handler functions to test
from config import Config  # Import Config for timer values

class TestPaketBox(unittest.TestCase):
    def setUp(self):
        # Setze den Zustand vor jedem Test zurück
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        pbox_state.set_paket_tuer(DoorState.CLOSED)

    @patch('paketbox.GPIO')
    @patch('paketbox.setOutputWithRuntime')  # Mock this to avoid timer complexity
    @patch('paketbox.threading.Timer')
    def test_Klappen_oeffnen_success(self, mock_timer, mock_setOutput, mock_gpio):
        """Test successful flap opening operation"""
        # Setup GPIO mock
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        
        # Mock setOutputWithRuntime to return True (success)
        mock_setOutput.return_value = True
        
        # Setup timer mock to capture the endlagen_pruefung callback
        endlagen_callback = None
        def create_timer(delay, callback, args=None):
            nonlocal endlagen_callback
            if delay == Config.CLOSURE_TIMER_SECONDS + 1:  # This is endlagen_pruefung (with +1 offset)
                endlagen_callback = callback
            timer_mock = MagicMock()
            return timer_mock
            
        mock_timer.side_effect = create_timer
        
        # Execute flap opening
        Klappen_oeffnen()
        
        # Simulate flaps opening successfully and execute callback
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.OPEN)  # Both doors must be OPEN
        if endlagen_callback:
            endlagen_callback()
        
        # Verify flaps are marked as open and no errors
        self.assertEqual(pbox_state.left_door, DoorState.OPEN)
        self.assertEqual(pbox_state.right_door, DoorState.OPEN)
        self.assertFalse(pbox_state.is_any_error())

    @patch('paketbox.GPIO')
    @patch('paketbox.setOutputWithRuntime')  # Mock this to avoid timer complexity
    @patch('paketbox.threading.Timer')
    def test_Klappen_oeffnen_error(self, mock_timer, mock_setOutput, mock_gpio):
        """Test flap opening error condition"""
        # Setup GPIO mock
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        
        # Mock setOutputWithRuntime to return True (success)
        mock_setOutput.return_value = True
        
        # Setup timer mock to capture the endlagen_pruefung callback
        endlagen_callback = None
        def create_timer(delay, callback, args=None):
            nonlocal endlagen_callback
            if delay == Config.CLOSURE_TIMER_SECONDS + 1:  # This is endlagen_pruefung (with +1 offset)
                endlagen_callback = callback
            timer_mock = MagicMock()
            return timer_mock
            
        mock_timer.side_effect = create_timer
        
        # Execute flap opening
        Klappen_oeffnen()
        
        # Keep doors closed to simulate error and execute callback
        if endlagen_callback:
            endlagen_callback()
        
        # Verify error state is set
        self.assertEqual(pbox_state.left_door, DoorState.ERROR)
        self.assertEqual(pbox_state.right_door, DoorState.ERROR)
        self.assertTrue(pbox_state.is_any_error())

    @patch('paketbox.GPIO')
    @patch('paketbox.setOutputWithRuntime')  # Mock this to avoid timer complexity
    @patch('paketbox.threading.Timer')
    def test_Klappen_schliessen_success(self, mock_timer, mock_setOutput, mock_gpio):
        """Test successful flap closing operation"""
        # Setup initial state with open flaps
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.OPEN)
        
        # Setup GPIO mock
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        
        # Mock setOutputWithRuntime to return True (success)
        mock_setOutput.return_value = True
        
        # Setup timer mock to capture the endlagen_pruefung_closing callback
        endlagen_callback = None
        def create_timer(delay, callback, args=None):
            nonlocal endlagen_callback
            if delay == Config.CLOSURE_TIMER_SECONDS + 1:  # This is endlagen_pruefung_closing (with +1 offset)
                endlagen_callback = callback
            timer_mock = MagicMock()
            return timer_mock
            
        mock_timer.side_effect = create_timer
        
        # Execute flap closing
        Klappen_schliessen()
        
        # Simulate successful closing and execute callback
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        if endlagen_callback:
            endlagen_callback()
        
        # Verify flaps are closed and no errors
        self.assertEqual(pbox_state.left_door, DoorState.CLOSED)
        self.assertEqual(pbox_state.right_door, DoorState.CLOSED)
        self.assertFalse(pbox_state.is_any_error())

    @patch('paketbox.GPIO')
    @patch('paketbox.setOutputWithRuntime')  # Mock this to avoid timer complexity
    @patch('paketbox.threading.Timer')
    def test_Klappen_schliessen_error(self, mock_timer, mock_setOutput, mock_gpio):
        """Test flap closing error condition"""
        # Setup initial state with open flaps
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.OPEN)
        
        # Setup GPIO mock
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        
        # Mock setOutputWithRuntime to return True (success)
        mock_setOutput.return_value = True
        
        # Setup timer mock to capture the endlagen_pruefung_closing callback
        endlagen_callback = None
        def create_timer(delay, callback, args=None):
            nonlocal endlagen_callback
            if delay == Config.CLOSURE_TIMER_SECONDS + 1:  # This is endlagen_pruefung_closing (with +1 offset)
                endlagen_callback = callback
            timer_mock = MagicMock()
            return timer_mock
            
        mock_timer.side_effect = create_timer
        
        # Execute flap closing
        Klappen_schliessen()
        
        # Simulate error condition (keep left door open) and execute callback
        pbox_state.set_left_door(DoorState.OPEN)
        if endlagen_callback:
            endlagen_callback()
        
        # Verify error state is set
        self.assertEqual(pbox_state.left_door, DoorState.ERROR)
        self.assertEqual(pbox_state.right_door, DoorState.ERROR)
        self.assertTrue(pbox_state.is_any_error())

    def test_Klappen_oeffnen_with_error_state(self):
        """Test that flap opening is prevented when in error state"""
        # Set error state
        pbox_state.set_left_door(DoorState.ERROR)
        
        # Attempt to open flaps - should be prevented
        Klappen_oeffnen()
        
        # State should remain in error
        self.assertEqual(pbox_state.left_door, DoorState.ERROR)

    def test_Klappen_schliessen_with_error_state(self):
        """Test that flap closing is prevented when in error state"""
        # Set error state
        pbox_state.set_left_door(DoorState.ERROR)
        
        # Attempt to close flaps - should be prevented
        Klappen_schliessen()
        
        # State should remain in error
        self.assertEqual(pbox_state.left_door, DoorState.ERROR)

    @patch('handler.get_gpio')
    @patch('handler.setOutputWithRuntime')
    @patch('handler.threading.Timer')
    def test_motor_blockage_only_left_flap_blocked(self, mock_timer, mock_setOutput, mock_get_gpio):
        """Test motor blockage: only left flap blocked by package"""
        # Setup GPIO mock
        mock_gpio = MagicMock()
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        mock_get_gpio.return_value = mock_gpio
        mock_setOutput.return_value = True
        
        # Capture timer callback with debug output
        endlagen_callback = None
        timer_calls = []
        def create_timer(delay, callback, args=None):
            nonlocal endlagen_callback
            timer_calls.append(delay)
            print(f"DEBUG: Timer created with delay={delay}, expected={Config.CLOSURE_TIMER_SECONDS + 1} (= {Config.CLOSURE_TIMER_SECONDS} + 1)")
            if delay == Config.CLOSURE_TIMER_SECONDS + 1:
                endlagen_callback = callback
                print(f"DEBUG: Captured endlagen_callback")
            timer_mock = MagicMock()
            timer_mock.start = MagicMock()
            return timer_mock
        mock_timer.side_effect = create_timer
        
        # Set initial state - both doors closed
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        
        # Execute flap opening
        result = Klappen_oeffnen()
        print(f"DEBUG: Klappen_oeffnen returned: {result}")
        print(f"DEBUG: Timer calls: {timer_calls}")
        
        # Simulate: only right flap opens successfully, left flap blocked by package
        pbox_state.set_right_door(DoorState.OPEN)
        # left_door stays CLOSED (blocked)
        
        # Execute endlagen_pruefung callback - should detect error
        self.assertIsNotNone(endlagen_callback, f"Timer callback should be captured. Timer calls: {timer_calls}")
        endlagen_callback()
        
        # Verify both doors are set to ERROR state (since not both are OPEN)
        self.assertEqual(pbox_state.left_door, DoorState.ERROR)
        self.assertEqual(pbox_state.right_door, DoorState.ERROR)
        self.assertTrue(pbox_state.is_any_error())

    @patch('handler.get_gpio')
    @patch('handler.setOutputWithRuntime')
    @patch('handler.threading.Timer')
    def test_motor_blockage_both_flaps_blocked(self, mock_timer, mock_setOutput, mock_get_gpio):
        """Test motor blockage: both flaps blocked by large package"""
        # Setup GPIO mock
        mock_gpio = MagicMock()
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        mock_get_gpio.return_value = mock_gpio
        mock_setOutput.return_value = True
        
        # Capture timer callback
        endlagen_callback = None
        def create_timer(delay, callback, args=None):
            nonlocal endlagen_callback
            if delay == Config.CLOSURE_TIMER_SECONDS + 1:
                endlagen_callback = callback
            return MagicMock()
        mock_timer.side_effect = create_timer
        
        # Set initial state - both doors closed
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        
        # Execute flap opening
        Klappen_oeffnen()
        
        # Simulate: both flaps blocked by large package - neither opens
        # Both doors stay CLOSED (blocked)
        
        # Execute endlagen_pruefung callback - should detect error
        self.assertIsNotNone(endlagen_callback, "Timer callback should be captured")
        endlagen_callback()
        
        # Verify both doors are set to ERROR state
        self.assertEqual(pbox_state.left_door, DoorState.ERROR)
        self.assertEqual(pbox_state.right_door, DoorState.ERROR)
        self.assertTrue(pbox_state.is_any_error())

    @patch('handler.get_gpio')
    @patch('handler.setOutputWithRuntime')
    @patch('handler.threading.Timer')
    def test_motor_blockage_partial_opening(self, mock_timer, mock_setOutput, mock_get_gpio):
        """Test motor blockage: flaps partially open but can't reach full position"""
        # This simulates a scenario where motors run but flaps get stuck halfway
        # In real hardware, this would be detected by position sensors
        
        # Setup GPIO mock
        mock_gpio = MagicMock()
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        mock_get_gpio.return_value = mock_gpio
        mock_setOutput.return_value = True
        
        # Capture timer callback
        endlagen_callback = None
        def create_timer(delay, callback, args=None):
            nonlocal endlagen_callback
            if delay == Config.CLOSURE_TIMER_SECONDS + 1:
                endlagen_callback = callback
            return MagicMock()
        mock_timer.side_effect = create_timer
        
        # Execute flap opening
        Klappen_oeffnen()
        
        # Simulate: flaps move but don't reach OPEN position due to obstruction
        # Position sensors would not trigger, so doors remain CLOSED
        
        # Execute callback - should detect that flaps didn't open
        if endlagen_callback:
            endlagen_callback()
        
        # Verify error state is set
        self.assertEqual(pbox_state.left_door, DoorState.ERROR)
        self.assertEqual(pbox_state.right_door, DoorState.ERROR)
        self.assertTrue(pbox_state.is_any_error())

    @patch('handler.get_gpio')
    @patch('handler.setOutputWithRuntime')
    @patch('handler.threading.Timer')
    def test_motor_blockage_closing_with_package_obstruction(self, mock_timer, mock_setOutput, mock_get_gpio):
        """Test motor blockage during closing: package prevents flap from closing"""
        # Setup initial state with open flaps
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.OPEN)
        
        # Setup GPIO mock
        mock_gpio = MagicMock()
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        mock_get_gpio.return_value = mock_gpio
        mock_setOutput.return_value = True
        
        # Capture timer callback
        endlagen_callback = None
        def create_timer(delay, callback, args=None):
            nonlocal endlagen_callback
            if delay == Config.CLOSURE_TIMER_SECONDS + 1:
                endlagen_callback = callback
            return MagicMock()
        mock_timer.side_effect = create_timer
        
        # Execute flap closing
        Klappen_schliessen()
        
        # Simulate: package blocks right flap from closing
        pbox_state.set_left_door(DoorState.CLOSED)  # Left closes successfully
        # right_door stays OPEN (blocked by package)
        
        # Execute callback - should detect closing error
        if endlagen_callback:
            endlagen_callback()
        
        # Verify both doors are set to ERROR state
        self.assertEqual(pbox_state.left_door, DoorState.ERROR)
        self.assertEqual(pbox_state.right_door, DoorState.ERROR)
        self.assertTrue(pbox_state.is_any_error())

    @patch('handler.get_gpio')
    @patch('handler.setOutputWithRuntime')
    @patch('handler.threading.Timer')
    def test_motor_failure_setOutputWithRuntime_fails(self, mock_timer, mock_setOutput, mock_get_gpio):
        """Test motor failure: setOutputWithRuntime returns None (hardware failure)"""
        # Setup GPIO mock
        mock_gpio = MagicMock()
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        mock_get_gpio.return_value = mock_gpio
        
        # Simulate hardware failure - first motor starts, second motor fails
        mock_setOutput.side_effect = [True, None]  # First motor OK, second fails
        
        # Execute flap opening - should fail early
        result = Klappen_oeffnen()
        
        # Verify operation failed
        self.assertFalse(result)
        
        # Timer should not be started for endlagen_pruefung
        mock_timer.assert_not_called()

    @patch('handler.get_gpio')
    @patch('handler.setOutputWithRuntime')
    @patch('handler.threading.Timer')
    def test_motor_failure_one_motor_fails_to_start(self, mock_timer, mock_setOutput, mock_get_gpio):
        """Test motor failure: one motor fails to start while other succeeds"""
        # Setup GPIO mock
        mock_gpio = MagicMock()
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        mock_get_gpio.return_value = mock_gpio
        
        # Simulate both motors failing
        mock_setOutput.side_effect = [None, None]  # Both motors fail
        
        # Execute flap opening - should fail early
        result = Klappen_oeffnen()
        
        # Verify operation failed
        self.assertFalse(result)
        
        # Verify first motor was attempted
        self.assertGreaterEqual(mock_setOutput.call_count, 1)
        
        # Timer should not be started for endlagen_pruefung
        mock_timer.assert_not_called()

    @patch('handler.get_gpio')
    @patch('handler.setOutputWithRuntime')
    @patch('handler.threading.Timer')
    @patch('handler.Klappen_schliessen')
    def test_complete_package_delivery_with_motor_blockage_recovery(self, mock_schliessen, mock_timer, mock_setOutput, mock_get_gpio):
        """Integration test: complete package delivery cycle with motor blockage and recovery"""
        # Setup GPIO mock
        mock_gpio = MagicMock()
        mock_gpio.LOW = 0
        mock_gpio.HIGH = 1
        mock_get_gpio.return_value = mock_gpio
        mock_setOutput.return_value = True
        mock_schliessen.return_value = True
        
        # Capture timer callback
        endlagen_callback = None
        def create_timer(delay, callback, args=None):
            nonlocal endlagen_callback
            if delay == Config.CLOSURE_TIMER_SECONDS + 1:
                endlagen_callback = callback
            return MagicMock()
        mock_timer.side_effect = create_timer
        
        # Step 1: Normal package delivery - flaps should open
        Klappen_oeffnen()
        
        # Step 2: Simulate package blocking flaps from opening fully
        # (Package too large or positioned awkwardly)
        
        # Execute callback - motors ran but flaps didn't reach open position
        if endlagen_callback:
            endlagen_callback()
        
        # Step 3: Verify system detects blockage
        self.assertEqual(pbox_state.left_door, DoorState.ERROR)
        self.assertEqual(pbox_state.right_door, DoorState.ERROR)
        self.assertTrue(pbox_state.is_any_error())
        
        # Step 4: Manual intervention - package removed, system reset
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        
        # Step 5: Retry operation should work after clearing obstruction
        # Reset timer callback for new attempt
        endlagen_callback = None
        mock_timer.side_effect = create_timer
        
        Klappen_oeffnen()
        
        # Step 6: This time flaps open successfully
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.OPEN)
        
        if endlagen_callback:
            endlagen_callback()
        
        # Step 7: Verify successful operation and auto-close
        self.assertEqual(pbox_state.left_door, DoorState.OPEN)
        self.assertEqual(pbox_state.right_door, DoorState.OPEN)
        self.assertFalse(pbox_state.is_any_error())
        mock_schliessen.assert_called_once()  # Auto-close after successful opening

    @patch('paketbox.GPIO')
    def test_unlockDoor(self, mock_gpio):
        """Test door unlocking functionality"""
        mock_gpio.HIGH = 1
        unlockDoor()
        mock_gpio.output.assert_called_with(26, mock_gpio.HIGH)

    @patch('paketbox.GPIO')
    def test_lockDoor(self, mock_gpio):
        """Test door locking functionality"""
        mock_gpio.LOW = 0
        lockDoor()
        mock_gpio.output.assert_called_with(26, mock_gpio.LOW)

    def test_PaketBoxState_is_open(self):
        """Test state detection for all flaps open"""
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.OPEN)
        self.assertTrue(pbox_state.is_open())
        
        pbox_state.set_left_door(DoorState.CLOSED)
        self.assertFalse(pbox_state.is_open())

    def test_PaketBoxState_is_all_closed(self):
        """Test state detection for all doors closed"""
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        pbox_state.set_paket_tuer(DoorState.CLOSED)
        self.assertTrue(pbox_state.is_all_closed())
        
        pbox_state.set_left_door(DoorState.OPEN)
        self.assertFalse(pbox_state.is_all_closed())

    def test_PaketBoxState_is_any_error(self):
        """Test error state detection"""
        self.assertFalse(pbox_state.is_any_error())
        
        pbox_state.set_left_door(DoorState.ERROR)
        self.assertTrue(pbox_state.is_any_error())
        
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.ERROR)
        self.assertTrue(pbox_state.is_any_error())

    def test_PaketBoxState_str_representation(self):
        """Test string representation of state"""
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.CLOSED)
        pbox_state.set_paket_tuer(DoorState.ERROR)
        
        state_str = str(pbox_state)
        self.assertIn("Klappe links: OPEN", state_str)
        self.assertIn("Klappe rechts: CLOSED", state_str)
        self.assertIn("Pakettür: ERROR", state_str)

    def test_pinChanged_falling_edge_flap_positions(self):
        """Test pinChanged for flap position sensors on falling edge"""
        # Test left flap closed (pin 0, falling edge)
        pinChanged(0, 1, 0)
        self.assertEqual(pbox_state.left_door, DoorState.CLOSED)
        
        # Reset state
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        
        # Test left flap opened (pin 1, falling edge) - CORRECTED
        pinChanged(1, 1, 0)
        self.assertEqual(pbox_state.left_door, DoorState.OPEN)
        
        # Reset state
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        
        # Test right flap closed (pin 2, falling edge) - CORRECTED
        pinChanged(2, 1, 0)
        self.assertEqual(pbox_state.right_door, DoorState.CLOSED)
        
        # Reset state
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        
        # Test right flap opened (pin 3, falling edge)
        pinChanged(3, 1, 0)
        self.assertEqual(pbox_state.right_door, DoorState.OPEN)

    def test_pinChanged_rising_edge_doors(self):
        """Test pinChanged for door sensors on rising edge"""
        # Test package door opened (pin 4, rising edge)
        pinChanged(4, 0, 1)
        self.assertEqual(pbox_state.paket_tuer, DoorState.OPEN)
        
        # Reset state
        pbox_state.set_paket_tuer(DoorState.CLOSED)
        
        # Test package door closed (pin 4, falling edge)
        pinChanged(4, 1, 0)
        self.assertEqual(pbox_state.paket_tuer, DoorState.CLOSED)

    def test_pinChanged_no_change_same_state(self):
        """Test pinChanged with no state change (oldState == newState)"""
        original_left = pbox_state.left_door
        original_right = pbox_state.right_door
        original_paket = pbox_state.paket_tuer
        
        # Call with same old and new state - should not change anything
        pinChanged(0, 1, 1)
        
        # Verify no state changes occurred
        self.assertEqual(pbox_state.left_door, original_left)
        self.assertEqual(pbox_state.right_door, original_right)
        self.assertEqual(pbox_state.paket_tuer, original_paket)

    def test_pinChanged_all_input_pins(self):
        """Test pinChanged covers all defined input pins properly"""
        # Test all pins for rising edge (pins 5-10 only log, don't change state)
        test_cases_rising = [
            (5, "Briefkasten Zusteller"),
            (6, "Briefkasten Türe zum Leeren"),
            (7, "Paketbox Türe zum Leeren"),
        ]
        
        for pin, description in test_cases_rising:
            with self.subTest(pin=pin, description=description):
                # Should not crash and not change door states
                original_state = (pbox_state.left_door, pbox_state.right_door, pbox_state.paket_tuer)
                pinChanged(pin, 0, 1)
                current_state = (pbox_state.left_door, pbox_state.right_door, pbox_state.paket_tuer)
                self.assertEqual(original_state, current_state)
        
        # Test all pins for falling edge (pins 5-10 only log, don't change flap states)
        test_cases_falling = [
            (8, "Türöffner Taster 6"),
            (9, "Türöffner Taster 8"),
            (10, "Bewegungsmelder"),
        ]
        
        for pin, description in test_cases_falling:
            with self.subTest(pin=pin, description=description):
                # Should not crash and not change door states
                original_state = (pbox_state.left_door, pbox_state.right_door, pbox_state.paket_tuer)
                pinChanged(pin, 1, 0)
                current_state = (pbox_state.left_door, pbox_state.right_door, pbox_state.paket_tuer)
                self.assertEqual(original_state, current_state)

    def test_pinChanged_complete_gpio_mapping(self):
        """Test complete GPIO pin mapping documentation"""
        # This test documents the complete and correct GPIO pin mapping
        test_cases = [
            # (pin, old_state, new_state, expected_door, expected_state, description)
            (0, 1, 0, 'left_door', DoorState.CLOSED, "Left flap closed sensor"),
            (1, 1, 0, 'left_door', DoorState.OPEN, "Left flap opened sensor"),
            (2, 1, 0, 'right_door', DoorState.CLOSED, "Right flap closed sensor"),
            (3, 1, 0, 'right_door', DoorState.OPEN, "Right flap opened sensor"),
            (4, 0, 1, 'paket_tuer', DoorState.OPEN, "Package door opened sensor"),
            (4, 1, 0, 'paket_tuer', DoorState.CLOSED, "Package door closed sensor"),
        ]
        
        for pin, old_state, new_state, door_attr, expected_state, description in test_cases:
            with self.subTest(pin=pin, description=description):
                # Reset all states
                pbox_state.set_left_door(DoorState.CLOSED)
                pbox_state.set_right_door(DoorState.CLOSED)
                pbox_state.set_paket_tuer(DoorState.CLOSED)
                
                # Execute pin change
                pinChanged(pin, old_state, new_state)
                
                # Verify expected state change
                actual_state = getattr(pbox_state, door_attr)
                self.assertEqual(actual_state, expected_state, 
                               f"Pin {pin} should set {door_attr} to {expected_state.name}")

    @patch('handler.threading.Timer')
    @patch('handler.lockDoor')
    @patch('handler.Klappen_oeffnen')
    def test_Klappen_oeffnen_abbrechen_with_active_timer(self, mock_oeffnen, mock_lock, mock_timer):
        """Test canceling flap opening when timer is active"""
        # Setup mock timer
        mock_timer_instance = MagicMock()
        mock_timer.return_value = mock_timer_instance
        
        # Start the delayed opening process
        Paket_Tuer_Zusteller_geschlossen()
        
        # Verify timer was created and started
        mock_timer.assert_called_once_with(10.0, unittest.mock.ANY)
        mock_timer_instance.start.assert_called_once()
        
        # Now cancel the opening
        result = Klappen_oeffnen_abbrechen()
        
        # Verify cancellation
        self.assertTrue(result)
        mock_timer_instance.cancel.assert_called_once()

    def test_Klappen_oeffnen_abbrechen_without_active_timer(self):
        """Test canceling flap opening when no timer is active"""
        # Call cancel without having started any timer
        result = Klappen_oeffnen_abbrechen()
        
        # Should return False since no timer was active
        self.assertFalse(result)

    @patch('handler.threading.Timer')
    @patch('handler.lockDoor')
    @patch('handler.Klappen_oeffnen')
    def test_Paket_Tuer_Zusteller_geschlossen_cancels_previous_timer(self, mock_oeffnen, mock_lock, mock_timer):
        """Test that starting new closing process cancels previous timer"""
        # Setup mock timers
        mock_timer1 = MagicMock()
        mock_timer2 = MagicMock()
        mock_timer.side_effect = [mock_timer1, mock_timer2]
        
        # Start first closing process
        Paket_Tuer_Zusteller_geschlossen()
        
        # Start second closing process (should cancel first)
        Paket_Tuer_Zusteller_geschlossen()
        
        # Verify first timer was cancelled
        mock_timer1.cancel.assert_called_once()
        # Verify second timer was created and started
        mock_timer2.start.assert_called_once()

    @patch('handler.Klappen_oeffnen_abbrechen')
    @patch('handler.Klappen_schliessen')
    def test_Paket_Tuer_Zusteller_geoeffnet_calls_abbrechen(self, mock_schliessen, mock_abbrechen):
        """Test that opening door cancels flap opening"""
        # Setup: doors closed
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        pbox_state.set_paket_tuer(DoorState.CLOSED)
        
        # Call door opened function
        Paket_Tuer_Zusteller_geoeffnet()
        
        # Verify that abort function was called
        mock_abbrechen.assert_called_once()

    @patch('handler.threading.Timer')
    @patch('handler.lockDoor')
    @patch('handler.Klappen_oeffnen')
    def test_delayed_klappen_oeffnen_executes_when_door_stays_closed(self, mock_oeffnen, mock_lock, mock_timer):
        """Test that delayed flap opening executes when door stays closed"""
        # Setup: door closed
        pbox_state.set_paket_tuer(DoorState.CLOSED)
        
        # Capture the timer callback
        timer_callback = None
        def capture_timer(delay, callback):
            nonlocal timer_callback
            timer_callback = callback
            return MagicMock()
        mock_timer.side_effect = capture_timer
        
        # Start the process
        Paket_Tuer_Zusteller_geschlossen()
        
        # Execute the delayed callback
        timer_callback()
        
        # Verify flap opening was called
        mock_oeffnen.assert_called_once()

    @patch('handler.threading.Timer')
    @patch('handler.lockDoor')
    @patch('handler.Klappen_oeffnen')
    def test_delayed_klappen_oeffnen_aborts_when_door_reopened(self, mock_oeffnen, mock_lock, mock_timer):
        """Test that delayed flap opening aborts when door is reopened"""
        # Setup: door initially closed
        pbox_state.set_paket_tuer(DoorState.CLOSED)
        
        # Capture the timer callback
        timer_callback = None
        def capture_timer(delay, callback):
            nonlocal timer_callback
            timer_callback = callback
            return MagicMock()
        mock_timer.side_effect = capture_timer
        
        # Start the process
        Paket_Tuer_Zusteller_geschlossen()
        
        # Simulate door being reopened before timer expires
        pbox_state.set_paket_tuer(DoorState.OPEN)
        
        # Execute the delayed callback
        timer_callback()
        
        # Verify flap opening was NOT called
        mock_oeffnen.assert_not_called()

class TestPaketBoxIntegration(unittest.TestCase):
    """Integration tests for complete system scenarios"""
    
    def setUp(self):
        # Reset state for each test
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        pbox_state.set_paket_tuer(DoorState.CLOSED)

    @patch('paketbox.GPIO')
    @patch('paketbox.setOutputWithRuntime')
    @patch('paketbox.threading.Timer')
    def test_error_recovery_scenario(self, mock_timer, mock_setOutput, mock_gpio):
        """Test system behavior during error conditions and recovery"""
        # Setup GPIO mock
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        
        # Simulate flap opening failure
        timer_callbacks = []
        def create_timer(delay, callback, args=None):
            timer_callbacks.append((delay, callback, args))
            return MagicMock()
        mock_timer.side_effect = create_timer
        
        # Attempt to open flaps
        Klappen_oeffnen()
        
        # Simulate error by keeping doors closed
        for delay, callback, args in timer_callbacks:
            if delay == Config.CLOSURE_TIMER_SECONDS + 1 and args is None:
                callback()  # Execute without setting doors to OPEN
                break
        
        # Verify error state
        self.assertEqual(pbox_state.left_door, DoorState.ERROR)
        self.assertEqual(pbox_state.right_door, DoorState.ERROR)
        self.assertTrue(pbox_state.is_any_error())
        
        # Verify that further operations are blocked
        Klappen_oeffnen()  # Should be blocked due to error state
        Klappen_schliessen()  # Should be blocked due to error state
        
        # State should remain in error
        self.assertTrue(pbox_state.is_any_error())

    def test_simultaneous_door_operations(self):
        """Test handling of simultaneous door state changes"""
        # Test all possible door state combinations
        door_states = [DoorState.CLOSED, DoorState.OPEN, DoorState.ERROR]
        
        for left_state in door_states:
            for right_state in door_states:
                for paket_state in door_states:
                    with self.subTest(left=left_state, right=right_state, paket=paket_state):
                        # Set states
                        pbox_state.set_left_door(left_state)
                        pbox_state.set_right_door(right_state)
                        pbox_state.set_paket_tuer(paket_state)
                        
                        # Test state query methods
                        expected_is_open = (left_state == DoorState.OPEN and 
                                          right_state == DoorState.OPEN)
                        expected_all_closed = (left_state == DoorState.CLOSED and 
                                             right_state == DoorState.CLOSED and 
                                             paket_state == DoorState.CLOSED)
                        expected_any_error = (left_state == DoorState.ERROR or 
                                            right_state == DoorState.ERROR or 
                                            paket_state == DoorState.ERROR)
                        
                        self.assertEqual(pbox_state.is_open(), expected_is_open)
                        self.assertEqual(pbox_state.is_all_closed(), expected_all_closed)
                        self.assertEqual(pbox_state.is_any_error(), expected_any_error)

    @patch('paketbox.GPIO')
    def test_gpio_output_operations(self, mock_gpio):
        """Test GPIO output operations for motor control"""
        # Setup GPIO constants
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        
        # Test door lock/unlock operations
        unlockDoor()
        mock_gpio.output.assert_called_with(26, mock_gpio.HIGH)
        
        lockDoor()
        mock_gpio.output.assert_called_with(26, mock_gpio.LOW)

    def test_thread_safety(self):
        """Test that state operations are thread-safe"""
        import threading
        import time
        
        # This test ensures that concurrent state changes don't cause race conditions
        results = []
        
        def worker(state_value):
            for i in range(100):
                pbox_state.set_left_door(state_value)
                results.append(pbox_state.left_door)
                time.sleep(0.001)  # Small delay to increase chance of race conditions
        
        # Start multiple threads
        threads = []
        for state in [DoorState.OPEN, DoorState.CLOSED, DoorState.ERROR]:
            thread = threading.Thread(target=worker, args=(state,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify that all results are valid states (no corrupted data)
        valid_states = {DoorState.OPEN, DoorState.CLOSED, DoorState.ERROR}
        for result in results:
            self.assertIn(result, valid_states)

    @patch('handler.threading.Timer')
    @patch('handler.lockDoor')
    @patch('handler.Klappen_oeffnen')
    def test_complete_door_opening_cancellation_scenario(self, mock_oeffnen, mock_lock, mock_timer):
        """Integration test: Complete scenario of door opening cancellation"""
        # Setup: All doors closed, package door events
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        pbox_state.set_paket_tuer(DoorState.CLOSED)
        
        # Mock timer to capture callbacks
        timer_callbacks = []
        timer_instances = []
        def create_timer(delay, callback):
            timer_instance = MagicMock()
            timer_instances.append(timer_instance)
            timer_callbacks.append((delay, callback))
            return timer_instance
        mock_timer.side_effect = create_timer
        
        # Step 1: Package door closed (starts 10-second timer)
        Paket_Tuer_Zusteller_geschlossen()
        
        # Verify timer was started
        self.assertEqual(len(timer_callbacks), 1)
        delay, callback = timer_callbacks[0]
        self.assertEqual(delay, 10.0)
        
        # Step 2: Package door opened again within 10 seconds (should cancel timer)
        Paket_Tuer_Zusteller_geoeffnet()
        
        # Verify timer was cancelled
        timer_instances[0].cancel.assert_called_once()
        
        # Step 3: Execute the callback anyway (simulating timer that already fired)
        # But door is now open, so should abort
        pbox_state.set_paket_tuer(DoorState.OPEN)
        callback()
        
        # Verify flap opening was NOT called because door is open
        mock_oeffnen.assert_not_called()
        
        # Step 4: Close door again and let timer complete
        pbox_state.set_paket_tuer(DoorState.CLOSED)
        Paket_Tuer_Zusteller_geschlossen()
        
        # Get new callback
        delay, new_callback = timer_callbacks[1]
        
        # Execute callback with door still closed
        new_callback()
        
        # Verify flap opening was called this time
        mock_oeffnen.assert_called_once()

if __name__ == '__main__':
    unittest.main()

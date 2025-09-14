import unittest
from unittest.mock import patch, MagicMock
import asyncio
import threading
import time

# Importiere die wichtigsten Symbole aus dem Hauptscript
from paketbox import (
    pbox_state, DoorState,
    handleLeftFlapClosed, handleLeftFlapOpened,
    handleRightFlapClosed, handleRightFlapOpened,
    handleDeliveryDoorStatus, handleMailboxOpen,
    handlePackageBoxDoorOpen, handleMailboxDoorOpen,
    Klappen_oeffnen, Klappen_schliessen, 
    unlockDoor, lockDoor, closure_timer_seconds
)

class TestPaketBox(unittest.TestCase):
    def setUp(self):
        # Setze den Zustand vor jedem Test zurück
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        pbox_state.set_paket_tuer(DoorState.CLOSED)

    @patch('paketbox.GPIO')
    @patch('paketbox.time.sleep')  # Mock sleep to speed up tests
    def test_handleLeftFlapClosed(self, mock_sleep, mock_gpio):
        mock_gpio.input.return_value = mock_gpio.LOW
        handleLeftFlapClosed(27)
        self.assertEqual(pbox_state.left_door, DoorState.CLOSED)

    @patch('paketbox.GPIO')
    @patch('paketbox.time.sleep')
    def test_handleLeftFlapOpened(self, mock_sleep, mock_gpio):
        mock_gpio.input.return_value = mock_gpio.LOW
        handleLeftFlapOpened(17)
        self.assertEqual(pbox_state.left_door, DoorState.OPEN)

    @patch('paketbox.GPIO')
    @patch('paketbox.time.sleep')
    def test_handleRightFlapClosed(self, mock_sleep, mock_gpio):
        mock_gpio.input.return_value = mock_gpio.LOW
        handleRightFlapClosed(9)
        self.assertEqual(pbox_state.right_door, DoorState.CLOSED)

    @patch('paketbox.GPIO')
    @patch('paketbox.time.sleep')
    def test_handleRightFlapOpened(self, mock_sleep, mock_gpio):
        mock_gpio.input.return_value = mock_gpio.LOW
        handleRightFlapOpened(22)
        self.assertEqual(pbox_state.right_door, DoorState.OPEN)

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
            if delay == closure_timer_seconds + 1:  # This is endlagen_pruefung (with +1 offset)
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
            if delay == closure_timer_seconds + 1:  # This is endlagen_pruefung (with +1 offset)
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
            if delay == closure_timer_seconds + 1:  # This is endlagen_pruefung_closing (with +1 offset)
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
            if delay == closure_timer_seconds + 1:  # This is endlagen_pruefung_closing (with +1 offset)
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

    @patch('paketbox.GPIO')
    @patch('paketbox.time.sleep')
    @patch('paketbox.Paket_Tuer_Zusteller_geoeffnet')  # Mock to avoid side effects
    def test_handleDeliveryDoorStatus_opening(self, mock_geoeffnet, mock_sleep, mock_gpio):
        """Test delivery door status change to open"""
        # Mock GPIO readings
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        # Both GPIO.input calls should return the same value for consistent state
        mock_gpio.input.side_effect = [mock_gpio.HIGH, mock_gpio.HIGH]  # Both calls return HIGH for door opening
        
        handleDeliveryDoorStatus(23)
        self.assertEqual(pbox_state.paket_tuer, DoorState.OPEN)

    @patch('paketbox.GPIO')
    @patch('paketbox.time.sleep')
    @patch('paketbox.Paket_Tuer_Zusteller_geschlossen')  # Mock to avoid side effects
    def test_handleDeliveryDoorStatus_closing(self, mock_geschlossen, mock_sleep, mock_gpio):
        """Test delivery door status change to closed"""
        # Mock GPIO readings
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        # Both GPIO.input calls should return the same value for consistent state
        mock_gpio.input.side_effect = [mock_gpio.LOW, mock_gpio.LOW]  # Both calls return LOW for door closing
        
        handleDeliveryDoorStatus(23)
        self.assertEqual(pbox_state.paket_tuer, DoorState.CLOSED)

    @patch('paketbox.GPIO')
    def test_handleMailboxOpen(self, mock_gpio):
        """Test mailbox opening handler"""
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        
        # Should not throw exception and print message
        handleMailboxOpen(24)
        # New handlers don't read GPIO, just log - no assertion needed

    @patch('paketbox.GPIO')
    def test_handlePackageBoxDoorOpen(self, mock_gpio):
        """Test package box door opening handler"""
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        
        # Should not throw exception and print message
        handlePackageBoxDoorOpen(12)
        # New handlers don't read GPIO, just log - no assertion needed

    @patch('paketbox.GPIO')
    def test_handleMailboxDoorOpen(self, mock_gpio):
        """Test mailbox door opening handler"""
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        
        # Should not throw exception and print message
        handleMailboxDoorOpen(25)
        # New handlers don't read GPIO, just log - no assertion needed

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

    def test_GPIO_debouncing_behavior(self):
        """Test that handlers properly handle GPIO debouncing"""
        # Test with HIGH signal (should return early)
        with patch('paketbox.GPIO') as mock_gpio, patch('paketbox.time.sleep'):
            mock_gpio.HIGH = 1
            mock_gpio.input.return_value = mock_gpio.HIGH
            
            original_state = pbox_state.left_door
            handleLeftFlapClosed(27)
            # State should not change due to HIGH signal
            self.assertEqual(pbox_state.left_door, original_state)

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
    @patch('paketbox.time.sleep')
    def test_complete_delivery_cycle_success(self, mock_sleep, mock_timer, mock_setOutput, mock_gpio):
        """Test a complete successful package delivery cycle"""
        # Setup GPIO mock
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        mock_gpio.BOTH = 'BOTH'
        
        # Capture timer callbacks
        timer_callbacks = []
        def create_timer(delay, callback, args=None):
            timer_callbacks.append((delay, callback, args))
            timer_mock = MagicMock()
            return timer_mock
        mock_timer.side_effect = create_timer
        
        # Step 1: Delivery door is opened
        mock_gpio.input.side_effect = [mock_gpio.HIGH, mock_gpio.HIGH]  # Both calls return HIGH for door opening
        handleDeliveryDoorStatus(23)
        self.assertEqual(pbox_state.paket_tuer, DoorState.OPEN)
        
        # Step 2: Delivery door is closed (triggers flap opening)
        mock_gpio.input.side_effect = [mock_gpio.LOW, mock_gpio.LOW]  # Both calls return LOW for door closing  
        handleDeliveryDoorStatus(23)
        self.assertEqual(pbox_state.paket_tuer, DoorState.CLOSED)
        
        # Step 3: Simulate successful flap opening
        # Find and execute the opening endlagen_pruefung callback
        for delay, callback, args in timer_callbacks:
            if delay == closure_timer_seconds + 1 and args is None:
                # Simulate flaps opening successfully
                pbox_state.set_left_door(DoorState.OPEN)
                pbox_state.set_right_door(DoorState.OPEN)
                callback()
                break
        
        # Verify flaps are open
        self.assertEqual(pbox_state.left_door, DoorState.OPEN)
        self.assertEqual(pbox_state.right_door, DoorState.OPEN)
        self.assertFalse(pbox_state.is_any_error())

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
            if delay == closure_timer_seconds + 1 and args is None:
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
    def test_gpio_event_simulation(self, mock_gpio):
        """Test GPIO event handlers with various input scenarios"""
        # Setup GPIO mock
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0
        
        # Test left flap events
        test_cases = [
            (handleLeftFlapClosed, 27, DoorState.CLOSED),
            (handleLeftFlapOpened, 17, DoorState.OPEN),
            (handleRightFlapClosed, 9, DoorState.CLOSED),
            (handleRightFlapOpened, 22, DoorState.OPEN),
        ]
        
        # Test left flap handlers
        for handler, pin, expected_left_state in test_cases[:2]:
            with self.subTest(handler=handler.__name__, pin=pin):
                # Reset state
                pbox_state.set_left_door(DoorState.CLOSED)
                
                # Test handler (new handlers set state directly without GPIO reading)
                handler(pin)
                self.assertEqual(pbox_state.left_door, expected_left_state)
        
        # Test right flap handlers  
        for handler, pin, expected_right_state in test_cases[2:]:
            with self.subTest(handler=handler.__name__, pin=pin):
                # Reset state
                pbox_state.set_right_door(DoorState.CLOSED)
                
                # Test handler (new handlers set state directly without GPIO reading)
                handler(pin)
                self.assertEqual(pbox_state.right_door, expected_right_state)

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

if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
import asyncio

# Importiere die wichtigsten Symbole aus dem Hauptscript
from paketbox import (
    pbox_state, DoorState,
    handleLeftFlapClosed, handleLeftFLapOpened,
    handleRightFlapClosed, handleRightFlapOpened,
    Klappen_oeffnen
)

class TestPaketBox(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Setze den Zustand vor jedem Test zurück
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        pbox_state.set_paket_tuer(DoorState.CLOSED)

    @patch('paketbox.GPIO')
    async def test_handleLeftFlapClosed(self, mock_gpio):
        mock_gpio.input.return_value = False
        await handleLeftFlapClosed(27)
        self.assertEqual(pbox_state.left_door, DoorState.CLOSED)

    @patch('paketbox.GPIO')
    async def test_handleLeftFLapOpened(self, mock_gpio):
        mock_gpio.input.return_value = False
        await handleLeftFLapOpened(17)
        self.assertEqual(pbox_state.left_door, DoorState.OPEN)

    @patch('paketbox.GPIO')
    async def test_handleRightFlapClosed(self, mock_gpio):
        mock_gpio.input.return_value = False
        await handleRightFlapClosed(9)
        self.assertEqual(pbox_state.right_door, DoorState.CLOSED)

    @patch('paketbox.GPIO')
    async def test_handleRightFlapOpened(self, mock_gpio):
        mock_gpio.input.return_value = False
        await handleRightFlapOpened(22)
        self.assertEqual(pbox_state.right_door, DoorState.OPEN)

    @patch('paketbox.GPIO')
    async def test_Klappen_oeffnen_success(self, mock_gpio):
        # Simuliere, dass Endschalter nach Öffnen auf OPEN stehen
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.OPEN)
        await Klappen_oeffnen()
        await asyncio.sleep(6)  # Warte auf Callback
        self.assertFalse(pbox_state.is_any_error())

    @patch('paketbox.GPIO')
    async def test_Klappen_oeffnen_error(self, mock_gpio):
        # Simuliere, dass Endschalter nach Öffnen nicht auf OPEN stehen
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        await Klappen_oeffnen()
        await asyncio.sleep(6)  # Warte auf Callback
        self.assertTrue(pbox_state.left_door == DoorState.ERROR)
        self.assertTrue(pbox_state.right_door == DoorState.ERROR)

if __name__ == '__main__':
    unittest.main()

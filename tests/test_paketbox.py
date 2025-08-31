import unittest
from unittest.mock import patch, MagicMock
import asyncio

from paketbox import (
    pbox_state, DoorState,
    handleLeftFlapClosed, handleLeftFLapOpened,
    handleRightFlapClosed, handleRightFlapOpened,
    handleDeliveryDoorStatus,
    Klappen_oeffnen, Klappen_schliessen,
    unlockDoor, lockDoor, ResetDoors
)

class TestPaketBox(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
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
    async def test_handleDeliveryDoorStatus_open(self, mock_gpio):
        mock_gpio.input.return_value = False
        await handleDeliveryDoorStatus(23)
        self.assertEqual(pbox_state.paket_tuer, DoorState.OPEN)

    @patch('paketbox.GPIO')
    async def test_handleDeliveryDoorStatus_closed(self, mock_gpio):
        mock_gpio.input.return_value = True
        await handleDeliveryDoorStatus(23)
        self.assertEqual(pbox_state.paket_tuer, DoorState.CLOSED)

    @patch('paketbox.GPIO')
    async def test_Klappen_oeffnen_success(self, mock_gpio):
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.OPEN)
        await Klappen_oeffnen()
        await asyncio.sleep(2)
        self.assertFalse(pbox_state.is_any_error())

    @patch('paketbox.GPIO')
    async def test_Klappen_oeffnen_error(self, mock_gpio):
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        await Klappen_oeffnen()
        await asyncio.sleep(2)
        self.assertTrue(pbox_state.left_door == DoorState.ERROR)
        self.assertTrue(pbox_state.right_door == DoorState.ERROR)

    @patch('paketbox.GPIO')
    async def test_Klappen_schliessen_success(self, mock_gpio):
        pbox_state.set_left_door(DoorState.CLOSED)
        pbox_state.set_right_door(DoorState.CLOSED)
        await Klappen_schliessen()
        await asyncio.sleep(2)
        self.assertFalse(pbox_state.is_any_error())

    @patch('paketbox.GPIO')
    async def test_Klappen_schliessen_error(self, mock_gpio):
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.OPEN)
        await Klappen_schliessen()
        await asyncio.sleep(2)
        self.assertTrue(pbox_state.left_door == DoorState.ERROR)
        self.assertTrue(pbox_state.right_door == DoorState.ERROR)

    @patch('paketbox.GPIO')
    async def test_unlockDoor(self, mock_gpio):
        unlockDoor()
        mock_gpio.output.assert_called_with(26, mock_gpio.HIGH)

    @patch('paketbox.GPIO')
    async def test_lockDoor(self, mock_gpio):
        lockDoor()
        mock_gpio.output.assert_called_with(26, mock_gpio.LOW)

    @patch('paketbox.GPIO')
    async def test_ResetDoors(self, mock_gpio):
        pbox_state.set_left_door(DoorState.OPEN)
        pbox_state.set_right_door(DoorState.OPEN)
        ResetDoors()
        self.assertEqual(pbox_state.left_door, DoorState.CLOSED)
        self.assertEqual(pbox_state.right_door, DoorState.CLOSED)

if __name__ == '__main__':
    unittest.main()

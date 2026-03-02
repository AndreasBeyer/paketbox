import unittest
from unittest.mock import MagicMock, patch, call

import importlib

mqtt_module = importlib.import_module('mqtt')


class TestMQTT(unittest.TestCase):
    def setUp(self):
        self.original_topics = {
            'MQTT_USER': mqtt_module.config.MQTT_USER,
            'MQTT_PASS': mqtt_module.config.MQTT_PASS,
            'MQTT_BROKER': mqtt_module.config.MQTT_BROKER,
            'MQTT_PORT': mqtt_module.config.MQTT_PORT,
            'MQTT_TOPIC_MESSAGE': mqtt_module.config.MQTT_TOPIC_MESSAGE,
            'MQTT_TOPIC_PAKETZUSTELLER': mqtt_module.config.MQTT_TOPIC_PAKETZUSTELLER,
            'MQTT_TOPIC_BRIEFKASTEN': mqtt_module.config.MQTT_TOPIC_BRIEFKASTEN,
            'MQTT_TOPIC_BRIEFKASTEN_ENTLEEREN': mqtt_module.config.MQTT_TOPIC_BRIEFKASTEN_ENTLEEREN,
            'MQTT_TOPIC_PAKETBOX_ENTLEEREN': mqtt_module.config.MQTT_TOPIC_PAKETBOX_ENTLEEREN,
        }
        mqtt_module.config.MQTT_USER = 'user'
        mqtt_module.config.MQTT_PASS = 'pass'
        mqtt_module.config.MQTT_BROKER = 'broker'
        mqtt_module.config.MQTT_PORT = 1883
        mqtt_module.config.MQTT_TOPIC_MESSAGE = 'topic/message'
        mqtt_module.config.MQTT_TOPIC_PAKETZUSTELLER = 'topic/paket'
        mqtt_module.config.MQTT_TOPIC_BRIEFKASTEN = 'topic/brief'
        mqtt_module.config.MQTT_TOPIC_BRIEFKASTEN_ENTLEEREN = 'topic/brief_empty'
        mqtt_module.config.MQTT_TOPIC_PAKETBOX_ENTLEEREN = 'topic/paket_empty'
        self.original_client = mqtt_module._client
        self.original_available = mqtt_module.MQTT_AVAILABLE
        mqtt_module._client = None
        mqtt_module.MQTT_AVAILABLE = True

    def tearDown(self):
        for key, value in self.original_topics.items():
            setattr(mqtt_module.config, key, value)
        mqtt_module._client = self.original_client
        mqtt_module.MQTT_AVAILABLE = self.original_available

    @patch('mqtt.mqtt', new_callable=MagicMock)
    def test_start_mqtt_initializes_client(self, mock_mqtt_module):
        mock_client = MagicMock()
        mock_mqtt_module.Client.return_value = mock_client

        result = mqtt_module.start_mqtt()

        self.assertTrue(result)
        self.assertIs(mqtt_module._client, mock_client)
        mock_client.username_pw_set.assert_called_once_with('user', 'pass')
        mock_client.connect.assert_called_once_with('broker', 1883, 60)
        mock_client.loop_start.assert_called_once()
        self.assertIs(mock_client.on_connect, mqtt_module.mqtt_connect)
        self.assertIs(mock_client.on_disconnect, mqtt_module.mqtt_disconnect)
        self.assertIs(mock_client.on_message, mqtt_module.mqtt_message)

    def test_start_mqtt_returns_false_when_unavailable(self):
        mqtt_module.MQTT_AVAILABLE = False

        result = mqtt_module.start_mqtt()

        self.assertFalse(result)
        self.assertIsNone(mqtt_module._client)

    def test_stop_mqtt_stops_loop_and_disconnects(self):
        client = MagicMock()
        mqtt_module._client = client

        mqtt_module.stop_mqtt()

        client.loop_stop.assert_called_once_with()
        client.disconnect.assert_called_once_with()

    @patch('mqtt.time.sleep')
    def test_mqtt_disconnect_retries_with_backoff(self, mock_sleep):
        client = MagicMock()
        client.reconnect.side_effect = [Exception('fail1'), Exception('fail2'), None]

        mqtt_module.mqtt_disconnect(client, None, 0)

        self.assertEqual(client.reconnect.call_count, 3)
        mock_sleep.assert_has_calls([call(5), call(10), call(20)])

    @patch('mqtt.time.sleep')
    def test_mqtt_disconnect_returns_immediately_when_unavailable(self, mock_sleep):
        mqtt_module.MQTT_AVAILABLE = False
        client = MagicMock()

        mqtt_module.mqtt_disconnect(client, None, 0)

        mock_sleep.assert_not_called()
        client.reconnect.assert_not_called()

    def test_publish_helpers_use_correct_topics(self):
        client = MagicMock()
        mqtt_module._client = client
        publish_calls = [
            (mqtt_module.publish_status, 'MQTT_TOPIC_MESSAGE', 'status'),
            (mqtt_module.publish_paket_zusteller_event, 'MQTT_TOPIC_PAKETZUSTELLER', 'zusteller'),
            (mqtt_module.publish_briefkasten_event, 'MQTT_TOPIC_BRIEFKASTEN', 'brief'),
            (mqtt_module.publish_briefkasten_entleeren_event, 'MQTT_TOPIC_BRIEFKASTEN_ENTLEEREN', 'brief_empty'),
            (mqtt_module.publish_paketbox_entleeren_event, 'MQTT_TOPIC_PAKETBOX_ENTLEEREN', 'paket_empty'),
        ]

        for func, topic_attr, payload in publish_calls:
            with self.subTest(func=func.__name__):
                client.publish.reset_mock()
                result = func(payload)
                self.assertTrue(result)
                client.publish.assert_called_once_with(getattr(mqtt_module.config, topic_attr), payload)

    def test_publish_status_handles_missing_client_and_unavailable(self):
        mqtt_module._client = None
        result_no_client = mqtt_module.publish_status('status')
        self.assertFalse(result_no_client)

        mqtt_module.MQTT_AVAILABLE = False
        mqtt_module._client = MagicMock()
        result_unavailable = mqtt_module.publish_status('status')
        self.assertFalse(result_unavailable)
        mqtt_module._client.publish.assert_not_called()


if __name__ == '__main__':
    unittest.main()

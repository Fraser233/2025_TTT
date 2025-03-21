# Author: Fengze Yang, Email: fred.yang@utah.edu
# Date: 2025-03-21

import unittest
from unittest.mock import patch
from modules.communication import Communication


class TestCommunication(unittest.TestCase):
    
    def setUp(self):
        self.comm = Communication()
        self.sample_ego_data = {"location_x": 1.0, "location_y": 2.0}


    def test_format_broadcast_message(self):
        ranked_objects = [{"id":"OBJ1"}, {"id":"OBJ2"}]
        msg = self.comm.format_broadcast_message(ranked_objects)
        self.assertIn("alert_type", msg)
        self.assertIn("highest_risk_object", msg)
        self.assertEqual(msg["highest_risk_object"], {"id":"OBJ1"})
        self.assertEqual(msg["objects_in_scene"], 2)


    def test_format_personalized_message(self):
        ranked_objects = [{"id":"OBJ1"}, {"id":"OBJ2"}]
        msg = self.comm.format_personalized_message(self.sample_ego_data, ranked_objects)
        self.assertIn("ego_vehicle", msg)
        self.assertIn("threat_entities", msg)


    @patch("modules.communication.logger.info")
    @patch.object(Communication, "_get_microseconds", return_value=1234567890)
    def test_send_broadcast_message(self, mock_timestamp, mock_logger):
        msg = {"alert_type": "Test", "timestamp": None}
        self.comm.send_broadcast_message(msg)
        self.assertEqual(msg["timestamp"], 1234567890)
        mock_logger.assert_called_once()


    @patch("modules.communication.logger.info")
    @patch.object(Communication, "_get_microseconds", return_value=987654321)
    def test_send_personalized_message(self, mock_timestamp, mock_logger):
        msg = {"alert_type":"TestPersonalized", "timestamp":None}
        self.comm.send_personalized_message(self.sample_ego_data, msg)
        self.assertEqual(msg["timestamp"], 987654321)
        mock_logger.assert_called_once()


    def test_get_microseconds(self):
        ts = self.comm._get_microseconds()
        self.assertIsInstance(ts, int)
        # Not further tested because it depends on time.time() accuracy


if __name__ == '__main__':
    unittest.main()

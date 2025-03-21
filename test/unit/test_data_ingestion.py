# Author: Fengze Yang, Email: fred.yang@utah.edu
# Date: 2025-03-21

import unittest
from modules.data_ingestion import DataIngestion


class TestDataIngestion(unittest.TestCase):

    def setUp(self):
        """Initialize DataIngestion before each test."""
        self.ingestion = DataIngestion()


    def test_get_ego_data(self):
        """Test that get_ego_data returns a dictionary with expected keys."""
        ego_data = self.ingestion.get_ego_data()
        self.assertIsInstance(ego_data, dict)
        self.assertIn("location_x", ego_data)
        self.assertIn("location_y", ego_data)
        self.assertIn("speed_mps", ego_data)


    def test_get_lidar_data(self):
        """Test that get_lidar_data returns a list of object dicts."""
        lidar_data = self.ingestion.get_lidar_data()
        self.assertIsInstance(lidar_data, list)
        for obj in lidar_data:
            self.assertIsInstance(obj, dict)
            self.assertIn("id", obj)
            self.assertIn("type", obj)
            self.assertIn("position", obj)


if __name__ == '__main__':
    unittest.main()
    
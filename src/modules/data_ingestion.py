# Author: Fengze Yang, Email: fred.yang@utah.edu
# Date: 2025-03-21

"""
data_ingestion.py

Class for receiving ego vehicle data and fetching LiDAR detections.
Replace placeholder logic with your actual data interfaces.
"""

from typing import Dict, List, Any


class DataIngestion:

    def __init__(self):
        """
        Could initialize hardware drivers, network connections, etc.
        Placeholder for demonstration.
        """
        pass


    def get_ego_data(self) -> Dict[str, float]:
        """
        Retrieve ego vehicle data (location, speed, heading, etc.).
        Replace with real code for reading from CAN, V2X, or network sockets.
        """
        return {
            "location_x": 12.5,
            "location_y": 38.2,
            "speed_mps": 11.4,
            "heading_deg": 82.3,
            "acc_mps2": 0.0
        }


    def get_lidar_data(self) -> List[Dict[str, Any]]:
        """
        Fetch LiDAR object detections from an SDK, MQTT, or WebSocket subscription.
        Placeholder logic simulating two objects in the scene.
        """
        return [
            {
                "id": "OBJ456",
                "type": "PEDESTRIAN",
                "position": {"x": 13.1, "y": 38.5},
                "speed_mps": 1.2,
                "heading_deg": 270.0
            },
            {
                "id": "OBJ789",
                "type": "VEHICLE",
                "position": {"x": 11.8, "y": 37.9},
                "speed_mps": 9.0,
                "heading_deg": 85.0
            }
        ]
    
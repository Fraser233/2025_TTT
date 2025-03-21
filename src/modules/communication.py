# Author: Fengze Yang, Email: fred.yang@utah.edu
# Date: 2025-03-21

"""
Encapsulates message formatting (broadcast, personalized) and sending logic
into a Communication class.
"""

import json
from typing import List, Dict, Any
from utils.logger import logger


class Communication:

    def __init__(self):
        """
        Could initialize network sockets, MQTT clients, or DSRC/C-V2X stacks.
        """
        pass
    

    def format_broadcast_message(self, ranked_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates a general broadcast message for all road users.
        """
        msg = {
            "alert_type": "Intersection Hazard",
            "timestamp": None,  # Will populate on send
            "highest_risk_object": ranked_objects[0] if ranked_objects else None,
            "objects_in_scene": len(ranked_objects)
        }
        return msg
    

    def format_personalized_message(
        self,
        ego_data: Dict[str, float],
        ranked_objects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Creates a personalized message specifically for the ego vehicle.
        """
        msg = {
            "alert_type": "Collision Risk",
            "timestamp": None,  # Will populate on send
            "ego_vehicle": {
                "location": {
                    "x": ego_data.get("location_x", 0.0),
                    "y": ego_data.get("location_y", 0.0)
                },
                "speed_mps": ego_data.get("speed_mps", 0.0),
                "heading_deg": ego_data.get("heading_deg", 0.0)
            },
            "threat_entities": ranked_objects,
            "recommended_action": "Prepare to stop; high collision risk."
        }
        return msg
    

    def send_broadcast_message(self, msg: Dict[str, Any]) -> None:
        """
        In a real system, this might publish to an MQTT topic or DSRC broadcast.
        """
        msg["timestamp"] = self._get_microseconds()
        logger.info("[Broadcast] --> " + json.dumps(msg, indent=2))


    def send_personalized_message(self, ego_data: Dict[str, Any], msg: Dict[str, Any]) -> None:
        """
        In a real system, you might do a point-to-point V2X or socket message to the vehicle.
        """
        msg["timestamp"] = self._get_microseconds()
        logger.info(
            f"[Personalized to Vehicle at ({ego_data['location_x']}, {ego_data['location_y']})] --> "
            + json.dumps(msg, indent=2)
        )
        

    def _get_microseconds(self) -> int:
        """
        Returns a current timestamp in microseconds for consistency.
        """
        import time
        return int(time.time() * 1e6)
    
# Author: Fengze Yang, Email: fred.yang@utah.edu
# Date: 2025-03-21

"""
main.py

This file orchestrates the entire SHIELD-RSU system. The steps are:
1) Ego vehicle & LiDAR data ingestion
2) End-to-end LLM analysis (trajectory, collision risk, severity ranking)
3) Message formatting & sending
"""

import time
from utils.logger import logger

from modules.data_ingestion import DataIngestion
from modules.llm_inference import LLMInference
from modules.communication import Communication


class SHIELDRSUSystem:

    def __init__(self):
        """
        Initialize the subsystem classes. In a real deployment on Jetson Orin Nano,
        you might also handle GPU initialization or other system setup here.
        """
        logger.info("Initializing SHIELD-RSU system...")

        self.data_ingestion = DataIngestion()
        self.llm_inference = LLMInference()
        self.communication = Communication()


    def run_cycle(self):
        """
        One iteration of the pipeline:
        1) Ingest data
        2) Run LLM end-to-end analysis
        3) Send broadcast & personalized messages
        """
        # 1) Data Ingestion
        ego_data = self.data_ingestion.get_ego_data()
        lidar_objects = self.data_ingestion.get_lidar_data()

        # 2) LLM End-to-end analysis
        llm_results = self.llm_inference.end_to_end_analysis(
            ego_data=ego_data,
            lidar_objects=lidar_objects
        )
        ranked_objects = llm_results.get("ranked_objects", [])

        # 3) Communication
        broadcast_msg = self.communication.format_broadcast_message(ranked_objects)
        self.communication.send_broadcast_message(broadcast_msg)

        personalized_msg = self.communication.format_personalized_message(ego_data, ranked_objects)
        self.communication.send_personalized_message(ego_data, personalized_msg)


    def main_loop(self):
        """
        Main loop to continuously run cycles at ~10Hz or the desired frequency.
        """
        while True:
            start = time.time()
            try:
                self.run_cycle()
            except Exception as e:
                logger.error(f"Error in run_cycle: {e}")

            elapsed = time.time() - start
            time.sleep(max(0.0, 0.1 - elapsed))  # ~10Hz


def main():
    shield_rsu = SHIELDRSUSystem()
    shield_rsu.main_loop()


if __name__ == "__main__":
    main()

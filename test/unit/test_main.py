# Author: Fengze Yang, Email: fred.yang@utah.edu
# Date: 2025-03-21

import unittest
from unittest.mock import patch, MagicMock
from main import SHIELDRSUSystem


class TestMain(unittest.TestCase):

    @patch("main.DataIngestion")
    @patch("main.LLMInference")
    @patch("main.Communication")
    def test_run_cycle(self, mock_comm, mock_llm, mock_ingestion):
        """
        Test run_cycle calls the expected methods 
        from DataIngestion, LLMInference, and Communication.
        """
        system = SHIELDRSUSystem()

        # Mock return values
        mock_ingest_instance = mock_ingestion.return_value
        mock_ingest_instance.get_ego_data.return_value = {"location_x":0.0,"location_y":0.0}
        mock_ingest_instance.get_lidar_data.return_value = [{"id":"OBJ1"}]

        mock_llm_instance = mock_llm.return_value
        mock_llm_instance.end_to_end_analysis.return_value = {"ranked_objects":[{"id":"DANGER"}]}

        system.run_cycle()

        mock_ingest_instance.get_ego_data.assert_called_once()
        mock_ingest_instance.get_lidar_data.assert_called_once()
        mock_llm_instance.end_to_end_analysis.assert_called_once()

        # Communication checks
        mock_comm_instance = mock_comm.return_value
        mock_comm_instance.format_broadcast_message.assert_called_once()
        mock_comm_instance.send_broadcast_message.assert_called_once()
        mock_comm_instance.format_personalized_message.assert_called_once()
        mock_comm_instance.send_personalized_message.assert_called_once()


    def test_main_loop(self):
        """
        This is more of an integration test. 
        Typically you'd test main_loop with a mocking approach or a minimal times run.
        """
        pass
    

if __name__ == '__main__':
    unittest.main()
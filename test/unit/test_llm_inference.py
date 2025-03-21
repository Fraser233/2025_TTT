# Author: Fengze Yang, Email: fred.yang@utah.edu
# Date: 2025-03-21

import unittest
from unittest.mock import patch, MagicMock
from modules.llm_inference import LLMInference


class TestLLMInference(unittest.TestCase):
    def setUp(self):
        """Initialize LLMInference before each test."""
        self.inference = LLMInference()
        self.sample_ego_data = {
            "location_x": 0.0,
            "location_y": 0.0,
            "speed_mps": 10.0,
            "heading_deg": 90.0
        }
        self.sample_lidar_objects = [
            {
                "id": "OBJ123",
                "type": "VEHICLE",
                "position": {"x": 5.0, "y": 5.0},
                "speed_mps": 2.0,
                "heading_deg": 0.0
            }
        ]


    @patch("modules.llminference.Path.read_text", return_value="Mock Prompt")
    @patch("modules.llminference.AutoTokenizer")
    @patch("modules.llminference.AutoModelForCausalLM")
    def test_init(self, mock_model, mock_tokenizer, mock_read_text):
        """Test initialization loads the model and prompt correctly."""
        inf = LLMInference()
        self.assertEqual(inf.prompt_template, "Mock Prompt")
        mock_tokenizer.from_pretrained.assert_called_once()
        mock_model.from_pretrained.assert_called_once()


    @patch.object(LLMInference, "_call_llm", return_value='{"dangerous_objects":[{"id":"OBJ123"}]}')
    def test_end_to_end_analysis(self, mock_call_llm):
        """
        Test that end_to_end_analysis returns the structure we expect 
        after post-process is called.
        """
        result = self.inference.end_to_end_analysis(
            self.sample_ego_data,
            self.sample_lidar_objects
        )
        self.assertIsInstance(result, dict)
        self.assertIn("ranked_objects", result)
        self.assertEqual(result["ranked_objects"], [{"id": "OBJ123"}])


    def test_format_prompt(self):
        """Test that _format_prompt returns a string containing EGO and object data."""
        prompt = self.inference._format_prompt(self.sample_ego_data, self.sample_lidar_objects)
        self.assertIn("EGO Vehicle Data", prompt)
        self.assertIn("Detected Objects", prompt)
        self.assertIn('"location_x": 0.0', prompt)


    @patch("modules.llminference.json.loads", return_value={"dangerous_objects":[{"id":"OBJXYZ"}]})
    def test_parse_llm_output(self, mock_json_loads):
        """Test that _parse_llm_output extracts JSON from the raw output."""
        output = self.inference._parse_llm_output('{"dangerous_objects":[{"id":"OBJXYZ"}]}')
        self.assertIn("dangerous_objects", output)
        self.assertEqual(output["dangerous_objects"][0]["id"], "OBJXYZ")


    def test_parse_llm_output_invalid_json(self):
        """Test that parse handles invalid JSON gracefully."""
        output = self.inference._parse_llm_output("INVALID JSON")
        self.assertIn("dangerous_objects", output)
        self.assertEqual(len(output["dangerous_objects"]), 0)


    def test_post_process(self):
        """Test final dictionary from _post_process includes only dangerous objects."""
        llm_parsed = {"dangerous_objects":[{"id":"OBJ999","risk_score":0.95}]}
        result = self.inference._post_process(self.sample_ego_data, self.sample_lidar_objects, llm_parsed)
        self.assertIn("ranked_objects", result)
        self.assertEqual(len(result["ranked_objects"]), 1)
        self.assertEqual(result["ranked_objects"][0]["id"], "OBJ999")


if __name__ == '__main__':
    unittest.main()
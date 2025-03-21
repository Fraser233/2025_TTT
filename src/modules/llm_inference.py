# Author: Fengze Yang, Email: fred.yang@utah.edu
# Date: 2025-03-21

"""
llminference.py

Encapsulates an LLMInference class that performs:
- Prompt reading (with chain-of-thought)
- Single end-to-end LLM call
- Parsing and post-processing results
"""

import math
import time
import json
from pathlib import Path
from typing import Dict, Any, List

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM  # Example HF usage


class LLMInference:

    def __init__(self):
        """
        Load the Qwen Qwen2.5-14B-Instruct model from Hugging Face 
        and read the chain-of-thought prompt from property/prompt.txt.
        """
        self.model_name = "Qwen/Qwen2.5-14B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.model.eval()

        # Load the chain-of-thought prompt template from file
        prompt_file = Path("properties/prompt.txt")
        self.prompt_template = prompt_file.read_text(encoding="utf-8")


    def end_to_end_analysis(self,
                            ego_data: Dict[str, float],
                            lidar_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        1) Format the prompt
        2) Call the LLM
        3) Parse JSON
        4) Post-process -> Return only dangerous objects
        """
        prompt = self._format_prompt(ego_data, lidar_objects)
        llm_raw_output = self._call_llm(prompt)
        llm_parsed_output = self._parse_llm_output(llm_raw_output)
        result = self._post_process(ego_data, lidar_objects, llm_parsed_output)
        return result


    def _format_prompt(self,
                       ego_data: Dict[str, float],
                       lidar_objects: List[Dict[str, Any]]) -> str:
        """
        Insert the EGO data and LiDAR objects into the chain-of-thought prompt template.
        """
        prompt = (
            self.prompt_template
            + "\n\nEGO Vehicle Data:\n"
            + json.dumps(ego_data, indent=2)
            + "\n\nDetected Objects:\n"
            + json.dumps(lidar_objects, indent=2)
        )
        return prompt


    def _call_llm(self, prompt: str) -> str:
        """
        Use the loaded HF model to generate text from the prompt.
        This is a synchronous example - consider your performance constraints.
        """
        # Encode input
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_length=1024,
                do_sample=False,  # or True if you want sampling
            )
        output_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return output_text
    

    def _parse_llm_output(self, llm_raw_output: str) -> Dict[str, Any]:
        """
        Convert the LLM's raw text into a Python dict.
        Expected to be valid JSON with a 'dangerous_objects' key.
        """
        # Find JSON substring or assume the entire output is JSON
        try:
            # A naive approach: we assume the LLM output is fully JSON
            parsed = json.loads(llm_raw_output)
        except json.JSONDecodeError:
            parsed = {"dangerous_objects": []}
        return parsed
    

    def _post_process(self,
                      ego_data: Dict[str, float],
                      lidar_objects: List[Dict[str, Any]],
                      llm_parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        The final output should be a dict containing only the 'dangerous_objects' 
        from the LLM output.
        """
        dangerous_objs = llm_parsed.get("dangerous_objects", [])
        return {
            "ranked_objects": dangerous_objs,  # For consistency with the system
            "analysis_timestamp": int(time.time() * 1e6)
        }

#!/usr/bin/env python
# Author: Fengze Yang <fred.yang@utah.edu>
# Date: 2025-03-30

from typing import Any, Dict
from lidar_buffer import LidarBuffer

# Define VRU classifications
VRU_CLASSIFICATIONS = {"PERSON", "BICYCLE"}

class VruDetector:
    """
    Helper class to detect VRU presence in incoming LiDAR data.

    When a VRU is detected, data collection starts immediately.
    If no VRU is detected for a specified number of consecutive frames,
    the detector finalizes the current session by calling LidarBuffer.stop_recording()
    and resets its state.
    """
    def __init__(self, lidar_buffer: LidarBuffer, no_vru_threshold: int):
        self.lidar_buffer = lidar_buffer
        self.no_vru_threshold = no_vru_threshold
        self.consecutive_no_vru_count = 0
        self.vru_started = False
        self.current_video_path = None  # Track the current video path


    def handle_frame(self, data: Dict[str, Any]) -> bool:
        """
        Process a single frame's data.

        Returns:
            True if no VRU is detected for no_vru_threshold consecutive frames
            after data collection has started (i.e. session ends);
            False to continue processing frames.
        """
        vru_found = False

        if "object_list" in data:
            for frame_obj in data["object_list"]:
                if "objects" not in frame_obj:
                    continue
                for obj in frame_obj["objects"]:
                    classification = obj.get("classification", "")
                    if classification in VRU_CLASSIFICATIONS:
                        vru_found = True
                        print(f"VRU detected: {classification}, frame_count: {frame_obj.get('frame_count')}")
                        break
                if vru_found:
                    break

        if vru_found:
            if not self.vru_started:
                # Start data collection immediately upon detecting a VRU.
                self.vru_started = True
                print("Data collection started upon VRU detection.")
                
                # Start screen recording first and get the video path
                self.current_video_path = self.lidar_buffer.start_screen_recording()
                print(f"Started recording to: {self.current_video_path}")

            # Add the current frame data and reset the no-VRU counter.
            # Save the potentially new video path if returned
            new_path = self.lidar_buffer.add_data(data, self.current_video_path)
            if new_path and new_path != self.current_video_path:
                print(f"Recording path updated from {self.current_video_path} to {new_path}")
                self.current_video_path = new_path
                
            self.consecutive_no_vru_count = 0
        else:
            if self.vru_started:
                # Still need to add data even if no VRU is found to maintain continuity
                new_path = self.lidar_buffer.add_data(data, self.current_video_path)
                
                if new_path and new_path != self.current_video_path:
                    print(f"Recording path updated from {self.current_video_path} to {new_path}")
                    self.current_video_path = new_path
                
                self.consecutive_no_vru_count += 1

                if self.consecutive_no_vru_count >= self.no_vru_threshold:
                    print(f"No VRU detected for {self.no_vru_threshold} consecutive frames. Finalizing session...")
                    # Pass the current video path to stop_recording
                    self.lidar_buffer.stop_recording(self.current_video_path)

                    # Reset state to allow a new session.
                    self.vru_started = False
                    self.consecutive_no_vru_count = 0
                    self.current_video_path = None

                    return True  # Signal that the current session is complete

        return False  # Continue processing frames
#!/usr/bin/env python
# Author: Fengze Yang <fred.yang@utah.edu>
# Date: 2025-03-31

import json
import os
import time
import subprocess
import threading
import copy
import uuid
from typing import Any, Dict, Tuple


class LidarBuffer:

    def __init__(self,
                 max_frames: int,
                 min_video_duration: int,
                 capture_area: Tuple[int, int, int, int] = (1920, 1080, 0, 0),
                 session_counters: Dict[str, int] = None):
        """
        Initialize LidarBuffer with an optional capture area and max frames setting.
        
        Args:
            max_frames: Maximum number of frames to accumulate before saving a batch.
            min_video_duration: Minimum required video duration in seconds.
            capture_area: A tuple (width, height, offset_x, offset_y) defining
              the region of the screen to record. Defaults to 1920x1080 starting
              at (0, 0).
            session_counters: Dictionary with session counting stats, should have
              'total_sessions', 'valid_sessions', and 'current_session_valid' keys.
        """
        self.capture_area = capture_area  # (width, height, offset_x, offset_y)
        self.raw_data = []  # List to accumulate raw frames from incoming JSON data
        self.recording_active = False
        self.recording_process = None
        self.max_frames = max_frames  # Maximum number of frames before saving batch
        self.min_video_duration = min_video_duration  # Minimum video duration in seconds
        
        # Session tracking - using externally provided counters if available
        self.session_counters = session_counters or {
            'total_sessions': 0,
            'valid_sessions': 0,
            'current_session_valid': False
        }
        
        # Create necessary directories
        self._create_directories()
        
    def _create_directories(self):
        """Create all necessary directories for data storage."""
        os.makedirs(os.path.join("data", "videos"), exist_ok=True)
        os.makedirs(os.path.join("data", "invalid_videos"), exist_ok=True)
        os.makedirs(os.path.join("data", "object_lists"), exist_ok=True)
        os.makedirs(os.path.join("data", "invalid_objects"), exist_ok=True)
        

    def _generate_temp_video_path(self):
        """
        Generates a unique temporary video path for each recording session.
        
        Return:
            Path to a unique temporary video file
        """
        videos_dir = os.path.join("data", "videos")
        os.makedirs(videos_dir, exist_ok=True)
        
        # Generate unique identifier
        unique_id = str(uuid.uuid4())[:8]
        timestamp = int(time.time())
        
        # Create a unique filename
        temp_filename = f"temp_{timestamp}_{unique_id}.mp4"
        return os.path.join(videos_dir, temp_filename)


    def start_screen_recording(self):
        """
        Starts screen recording using ffmpeg on screen 1.
        Generates a unique temporary video path for each recording session.
        
        Return:
            Path to the temporary video file or None if recording fails
        """
        if not self.recording_active:
            print("Starting screen recording.")
            
            # Generate a new temporary video path
            temp_video_path = self._generate_temp_video_path()
            print(f"Recording to temporary file: {temp_video_path}")

            width, height, offset_x, offset_y = self.capture_area

            # Use screen 1: note the input string is ":1.0+{offset_x},{offset_y}"
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-video_size", f"{width}x{height}", "-framerate", "30",
                "-f", "x11grab", "-i", f":1.0+{offset_x},{offset_y}", temp_video_path
            ]
            try:
                self.recording_process = subprocess.Popen(
                    ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                self.recording_active = True
                print("Screen recording started.")
                
                # Reset session validity for the new recording
                self.session_counters['current_session_valid'] = False
                
                return temp_video_path
            except Exception as e:
                print(f"Failed to start screen recording: {e}")
                return None
        else:
            print("Screen recording is already active.")
            return None


    def stop_screen_recording(self):
        """
        Stops the screen recording by terminating the ffmpeg process.
        """
        if self.recording_active and self.recording_process:
            print("Stopping screen recording.")
            try:
                self.recording_process.terminate()
                self.recording_process.wait(timeout=5)
                print("Screen recording stopped.")
            except Exception as e:
                print(f"Error stopping screen recording: {e}")
            finally:
                self.recording_active = False
                self.recording_process = None
        else:
            print("No active screen recording to stop.")


    def add_data(self, incoming_data: Dict[str, Any], video_path: str = None):
        """
        Accumulates raw JSON data.
        The incoming data is expected to have a structure like:
            {
                "object_list": [
                    {
                        "frame_count": <int>,
                        "objects": [ {...}, {...}, ... ]
                    },
                    ...
                ]
            }
        After adding, if more than max_frames are accumulated, the current batch is saved
        in the background and a new recording is started immediately.
        
        Args:
            incoming_data: JSON data to add to the buffer
            video_path: Current video path associated with this data
            
        Returns:
            The current video path or a new video path if recording was restarted
        """
        if "object_list" not in incoming_data:
            return video_path
        
        self.raw_data.extend(incoming_data["object_list"])
        print(f"Accumulated frames: {len(self.raw_data)}")

        # If more than max_frames frames have been accumulated, save the current batch.
        if len(self.raw_data) > self.max_frames:
            print(f"Raw data length exceeded {self.max_frames} frames. Saving current batch in background...")
            # Stop the current screen recording.
            self.stop_screen_recording()

            # Make a deep copy of raw_data for saving.
            data_to_save = copy.deepcopy(self.raw_data)
            
            # Clear the current buffer for the new session.
            self.raw_data.clear()

            # Start background saving.
            threading.Thread(target=self._save_batch,
                             args=(data_to_save, video_path), 
                             daemon=True).start()

            # Start a new recording immediately.
            new_video_path = self.start_screen_recording()
            
            return new_video_path
            
        return video_path


    def _validate_video_duration(self, video_path):
        """
        Validates if the recorded video meets the minimum duration requirement.
        
        Args:
            video_path: Path to the video file to validate
        
        Return:
            True if video is valid, False otherwise.
        """
        if not video_path or not os.path.exists(video_path):
            print(f"Screen recording file not found: {video_path}")
            return False

        try:
            ffprobe_cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", video_path
            ]
            result = subprocess.run(ffprobe_cmd, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
            
            duration_str = result.stdout.strip()
            duration = float(duration_str)

            if duration < self.min_video_duration:
                print(f"Video length ({duration:.2f} seconds) is less than {self.min_video_duration} seconds. Moving to invalid videos directory.")
                return False
            return True
        except Exception as e:
            print(f"Error checking video duration: {e}")
            return False


    def _save_json_data(self, identifier: str, data_to_save, is_valid=True):
        """
        Saves each raw JSON frame as a separate file in a folder named with the identifier.
        
        Args:
            identifier: Folder name to use (first frame's frame_count).
            data_to_save: List of raw frames (dictionaries) to save.
            is_valid: Whether to save to the valid or invalid directory.
        """
        if is_valid:
            base_dir = os.path.join("data", "object_lists")
        else:
            base_dir = os.path.join("data", "invalid_objects")
            
        json_folder = os.path.join(base_dir, identifier)
        os.makedirs(json_folder, exist_ok=True)

        for frame in data_to_save:
            frame_count = frame.get("frame_count")

            if frame_count is None:
                continue

            key = str(frame_count)
            json_path = os.path.join(json_folder, f"{key}.json")

            with open(json_path, "w") as f:
                json.dump(frame, f, indent=4)

            print(f"Saved JSON for frame {key} to {json_path}")


    def _save_video_file(self, identifier: str, video_path: str, is_valid=True):
        """
        Moves the temporary video file to its final location with the identifier as filename.
        
        Args:
            identifier: Filename to use for the saved video (first frame's frame_count).
            video_path: Path to the temporary video file to move
            is_valid: Whether to save to the valid or invalid directory.
        """
        if not video_path:
            print("No video path provided for saving.")
            return
        
        if is_valid:
            target_dir = os.path.join("data", "videos")
        else:
            target_dir = os.path.join("data", "invalid_videos")
            
        final_video_path = os.path.join(target_dir, f"{identifier}.mp4")
        
        try:
            os.rename(video_path, final_video_path)
            status = "valid" if is_valid else "invalid"
            print(f"Screen recording saved to {final_video_path} (as {status})")
        except Exception as e:
            print(f"Error saving screen recording: {e}")


    def _save_batch(self, data_to_save, video_path):
        """
        Saves a batch of accumulated frames.
        Uses the frame_count of the first frame in the batch as the identifier.
        Checks the video duration; if valid, saves JSON files under data/object_lists
        (in a folder named with the identifier) and moves the temporary video file
        into data/videos using the identifier.
        
        If invalid, saves to data/invalid_videos and data/invalid_objects instead.
        
        Args:
            data_to_save: List of raw frames to save
            video_path: Path to the temporary video file associated with this batch
        """
        if not data_to_save:
            print("No data to save in batch.")
            return

        first_frame = data_to_save[0]
        first_key = str(first_frame.get("frame_count"))

        if not first_key:
            print("First frame in batch does not have a frame_count.")
            return

        # Validate video duration.
        is_valid = self._validate_video_duration(video_path)
        
        # Mark session as having a valid batch if at least one batch is valid
        if is_valid:
            self.session_counters['current_session_valid'] = True

        # Save JSON data
        self._save_json_data(first_key, data_to_save, is_valid)
        
        # Save video file
        self._save_video_file(first_key, video_path, is_valid)


    def stop_recording(self, video_path=None):
        """
        Finalizes the recording by stopping the screen recording and saving any
          remaining frames.
        
        Args:
            video_path: Path to the current video file (if not provided, nothing
              will be saved)
            
        Returns:
            True if the session had at least one valid batch, False otherwise
        """
        self.stop_screen_recording()
        
        if self.raw_data:
            print("Final save of remaining frames...")
            
            # Save remaining frames directly (not in background) for this final save
            data_to_save = copy.deepcopy(self.raw_data)
            self.raw_data.clear()
            self._save_batch(data_to_save, video_path)
        
        # Return the current session validity 
        session_valid = self.session_counters['current_session_valid']
        print(f"Session completed with {'valid' if session_valid else 'no valid'} data.")
        
        # Reset for next session
        self.session_counters['current_session_valid'] = False

        print("Recording stopped. Internal buffers cleared.")
        
        return session_valid
    
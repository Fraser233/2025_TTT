#!/usr/bin/env python
# Author: Fengze Yang <fred.yang@utah.edu>
# Date: 2025-03-30

import json
import socket
import ssl
import os
from typing import Any, Dict
from lidar_buffer import LidarBuffer
from vru_detector import VruDetector

# Configuration for the TCP stream (Ouster Gemini Detect)
HOST = "10.206.12.168"
PORT = 3302
ENDIAN_TYPE = "big"
FRAME_SIZE_B = 4
ADDRESS = (HOST, PORT)

# Capture area: (width, height, offset_x, offset_y)
CAPTURE_AREA = (1280, 720, 350, 300)

# Maximum number of frames to keep in the buffer.
# AKA the video length (MAX_BUFFER_SIZE * 0.1 seconds).
MAX_BUFFER_SIZE = 70

# Minimum valid video duration in seconds.
MIN_VIDEO_DURATION = 6

# Number of consecutive frames without a VRU before finalizing the session.
NO_VRU_THRESHOLD = 15


def recv(socket_client: ssl.SSLSocket, num_bytes: int) -> bytearray:
    """
    Reads exactly num_bytes from the socket_client or returns an empty bytearray if EOF is reached.
    """
    data = bytearray()
    while len(data) < num_bytes:
        remaining_bytes = num_bytes - len(data)
        try:
            packet = socket_client.recv(remaining_bytes)
        except (socket.timeout, ConnectionResetError):
            return bytearray()
        if not packet:
            return bytearray()
        data.extend(packet)
    return data


def read_frames(socket_client: ssl.SSLSocket, callback_function: Any) -> None:
    """
    Reads frames indefinitely from the TCP stream.
    Each frame begins with a 4-byte size indicator, followed by the JSON payload.
    Calls callback_function(data) for every frame.
    The reading loop stops if callback_function returns True.
    """
    while True:
        # Read the frame size (first 4 bytes).
        frame_size_b = recv(socket_client, FRAME_SIZE_B)
        if len(frame_size_b) == 0:
            return  # Connection closed or error.

        frame_size = int.from_bytes(frame_size_b, ENDIAN_TYPE)
        data_bytes = recv(socket_client, frame_size)
        if len(data_bytes) == 0:
            return

        try:
            data = json.loads(data_bytes.decode("utf-8"))
        except json.JSONDecodeError:
            continue  # Skip invalid JSON frames.

        # Skip heartbeat messages.
        if "heartbeat" in data.keys():
            continue

        # If callback_function returns True, break the reading loop.
        if callback_function(data):
            break


def print_session_statistics(session_counters):
    """
    Print statistics about the data collection sessions.
    
    Args:
        session_counters: Dictionary with session counting stats.
    """
    total_sessions = session_counters['total_sessions']
    valid_sessions = session_counters['valid_sessions']
    
    if total_sessions > 0:
        valid_percentage = (valid_sessions / total_sessions) * 100
        invalid_sessions = total_sessions - valid_sessions
        
        print(f"\nSession Statistics:")
        print(f"  Total Sessions: {total_sessions}")
        print(f"  Valid Sessions: {valid_sessions} ({valid_percentage:.1f}%)")
        print(f"  Invalid Sessions: {invalid_sessions} ({100-valid_percentage:.1f}%)")
    else:
        print("No sessions were recorded.")


def main():
    # Create SSL context for secure connection.
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.verify_mode = ssl.CERT_NONE

    # Initialize session counters
    session_counters = {
        'total_sessions': 0,
        'valid_sessions': 0,
        'current_session_valid': False
    }

    # Connect to the TCP stream.
    with ssl_context.wrap_socket(socket.create_connection(ADDRESS)) as socket_client:
        print(f"Connected to {ADDRESS}. Listening for LiDAR data...")

        while True:
            # Create a new LidarBuffer for this session, passing in the session counters
            lidar_buffer = LidarBuffer(
                max_frames=MAX_BUFFER_SIZE,
                min_video_duration=MIN_VIDEO_DURATION,
                capture_area=CAPTURE_AREA,
                session_counters=session_counters
            )
            
            # Create a new VruDetector using the LidarBuffer and NO_VRU_THRESHOLD.
            vru_detector = VruDetector(lidar_buffer, NO_VRU_THRESHOLD)

            # Read frames until the detector signals the current session is complete.
            # This call blocks until vru_detector.handle_frame() returns True.
            read_frames(socket_client, vru_detector.handle_frame)
            
            # Increment session counters after a session completes
            session_counters['total_sessions'] += 1
            
            # Update valid sessions counter if the session was valid
            if session_counters['current_session_valid']:
                session_counters['valid_sessions'] += 1
            
            # Print current statistics after each session
            print_session_statistics(session_counters)


if __name__ == "__main__":
    main()
    
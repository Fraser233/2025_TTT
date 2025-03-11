# Precondition: Make sure you have installed the .whl package first:
# pip install LiDAR_API_Docs/Realtime_API/V2.3.1/bctRealtimeSubscriber-2.3.1-py3-none-any.whl

import threading
from realtime_subscriber.Realtime_subscriber_api import BCTWSConnection
from dotenv import load_dotenv
import os


# Global & constant parameters
TOKEN_FILE = "access_token.txt"

# Load .env file
load_dotenv()

# -------------------- Configuration --------------------
UDID = "your_sensor_udid_here"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# -------------------- Create Stream --------------------
stream = BCTWSConnection(
    UDID,
    username=USERNAME,
    password=PASSWORD,
    singleton=False,
    subscriptions=[
        BCTWSConnection.subscriptionOption.FRAME,
        BCTWSConnection.subscriptionOption.PHASE_CHANGE,
        BCTWSConnection.subscriptionOption.LOOP_CHANGE
    ]
)

# -------------------- Handlers for Multithreaded Events --------------------
def get_frame():
    while True:
        try:
            data = stream.get_frame()
            print("[FRAME]")
            print(data)
        except Exception as e:
            print("Error in frame stream:", e)

def get_occupancy():
    while True:
        try:
            data = stream.get_occupancy()
            print("[OCCUPANCY]")
            print(data)
        except Exception as e:
            print("Error in occupancy stream:", e)

def get_phase():
    while True:
        try:
            data = stream.get_phase()
            print("[PHASE CHANGE]")
            print(data)
        except Exception as e:
            print("Error in phase stream:", e)

# -------------------- Start Threads --------------------
frame_thread = threading.Thread(target=get_frame)
occupancy_thread = threading.Thread(target=get_occupancy)
phase_thread = threading.Thread(target=get_phase)

frame_thread.start()
occupancy_thread.start()
phase_thread.start()

frame_thread.join()
occupancy_thread.join()
phase_thread.join()

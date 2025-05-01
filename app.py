'''
import cv2
import os
import csv
from datetime import datetime
from model.detector import calculate_fake_risk
from camera.virtual_cam import start_virtual_camera

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "risk_log.csv")

def overlay_risk_score(frame, risk_score):
    text = f"FAKE RISK: {risk_score}%"
    color = (0, 0, 255) if risk_score > 60 else (0, 255, 0)
    cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
    return frame

def get_frame_overlay(frame):
    risk_score = calculate_fake_risk(frame)

    # log score
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", newline="") as log_file:
        writer = csv.writer(log_file)
        writer.writerow([timestamp, risk_score])

    return overlay_risk_score(frame, risk_score)

if __name__ == "__main__":
    print("Starting PhantomShield virtual camera...")
    start_virtual_camera(get_frame_overlay)

'''

# app.py

import cv2
import os
import csv
from datetime import datetime
from model.detector import calculate_fake_risk
from camera.virtual_cam import start_camera_preview

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "risk_log.csv")

def overlay_risk_score(frame, risk_score):
    text = f"FAKE RISK: {risk_score}%"
    color = (0, 0, 255) if risk_score > 60 else (0, 255, 0)
    cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
    return frame

def get_frame_overlay(frame):
    raw_score = calculate_fake_risk(frame)
    threshold = 60  # you decide where to draw the "fake" line
    risk_score = min(max(raw_score, 0), 100)

    if risk_score >= threshold:
        print(f"[ALERT] FAKE RISK HIGH: {risk_score}%")

    # log + overlay
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", newline="") as log_file:
        writer = csv.writer(log_file)
        writer.writerow([timestamp, risk_score])

    return overlay_risk_score(frame, risk_score)


if __name__ == "__main__":
    print("PhantomShield: Testing OBS Virtual Cam input")
    start_camera_preview(get_frame_overlay, cam_index=1)  # Change index if needed

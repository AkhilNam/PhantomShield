import os
import sys
import cv2
import csv
from datetime import datetime
from model.detector import calculate_fake_risk
from camera.virtual_cam import start_camera_preview

# Robust sys.path logic for both dev and packaged environments
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)
sys.path.insert(0, os.path.join(base_path, 'model'))
sys.path.insert(0, os.path.join(base_path, 'camera'))
sys.path.insert(0, os.path.join(base_path, 'audio'))

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "risk_log.csv")

smoothed_score = 0

def amplify_score(raw):
    gain = 1.5  # Amplify mid-high scores
    amplified = min(max(raw * gain, 0), 100)
    return int(amplified)

def overlay_warning(frame, show_warning):
    if show_warning:
        text = "DEEPFAKE WARNING"
        cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    return frame

def get_frame_overlay(frame):
    global smoothed_score
    raw_score = calculate_fake_risk(frame)
    amplified_score = amplify_score(raw_score)
    smoothed_score = 0.85 * smoothed_score + 0.15 * amplified_score
    risk_score = int(smoothed_score)

    show_warning = risk_score > 60

    if show_warning:
        print(f"[ALERT] DEEPFAKE WARNING ({risk_score}%)")

    # Save log (full score still saved for analysis)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", newline="") as log_file:
        writer = csv.writer(log_file)
        writer.writerow([timestamp, risk_score])

    return overlay_warning(frame, show_warning)

if __name__ == "__main__":
    print("PhantomShield: Testing OBS Virtual Cam input")
    start_camera_preview(get_frame_overlay, cam_index=1)  # Change index if needed

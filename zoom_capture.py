import pygetwindow as gw
import mss
import cv2
import numpy as np
import os
import time
import csv
from collections import deque
from model.detector import calculate_fake_risk

# --- Config ---
GRID_ROWS = 1
GRID_COLS = 2
THRESHOLD = 50          # Alert when smoothed average exceeds this
GAIN = 1.2           # Amplification gain
BUFFER_SIZE = 40         # Number of frames to average

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
os.makedirs("logs/faces", exist_ok=True)
LOG_PATH = "logs/risk_log.csv"

# Score buffers for smoothing
risk_buffers = {
    (row, col): deque(maxlen=BUFFER_SIZE)
    for row in range(GRID_ROWS) for col in range(GRID_COLS)
}
alerted_tiles = set()  # Tiles we've already notified once

def amplify_score(raw):
    return min(max(raw * GAIN, 0), 100)

def get_zoom_window_bbox():
    for window in gw.getWindowsWithTitle("Zoom"):
        if window.visible:
            return (window.left, window.top, window.width, window.height)
    raise RuntimeError("Zoom window not found. Make sure Zoom is open and not minimized.")

def capture_zoom_region(bbox):
    with mss.mss() as sct:
        monitor = {
            "left": bbox[0],
            "top": bbox[1],
            "width": bbox[2],
            "height": bbox[3]
        }
        sct_img = sct.grab(monitor)
        img = np.array(sct_img)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

def scan_zoom_tiles_with_face_detection(frame):
    tile_height = frame.shape[0] // GRID_ROWS
    tile_width = frame.shape[1] // GRID_COLS

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            tile_coords = (row, col)

            if tile_coords in alerted_tiles:
                continue  # already alerted for this tile

            x1 = col * tile_width
            y1 = row * tile_height
            x2 = x1 + tile_width
            y2 = y1 + tile_height
            tile = frame[y1:y2, x1:x2]

            gray_tile = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_tile, scaleFactor=1.3, minNeighbors=5)

            if len(faces) > 0:
                (fx, fy, fw, fh) = max(faces, key=lambda f: f[2] * f[3])
                pad = int(0.2 * min(fw, fh))
                fx, fy = max(0, fx - pad), max(0, fy - pad)
                fw, fh = fw + 2 * pad, fh + 2 * pad
                face_crop = tile[fy:fy+fh, fx:fx+fw]
                raw_score = calculate_fake_risk(face_crop)
                cropped_image = face_crop
            else:
                # fallback center crop
                mx, my = tile.shape[1] // 5, tile.shape[0] // 5
                fallback = tile[my:-my, mx:-mx]
                raw_score = calculate_fake_risk(fallback)
                cropped_image = fallback

            if raw_score < 30:
                continue  # ignore low-confidence noise

            amplified_score = amplify_score(raw_score)
            risk_buffers[tile_coords].append(amplified_score)

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(LOG_PATH, "a", newline="") as log_file:
                writer = csv.writer(log_file)
                writer.writerow([timestamp, f"tile_{row}_{col}", int(amplified_score)])

            # only alert once per tile
            if len(risk_buffers[tile_coords]) == BUFFER_SIZE:
                avg = sum(risk_buffers[tile_coords]) / BUFFER_SIZE
                if avg > THRESHOLD:
                    print(f"⚠️  Tile ({row},{col}) may be a deepfake. Avg risk: {int(avg)}%")
                    cv2.imwrite(f"logs/faces/tile_{row}_{col}_{int(avg)}_{int(time.time())}.jpg", cropped_image)
                    alerted_tiles.add(tile_coords)

if __name__ == "__main__":
    try:
        bbox = get_zoom_window_bbox()
        print(f"[INFO] Capturing Zoom window at {bbox}")
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        exit()

    while True:
        frame = capture_zoom_region(bbox)
        scan_zoom_tiles_with_face_detection(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

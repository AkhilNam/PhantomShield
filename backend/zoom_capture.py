import pygetwindow as gw
import mss
import cv2
import numpy as np
import os
import time
import csv
import json
from collections import deque
from model.detector import calculate_fake_risk
import sys
import threading
sys.stdout.reconfigure(encoding='utf-8')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# --- Config ---
config = {
    'gridRows': 1,
    'gridCols': 2,
    'threshold': 50,    # Alert when smoothed average exceeds this
    'gain': 1.2,       # Amplification gain
    'bufferSize': 40   # Number of frames to average
}

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
os.makedirs("logs/faces", exist_ok=True)
LOG_PATH = "logs/risk_log.csv"

# Score buffers for smoothing
def create_risk_buffers():
    return {
        (row, col): deque(maxlen=config['bufferSize'])
        for row in range(config['gridRows']) 
        for col in range(config['gridCols'])
    }

risk_buffers = create_risk_buffers()
alerted_tiles = set()  # Tiles we've already notified once

def send_alert(tile, risk):
    alert = {
        "type": "alert",
        "tile": f"Tile {tile[0]},{tile[1]}",
        "risk": int(risk)
    }
    print(json.dumps(alert))
    sys.stdout.flush()

def send_status(status):
    status_msg = {
        "type": "status",
        "message": status
    }
    print(json.dumps(status_msg))
    sys.stdout.flush()

def send_tiles(count):
    tiles_msg = {
        "type": "tiles",
        "count": count
    }
    print(json.dumps(tiles_msg))
    sys.stdout.flush()

def send_config_response(success, error=None):
    response = {
        "type": "config-response",
        "success": success
    }
    if error:
        response["error"] = str(error)
    print(json.dumps(response))
    sys.stdout.flush()

def amplify_score(raw):
    return min(max(raw * config['gain'], 0), 100)

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
    global risk_buffers
    
    tile_height = frame.shape[0] // config['gridRows']
    tile_width = frame.shape[1] // config['gridCols']
    active_tiles = 0

    for row in range(config['gridRows']):
        for col in range(config['gridCols']):
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
                active_tiles += 1
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
            if tile_coords not in risk_buffers:
                risk_buffers[tile_coords] = deque(maxlen=config['bufferSize'])
            risk_buffers[tile_coords].append(amplified_score)

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(LOG_PATH, "a", newline="") as log_file:
                writer = csv.writer(log_file)
                writer.writerow([timestamp, f"tile_{row}_{col}", int(amplified_score)])

            # only alert once per tile
            if len(risk_buffers[tile_coords]) == config['bufferSize']:
                avg = sum(risk_buffers[tile_coords]) / config['bufferSize']
                if avg > config['threshold']:
                    send_alert(tile_coords, avg)
                    cv2.imwrite(f"logs/faces/tile_{row}_{col}_{int(avg)}_{int(time.time())}.jpg", cropped_image)
                    alerted_tiles.add(tile_coords)

    send_tiles(active_tiles)

def handle_config_update():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            new_config = json.loads(line)
            if new_config['type'] == 'config':
                # Update configuration
                config['gridRows'] = new_config['gridRows']
                config['gridCols'] = new_config['gridCols']
                config['threshold'] = new_config['threshold']
                config['gain'] = new_config['gain']
                config['bufferSize'] = new_config['bufferSize']
                
                # Reset buffers and alerts
                global risk_buffers, alerted_tiles
                risk_buffers = create_risk_buffers()
                alerted_tiles.clear()
                
                send_config_response(True)
                send_status("Configuration updated")
        except Exception as e:
            send_config_response(False, str(e))

if __name__ == "__main__":
    # Start config update thread
    config_thread = threading.Thread(target=handle_config_update, daemon=True)
    config_thread.start()

    try:
        bbox = get_zoom_window_bbox()
        send_status(f"Capturing Zoom window at {bbox}")
    except RuntimeError as e:
        send_status(f"ERROR: {e}")
        exit()

    while True:
        frame = capture_zoom_region(bbox)
        scan_zoom_tiles_with_face_detection(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

# PhantomShield

**PhantomShield** is a real-time deepfake detection system that monitors video conferencing applications like Zoom, Microsoft Teams, and Google Meet. It analyzes facial frames for deepfake indicators and provides real-time risk assessment.

## 🎯 Features

- ✅ Real-time deepfake detection using MesoNet architecture
- ✅ Multi-tile monitoring for Zoom meetings
- ✅ Adaptive face detection with fallback mechanisms
- ✅ Risk score smoothing and buffering to reduce false positives
- ✅ Automatic logging of risk scores and flagged frames
- ✅ Configurable detection thresholds and sensitivity
- ✅ Support for both webcam and virtual camera inputs

## 🛠️ Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download the pre-trained model weights:
```bash
# Place Meso4_F2F.h5 in the model/ directory
```

3. Run the application:
```bash
# For webcam monitoring:
python app.py

# For Zoom window monitoring:
python zoom_capture.py
```

## ⚙️ Configuration

Key parameters in `zoom_capture.py`:
- `GRID_ROWS`, `GRID_COLS`: Number of tiles to monitor
- `THRESHOLD`: Risk score threshold for alerts (default: 50)
- `GAIN`: Score amplification factor (default: 1.2)
- `BUFFER_SIZE`: Number of frames for score averaging (default: 40)

## 📊 Logging

- Risk scores are logged to `logs/risk_log.csv`
- Flagged frames are saved to `logs/faces/` with timestamps
- Each log entry includes:
  - Timestamp
  - Tile coordinates
  - Risk score

## 🔍 How It Works

1. Captures video feed from Zoom window or webcam
2. Divides frame into configurable grid
3. Detects faces in each tile
4. Processes detected faces through MesoNet model
5. Applies score smoothing and buffering
6. Alerts when risk exceeds threshold
7. Logs results for analysis

## ⚠️ Notes

- Requires OpenCV and Keras/TensorFlow
- Works best with well-lit, front-facing video
- May have false positives in low-light conditions
- Performance depends on system resources

## 📝 License
See LICENSE file for details

---

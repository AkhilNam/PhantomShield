# PhantomShield

**PhantomShield** is a real-time deepfake detection system that monitors video conferencing applications like Zoom, Microsoft Teams, and Google Meet. It analyzes facial frames for deepfake indicators and provides real-time risk assessment.

## 🎯 Features

- ✅ Real-time deepfake detection using MesoNet architecture
- ✅ Dynamic grid-based monitoring system
- ✅ Real-time configuration adjustments
- ✅ Adaptive face detection with fallback mechanisms
- ✅ Risk score smoothing and buffering
- ✅ Automatic logging of risk scores and flagged frames
- ✅ Modern Electron-based UI

## 🛠️ Setup

1. Install dependencies:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

2. Download the pre-trained model weights:
```bash
# Place Meso4_F2F.h5 in the model/ directory
```

3. Run the application:
```bash
# Run in development mode
npm run dev

# Build and run in production
npm run build
```

## 🎛️ Configuration

The application features a real-time configuration panel that allows you to adjust:

- **Grid Layout**
  - Rows (1-4): Number of vertical tiles
  - Columns (1-4): Number of horizontal tiles
  - Useful for different Zoom layouts and participant counts

- **Detection Parameters**
  - Alert Threshold (0-100%): Risk level that triggers alerts
  - Amplification Gain (0.1-5.0): Adjusts sensitivity
  - Buffer Size (1-100): Frames to average for smoothing

Changes take effect immediately without requiring restart.

## 📊 Monitoring

- **Status Panel**
  - Current operation status
  - Number of active tiles being monitored
  - Real-time alerts for detected deepfakes

- **Alert System**
  - Visual alerts for high-risk detections
  - Risk percentage display
  - Automatic alert clearing

- **Logging**
  - Risk scores logged to `logs/risk_log.csv`
  - Flagged frames saved to `logs/faces/`
  - Timestamps and tile coordinates included

## 🔍 How It Works

1. **Initialization**
   - Launches Electron UI
   - Starts Python backend
   - Establishes IPC communication

2. **Detection Process**
   - Captures Zoom window content
   - Divides into configurable grid
   - Performs face detection
   - Analyzes each face with MesoNet
   - Applies smoothing and thresholds
   - Generates alerts for suspicious content

3. **Data Flow**
   - Real-time frame processing
   - JSON-based communication
   - Bidirectional config updates
   - Asynchronous alert handling

## ⚠️ Notes

- Requires OpenCV and TensorFlow
- Works best with well-lit, front-facing video
- May have false positives in low-light conditions
- Performance depends on:
  - System resources
  - Grid size configuration
  - Number of active participants

## 🔧 Troubleshooting

- Ensure Zoom window is visible and not minimized
- Check lighting conditions for better detection
- Adjust grid size to match Zoom's layout
- Fine-tune threshold and gain for your environment

## 📝 License

See LICENSE file for details

---

import cv2
import numpy as np
import os
from keras.models import load_model
from model.mesonet import build_model

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Build and load model weights using absolute path
model = build_model()
model_path = os.path.join(os.path.dirname(__file__), "Meso4_F2F.h5")
model.load_weights(model_path)

def preprocess_frame(frame):
    face = cv2.resize(frame, (256, 256), interpolation=cv2.INTER_CUBIC)
    face = face.astype(np.float32) / 255.0
    face = np.expand_dims(face, axis=0)
    return face

def calculate_fake_risk(face_crop):
    try:
        input_tensor = preprocess_frame(face_crop)
        pred = model.predict(input_tensor, verbose=0)[0][0]
        return int(pred * 100)
    except Exception as e:
        print(f"[ERROR in calculate_fake_risk] {e}")
        return 0

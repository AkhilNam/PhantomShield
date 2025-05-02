import cv2
import numpy as np
from keras.models import load_model
from model.mesonet import build_model

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
model = build_model()
model.load_weights("model/Meso4_F2F.h5")

def preprocess_frame(frame):
    # Resize and normalize
    face = cv2.resize(frame, (256, 256))
    face = face.astype(np.float32) / 255.0
    face = np.expand_dims(face, axis=0)
    return face
def calculate_fake_risk(face_crop):
    try:
        resized = cv2.resize(face_crop, (256, 256))
        normalized = resized.astype(np.float32) / 255.0
        input_tensor = np.expand_dims(normalized, axis=0)
        pred = model.predict(input_tensor, verbose=0)[0][0]
        return int(pred * 100)
    except Exception as e:
        print(f"[ERROR in calculate_fake_risk] {e}")
        return 0

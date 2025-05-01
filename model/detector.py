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

def calculate_fake_risk(frame):
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return 0  # No face = not applicable

        # Take the largest face
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face_crop = frame[y:y+h, x:x+w]
        face_resized = cv2.resize(face_crop, (256, 256))
        input_tensor = face_resized.astype(np.float32) / 255.0
        input_tensor = np.expand_dims(input_tensor, axis=0)

        pred = model.predict(input_tensor)[0][0]
        return int(pred * 100)
    except Exception as e:
        print(f"[Error in detection] {e}")
        return 0

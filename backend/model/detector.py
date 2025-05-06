import cv2
import numpy as np
import os
import torch
import torch.nn as nn
from torchvision import transforms, models

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load ResNet18 model and weights
model_path = os.path.join(os.path.dirname(__file__), "actualModel.pt")
model = models.resnet18(weights=None)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 2)  # 2 classes: Real and Fake
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()

# Define image transformation (as per your notebook: 224x224, mean/std=0.5)
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

def preprocess_frame(frame):
    # frame is expected to be a BGR numpy array (from OpenCV)
    face = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face = transform(face)
    face = face.unsqueeze(0)  # Add batch dimension
    return face

def calculate_fake_risk(face_crop):
    try:
        input_tensor = preprocess_frame(face_crop)
        with torch.no_grad():
            outputs = model(input_tensor)
            probs = torch.softmax(outputs, dim=1)
            fake_prob = probs[0, 0].item()  # Probability of class 0 (Fake)
        return int(fake_prob * 100)
    except Exception as e:
        print(f"[ERROR in calculate_fake_risk] {e}")
        return 0

import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat

def start_virtual_camera(get_frame_overlay):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not access webcam.")

    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = int(cap.get(cv2.CAP_PROP_FPS)) or 20

    with pyvirtualcam.Camera(width=width, height=height, fps=fps, fmt=PixelFormat.BGR) as cam:
        print(f"Virtual camera started: {cam.device}")
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = get_frame_overlay(frame)
            cam.send(frame)
            cam.sleep_until_next_frame()

    cap.release()

def start_camera_preview(get_frame_overlay, cam_index=1):
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {cam_index}")

    print(f"[INFO] Reading from camera index {cam_index}")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame")
            break

        frame = get_frame_overlay(frame)

        cv2.imshow("PhantomShield Preview", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Exiting preview...")
            break

    cap.release()
    cv2.destroyAllWindows()
    

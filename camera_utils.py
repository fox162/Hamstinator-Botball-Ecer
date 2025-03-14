import cv2

def init_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Error: Could not open camera.")

    # Set camera to capture in full resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    return cap

def release_camera(cap):
    cap.release()
    cv2.destroyAllWindows()
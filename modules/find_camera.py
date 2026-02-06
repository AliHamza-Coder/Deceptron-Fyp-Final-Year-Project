import cv2

for i in range(5):
    cam = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cam.isOpened():
        print(f"✅ Camera detected at index {i}")
        cam.release()
    else:
        print(f"❌ No camera at index {i}")

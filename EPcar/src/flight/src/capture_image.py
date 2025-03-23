import cv2
import datetime

rtsp_url = 'rtsp://192.168.0.10:8554/live'

cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("fail open")
    exit()

ret, frame = cap.read()

if ret:

    timestamp=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename=f'output_{timestamp}.jpg'
    
    cv2.imwrite(filename, frame)
    print("success")
else:
    print("fail")

cap.release()


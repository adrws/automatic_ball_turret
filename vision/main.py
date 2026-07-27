import cv2
from ultralytics import YOLO
import time
import json
import math
import serial

camera = cv2.VideoCapture(0)
base_model = YOLO("yolo26n.pt")
base_model.export(format="openvino")
model = YOLO("yolo26n_openvino_model/")

ser = serial.Serial('COM4', 115200, timeout = 1)

camera_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
camera_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
center_x = math.floor(camera_width / 2)
center_y = math.floor(camera_height / 2)

start_time = time.perf_counter()
end_time = None

def send_command(direction: str):
    global end_time 
    global start_time
    end_time = time.perf_counter()
    duration = end_time - start_time

    if (duration < 0.0015):
        return
    
    data = {
        "direction": f"{direction}",
    }
    
    payload = json.dumps(data) + "\n"
    ser.write(payload.encode('utf-8'))
    start_time = time.perf_counter()
    print(f"Direction: {direction}")


while True:
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame.")
        break

    results = model(frame, verbose=False)
    
    for box in results[0].boxes:

        if ((box.cls == 0) & (box.conf.item() >= 0.90)):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            confidence = round(box.conf.item(), 2)
            area = round((x2 - x1) * (y2 - y1), 1)
            obj_center_x = math.floor(x1 + ((x2 - x1)/2))
            obj_center_y = math.floor(y1 + ((y2 - y1)/2))
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.putText(frame, f"Confidence: {confidence}, Size: {area} px", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA, False)
            cv2.circle(frame, (obj_center_x, obj_center_y), 5, (255, 0, 0), -1)

            delta_x = obj_center_x - center_x

            if (center_x - 20 <= obj_center_x <= center_x + 20):
                send_command("center")
            elif (delta_x > 0):
                send_command("right")
            elif (delta_x < 0):
                send_command("left")
            

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()


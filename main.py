# 1) Get bounding box information of highest conf. object that is "person".
# 2) Display the bounding box and format the information to be sent.
# 3) Export the information using pyserial.

import cv2
from ultralytics import YOLO
import serial

capture = cv2.VideoCapture(0)

base_model = YOLO("yolo26n.pt")
base_model.export(format="openvino")

model = YOLO("yolo26n_openvino_model/")


while True:
    ret, frame = capture.read()
    if not ret:
        print("Failed to grab frame.")
        break

    results = model(frame)
    
    for box in results[0].boxes:

        if ((box.cls == 0) & (box.conf.item() >= 0.90)):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            confidence = round(box.conf.item(), 2)
            area = round((x2 - x1) * (y2 - y1), 1)
            center_x = int(x1 + ((x2 - x1)/2))
            center_y = int(y1 + ((y2 - y1)/2))
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.putText(frame, f"Confidence: {confidence}, Size: {area} px", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA, False)
            cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()


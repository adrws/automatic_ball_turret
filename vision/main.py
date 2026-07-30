import cv2
from ultralytics import YOLO
import math
import keyboard
from controller import TurretController, Direction
import projectile_kinematics

camera = cv2.VideoCapture(0)
base_model = YOLO("yolo26n.pt")
base_model.export(format="openvino")
model = YOLO("yolo26n_openvino_model/")

Turret = TurretController("COM4")
Turret.setVerbose(True)

camera_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
camera_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
center_x = math.floor(camera_width / 2)
center_y = math.floor(camera_height / 2)
inner_bound = camera_width * 0.05
outer_bound = camera_width * 0.15

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
            obj_height = y2 - y1
            area = round((x2 - x1) * (y2 - y1), 1)
            obj_center_x = math.floor(x1 + ((x2 - x1)/2))
            obj_center_y = math.floor(y1 + ((y2 - y1)/2))
            object_height = y1 - y2
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.putText(frame, f"Confidence: {confidence}, Height: {obj_height} px", (x1 - 250, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA, False)
            cv2.circle(frame, (obj_center_x, obj_center_y), 5, (255, 0, 0), -1)
            cv2.line(frame, (obj_center_x - 20, y1), (obj_center_x + 20, y1), (0, 0, 255), 2)
            cv2.line(frame, (obj_center_x - 20, y2), (obj_center_x + 20, y2), (0, 0, 255), 2)

            delta_x = obj_center_x - center_x

            if (center_x - inner_bound <= obj_center_x <= center_x + inner_bound):
                Turret.setSpeed(255, Direction.right)
                Turret.setSpeed(255, Direction.left)
            else:
                Turret.setSpeed(0, Direction.right)
                Turret.setSpeed(0, Direction.left)

            if (center_x - inner_bound <= obj_center_x <= center_x + inner_bound):
                pass
            elif (delta_x > 0):
                if (delta_x < outer_bound): 
                    Turret.rotateX(-1)
                else:
                    Turret.rotateX(-5)
            elif (delta_x < 0):
                if (delta_x > -outer_bound):
                    Turret.rotateX(1)
                else:
                    Turret.rotateX(5)
            
            keyboard.add_hotkey('w', lambda: Turret.rotateY(1))
            keyboard.add_hotkey('s', lambda: Turret.rotateY(-1))

    cv2.imshow('frame', frame)

    if cv2.waitKey(2) == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
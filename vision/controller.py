import serial
import sys
import json
import time
from datetime import datetime
from enum import Enum
class Direction(Enum):
    left = 1,
    right = 2,
class TurretController:
    verbose_flag = True
    
    x_servo_angle = 90
    y_servo_angle = 90
    right_motor_speed = None
    left_motor_speed = None
    prev_right_motor_speed = None
    prev_left_motor_speed = None

    def __init__(self, port: str) -> None:
        print(f"Initializing serial communication on port {port}.")

        try:
            self.ser = serial.Serial(port, 921600, timeout = 1)
        except serial.SerialException as e:
            sys.exit(f"Error: {e}")

        print(f"Port: {port} found.")

        self.command_start_time = time.perf_counter()
        self.command_end_time = None
        self.ball_release_start_time = time.perf_counter()
        self.ball_release_end_time = None


    def rotateX(self, step: int):
        data = {
            "command": "rotateX",
            "step" : f"{step}",
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.__sendCommand(data)

        self.x_servo_angle += step

    def setX(self, angle: int):
        data = {
            "command": "setX",
            "angle" : f"{angle}",
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.__sendCommand(data)

        self.x_servo_angle = angle

    def rotateY(self, step: int):
        data = {
            "command": "rotateY",
            "step" : f"{step}",
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.__sendCommand(data)

        self.y_servo_angle += step

    def setY(self, angle: int):
        step = angle - self.y_servo_angle

        data = {
            "command": "rotateY",
            "step" : f"{step}",
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.__sendCommand(data)

        self.y_servo_angle = angle

    def setSpeed(self, intensity: int, direction: Direction):
        pwm = max(0, min(intensity, 255))
        is_right = direction.name == "right"
        is_left = direction.name == "left"
        right_stale_command = pwm == self.prev_right_motor_speed
        left_stale_command = pwm == self.prev_left_motor_speed
        
        data = {
        "command": "setSpeed",
        "motor": f"{direction.name}",
        "speed" : f"{pwm}",
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if (is_right and right_stale_command) or (is_left and left_stale_command):
            return
        
        self.__sendCommand(data)

        if direction.name == "right":
            self.prev_right_motor_speed = pwm
        elif direction.name == "left":
            self.prev_left_motor_speed = pwm

        time.sleep(0.01)

    def releaseBall(self):
        self.ball_release_end_time = time.perf_counter()
        ball_release_delay = self.ball_release_end_time - self.ball_release_start_time

        if ball_release_delay < 1:
            return

        data = {
            "command": "releaseBall",
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.__sendCommand(data)

    def setVerbose(self, state: bool):
        self.verbose_flag = state

    def __sendCommand(self, command: dict):
        self.command_end_time = time.perf_counter()
        command_delay = self.command_end_time - self.command_start_time

        if command_delay < 0.01:
            return

        payload = json.dumps(command) + "\n"

        try:
            self.ser.write(payload.encode('utf-8'))
        except serial.SerialTimeoutException:
            print(f"The write operation failed.")
            return

        self.command_start_time = time.perf_counter()

        if self.verbose_flag:
            print(f"Sent: {payload}")
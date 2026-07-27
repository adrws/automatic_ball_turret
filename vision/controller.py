import serial
import sys
import json
import time
from datetime import datetime

class TurretController:
    verbose_flag = True
    x_angle = 90
    y_angle = 90

    def __init__(self, port: str) -> None:
        print(f"Initializing serial communication on port {port}.")

        try:
            self.ser = serial.Serial(port, 921600, timeout = 1)
        except serial.SerialException as e:
            sys.exit(f"Error: {e}")

        print(f"Port: {port} found.")

        self.command_start_time = time.perf_counter()
        self.command_end_time = None

    def rotateX(self, step: int):
        data = {
            "command": "rotateX",
            "step" : f"{step}",
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.__sendCommand(data)

        self.x_angle += step

    def setX(self, angle: int):
        step = angle - self.x_angle

        data = {
            "command": "rotateX",
            "step" : f"{step}",
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.__sendCommand(data)

        self.x_angle = angle

    def rotateY(self, step: int):
        data = {
            "command": "rotateY",
            "step" : f"{step}"
        }

        self.__sendCommand(data)

        self.y_angle += step

    def setY(self, angle: int):
        step = angle - self.y_angle

        data = {
            "command": "rotateY",
            "step" : f"{step}",
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.__sendCommand(data)

        self.y_angle = angle

    def setSpeed(self, intensity: int):
        pwm = max(0, min(intensity, 255))

        data = {
        "command": "setSpeed",
        "step" : f"{pwm}"
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




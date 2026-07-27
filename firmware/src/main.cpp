#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

#define SERVO_X_PIN 33
#define SERVO_Y_PIN 32

Servo SERVO_X;
Servo SERVO_Y;

void parseCommand(String incoming);
void setServo(int step, Servo& SERVO, int& position);
void initServo(Servo& SERVO, int SERVO_PIN);

int x_position{90};
int y_position{90};

void setup() {
    Serial.begin(921600);
    initServo(SERVO_X, SERVO_X_PIN);
}

void loop() {
    if (Serial.available() > 0) {
        String incoming = Serial.readStringUntil('\n');
        parseCommand(incoming);
    }
}

void parseCommand(String incoming) {
    JsonDocument json;
    String command;
    DeserializationError error = deserializeJson(json, incoming);

    if (error) {
        return;
    }

    command = json["command"].as<String>();

    if (command == "rotateX") {
        signed int step = json["step"].as<signed int>();
        setServo(step, SERVO_X, x_position);
    }
    else if (command == "rotateY") {
        signed int step = json["step"].as<signed int>();
        setServo(step, SERVO_Y, y_position);
    }
    else if (command == "setSpeed") {
        return;
        // TODO: Add the motor speed control.
    }
}

void setServo(int step, Servo& SERVO, int& position) {
    position = constrain(position + step, 0, 180);
    SERVO.write(position);
}

void initServo(Servo& SERVO, int SERVO_PIN) {
    SERVO.setPeriodHertz(50);
    SERVO.attach(SERVO_PIN, 500, 2500);
    SERVO.write(90);
}



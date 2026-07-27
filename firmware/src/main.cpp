#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

#define DEBUG_LED 2
#define SERVO1_PIN 33

void blinkLed();
void parseCommand(String incoming);
void setServo(String direction, int& current_angle, Servo& SERVO);

Servo SERVO1;

int current_angle{90};

void setup() 
{
    Serial.begin(115200);
    pinMode(DEBUG_LED, OUTPUT);
    SERVO1.setPeriodHertz(50);
    SERVO1.attach(SERVO1_PIN, 500, 2500);
    SERVO1.write(90);
}

void loop() 
{
    if (Serial.available() > 0) 
    {
        String incoming = Serial.readStringUntil('\n');
        parseCommand(incoming);
    }
}

void parseCommand(String incoming) 
{
    JsonDocument json;
    String direction;
    DeserializationError error = deserializeJson(json, incoming);

    if (error) {
        return;
    }

    direction = json["direction"].as<String>();

    setServo(direction, current_angle, SERVO1);
}

void setServo(String direction, int& current_angle, Servo& SERVO) 
{
    if (direction == "center") {
        return;
    }
    else if (direction == "right") {
        current_angle = constrain(current_angle + 1, 0, 180);
        SERVO.write(current_angle);
    }
    else if (direction == "left") {
        current_angle = constrain(current_angle - 1, 0, 180);
        SERVO.write(current_angle);
    }
}

void blinkLed() 
{
    digitalWrite(DEBUG_LED, HIGH);
    digitalWrite(DEBUG_LED, LOW);
}



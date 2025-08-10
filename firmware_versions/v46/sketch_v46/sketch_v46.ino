#include <EEPROM.h>

const int temperaturePin = A0;
const int lightPin = A1;
const int humidityPin = A2;

int tempValue, lightValue, humidValue;

void setup() {
  Serial.begin(9600);
  
  pinMode(temperaturePin, INPUT);
  pinMode(lightPin, INPUT);
  pinMode(humidityPin, INPUT);

  EEPROM.get(0, tempValue);
}

void loop() {
  if (Serial.available() && Serial.readString().indexOf("READ") >= 0) {
    String sensorData = "{\"temp\":";
    sensorData += String(analogRead(temperaturePin));
    sensorData += "\",\"light\":";
    sensorData += String(analogRead(lightPin));
    sensorData += "\",\"humidity\":";
    sensorData += String(analogRead(humidityPin));
    sensorData += "}";

    Serial.println(sensorData);
  }

  if (analogRead(temperaturePin) > 700 && analogRead(lightPin) < 800) {
    delay(5000); // adjust delays based on activity
  } else {
    delay(1000);
  }
}

void readSensors() {
  tempValue = analogRead(temperaturePin);
  lightValue = analogRead(lightPin);
  humidValue = analogRead(humidityPin);

  if (tempValue > 700 && lightValue < 800) {
    EEPROM.put(0, tempValue + lightValue); // store sensor data in EEPROM
  }
}
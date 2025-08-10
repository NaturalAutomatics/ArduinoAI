void setup() {
  Serial.begin(9600);
  // Temperature sensor on A0
  // Light sensor on A1
  pinMode(2, INPUT); // Motion sensor
}

void loop() {
  if (Serial.available() && Serial.readString().indexOf("READ") >= 0) {
    Serial.print("{");
    Serial.print("\"temp\":" + String(analogRead(A0)) + ",");
    Serial.print("\"light\":" + String(analogRead(A1)) + ",");
    Serial.print("\"motion\":" + String(digitalRead(2)) + "");
    Serial.println("}");
  }
  
  // Read motion from D2
  
  delay(100);
}

// Helper functions can be added here
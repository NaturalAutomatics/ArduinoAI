void setup() {
  Serial.begin(9600);
  // Temperature sensor on A0
  // Humidity sensor on A2
}

void loop() {
  if (Serial.available() && Serial.readString().indexOf("READ") >= 0) {
    Serial.print("{");
    Serial.print("\"temp\":" + String(analogRead(A0)) + ",");
    Serial.print("\"humidity\":" + String(analogRead(A2)) + "");
    Serial.println("}");
  }
  
  // AI-generated exploration logic
delay(1000);
  
  delay(100);
}

// Helper functions can be added here
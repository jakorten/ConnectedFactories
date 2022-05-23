
void initSensor() {
  pinMode(sensorPin, INPUT);
}

void sendSensorState(bool state) {
  unsigned long sensorCurrentMillis = millis();

  if (sensorCurrentMillis - sensorPreviousMillis >= interval) {
    // save the last time a message was sent
    Serial.print("Sending message to topic: ");
    Serial.println(topic);
    Serial.print("sensor ");
    Serial.println(state);
    
    sensorPreviousMillis = sensorCurrentMillis;
    
    mqttClient.beginMessage(topic);
    mqttClient.print("sensor ");
    mqttClient.print(state);
    mqttClient.endMessage();
    
    Serial.println();
  }
}

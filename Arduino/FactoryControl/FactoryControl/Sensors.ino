void checkTouchSensor() {
  long now = millis();
  if ((touchSensor.capacitiveSensor(30) > sensorThreshold) && (now - lastTouchMsg > 2000)) {
    lastTouchMsg = millis();
    sensorStateTouched = true;

    char payLoadSensorState[1];
    itoa(sensorStateTouched, payLoadSensorState, 10);
    client.publish(pubSensorTopic, payLoadSensorState);
    Serial.print("Updated topic ");
    Serial.print(pubSensorTopic);
    Serial.print(" with payload ");
    Serial.println(payLoadSensorState);

    sensorStateTouched = false;
  }
}

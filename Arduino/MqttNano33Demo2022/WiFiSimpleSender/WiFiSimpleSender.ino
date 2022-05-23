/*
  ArduinoMqttClient - WiFi Simple Sender

  This example connects to a MQTT broker and publishes a message to
  a topic once a second.

  The circuit:
  - Arduino MKR 1000, MKR 1010 or Uno WiFi Rev.2 board

  This example code is in the public domain.
*/

#include <ArduinoMqttClient.h>
#if defined(ARDUINO_SAMD_MKRWIFI1010) || defined(ARDUINO_SAMD_NANO_33_IOT) || defined(ARDUINO_AVR_UNO_WIFI_REV2)
  #include <WiFiNINA.h>
#elif defined(ARDUINO_SAMD_MKR1000)
  #include <WiFi101.h>
#elif defined(ARDUINO_ESP8266_ESP12)
  #include <ESP8266WiFi.h>
#endif

#include "arduino_secrets.h"

char ssid[] = SECRET_SSID;         // your network SSID (name)
char pass[] = SECRET_PASS;         // your network password (use for WPA, or use as key for WEP)
char mqtt_user[] = MQTT_USERNAME;  // your HiveMQ username
char mqtt_pass[] = MQTT_PASS;      // your HiveMQ password

WiFiSSLClient wifiClient; // aangepast, WiFiClient -> WiFiSSLClient.
MqttClient mqttClient(wifiClient);

const long interval = 250;
unsigned long previousMillis = 0;
unsigned long sensorPreviousMillis = 0;
const int sensorPin = 7;

int count = 0;

void setup() {
  initSerial();
  connectToWiFi();
  initSensor();

  Serial.println("You're connected to the network");
  Serial.println();

  connectToMqttClient("iit_demo_33", mqtt_user, mqtt_pass);

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();
}

void loop() {
  // call poll() regularly to allow the library to send MQTT keep alives which
  // avoids being disconnected by the broker
  mqttClient.poll();

  //mqttSendTestMessage();
  sendSensorState(digitalRead(sensorPin));
}

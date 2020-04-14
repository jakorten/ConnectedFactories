/* Based on examples by: Frenoy Osburn
*/

#include <WiFiNINA.h>
#include <PubSubClient.h>
#include <CapacitiveSensor.h>
#include "credentials.h"

#define LED_PIN   13
#define SENSOR_PIN 8

bool sensorStateTouched = false;
const int sensorThreshold = 1000; // check / find with SensorTest sketch!

char subTopic[]       = "factory/indicatorLight";      // true / false will control/set LED
char pubLedTopic[]    = "factory/indicatorLightState"; // payload[0] will have control/set LED
char pubSensorTopic[] = "factory/touchSensorState";    // payload[0] will have touchSensorState value

WiFiClient wifiClient;
PubSubClient client(wifiClient);

// 1M resistor between pins 4 & 8 - add a wire and or foil if desired
CapacitiveSensor   touchSensor = CapacitiveSensor(4, SENSOR_PIN);

long lastMsg = 0;
long lastTouchMsg = 0;
char msg[50];
int value = 0;
int ledState = 0;

void setup()
{
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(115200);
  setup_wifi();
  setup_mqttServer();
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

  checkTouchSensor();
  updatePubStates();
}

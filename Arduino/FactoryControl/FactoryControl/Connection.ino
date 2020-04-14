const char* ssid = networkSSID;
const char* password = networkPASSWORD;
const char* mqttServer = mqttSERVER;
const char* mqttUsername = mqttUSERNAME;
const char* mqttPassword = mqttPASSWORD;

void setup_mqttServer() {
  client.setServer(mqttServer, 1883);
  client.setCallback(callback);
}

void setup_wifi()
{
  delay(10);

  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}


void reconnect()
{
  // Loop until we're reconnected
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ArduinoClient-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqttUsername, mqttPassword))
    {
      Serial.println("connected");
      // ... and resubscribe
      client.subscribe(subTopic);
    } else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length)
{
  String command = "";
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  for (int i = 0; i < length; i++)
  {
    command.concat((char)payload[i]);
  }
  Serial.println(command);

  // Switch on the LED if "true" was received as command

  if (command == "true")
  {
    digitalWrite(LED_PIN, HIGH);
    ledState = 1;
  }
  else
  {
    digitalWrite(LED_PIN, LOW);
    ledState = 0;
  }

  // Let's publish the changed state!
  char payLoadLedState[1];
  itoa(ledState, payLoadLedState, 10);
  client.publish(payLoadLedState, payLoadLedState);

}

void updatePubStates() {
  long now = millis();
  if (now - lastMsg > 2000)
  {
    lastMsg = now;
    char payLoadLedState[1];
    itoa(ledState, payLoadLedState, 10);
    client.publish(pubLedTopic, payLoadLedState);

    char payLoadSensorState[1];
    itoa(sensorStateTouched, payLoadSensorState, 10);
    client.publish(pubSensorTopic, payLoadSensorState);
  }
}

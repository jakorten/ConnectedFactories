/**
 * Broker: broker.hivemq.com
 * TCP Port: 1883
 * Websocket Port: 8000
 * 
 * See: https://www.instructables.com/ESP8266-Public-Free-MQTT-Broker-HiveMQ-Node-RED/
 */

char networkSSID[] = "RobotPatient";
char networkPASSWORD[] = "Toetje123!";

char mqttSERVER[] = "broker.hivemq.com";
char mqttUSERNAME[] = "iit_user";
char mqttPASSWORD[] = "Toetje123!";


/*
 Message voor in je terminal (niet die van Arduino maar van je Mac/PC/Pi):
   mosquitto_pub 
    -h broker.hivemq.com 
    -t "arduino/ledControl" 
    -u "itt_user" 
    -P "Toetje123!" 
    -m "0"
 */

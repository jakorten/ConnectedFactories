/*
  WiFi Web Server LED Blink

 A simple web server that lets you blink an LED via the web.
 This sketch will print the IP address of your WiFi module (once connected)
 to the Serial monitor. From there, you can open that address in a web browser
 to turn on and off the LED on pin 9.

 If the IP address of your board is yourAddress:
 http://yourAddress/H turns the LED on
 http://yourAddress/L turns it off

 This example is written for a network using WPA encryption. For
 WEP or WPA, change the Wifi.begin() call accordingly.

 Circuit:
 * Board with NINA module (Arduino MKR WiFi 1010, MKR VIDOR 4000 and UNO WiFi Rev.2)
 * LED attached to pin 9

 Original LED blink created 25 Nov 2012
 by Tom Igoe

 modified for the HAN Smart Industry AD by J.A. Korten
 April 1, 2020
 
 */
#include <SPI.h>
#include <WiFiNINA.h>

#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;                 // your network key Index number (needed only for WEP)
const int ledPin = 13;

int status = WL_IDLE_STATUS;
WiFiServer server(80); // server runs on port 80 (default for HTTP)

void setup() {
  initSerial();
  
  pinMode(ledPin, OUTPUT);      // set the LED pin mode

  checkWifiModule();            // check if Wifi module can be found
  checkFirmware();              // check if Firmware is up-to-date
  connectToWiFi();              // try to connect to your network (see: arduino_secrets.h)
  
  server.begin();               // start the web server on port 80
  printWifiStatus();            // you're connected now, so print out the status
}

void loop() {
  WiFiClient client = server.available();   // listen for incoming clients
  if (client) {                             // if you get a client,
    Serial.println("new client");           // print a message out the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    bool result = true;
    while (client.connected() && result) {            // loop while the client's connected
      if (client.available()) {             // if there's bytes to read from the client,
        result = serveSimpleWebsite(client, currentLine);
      }
    }
    // close the connection:
    client.stop();
    Serial.println("client disonnected");
  }
}

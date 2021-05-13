/*
  Callback LED
  This example creates a BLE peripheral with service that contains a
  characteristic to control an LED. The callback features of the
  library are used.
  The circuit:
  - Arduino MKR WiFi 1010, Arduino Uno WiFi Rev2 board, Arduino Nano 33 IoT,
    Arduino Nano 33 BLE, or Arduino Nano 33 BLE Sense board.
  You can use a generic BLE central app, like LightBlue (iOS and Android) or
  nRF Connect (Android), to interact with the services and characteristics
  created in this sketch.
  This example code is in the public domain.

  https://platformio.org/lib/show/5878/ArduinoBLE

  modified for the HAN Smart Industry AD by J.A. Korten
  April 2, 2020
  
*/

#include <ArduinoBLE.h>

BLEService ledService("19B10000-E8F2-537E-4F6C-D104768A1214"); // create service

// create switch characteristic and allow remote device to read and write
BLEByteCharacteristic switchCharacteristic("19B10001-E8F2-537E-4F6C-D104768A1214", BLERead | BLEWrite);

const int ledPin = LED_BUILTIN; // pin to use for the LED on pin 13

void setup() {
  initSerial(); // initialize communication between computer (terminal) and board
  
  pinMode(ledPin, OUTPUT); // use the LED pin as an output

  initBluetooth(); // try to initialize bluetooth
  setupBluetooth(); // do further setup

  Serial.println(("Bluetooth device active, waiting for connections..."));
}

void loop() {
  BLE.poll(); // poll for BLE events
}

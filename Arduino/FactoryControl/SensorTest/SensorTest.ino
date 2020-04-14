#include <CapacitiveSensor.h>

/*
 * CapacitativeSense Library Demo Sketch
 * Paul Badger 2008
 * Uses a high value resistor e.g. 10M between send pin and receive pin
 * Resistor effects sensitivity, experiment with values, 50K - 50M. Larger resistor values yield larger sensor values.
 * Receive pin is the sensor pin - try different amounts of foil/metal on this pin
 * 
 * Aanpassingen J.A. Korten voor AD Smart Industry 6 April, 2020
 */


CapacitiveSensor   touchSensor = CapacitiveSensor(4,8);        // 1M resistor between pins 4 & 8, pin 8 is sensor pin, add a wire and or foil if desired

void setup()                    
{
   Serial.begin(115200);
}

void loop()                    
{
    long start = millis();
    long total1 =  touchSensor.capacitiveSensor(30);
    
    Serial.print(millis() - start);        // check on performance in milliseconds
    Serial.print("\t");                    // tab character for debug windown spacing

    Serial.println(total1);                  // print sensor output 1
    

    delay(10);                             // arbitrary delay to limit data to serial port 
}

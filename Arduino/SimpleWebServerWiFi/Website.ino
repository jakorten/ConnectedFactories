bool serveSimpleWebsite(WiFiClient &client, String &currentLine) {
  char c = client.read();             // read a byte, then
  Serial.write(c);                    // print it out the serial monitor
  if (c == '\n') {                    // if the byte is a newline character

    // if the current line is blank, you got two newline characters in a row.
    // that's the end of the client HTTP request, so send a response:
    if (currentLine.length() == 0) {
      // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
      // and a content-type so the client knows what's coming, then a blank line:
      client.println("HTTP/1.1 200 OK");
      client.println("Content-type:text/html");
      client.println();

      // the content of the HTTP response follows the header:
      client.print("Look at that! A website on a tiny embedded device! <br> Way to go HAN Smart Industry students!<br><br><br>");
      
      client.print("Click <a href=\"/H\">here</a> turn the LED on pin 13 on<br>");
      client.print("Click <a href=\"/L\">here</a> turn the LED on pin 13 off<br>");

      // The HTTP response ends with another blank line:
      client.println();
      // break out of the while loop:
      return false;
    } else {    // if you got a newline, then clear currentLine:
      currentLine = "";
    }
  } else if (c != '\r') {  // if you got anything else but a carriage return character,
    currentLine += c;      // add it to the end of the currentLine
  }

  // Check to see if the client request was "GET /H" or "GET /L":
  if (currentLine.endsWith("GET /H")) {
    digitalWrite(ledPin, HIGH);               // GET /H turns the LED on
  }
  if (currentLine.endsWith("GET /L")) {
    digitalWrite(ledPin, LOW);                // GET /L turns the LED off
  }
  return true;
}

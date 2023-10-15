#include <WiFi.h>
#include <WiFiServer.h>
#include <WiFiClient.h>
#include <DHT.h>

#define DHTTYPE DHT22
#define LEDPIN 12
#define DHTPIN 13
#define BUZZER_PIN 15

const char* ssid = "startupvillage_2G";
const char* password = "startup307";

// Create an instance of the server
WiFiServer server(80);

// Create an instance of DHT sensor
DHT dht(DHTPIN, DHTTYPE);
float temp, humi;
String webString = "";
unsigned long previousMillis = 0;
const long interval = 2000;

bool alartActive = false;

void setup() {
    Serial.begin(115200);
    delay(10);
    dht.begin();
    pinMode(LEDPIN, OUTPUT);

    // Connect to WiFi network
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("WiFi connected");
    // Start the server
    server.begin();
    // Print the IP address
    Serial.println(WiFi.localIP());
}

void loop() {
    // Listen for incoming clients
    WiFiClient client = server.available();
    
    if (client) {
        Serial.println("New client");
        String currentLine = ""; // For holding incoming data
        webString = "";
        
        while (client.connected()) {
            if (client.available()) {
                char c = client.read();
                Serial.write(c);

                if (c == '\n') {
                    if (currentLine.length() == 0) {
                        client.println("HTTP/1.1 200 OK");
                        client.println("Content-type:text/html");
                        client.println();

                        client.print(webString);

                        client.println();
                        break;
                    } else {
                        currentLine = "";
                    }
                } else if (c != '\r') {
                    currentLine += c;
                }

                if (currentLine.endsWith("GET /temp")) {
                    gettemphumi();
                    webString="{\"temperature\": \"" + String(temp) + "\", \"humidity\": \"" + String(humi) + "\" }"; 
                }
                
                if (currentLine.endsWith("GET /led_on")) {
                    digitalWrite(LEDPIN, HIGH);
                    webString = "LED is now on.";
                }
                
                if (currentLine.endsWith("GET /led_off")) {
                    digitalWrite(LEDPIN, LOW);
                    webString = "LED is now off.";
                }
                
                if (currentLine.endsWith("GET /led_status")) {
                    int ledStatus = digitalRead(LEDPIN);
                    webString = "{\"status\": \"" + String(ledStatus == HIGH ? "on" : "off") + "\"}";
                }

                if (currentLine.endsWith("GET /alart_on")) {
                    alartActive = true;
                    webString = "Alart is now on.";
                }
                
                if (currentLine.endsWith("GET /alart_off")) {
                    alartActive = false;
                    webString = "Alart is now off.";
                }

                if (currentLine.endsWith("GET /alart_status")) {
                    webString = "{\"status\": \"" + String(alartActive ? "on" : "off") + "\"}";
                }
            }
        }
        delay(1);
        client.stop();
        Serial.println("client disconnected");
    }

    if (alartActive) {
        tone(BUZZER_PIN, 1500); // 1500Hz for high pitch
        delay(300); // Sound for 0.3 second
        noTone(BUZZER_PIN); // Stop sound
        delay(200); // Pause for 0.2 second
    }
}

void gettemphumi() {
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        humi = dht.readHumidity();
        temp = dht.readTemperature(false);
        
        if (isnan(humi) || isnan(temp)) {
            Serial.println("Failed to read dht sensor.");
            return;
        }
    }
}
void setup() {
    Serial.begin(9600); 
}

void loop() {
    // Generate 128 random signals between -1 and 1 at 125 Hz 
    for (int i = 0; i < 128; i++) {
        float randomSignal = random(-1000, 1001) / 1000.0; 
        Serial.println(randomSignal); 
        delay(8); 
    }
} 
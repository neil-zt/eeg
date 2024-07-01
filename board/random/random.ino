void setup() {
    Serial.begin(9600); 
}

void loop() {
    int seriesStamp = 0;
    // Generate random signals between -1 and 1 at 125 Hz 
    for (int i = 0; i < 128; i++) {
        float randomSignal = random(-1000, 1001) / 1000.0; 
        String message = "||" + String(seriesStamp) + "|" + String(randomSignal);
        Serial.println(message); 
        delay(8); 
        seriesStamp++;
        if (seriesStamp >= 100) seriesStamp = 0;
    }
} 
int NUM_CHANNELS = 8;

void setup() {
    Serial.begin(9600); 
}

void loop() {
    int seriesStamp = 0;

    // Generate 8 random signals between -1 and 1 at 125 Hz 
    for (int i = 0; i < 128; i++) {

        String message = "||" + String(seriesStamp) + "|";
        for (int j = 0; j < NUM_CHANNELS; j++) {
            float randomSignal = random(-1000, 1001) / 1000.0; 
            message += String(randomSignal) + ",";
        }

        Serial.println(message); 
        delay(8); 
        seriesStamp++;
        if (seriesStamp >= 100) seriesStamp = 0;
    }
} 
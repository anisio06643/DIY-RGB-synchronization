#include <FastLED.h>

#define NUM_LEDS 3
#define DATA_PIN 4  // Change to your data pin
CRGB leds[NUM_LEDS];

void setup() {
  Serial.begin(115200);
  // Ensure your color correction configuration matches your specific strip layout (usually GRB)
  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS); 
  FastLED.clear();
  FastLED.show();
}

void loop() {
  // We need at least 3 header bytes + 9 color bytes = 12 bytes
  if (Serial.available() >= 12) {
    // Check if incoming stream aligns with our magic prefix
    if (Serial.read() == 'M' && Serial.read() == 'G' && Serial.read() == 'K') {
      
      byte colorBuffer[9];
      Serial.readBytes(colorBuffer, 9);
      
      // Map the raw data arrays back safely to your layout regions
      leds[0] = CRGB(colorBuffer[0], colorBuffer[1], colorBuffer[2]);
      leds[1] = CRGB(colorBuffer[3], colorBuffer[4], colorBuffer[5]);
      leds[2] = CRGB(colorBuffer[6], colorBuffer[7], colorBuffer[8]);
      
      FastLED.show();
    }
  }
}

#include "arduinoFFT.h"

int SAMPLES = 512;
#define SAMPLING_FREQUENCY 10000

arduinoFFT FFT = arduinoFFT();
unsigned int sampling_period_us;
double vReal[4096];
double vImag[4096];
byte opcao;
int escolha = 1;
int i, j;

// Filter threshold for the high-pass filter (cutoff frequency)
const float FILTER_THRESHOLD = 100; // in Hz

void applyHighPassFilter() {
  // First high-pass filter application
  for (j = 0; j < (SAMPLES / 2); j++) {
    float frequency = (j * 1.0 * SAMPLING_FREQUENCY) / SAMPLES;
    if (frequency < FILTER_THRESHOLD) {
      vReal[j] = 0;  // Zero out low-frequency components
    }
  }
  
  // Perform FFT again to refine the filtering
  FFT.Windowing(vReal, SAMPLES, FFT_WIN_TYP_HANN, FFT_FORWARD);
  FFT.Compute(vReal, vImag, SAMPLES, FFT_FORWARD);
  FFT.ComplexToMagnitude(vReal, vImag, SAMPLES);
  
  // Apply high-pass filter again to further remove low-frequency components
  for (j = 0; j < (SAMPLES / 2); j++) {
    float frequency = (j * 1.0 * SAMPLING_FREQUENCY) / SAMPLES;
    if (frequency < FILTER_THRESHOLD) {
      vReal[j] = 0;  // Zero out low-frequency components again
    }
  }
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  sampling_period_us = round(1000000 * (1.0 / SAMPLING_FREQUENCY));
}

void loop() {
  if (Serial.available() > 0) {
    opcao = Serial.read();
  }
  
  switch (opcao) {
    case 'A': // Start FFT analysis
      // Read the signal sent by Python
      for (i = 0; i < SAMPLES; i++) {
        while (Serial.available() == 0); // Wait until data is available
        vReal[i] = Serial.parseFloat();  // Read the value from serial
        vImag[i] = 0;                    // Set imaginary part to 0
      }

      /* Apply FFT and Filter */
      FFT.Windowing(vReal, SAMPLES, FFT_WIN_TYP_HANN, FFT_FORWARD);
      FFT.Compute(vReal, vImag, SAMPLES, FFT_FORWARD);
      FFT.ComplexToMagnitude(vReal, vImag, SAMPLES);

      // Apply high-pass filter twice for more precision
      applyHighPassFilter();

      // Send the FFT results (filtered) back to Python
      for (j = 0; j < (SAMPLES / 2); j++) {
        float frequency = (j * 1.0 * SAMPLING_FREQUENCY) / SAMPLES;
        Serial.print(frequency);
        Serial.print(",");
        Serial.println(vReal[j]);
      }

      opcao = 100;  // Reset opcao
      break;
  }
}

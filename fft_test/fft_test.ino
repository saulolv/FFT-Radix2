#include "arduinoFFT.h" // importa a biblioteca da transformada de Fourier

int SAMPLES = 128; // número de amostras, deve ser uma potência de 2 (2^n)
#define SAMPLING_FREQUENCY 10000 // Hertz, deve ser menor que 10000

ArduinoFFT<double> FFT = ArduinoFFT<double>();  

unsigned int sampling_period_us; // variável para definir o tempo entre cada medição
unsigned long microseconds; // variável para a contagem do tempo
unsigned long tempo;
double vReal[128];
double vImag[128];
byte opcao;
int N, escolha = 1;
int i, j, k;
float kk;

// Substitua por valores do tipo FFTWindow
FFTWindow apodizacao[] = {FFT_WIN_TYP_RECTANGLE, FFT_WIN_TYP_HAMMING, FFT_WIN_TYP_HANN, 
                          FFT_WIN_TYP_TRIANGLE, FFT_WIN_TYP_NUTTALL,
                          FFT_WIN_TYP_BLACKMAN, FFT_WIN_TYP_BLACKMAN_NUTTALL, 
                          FFT_WIN_TYP_BLACKMAN_HARRIS, FFT_WIN_TYP_FLT_TOP, 
                          FFT_WIN_TYP_WELCH}; // Defina janelas corretas

void setup() {
  Serial.begin(115200);
  sampling_period_us = round(1000000 * (1.0 / SAMPLING_FREQUENCY));
}

void loop() {
  if (Serial.available() > 0) {
    opcao = Serial.read();
  }
  switch (opcao) {
    case 'E':
      SAMPLES = Serial.parseInt();
      escolha = Serial.parseInt();
      Serial.print(SAMPLES);
      opcao = 100;
      break;
    case 'A':
      tempo = millis();
      if (Serial.available() > 0) {
        if (Serial.read() == 'C') {
          i = 0;
          j = 0;
          opcao = 100;
          break;
        }
      }
      /* SAMPLING */
      for (i = 0; i < SAMPLES; i++) {
        microseconds = micros();
        vReal[i] = analogRead(0); // Certifique-se de que esta leitura é necessária
        vImag[i] = 0;

        while (micros() < (microseconds + sampling_period_us)) {
        }
      }

      for (k = 0; k < SAMPLES; k++) {
        kk = (k * 0.1); // ajuste conforme necessário
        Serial.print(kk, 6);
        Serial.print(",");
        Serial.println(vReal[k]);
      }
      
      /* FFT */
      FFT.windowing(vReal, SAMPLES, apodizacao[escolha], FFT_FORWARD);
      FFT.compute(vReal, vImag, SAMPLES, FFT_FORWARD);
      FFT.complexToMagnitude(vReal, vImag, SAMPLES);

      for (j = 0; j < (SAMPLES / 2); j++) {
        Serial.print((j * 1.0 * SAMPLING_FREQUENCY) / SAMPLES, 1);
        Serial.print(",");
        Serial.print(vReal[j], 1);
        Serial.print("\n");
      }
      opcao = 100;
      break;
  }
}

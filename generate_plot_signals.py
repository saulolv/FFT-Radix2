import serial
import numpy as np
import matplotlib.pyplot as plt
import time

# Constants
SAMPLES = 512
SAMPLING_FREQUENCY = 10000  # Hz
AMPLITUDE = 1000
SIGNAL_FREQUENCY = 500  # Main signal frequency (Hz)
FILTER_THRESHOLD = 100  # High-pass filter cutoff (Hz)

# Function to generate the signal
def generate_signal(frequency, amplitude, sampling_frequency, samples):
    t = np.linspace(0, samples / sampling_frequency, samples, endpoint=False)
    signal = amplitude * np.sin(2 * np.pi * frequency * t)
    return signal

# Function to generate low-frequency noise
def generate_noise(frequencies, amplitude, sampling_frequency, samples):
    t = np.linspace(0, samples / sampling_frequency, samples, endpoint=False)
    noise = np.zeros(samples)
    for freq in frequencies:
        noise += amplitude * np.sin(2 * np.pi * freq * t)
    return noise

# Establish serial communication
ser = serial.Serial('COM3', 115200)  # Adjust to your Arduino port
time.sleep(2)  # Wait for the serial connection to initialize

# Generate signal and noise
signal = generate_signal(SIGNAL_FREQUENCY, AMPLITUDE, SAMPLING_FREQUENCY, SAMPLES)
low_noise_frequencies = [10, 30, 60, 100]  # Low-frequency noise components
noise = generate_noise(low_noise_frequencies, 200, SAMPLING_FREQUENCY, SAMPLES)

# Combine signal and noise
noisy_signal = signal + noise

# Send signal to Arduino
ser.write(b'A')  # Tell Arduino to start processing
for value in noisy_signal:
    ser.write(f"{value}\n".encode())  # Send noisy signal via serial

# Receive FFT results from Arduino
frequencies = []
magnitudes = []
while True:
    line = ser.readline().decode().strip()
    if line:
        try:
            freq, mag = map(float, line.split(','))
            frequencies.append(freq)
            magnitudes.append(mag)
        except ValueError:
            break

# Close serial connection
ser.close()

# Plot FFT results received from Arduino
plt.figure(figsize=(10, 6))
plt.plot(frequencies, magnitudes, label="Filtered FFT")
plt.axvline(FILTER_THRESHOLD, color='red', linestyle='--', label="Filter Cutoff")
plt.title("Filtered FFT Results from Arduino")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude")
plt.grid(True)
plt.legend()
plt.show()

import serial
import numpy as np
import matplotlib.pyplot as plt
import time

# Constants
SAMPLES = 512
SAMPLING_FREQUENCY = 10000  # Hz
AMPLITUDE = 500
SIGNAL_FREQUENCY = 500  # Main signal frequency (Hz)
HIGH_NOISE_FREQUENCIES = [800, 900, 1000]  # Frequências altas de ruído

# Function to generate the signal
def generate_signal(frequency, amplitude, sampling_frequency, samples):
    t = np.linspace(0, samples / sampling_frequency, samples, endpoint=False)
    signal = amplitude * np.sin(2 * np.pi * frequency * t)
    return signal

# Function to generate high-frequency noise
def generate_noise(frequencies, amplitude, sampling_frequency, samples):
    t = np.linspace(0, samples / sampling_frequency, samples, endpoint=False)
    noise = np.zeros(samples)
    for freq in frequencies:
        noise += amplitude * np.sin(2 * np.pi * freq * t)
    return noise

# Estabelece comunicação serial
ser = serial.Serial('COM6', 115200)  # Ajuste para a porta correta
print("Comunicação serial estabelecida.")
time.sleep(2)  # Aguarda a inicialização da conexão

# Gerar sinal e ruído
signal = generate_signal(SIGNAL_FREQUENCY, AMPLITUDE, SAMPLING_FREQUENCY, SAMPLES)
noise = generate_noise(HIGH_NOISE_FREQUENCIES, 300, SAMPLING_FREQUENCY, SAMPLES)  # Ruído alto
noisy_signal = signal + noise

# Enviar sinal ao Arduino
print("Enviando sinal...")
ser.write(b'A')
print("Sinal enviado. Aguardando resposta...")

for value in noisy_signal:
    ser.write(f"{value}\n".encode())
    time.sleep(0.01)

# Receber os resultados da FFT
frequencies = []
magnitudes = []

print("Aguardando dados do Arduino...")

max_lines = 128  # Número máximo de linhas a ler
line_count = 0

while line_count < max_lines:
    line = ser.readline().decode().strip()
    if not line:
        break
    print(f"Linha recebida: {line}")
    try:
        freq, mag = map(float, line.split(','))
        frequencies.append(freq)
        magnitudes.append(mag)
        line_count += 1  # Incrementa o contador
    except ValueError:
        break

print(f"Número de frequências recebidas: {len(frequencies)}")
print(f"Número de magnitudes recebidas: {len(magnitudes)}")
# Fechar a comunicação serial
ser.close()

# Verifica se os dados foram recebidos
if len(frequencies) == 0 or len(magnitudes) == 0:
    print("Nenhum dado foi recebido.")
else:
    # Plota os resultados da FFT
    plt.figure(figsize=(10, 8))

    # Plot do sinal original
    plt.subplot(3, 1, 1)
    plt.plot(np.linspace(0, SAMPLES/SAMPLING_FREQUENCY, SAMPLES), noisy_signal, label="Sinal Ruidoso")
    plt.title("Sinal Ruidoso")
    plt.xlabel("Tempo [s]")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()

    # Plot da FFT
    plt.subplot(3, 1, 2)
    plt.plot(frequencies, magnitudes, label="FFT do Sinal", color='orange')
    plt.axvline(1000, color='red', linestyle='--', label="Filtro passa-baixa")
    plt.title("Resultados da FFT")
    plt.xlabel("Frequência [Hz]")
    plt.ylabel("Magnitude")
    plt.grid(True)
    plt.legend()

    # Adicionar um gráfico de comparação do sinal original
    plt.subplot(3, 1, 3)
    plt.plot(np.linspace(0, SAMPLES/SAMPLING_FREQUENCY, SAMPLES), signal, label="Sinal Original", color='green')
    plt.title("Sinal Original")
    plt.xlabel("Tempo [s]")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()

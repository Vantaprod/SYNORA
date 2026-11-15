import numpy as np
import soundfile as sf

# Create a 3-second audio file at 16kHz
samplerate = 16000
duration = 3.0
t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)

# Generate a synthetic voice-like harmonic tone
data = 0.1 * np.sin(2 * np.pi * 220 * t) + 0.05 * np.sin(2 * np.pi * 440 * t)

# Write as a standard 16-bit PCM WAV file
sf.write('target.wav', data, samplerate, subtype='PCM_16')
print("Successfully created a valid, readable target.wav file.")

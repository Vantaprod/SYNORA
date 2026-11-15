import time
import queue
import threading
import numpy as np
import sounddevice as sd
import torch
import os

# --- Audio Configuration ---
SAMPLE_RATE = 16000
CHUNK_MS = 40
CHUNK_SAMPLES = int(SAMPLE_RATE * (CHUNK_MS / 1000.0))
CHANNELS = 1

audio_in_queue = queue.Queue()
audio_out_queue = queue.Queue()

print("Bypassing model loading. Running pass-through test...")

# Mock model to verify the tensor shapes are fixed
class MockModel(torch.nn.Module):
    def forward(self, x):
        return x # Pass-through

model = MockModel()
model.eval()

def audio_callback(indata, outdata, frames, time_info, status):
    if status:
        pass
    audio_in_queue.put(indata.copy())
    try:
        processed_chunk = audio_out_queue.get_nowait()
        outdata[:] = processed_chunk
    except queue.Empty:
        outdata.fill(0)

def processing_thread():
    while True:
        try:
            in_chunk = audio_in_queue.get(timeout=1.0)
            t_start = time.perf_counter()
            
            # 1. Convert numpy to tensor (Shape is (640, 1))
            tensor_in = torch.from_numpy(in_chunk).float()
            
            # 2. Transpose to (1, 640) for the model
            tensor_in = tensor_in.T
            
            with torch.no_grad():
                tensor_out = model(tensor_in)
            
            # 3. Transpose back to (640, 1) for audio output
            out_chunk = tensor_out.T.numpy().astype(np.float32)
            
            t_end = time.perf_counter()
            latency_ms = (t_end - t_start) * 1000
            
            audio_out_queue.put(out_chunk)
            
            # Print occasionally to avoid spamming the console
            if int(t_start * 10) % 10 == 0:
                print(f"Inference done. Latency: {latency_ms:.2f} ms")
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Processing error: {e}")
            time.sleep(0.1)

if __name__ == "__main__":
    print("Starting Pipeline...")
    t = threading.Thread(target=processing_thread, daemon=True)
    t.start()
    
    try:
        with sd.Stream(samplerate=SAMPLE_RATE, 
                       blocksize=CHUNK_SAMPLES, 
                       channels=CHANNELS, 
                       callback=audio_callback):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nTest stopped.")

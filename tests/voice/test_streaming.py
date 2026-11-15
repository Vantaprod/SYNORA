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
CHUNK_SAMPLES = int(SAMPLE_RATE * (CHUNK_MS / 1000.0)) # 640 samples
CHANNELS = 1

# --- Model Paths ---
MODEL_PATH = "models/downloaded/meanvc2_40ms.safetensors"
VOCODER_PATH = "models/downloaded/vocos.pt"

# --- Queues for pipeline ---
audio_in_queue = queue.Queue()
audio_out_queue = queue.Queue()

# Load models globally so they are ready for the processing thread
print("Loading AI Models... (This may take a few seconds)")
# We simulate the loading to verify PyTorch is working
if not os.path.exists(MODEL_PATH):
    print(f"ERROR: Could not find {MODEL_PATH}. Did you run the download script?")
    exit(1)

# In a full implementation, we would load the weights here:
# model = load_meanvc2(MODEL_PATH)
# vocoder = load_vocos(VOCODER_PATH)

# For this test, we just create a dummy PyTorch tensor to simulate the AI compute
dummy_model_weights = torch.randn(18, 1024) # 18M params is roughly this size in a dense layer

def audio_callback(indata, outdata, frames, time_info, status):
    if status:
        print(f"Audio Status: {status}")
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
            
            # --- SIMULATED MEANVC2 INFERENCE ---
            # Convert numpy array to PyTorch tensor
            tensor_in = torch.from_numpy(in_chunk).float()
            
            # Simulate the model computation (Matrix multiplication)
            # This forces PyTorch to use the CPU exactly like the real model would
            tensor_out = torch.matmul(dummy_model_weights[:1, :], dummy_model_weights[:1, :].T) * tensor_in[0,0]
            
            # Simulate the model taking ~30ms to process a chunk
            time.sleep(0.030) 
            
            # Convert back to numpy for audio output
            out_chunk = tensor_out.numpy().astype(np.float32)
            # -----------------------------------
            
            t_end = time.perf_counter()
            latency_ms = (t_end - t_start) * 1000
            
            # Pad or trim the output to match expected chunk size
            if len(out_chunk) < CHUNK_SAMPLES:
                out_chunk = np.pad(out_chunk, (0, CHUNK_SAMPLES - len(out_chunk)))
            else:
                out_chunk = out_chunk[:CHUNK_SAMPLES]
                
            audio_out_queue.put(out_chunk.reshape(-1, 1))
            
            print(f"AI Chunk processed. Total latency: {latency_ms:.2f} ms")
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Processing error: {e}")

if __name__ == "__main__":
    print(f"Sample Rate: {SAMPLE_RATE} Hz | Chunk: {CHUNK_MS}ms")
    print("Starting Real-time Pipeline...")
    
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
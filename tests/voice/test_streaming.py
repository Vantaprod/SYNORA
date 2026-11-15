"""
Voice Engine Test: Real-time Microphone Streaming Loop
Target: MeanVC2 (18M params, 40ms chunks)
Hardware: Beelink SER8 (CPU only)
"""

import time
import queue
import threading
import numpy as np
import sounddevice as sd

# --- Audio Configuration ---
SAMPLE_RATE = 16000
CHUNK_MS = 40
CHUNK_SAMPLES = int(SAMPLE_RATE * (CHUNK_MS / 1000.0)) # 640 samples
CHANNELS = 1

# --- Queues for pipeline ---
audio_in_queue = queue.Queue()
audio_out_queue = queue.Queue()

def audio_callback(indata, outdata, frames, time_info, status):
    """Called by sounddevice for every audio block."""
    if status:
        print(f"Audio Status: {status}")
    
    # Push raw input to the processing queue
    audio_in_queue.put(indata.copy())
    
    # Pull processed audio from output queue (or output silence if empty)
    try:
        processed_chunk = audio_out_queue.get_nowait()
        outdata[:] = processed_chunk
    except queue.Empty:
        outdata.fill(0) # Output silence if inference hasn't caught up

def mock_inference(chunk):
    """
    Placeholder for MeanVC2 inference.
    For now, just returns the input chunk to prove the pipeline works.
    """
    return chunk

def processing_thread():
    """Worker thread that simulates the AI inference loop."""
    while True:
        try:
            # 1. Get a 40ms chunk from microphone
            in_chunk = audio_in_queue.get(timeout=1.0)
            
            # 2. Timestamp BEFORE inference
            t_start = time.perf_counter()
            
            # 3. Run inference
            out_chunk = mock_inference(in_chunk)
            
            # 4. Timestamp AFTER inference
            t_end = time.perf_counter()
            latency_ms = (t_end - t_start) * 1000
            
            # 5. Push to output queue
            audio_out_queue.put(out_chunk)
            
            print(f"Chunk processed. Inference latency: {latency_ms:.2f} ms")
            
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Processing error: {e}")

if __name__ == "__main__":
    print("Starting MeanVC2 Streaming Test...")
    print(f"Sample Rate: {SAMPLE_RATE} Hz | Chunk Size: {CHUNK_SAMPLES} samples ({CHUNK_MS}ms)")
    print("Speak into your microphone. You should hear yourself with a slight delay.")
    print("Press Ctrl+C to stop.\n")
    
    # Start the processing thread
    t = threading.Thread(target=processing_thread, daemon=True)
    t.start()
    
    # Start the audio stream (full duplex)
    try:
        with sd.Stream(samplerate=SAMPLE_RATE, 
                       blocksize=CHUNK_SAMPLES, 
                       channels=CHANNELS, 
                       callback=audio_callback):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nTest stopped.")
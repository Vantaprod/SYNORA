import subprocess
import os
import sys
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SYNORA Voice Engine API")

# Allow Tauri/React to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

voice_process = None

class VoiceConfig(BaseModel):
    target_wav: str = "target.wav"
    device: str = "cpu"
    model_size: str = "40ms"

@app.get("/status")
def get_status():
    global voice_process
    if voice_process is not None and voice_process.poll() is None:
        return {"status": "running", "pid": voice_process.pid}
    return {"status": "stopped"}

@app.post("/start")
def start_voice_conversion(config: VoiceConfig):
    global voice_process
    
    if voice_process is not None and voice_process.poll() is None:
        raise HTTPException(status_code=400, detail="Voice conversion is already running.")
    
    if not os.path.exists(config.target_wav):
        raise HTTPException(status_code=404, detail=f"Target file {config.target_wav} not found.")

    cmd = [
        sys.executable, 
        "vendor/meanvc2/runtime/run_rt.py",
        "--model", config.model_size,
        "--target-spk", config.target_wav,
        "--mode", "realtime",
        "--device", config.device
    ]

    try:
        voice_process = subprocess.Popen(cmd)
        time.sleep(2.0)
        if voice_process.poll() is not None:
            voice_process = None
            raise HTTPException(status_code=500, detail="AI Engine crashed on startup. Check API terminal logs.")
        return {"status": "started", "pid": voice_process.pid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop")
def stop_voice_conversion():
    global voice_process
    if voice_process is None or voice_process.poll() is not None:
        raise HTTPException(status_code=400, detail="Voice conversion is not running.")
    try:
        voice_process.terminate()
        voice_process.wait(timeout=5)
        voice_process = None
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop process: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)

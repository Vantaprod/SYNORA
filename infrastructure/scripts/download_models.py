import os
import urllib.request

MODEL_DIR = "models/downloaded"
os.makedirs(MODEL_DIR, exist_ok=True)

# The API revealed the exact names are: meanvc2_40ms_40ms.safetensors and vocos.pt
models_to_download = {
    "meanvc2_40ms_40ms.safetensors": "https://huggingface.co/ASLP-lab/MeanVC2/resolve/main/meanvc2_40ms_40ms.safetensors",
    "vocos.pt": "https://huggingface.co/ASLP-lab/MeanVC2/resolve/main/vocos.pt"
}

def download_file(url, filepath):
    print(f"Downloading {url}...")
    urllib.request.urlretrieve(url, filepath)
    print(f"Saved to {filepath}")

if __name__ == "__main__":
    print("Starting model download...")
    for filename, url in models_to_download.items():
        filepath = os.path.join(MODEL_DIR, filename)
        if os.path.exists(filepath):
            print(f"{filename} already exists. Skipping.")
        else:
            try:
                download_file(url, filepath)
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
    print("Download process complete.")

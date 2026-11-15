import os
import urllib.request

def download_file(url, filepath):
    if os.path.exists(filepath):
        print(f"{filepath} already exists. Skipping.")
        return
    print(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"Saved to {filepath}")
    except Exception as e:
        print(f"Failed to download {filepath}: {e}")

if __name__ == "__main__":
    print("Downloading missing MeanVC2 components...")
    
    # Download ASR model
    download_file(
        "https://huggingface.co/ASLP-lab/MeanVC2/resolve/main/fastu2pp_80ms.pt",
        "vendor/meanvc2/preprocess/ckpts/fastu2pp_80ms.pt"
    )
    
    # Download Config
    download_file(
        "https://huggingface.co/ASLP-lab/MeanVC2/resolve/main/config_40ms_40ms.json",
        "vendor/meanvc2/src/config/config_40ms_40ms.json"
    )

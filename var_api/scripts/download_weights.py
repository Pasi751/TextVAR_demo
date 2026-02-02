# ===== backend/scripts/download_weights.py =====

"""Download model weights from Hugging Face Hub"""

import os
from huggingface_hub import hf_hub_download

# Configuration
REPO_ID = "mpm751/textvar-demo"
CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), "..", "checkpoints")

def download_weights():
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    
    print(f"Downloading weights from {REPO_ID}...")
    
    # Download VAR checkpoint
    var_path = hf_hub_download(
        repo_id=REPO_ID,
        filename="ckpt_best.pth",
        local_dir=CHECKPOINT_DIR
    )
    print(f"✓ VAR weights: {var_path}")
    
    # Download VAE checkpoint
    vae_path = hf_hub_download(
        repo_id=REPO_ID,
        filename="vae_ch160v4096z32.pth",
        local_dir=CHECKPOINT_DIR
    )
    print(f" VAE weights: {vae_path}")
    
    print("\n All weights downloaded successfully!")

if __name__ == "__main__":
    download_weights()
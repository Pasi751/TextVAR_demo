# ===== app/config.py =====

import os
from pathlib import Path
from dataclasses import dataclass, field
import torch

@dataclass
class ModelConfig:
    """VAR Model configuration"""
    var_depth: int = 12
    var_embed_dim: int = 768
    var_num_heads: int = 12
    var_mlp_ratio: float = 4.0
    var_drop_path: float = 0.05
    var_attn_l2_norm: bool = True
    var_cond_drop: float = 0.0
    
    n_cond_embed: int = 768
    patch_nums: tuple = (1, 2, 3, 4, 5, 6, 8, 10, 13, 16)
    vocab_size: int = 4096
    Cvae: int = 32
    ch: int = 160


@dataclass 
class AppConfig:
    """Application configuration"""
    # HF Hub repository for weights
    hf_repo_id: str = "mpm751/textvar-demo"  # UPDATE THIS
    
    # Local cache paths
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".cache" / "var-model")
    
    # Device
    device: str = field(default_factory=lambda: "cuda" if torch.cuda.is_available() else "cpu")
    
    # Paths (will be set after download)
    model_path: Path = None
    vae_path: Path = None
    
    def download_weights(self):
        """Download weights from HF Hub if not cached"""
        from huggingface_hub import hf_hub_download
        
        os.makedirs(self.cache_dir, exist_ok=True)
        
        print(f"Downloading weights from {self.hf_repo_id}...")
        
        # Download VAR checkpoint
        self.model_path = Path(hf_hub_download(
            repo_id=self.hf_repo_id,
            filename="ckpt_best.pth",
            cache_dir=self.cache_dir
        ))
        print(f"✓ VAR weights: {self.model_path}")
        
        # Download VAE checkpoint
        self.vae_path = Path(hf_hub_download(
            repo_id=self.hf_repo_id,
            filename="vae_ch160v4096z32.pth",
            cache_dir=self.cache_dir
        ))
        print(f"✓ VAE weights: {self.vae_path}")


model_config = ModelConfig()
app_config = AppConfig()

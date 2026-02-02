# ===== app/config.py =====

import os
from pathlib import Path
from dataclasses import dataclass
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
    var_cond_drop: float = 0.0  # No dropout during inference
    
    # VQVAE config
    n_cond_embed: int = 768
    patch_nums: tuple = (1, 2, 3, 4, 5, 6, 8, 10, 13, 16)
    vocab_size: int = 4096
    Cvae: int = 32
    ch: int = 160


@dataclass
class AppConfig:
    """Application configuration"""
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    checkpoints_dir: Path = None
    model_path: Path = None
    vae_path: Path = None
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Device
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Generation defaults
    default_cfg_scale: float = 1.5
    default_top_k: int = 900
    default_top_p: float = 0.96
    max_batch_size: int = 8
    
    def __post_init__(self):
        self.checkpoints_dir = self.base_dir / "checkpoints"
        self.model_path = self.checkpoints_dir / "ckpt_best.pth"
        self.vae_path = self.checkpoints_dir / "vae_ch160v4096z32.pth"


# Global config instances
model_config = ModelConfig()
app_config = AppConfig()
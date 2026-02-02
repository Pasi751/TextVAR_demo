# ===== app/services/generator.py =====

import io
import base64
from typing import List, Optional, Tuple
import numpy as np
from PIL import Image

import torch
import torch.nn.functional as F
import open_clip

from app.config import app_config, model_config
from app.models import VQVAE, VAR


class ImageGenerator:
    """Service for generating images from text prompts"""
    
    def __init__(self):
        self.device = torch.device(app_config.device)
        self.vae: Optional[VQVAE] = None
        self.var: Optional[VAR] = None
        self.clip_model = None
        self.tokenizer = None
        self._loaded = False
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    def load_models(self):
        """Load all required models"""
        print(f"Loading models on device: {self.device}")
        
        # Download weights first
        print("Downloading weights from HF Hub...")
        app_config.download_weights()
        
        # Load VAE
        print("Loading VAE...")
        self.vae = VQVAE(
            vocab_size=model_config.vocab_size,
            z_channels=model_config.Cvae,
            ch=model_config.ch,
            v_patch_nums=model_config.patch_nums,
            test_mode=True
        ).to(self.device)
        
        vae_state = torch.load(app_config.vae_path, map_location='cpu', weights_only=False)
        self.vae.load_state_dict(vae_state, strict=False)
        self.vae.eval()
        print("✓ VAE loaded")
        
        # Load VAR
        print("Loading VAR...")
        self.var = VAR(
            vae_local=self.vae,
            n_cond_embed=model_config.n_cond_embed,
            depth=model_config.var_depth,
            embed_dim=model_config.var_embed_dim,
            num_heads=model_config.var_num_heads,
            mlp_ratio=model_config.var_mlp_ratio,
            drop_rate=0.,
            attn_drop_rate=0.,
            drop_path_rate=model_config.var_drop_path,
            attn_l2_norm=model_config.var_attn_l2_norm,
            cond_drop_rate=model_config.var_cond_drop,
            patch_nums=model_config.patch_nums,
        ).to(self.device)
        
        var_state = torch.load(app_config.model_path, map_location='cpu', weights_only=False)
        self.var.load_state_dict(var_state['model'])
        self.var.eval()
        print("✓ VAR loaded")
        
        # Load CLIP
        print("Loading CLIP...")
        self.clip_model, _, _ = open_clip.create_model_and_transforms(
            'ViT-L-14', 
            pretrained='laion2b_s32b_b82k'
        )
        self.clip_model = self.clip_model.to(self.device).eval()
        self.tokenizer = open_clip.get_tokenizer('ViT-L-14')
        print("✓ CLIP loaded")
        
        self._loaded = True
        print("\n✓ All models loaded successfully!")

    
    @torch.no_grad()
    def encode_text(self, texts: List[str]) -> torch.Tensor:
        """Encode text prompts using CLIP"""
        tokens = self.tokenizer(texts).to(self.device)
        emb = self.clip_model.encode_text(tokens)
        return F.normalize(emb, dim=-1).float()
    
    @staticmethod
    def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
        """Convert tensor to PIL Image"""
        img = tensor.cpu().numpy()
        img = (img * 255).clip(0, 255).astype(np.uint8)
        img = img.transpose(1, 2, 0)  # CHW -> HWC
        return Image.fromarray(img)
    
    @staticmethod
    def pil_to_base64(img: Image.Image, format: str = "PNG") -> str:
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def pil_to_bytes(img: Image.Image, format: str = "PNG") -> bytes:
        """Convert PIL Image to bytes"""
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate(
        self,
        prompt: str,
        cfg_scale: float = 1.5,
        top_k: int = 900,
        top_p: float = 0.96,
        seed: Optional[int] = None
    ) -> Tuple[Image.Image, dict]:
        """
        Generate a single image from text prompt
        
        Returns:
            Tuple of (PIL Image, generation parameters)
        """
        if not self._loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        # Encode text
        text_emb = self.encode_text([prompt])
        
        # Generate
        with torch.no_grad():
            image_tensor = self.var.generate(
                text_emb,
                cfg=cfg_scale,
                top_k=top_k,
                top_p=top_p,
                seed=seed
            )[0]
        
        # Convert to PIL
        pil_image = self.tensor_to_pil(image_tensor)
        
        params = {
            "prompt": prompt,
            "cfg_scale": cfg_scale,
            "top_k": top_k,
            "top_p": top_p,
            "seed": seed
        }
        
        return pil_image, params
    
    def generate_batch(
        self,
        prompts: List[str],
        cfg_scale: float = 1.5,
        top_k: int = 900,
        top_p: float = 0.96,
        seed: Optional[int] = None
    ) -> Tuple[List[Image.Image], dict]:
        """
        Generate multiple images from text prompts
        
        Returns:
            Tuple of (list of PIL Images, generation parameters)
        """
        if not self._loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        if len(prompts) > app_config.max_batch_size:
            raise ValueError(f"Maximum {app_config.max_batch_size} prompts allowed")
        
        # Encode texts
        text_emb = self.encode_text(prompts)
        
        # Generate
        with torch.no_grad():
            image_tensors = self.var.generate(
                text_emb,
                cfg=cfg_scale,
                top_k=top_k,
                top_p=top_p,
                seed=seed
            )
        
        # Convert to PIL
        pil_images = [self.tensor_to_pil(t) for t in image_tensors]
        
        params = {
            "cfg_scale": cfg_scale,
            "top_k": top_k,
            "top_p": top_p,
            "seed": seed
        }
        
        return pil_images, params


# Global generator instance
generator = ImageGenerator()

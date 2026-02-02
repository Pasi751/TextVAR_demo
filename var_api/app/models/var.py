# ===== app/models/var.py =====

"""VAR (Visual AutoRegressive) model"""

import math
from typing import Tuple, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F

from .components import AdaLNSelfAttn, AdaLNBeforeHead
from .vae import VQVAE


class VAR(nn.Module):
    """Visual AutoRegressive Model for text-to-image generation"""
    
    def __init__(
        self, 
        vae_local: VQVAE, 
        n_cond_embed: int = 768, 
        depth: int = 16, 
        embed_dim: int = 1024, 
        num_heads: int = 16,
        mlp_ratio: float = 4., 
        drop_rate: float = 0., 
        attn_drop_rate: float = 0., 
        drop_path_rate: float = 0.1,
        attn_l2_norm: bool = True, 
        cond_drop_rate: float = 0.1, 
        patch_nums: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 8, 10, 13, 16)
    ):
        super().__init__()
        
        self.Cvae = vae_local.Cvae
        self.V = vae_local.vocab_size
        self.depth = depth
        self.C = embed_dim
        self.D = embed_dim
        self.num_heads = num_heads
        self.cond_drop_rate = cond_drop_rate
        
        self.patch_nums = patch_nums
        self.L = sum(pn ** 2 for pn in patch_nums)
        self.first_l = patch_nums[0] ** 2
        self.num_stages_minus_1 = len(patch_nums) - 1
        
        # Store VAE reference (not as parameter)
        self.vae_proxy = (vae_local,)
        self.vae_quant_proxy = (vae_local.quantize,)
        
        # Word embedding
        self.word_embed = nn.Linear(self.Cvae, self.C)
        
        # Position start token
        init_std = math.sqrt(1 / self.C / 3)
        self.pos_start = nn.Parameter(torch.empty(1, self.first_l, self.C))
        nn.init.trunc_normal_(self.pos_start, std=init_std)
        
        # Condition embedding
        self.noise = nn.Embedding(1, n_cond_embed)
        nn.init.trunc_normal_(self.noise.weight, std=init_std)
        self.cond_proj = nn.Linear(n_cond_embed, self.C)
        
        # Position embeddings
        pos_1LC = []
        for pn in patch_nums:
            pe = torch.empty(1, pn * pn, self.C)
            nn.init.trunc_normal_(pe, std=init_std)
            pos_1LC.append(pe)
        self.pos_1LC = nn.Parameter(torch.cat(pos_1LC, dim=1))
        
        # Level embedding
        self.lvl_embed = nn.Embedding(len(patch_nums), self.C)
        nn.init.trunc_normal_(self.lvl_embed.weight, std=init_std)
        
        # Transformer blocks
        dpr = [x.item() for x in torch.linspace(0, drop_path_rate, depth)]
        self.blocks = nn.ModuleList([
            AdaLNSelfAttn(
                embed_dim=self.C, 
                cond_dim=self.D, 
                num_heads=num_heads,
                mlp_ratio=mlp_ratio, 
                drop=drop_rate, 
                attn_drop=attn_drop_rate,
                drop_path=dpr[i], 
                attn_l2_norm=attn_l2_norm
            ) 
            for i in range(depth)
        ])
        
        # Attention mask
        d = torch.cat([torch.full((pn*pn,), i) for i, pn in enumerate(patch_nums)]).view(1, self.L, 1)
        dT = d.transpose(1, 2)
        lvl_1L = dT[:, 0].contiguous()
        self.register_buffer('lvl_1L', lvl_1L)
        attn_bias = torch.where(d >= dT, 0., -torch.inf).reshape(1, 1, self.L, self.L)
        self.register_buffer('attn_bias_for_masking', attn_bias.contiguous())
        
        # Output head
        self.head_nm = AdaLNBeforeHead(self.C, self.D)
        self.head = nn.Linear(self.C, self.V)
        
        self.prog_si = -1
    
    @torch.no_grad()
    def generate(
        self, 
        embed: torch.Tensor, 
        cfg: float = 1.5, 
        top_k: int = 0, 
        top_p: float = 0.0, 
        seed: Optional[int] = None
    ) -> torch.Tensor:
        """
        Generate images from text embeddings
        
        Args:
            embed: Text embeddings [B, n_cond_embed]
            cfg: Classifier-free guidance scale
            top_k: Top-k sampling (0 to disable)
            top_p: Top-p (nucleus) sampling (0 to disable)
            seed: Random seed for reproducibility
            
        Returns:
            Generated images [B, 3, H, W] in range [0, 1]
        """
        B = embed.shape[0]
        device = embed.device
        self.eval()
        
        if seed is not None:
            torch.manual_seed(seed)
            if device.type == 'cuda':
                torch.cuda.manual_seed(seed)
        
        # Prepare conditional and unconditional embeddings
        noise = self.noise(torch.tensor(0, device=device)).expand(B, -1)
        cond_BD = self.cond_proj(torch.cat([embed, noise], dim=0))
        
        lvl_pos = self.lvl_embed(self.lvl_1L) + self.pos_1LC
        next_token_map = (
            cond_BD.unsqueeze(1).expand(2*B, self.first_l, -1) + 
            self.pos_start + lvl_pos[:, :self.first_l]
        )
        
        cur_L = 0
        f_hat = embed.new_zeros(B, self.Cvae, self.patch_nums[-1], self.patch_nums[-1])
        
        # Enable KV caching
        for block in self.blocks:
            block.attn.kv_caching(True)
        
        # Autoregressive generation
        for si, pn in enumerate(self.patch_nums):
            ratio = si / self.num_stages_minus_1 if self.num_stages_minus_1 > 0 else 0
            cur_L += pn * pn
            x = next_token_map
            
            for block in self.blocks:
                x = block(x, cond_BD, attn_bias=None)
            
            logits_BlV = self.head(self.head_nm(x.float(), cond_BD).float())
            
            # CFG
            t = cfg * ratio
            logits_BlV = (1 + t) * logits_BlV[:B] - t * logits_BlV[B:]
            
            # Top-k sampling
            if top_k > 0:
                v, _ = logits_BlV.topk(top_k, dim=-1)
                logits_BlV[logits_BlV < v[..., -1:]] = -float('inf')
            
            # Top-p sampling
            if top_p > 0:
                sorted_logits, sorted_idx = logits_BlV.sort(dim=-1, descending=True)
                cumsum = sorted_logits.softmax(dim=-1).cumsum(dim=-1)
                mask = cumsum - sorted_logits.softmax(dim=-1) > top_p
                sorted_logits[mask] = -float('inf')
                logits_BlV = sorted_logits.scatter(-1, sorted_idx, sorted_logits)
            
            # Sample
            idx_Bl = logits_BlV.softmax(dim=-1).view(-1, self.V).multinomial(1).view(B, pn*pn)
            
            # Get embeddings and update f_hat
            h_BChw = self.vae_quant_proxy[0].embedding(idx_Bl).transpose(1, 2).view(B, self.Cvae, pn, pn)
            f_hat, next_token_map = self.vae_quant_proxy[0].get_next_autoregressive_input(
                si, len(self.patch_nums), f_hat, h_BChw
            )
            
            # Prepare next token map
            if si != self.num_stages_minus_1:
                next_token_map = next_token_map.view(B, self.Cvae, -1).transpose(1, 2)
                next_token_map = self.word_embed(next_token_map) + lvl_pos[:, cur_L:cur_L + self.patch_nums[si+1]**2]
                next_token_map = next_token_map.repeat(2, 1, 1)
        
        # Disable KV caching
        for block in self.blocks:
            block.attn.kv_caching(False)
        
        # Decode to image
        return self.vae_proxy[0].fhat_to_img(f_hat).add_(1).mul_(0.5)
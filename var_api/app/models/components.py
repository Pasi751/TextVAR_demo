# ===== app/models/components.py =====

"""Shared model components for VAE and VAR
Reference code from the original VAR repository - https://github.com/FoundationVision/VAR.git
"""

import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def drop_path(x: torch.Tensor, drop_prob: float = 0., training: bool = False) -> torch.Tensor:
    """Drop paths (Stochastic Depth) per sample"""
    if drop_prob == 0. or not training:
        return x
    keep_prob = 1 - drop_prob
    shape = (x.shape[0],) + (1,) * (x.ndim - 1)
    random_tensor = x.new_empty(shape).bernoulli_(keep_prob)
    if keep_prob > 0.0:
        random_tensor.div_(keep_prob)
    return x * random_tensor


class DropPath(nn.Module):
    """Drop paths (Stochastic Depth) per sample"""
    
    def __init__(self, drop_prob: float = 0.):
        super().__init__()
        self.drop_prob = drop_prob
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return drop_path(x, self.drop_prob, self.training)


def Normalize(in_channels: int, num_groups: int = 32) -> nn.GroupNorm:
    """Group normalization"""
    return nn.GroupNorm(num_groups=num_groups, num_channels=in_channels, eps=1e-6, affine=True)


class Upsample2x(nn.Module):
    """2x upsampling with convolution"""
    
    def __init__(self, in_channels: int):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, in_channels, kernel_size=3, stride=1, padding=1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(F.interpolate(x, scale_factor=2, mode='nearest'))


class Downsample2x(nn.Module):
    """2x downsampling with convolution"""
    
    def __init__(self, in_channels: int):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, in_channels, kernel_size=3, stride=2, padding=0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(F.pad(x, pad=(0, 1, 0, 1), mode='constant', value=0))


class ResnetBlock(nn.Module):
    """Residual block for VAE"""
    
    def __init__(self, *, in_channels: int, out_channels: int = None, dropout: float = 0.0):
        super().__init__()
        self.in_channels = in_channels
        out_channels = in_channels if out_channels is None else out_channels
        self.out_channels = out_channels
        
        self.norm1 = Normalize(in_channels)
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.norm2 = Normalize(out_channels)
        self.dropout = nn.Dropout(dropout) if dropout > 1e-6 else nn.Identity()
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1)
        
        if self.in_channels != self.out_channels:
            self.nin_shortcut = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0)
        else:
            self.nin_shortcut = nn.Identity()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.conv1(F.silu(self.norm1(x)))
        h = self.conv2(self.dropout(F.silu(self.norm2(h))))
        return self.nin_shortcut(x) + h


class AttnBlock(nn.Module):
    """Self-attention block for VAE"""
    
    def __init__(self, in_channels: int):
        super().__init__()
        self.C = in_channels
        self.norm = Normalize(in_channels)
        self.qkv = nn.Conv2d(in_channels, 3 * in_channels, kernel_size=1, stride=1, padding=0)
        self.w_ratio = int(in_channels) ** (-0.5)
        self.proj_out = nn.Conv2d(in_channels, in_channels, kernel_size=1, stride=1, padding=0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        qkv = self.qkv(self.norm(x))
        B, _, H, W = qkv.shape
        C = self.C
        q, k, v = qkv.reshape(B, 3, C, H, W).unbind(1)
        
        q = q.view(B, C, H * W).permute(0, 2, 1)
        k = k.view(B, C, H * W)
        w = torch.bmm(q, k).mul_(self.w_ratio)
        w = F.softmax(w, dim=2)
        
        v = v.view(B, C, H * W)
        w = w.permute(0, 2, 1)
        h = torch.bmm(v, w)
        h = h.view(B, C, H, W)
        
        return x + self.proj_out(h)


def make_attn(in_channels: int, using_sa: bool = True) -> nn.Module:
    """Create attention block or identity"""
    return AttnBlock(in_channels) if using_sa else nn.Identity()


# ============ Transformer Components ============

class SelfAttention(nn.Module):
    """Self-attention for VAR transformer"""
    
    def __init__(
        self, 
        embed_dim: int = 768, 
        num_heads: int = 12, 
        attn_drop: float = 0., 
        proj_drop: float = 0., 
        attn_l2_norm: bool = True
    ):
        super().__init__()
        assert embed_dim % num_heads == 0
        
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.attn_l2_norm = attn_l2_norm
        
        if attn_l2_norm:
            self.scale = 1.0
            self.scale_mul = nn.Parameter(torch.full((1, num_heads, 1, 1), 4.0).log())
            self.max_scale_mul = torch.log(torch.tensor(100)).item()
        else:
            self.scale = 0.25 / math.sqrt(self.head_dim)
        
        self.mat_qkv = nn.Linear(embed_dim, embed_dim * 3, bias=False)
        self.q_bias = nn.Parameter(torch.zeros(embed_dim))
        self.v_bias = nn.Parameter(torch.zeros(embed_dim))
        self.register_buffer('zero_k_bias', torch.zeros(embed_dim))
        
        self.proj = nn.Linear(embed_dim, embed_dim)
        self.proj_drop = nn.Dropout(proj_drop) if proj_drop > 0 else nn.Identity()
        self.attn_drop = attn_drop
        
        # KV caching for inference
        self.caching = False
        self.cached_k = None
        self.cached_v = None
    
    def kv_caching(self, enable: bool):
        """Enable/disable KV caching"""
        self.caching = enable
        self.cached_k = None
        self.cached_v = None
    
    def forward(self, x: torch.Tensor, attn_bias: torch.Tensor = None) -> torch.Tensor:
        B, L, C = x.shape
        
        qkv = F.linear(x, self.mat_qkv.weight, torch.cat([self.q_bias, self.zero_k_bias, self.v_bias]))
        qkv = qkv.view(B, L, 3, self.num_heads, self.head_dim)
        q, k, v = qkv.permute(2, 0, 3, 1, 4).unbind(0)
        
        if self.attn_l2_norm:
            scale_mul = self.scale_mul.clamp_max(self.max_scale_mul).exp()
            q = F.normalize(q, dim=-1) * scale_mul
            k = F.normalize(k, dim=-1)
        
        if self.caching:
            if self.cached_k is None:
                self.cached_k, self.cached_v = k, v
            else:
                k = torch.cat([self.cached_k, k], dim=2)
                v = torch.cat([self.cached_v, v], dim=2)
                self.cached_k, self.cached_v = k, v
        
        attn = (q * self.scale) @ k.transpose(-2, -1)
        if attn_bias is not None:
            attn = attn + attn_bias
        attn = attn.softmax(dim=-1)
        
        if self.training and self.attn_drop > 0:
            attn = F.dropout(attn, p=self.attn_drop)
        
        out = (attn @ v).transpose(1, 2).reshape(B, L, C)
        return self.proj_drop(self.proj(out))


class FFN(nn.Module):
    """Feed-forward network"""
    
    def __init__(self, in_features: int, hidden_features: int = None, drop: float = 0.):
        super().__init__()
        hidden_features = hidden_features or in_features * 4
        self.fc1 = nn.Linear(in_features, hidden_features)
        self.act = nn.GELU(approximate='tanh')
        self.fc2 = nn.Linear(hidden_features, in_features)
        self.drop = nn.Dropout(drop) if drop > 0 else nn.Identity()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.drop(self.fc2(self.act(self.fc1(x))))


class AdaLNSelfAttn(nn.Module):
    """Adaptive LayerNorm Self-Attention block"""
    
    def __init__(
        self, 
        embed_dim: int, 
        cond_dim: int, 
        num_heads: int, 
        mlp_ratio: float = 4., 
        drop: float = 0., 
        attn_drop: float = 0., 
        drop_path: float = 0., 
        attn_l2_norm: bool = True
    ):
        super().__init__()
        self.C = embed_dim
        self.D = cond_dim
        
        self.drop_path = DropPath(drop_path) if drop_path > 0 else nn.Identity()
        self.attn = SelfAttention(embed_dim, num_heads, attn_drop, drop, attn_l2_norm)
        self.ffn = FFN(embed_dim, int(embed_dim * mlp_ratio), drop)
        
        self.ln_wo_grad = nn.LayerNorm(embed_dim, elementwise_affine=False, eps=1e-6)
        self.ada_lin = nn.Sequential(nn.SiLU(), nn.Linear(cond_dim, 6 * embed_dim))
    
    def forward(self, x: torch.Tensor, cond_BD: torch.Tensor, attn_bias: torch.Tensor) -> torch.Tensor:
        gamma1, gamma2, scale1, scale2, shift1, shift2 = self.ada_lin(cond_BD).view(-1, 1, 6, self.C).unbind(2)
        
        x = x + self.drop_path(
            self.attn(self.ln_wo_grad(x).mul(scale1.add(1)).add_(shift1), attn_bias).mul_(gamma1)
        )
        x = x + self.drop_path(
            self.ffn(self.ln_wo_grad(x).mul(scale2.add(1)).add_(shift2)).mul(gamma2)
        )
        return x


class AdaLNBeforeHead(nn.Module):
    """Adaptive LayerNorm before output head"""
    
    def __init__(self, C: int, D: int):
        super().__init__()
        self.C, self.D = C, D
        self.ln_wo_grad = nn.LayerNorm(C, elementwise_affine=False, eps=1e-6)
        self.ada_lin = nn.Sequential(nn.SiLU(), nn.Linear(D, 2 * C))
    
    def forward(self, x_BLC: torch.Tensor, cond_BD: torch.Tensor) -> torch.Tensor:
        scale, shift = self.ada_lin(cond_BD).view(-1, 1, 2, self.C).unbind(2)
        return self.ln_wo_grad(x_BLC).mul(scale.add(1)).add_(shift)
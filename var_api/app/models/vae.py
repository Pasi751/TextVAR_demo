# ===== app/models/vae.py =====

"""VQVAE model for VAR"""

from typing import Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .components import (
    Normalize, Upsample2x, Downsample2x, 
    ResnetBlock, make_attn
)


class Encoder(nn.Module):
    """VAE Encoder"""
    
    def __init__(
        self, 
        *, 
        ch: int = 128, 
        ch_mult: Tuple[int, ...] = (1, 2, 4, 8), 
        num_res_blocks: int = 2,
        dropout: float = 0.0, 
        in_channels: int = 3, 
        z_channels: int, 
        double_z: bool = False, 
        using_sa: bool = True, 
        using_mid_sa: bool = True
    ):
        super().__init__()
        self.ch = ch
        self.num_resolutions = len(ch_mult)
        self.num_res_blocks = num_res_blocks
        
        self.conv_in = nn.Conv2d(in_channels, self.ch, kernel_size=3, stride=1, padding=1)
        
        in_ch_mult = (1,) + tuple(ch_mult)
        self.down = nn.ModuleList()
        block_in = ch
        
        for i_level in range(self.num_resolutions):
            block = nn.ModuleList()
            attn = nn.ModuleList()
            block_in = ch * in_ch_mult[i_level]
            block_out = ch * ch_mult[i_level]
            
            for i_block in range(self.num_res_blocks):
                block.append(ResnetBlock(in_channels=block_in, out_channels=block_out, dropout=dropout))
                block_in = block_out
                if i_level == self.num_resolutions - 1 and using_sa:
                    attn.append(make_attn(block_in, using_sa=True))
            
            down = nn.Module()
            down.block = block
            down.attn = attn
            if i_level != self.num_resolutions - 1:
                down.downsample = Downsample2x(block_in)
            self.down.append(down)
        
        self.mid = nn.Module()
        self.mid.block_1 = ResnetBlock(in_channels=block_in, out_channels=block_in, dropout=dropout)
        self.mid.attn_1 = make_attn(block_in, using_sa=using_mid_sa)
        self.mid.block_2 = ResnetBlock(in_channels=block_in, out_channels=block_in, dropout=dropout)
        
        self.norm_out = Normalize(block_in)
        self.conv_out = nn.Conv2d(
            block_in, 
            (2 * z_channels if double_z else z_channels), 
            kernel_size=3, stride=1, padding=1
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.conv_in(x)
        
        for i_level in range(self.num_resolutions):
            for i_block in range(self.num_res_blocks):
                h = self.down[i_level].block[i_block](h)
                if len(self.down[i_level].attn) > 0:
                    h = self.down[i_level].attn[i_block](h)
            if i_level != self.num_resolutions - 1:
                h = self.down[i_level].downsample(h)
        
        h = self.mid.block_2(self.mid.attn_1(self.mid.block_1(h)))
        h = self.conv_out(F.silu(self.norm_out(h)))
        return h


class Decoder(nn.Module):
    """VAE Decoder"""
    
    def __init__(
        self, 
        *, 
        ch: int = 128, 
        ch_mult: Tuple[int, ...] = (1, 2, 4, 8), 
        num_res_blocks: int = 2,
        dropout: float = 0.0, 
        in_channels: int = 3, 
        z_channels: int, 
        using_sa: bool = True, 
        using_mid_sa: bool = True
    ):
        super().__init__()
        self.ch = ch
        self.num_resolutions = len(ch_mult)
        self.num_res_blocks = num_res_blocks
        
        block_in = ch * ch_mult[self.num_resolutions - 1]
        self.conv_in = nn.Conv2d(z_channels, block_in, kernel_size=3, stride=1, padding=1)
        
        self.mid = nn.Module()
        self.mid.block_1 = ResnetBlock(in_channels=block_in, out_channels=block_in, dropout=dropout)
        self.mid.attn_1 = make_attn(block_in, using_sa=using_mid_sa)
        self.mid.block_2 = ResnetBlock(in_channels=block_in, out_channels=block_in, dropout=dropout)
        
        self.up = nn.ModuleList()
        for i_level in reversed(range(self.num_resolutions)):
            block = nn.ModuleList()
            attn = nn.ModuleList()
            block_out = ch * ch_mult[i_level]
            
            for i_block in range(self.num_res_blocks + 1):
                block.append(ResnetBlock(in_channels=block_in, out_channels=block_out, dropout=dropout))
                block_in = block_out
                if i_level == self.num_resolutions - 1 and using_sa:
                    attn.append(make_attn(block_in, using_sa=True))
            
            up = nn.Module()
            up.block = block
            up.attn = attn
            if i_level != 0:
                up.upsample = Upsample2x(block_in)
            self.up.insert(0, up)
        
        self.norm_out = Normalize(block_in)
        self.conv_out = nn.Conv2d(block_in, in_channels, kernel_size=3, stride=1, padding=1)
    
    def forward(self, z: torch.Tensor) -> torch.Tensor:
        h = self.mid.block_2(self.mid.attn_1(self.mid.block_1(self.conv_in(z))))
        
        for i_level in reversed(range(self.num_resolutions)):
            for i_block in range(self.num_res_blocks + 1):
                h = self.up[i_level].block[i_block](h)
                if len(self.up[i_level].attn) > 0:
                    h = self.up[i_level].attn[i_block](h)
            if i_level != 0:
                h = self.up[i_level].upsample(h)
        
        h = self.conv_out(F.silu(self.norm_out(h)))
        return h


class Phi(nn.Conv2d):
    """Residual quantization refinement layer"""
    
    def __init__(self, embed_dim: int, quant_resi: float):
        ks = 3
        super().__init__(
            in_channels=embed_dim, 
            out_channels=embed_dim, 
            kernel_size=ks, 
            stride=1, 
            padding=ks // 2
        )
        self.resi_ratio = abs(quant_resi)
    
    def forward(self, h_BChw: torch.Tensor) -> torch.Tensor:
        return h_BChw.mul(1 - self.resi_ratio) + super().forward(h_BChw).mul_(self.resi_ratio)


class PhiPartiallyShared(nn.Module):
    """Partially shared Phi layers"""
    
    def __init__(self, qresi_ls: nn.ModuleList):
        super().__init__()
        self.qresi_ls = qresi_ls
        K = len(qresi_ls)
        self.ticks = np.linspace(1/3/K, 1-1/3/K, K) if K == 4 else np.linspace(1/2/K, 1-1/2/K, K)
    
    def __getitem__(self, at_from_0_to_1: float) -> Phi:
        return self.qresi_ls[np.argmin(np.abs(self.ticks - at_from_0_to_1)).item()]


class VectorQuantizer2(nn.Module):
    """Vector Quantizer for multi-scale VAE"""
    
    def __init__(
        self, 
        vocab_size: int, 
        Cvae: int, 
        using_znorm: bool = False, 
        beta: float = 0.25,
        v_patch_nums: Tuple[int, ...] = None, 
        quant_resi: float = 0.5, 
        share_quant_resi: int = 4
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.Cvae = Cvae
        self.using_znorm = using_znorm
        self.v_patch_nums = v_patch_nums
        self.beta = beta
        
        self.embedding = nn.Embedding(vocab_size, Cvae)
        self.quant_resi = PhiPartiallyShared(
            nn.ModuleList([Phi(Cvae, quant_resi) for _ in range(share_quant_resi)])
        )
        self.register_buffer('ema_vocab_hit_SV', torch.zeros(len(v_patch_nums), vocab_size))
    
    def get_next_autoregressive_input(
        self, 
        si: int, 
        SN: int, 
        f_hat: torch.Tensor, 
        h_BChw: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Get next autoregressive input for generation"""
        HW = self.v_patch_nums[-1]
        
        if si != SN - 1:
            h = self.quant_resi[si / (SN - 1)](F.interpolate(h_BChw, size=(HW, HW), mode='bicubic'))
            f_hat = f_hat + h
            return f_hat, F.interpolate(
                f_hat, 
                size=(self.v_patch_nums[si + 1], self.v_patch_nums[si + 1]), 
                mode='area'
            )
        else:
            h = self.quant_resi[si / (SN - 1)](h_BChw)
            f_hat = f_hat + h
            return f_hat, f_hat


class VQVAE(nn.Module):
    """Vector Quantized VAE for VAR"""
    
    def __init__(
        self, 
        vocab_size: int = 4096, 
        z_channels: int = 32, 
        ch: int = 160, 
        dropout: float = 0.0,
        using_znorm: bool = False, 
        quant_conv_ks: int = 3, 
        quant_resi: float = 0.5, 
        share_quant_resi: int = 4,
        v_patch_nums: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 8, 10, 13, 16), 
        test_mode: bool = True
    ):
        super().__init__()
        self.test_mode = test_mode
        self.V, self.Cvae = vocab_size, z_channels
        self.vocab_size = vocab_size
        
        ddconfig = dict(
            dropout=dropout, 
            ch=ch, 
            z_channels=z_channels, 
            in_channels=3, 
            ch_mult=(1, 1, 2, 2, 4), 
            num_res_blocks=2, 
            using_sa=True, 
            using_mid_sa=True
        )
        
        self.encoder = Encoder(double_z=False, **ddconfig)
        self.decoder = Decoder(**ddconfig)
        
        self.quantize = VectorQuantizer2(
            vocab_size=vocab_size, 
            Cvae=z_channels, 
            using_znorm=using_znorm,
            v_patch_nums=v_patch_nums, 
            quant_resi=quant_resi, 
            share_quant_resi=share_quant_resi
        )
        
        self.quant_conv = nn.Conv2d(z_channels, z_channels, quant_conv_ks, stride=1, padding=quant_conv_ks // 2)
        self.post_quant_conv = nn.Conv2d(z_channels, z_channels, quant_conv_ks, stride=1, padding=quant_conv_ks // 2)
        
        if test_mode:
            self.eval()
            for p in self.parameters():
                p.requires_grad_(False)
    
    def fhat_to_img(self, f_hat: torch.Tensor) -> torch.Tensor:
        """Convert f_hat to image"""
        return self.decoder(self.post_quant_conv(f_hat)).clamp_(-1, 1)
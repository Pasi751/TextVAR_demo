# ===== app/models/__init__.py =====

"""
Reference code from the original VAR repository - https://github.com/FoundationVision/VAR.git
"""

from .components import (
    DropPath,
    Normalize,
    SelfAttention,
    FFN,
    AdaLNSelfAttn,
    AdaLNBeforeHead
)
from .vae import VQVAE, VectorQuantizer2
from .var import VAR

__all__ = [
    'DropPath',
    'Normalize', 
    'SelfAttention',
    'FFN',
    'AdaLNSelfAttn',
    'AdaLNBeforeHead',
    'VQVAE',
    'VectorQuantizer2',
    'VAR'
]
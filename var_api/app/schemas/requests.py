# ===== app/schemas/requests.py =====

"""Pydantic models for API requests and responses"""

from typing import Optional, List
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Single image generation request"""
    prompt: str = Field(
        ..., 
        description="Text description of the image to generate",
        example="a beautiful red rose flower"
    )
    cfg_scale: float = Field(
        default=1.5, 
        ge=1.0, 
        le=10.0, 
        description="Classifier-free guidance scale"
    )
    top_k: int = Field(
        default=900, 
        ge=0, 
        le=4096, 
        description="Top-k sampling (0 to disable)"
    )
    top_p: float = Field(
        default=0.96, 
        ge=0.0, 
        le=1.0, 
        description="Top-p (nucleus) sampling"
    )
    seed: Optional[int] = Field(
        default=None, 
        description="Random seed for reproducibility"
    )


class GenerateResponse(BaseModel):
    """Single image generation response"""
    success: bool
    image_base64: Optional[str] = None
    prompt: str
    parameters: dict
    error: Optional[str] = None


class BatchGenerateRequest(BaseModel):
    """Batch image generation request"""
    prompts: List[str] = Field(
        ..., 
        description="List of text prompts",
        max_length=8
    )
    cfg_scale: float = Field(default=1.5, ge=1.0, le=10.0)
    top_k: int = Field(default=900, ge=0, le=4096)
    top_p: float = Field(default=0.96, ge=0.0, le=1.0)
    seed: Optional[int] = Field(default=None)


class BatchGenerateResponse(BaseModel):
    """Batch image generation response"""
    success: bool
    count: int
    images: List[dict]
    parameters: dict
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    device: str
    model_loaded: bool
    vae_loaded: bool
    clip_loaded: bool
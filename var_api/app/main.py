# ===== app/main.py =====

import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import base64
import io

# Import your generator
from app.services.generator import ImageGenerator
from app.config import app_config, model_config

# Initialize generator
generator = ImageGenerator()

# ============ FastAPI App ============
app = FastAPI(title="VAR Text-to-Image API")

# CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class GenerateRequest(BaseModel):
    prompt: str
    cfg_scale: float = 1.5
    top_k: int = 900
    top_p: float = 0.96
    seed: Optional[int] = None

# ============ REST API Endpoints ============

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": generator.is_loaded,
        "device": str(app_config.device)
    }

@app.post("/api/generate")
async def generate(request: GenerateRequest):
    """REST API endpoint for frontend"""
    try:
        if not generator.is_loaded:
            generator.load_models()
        
        pil_image, params = generator.generate(
            prompt=request.prompt,
            cfg_scale=request.cfg_scale,
            top_k=request.top_k,
            top_p=request.top_p,
            seed=request.seed
        )
        
        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "success": True,
            "image_base64": image_base64,
            "prompt": request.prompt,
            "parameters": params
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ============ Gradio Interface (Required for HF Spaces GPU) ============

def gradio_generate(prompt, cfg_scale, top_k, top_p, seed):
    """Gradio interface function"""
    if not generator.is_loaded:
        generator.load_models()
    
    seed_val = int(seed) if seed and seed.strip() else None
    
    pil_image, _ = generator.generate(
        prompt=prompt,
        cfg_scale=float(cfg_scale),
        top_k=int(top_k),
        top_p=float(top_p),
        seed=seed_val
    )
    return pil_image

# Create Gradio interface
demo = gr.Interface(
    fn=gradio_generate,
    inputs=[
        gr.Textbox(label="Prompt", placeholder="a beautiful red rose flower"),
        gr.Slider(1.0, 5.0, value=1.5, step=0.1, label="CFG Scale"),
        gr.Slider(0, 4096, value=900, step=50, label="Top-K"),
        gr.Slider(0.0, 1.0, value=0.96, step=0.01, label="Top-P"),
        gr.Textbox(label="Seed", placeholder="Leave empty for random"),
    ],
    outputs=gr.Image(type="pil", label="Generated Image"),
    title="🌸 VAR Flower Generator",
    examples=[
        ["a beautiful red rose flower", 1.5, 900, 0.96, "42"],
        ["a yellow sunflower with green leaves", 2.0, 900, 0.96, ""],
    ],
)

# ============ Mount Gradio to FastAPI ============
app = gr.mount_gradio_app(app, demo, path="/")

# This exports both:
# - FastAPI REST API at /api/*
# - Gradio UI at /

# ===== app/routes/generate.py =====

"""Generation API routes"""

import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..schemas import (
    GenerateRequest,
    GenerateResponse,
    BatchGenerateRequest,
    BatchGenerateResponse
)
from ..services import generator

router = APIRouter(prefix="/generate", tags=["Generation"])


@router.post("", response_model=GenerateResponse)
async def generate_image(request: GenerateRequest):
    """Generate a single image from text prompt"""
    try:
        if not generator.is_loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Generate image
        pil_image, params = generator.generate(
            prompt=request.prompt,
            cfg_scale=request.cfg_scale,
            top_k=request.top_k,
            top_p=request.top_p,
            seed=request.seed
        )
        
        # Convert to base64
        image_base64 = generator.pil_to_base64(pil_image)
        
        return GenerateResponse(
            success=True,
            image_base64=image_base64,
            prompt=request.prompt,
            parameters=params
        )
        
    except Exception as e:
        return GenerateResponse(
            success=False,
            prompt=request.prompt,
            parameters={},
            error=str(e)
        )


@router.post("/image")
async def generate_image_file(request: GenerateRequest):
    """Generate image and return as PNG file"""
    try:
        if not generator.is_loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Generate image
        pil_image, _ = generator.generate(
            prompt=request.prompt,
            cfg_scale=request.cfg_scale,
            top_k=request.top_k,
            top_p=request.top_p,
            seed=request.seed
        )
        
        # Convert to bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=generated_image.png"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchGenerateResponse)
async def generate_batch(request: BatchGenerateRequest):
    """Generate multiple images from text prompts"""
    try:
        if not generator.is_loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Generate images
        pil_images, params = generator.generate_batch(
            prompts=request.prompts,
            cfg_scale=request.cfg_scale,
            top_k=request.top_k,
            top_p=request.top_p,
            seed=request.seed
        )
        
        # Convert to base64
        results = []
        for img, prompt in zip(pil_images, request.prompts):
            image_base64 = generator.pil_to_base64(img)
            results.append({
                "prompt": prompt,
                "image_base64": image_base64
            })
        
        return BatchGenerateResponse(
            success=True,
            count=len(results),
            images=results,
            parameters=params
        )
        
    except Exception as e:
        return BatchGenerateResponse(
            success=False,
            count=0,
            images=[],
            parameters={},
            error=str(e)
        )
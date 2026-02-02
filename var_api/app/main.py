# ===== app/main.py =====

"""FastAPI application entry point"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import app_config
from .schemas import HealthResponse
from .services import generator
from .routes import generate_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("Starting up...")
    generator.load_models()
    yield
    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="VAR Text-to-Image API",
    description="Generate flower images from text descriptions using VAR model",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate_router)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        device=str(app_config.device),
        model_loaded=generator.is_loaded,
        vae_loaded=generator.vae is not None,
        clip_loaded=generator.clip_model is not None
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if generator.is_loaded else "not ready",
        device=str(app_config.device),
        model_loaded=generator.is_loaded,
        vae_loaded=generator.vae is not None,
        clip_loaded=generator.clip_model is not None
    )
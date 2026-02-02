# ===== run.py =====

"""Entry point script to run the API server"""

import uvicorn
from app.config import app_config


def main():
    """Run the FastAPI server"""
    uvicorn.run(
        "app.main:app",
        host=app_config.host,
        port=app_config.port,
        reload=False,
        workers=1  # Single worker for GPU
    )


if __name__ == "__main__":
    main()
# ===== test_client.py =====

"""Test client for the VAR API"""

import requests
import base64
from PIL import Image
import io


API_URL = "http://localhost:8000"


def check_health():
    """Check API health"""
    response = requests.get(f"{API_URL}/health")
    return response.json()


def generate_image(prompt: str, cfg_scale: float = 1.5, seed: int = None) -> Image.Image:
    """Generate a single image"""
    response = requests.post(
        f"{API_URL}/generate",
        json={
            "prompt": prompt,
            "cfg_scale": cfg_scale,
            "top_k": 900,
            "top_p": 0.96,
            "seed": seed
        }
    )
    
    data = response.json()
    
    if data["success"]:
        image_data = base64.b64decode(data["image_base64"])
        return Image.open(io.BytesIO(image_data))
    else:
        raise Exception(data["error"])


def generate_and_save(prompt: str, filename: str, **kwargs):
    """Generate and save image to file"""
    image = generate_image(prompt, **kwargs)
    image.save(filename)
    print(f"Saved: {filename}")
    return image


def generate_batch(prompts: list, cfg_scale: float = 1.5, seed: int = None) -> list:
    """Generate multiple images"""
    response = requests.post(
        f"{API_URL}/generate/batch",
        json={
            "prompts": prompts,
            "cfg_scale": cfg_scale,
            "seed": seed
        }
    )
    
    data = response.json()
    
    if data["success"]:
        images = []
        for item in data["images"]:
            image_data = base64.b64decode(item["image_base64"])
            images.append(Image.open(io.BytesIO(image_data)))
        return images
    else:
        raise Exception(data["error"])


if __name__ == "__main__":
    # Check health
    print("Health:", check_health())
    
    # Generate single image
    generate_and_save("a beautiful red rose flower", "rose.png", cfg_scale=2.0, seed=42)
    
    # Generate batch
    prompts = [
        "a yellow sunflower",
        "a purple orchid flower",
        "a white daisy flower"
    ]
    images = generate_batch(prompts, cfg_scale=1.5)
    for i, img in enumerate(images):
        img.save(f"flower_{i}.png")
        print(f"Saved: flower_{i}.png")

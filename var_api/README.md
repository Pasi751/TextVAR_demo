# ===== backend/README.md =====

---
title: TextVAR demo
emoji: 🌸🌸🌸
colorFrom: pink
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
suggested_hardware: t4-small
---

# 🌸 VAR Flower Image Generator

Generate beautiful flower images from text descriptions using the VAR (Visual AutoRegressive) model.

## Usage

1. Enter a text prompt describing a flower
2. Adjust CFG scale (higher = stronger prompt adherence)
3. Optionally set a seed for reproducible results
4. Click Generate

## Example Prompts

- "a beautiful red rose flower"
- "a yellow sunflower with green leaves"
- "a purple orchid flower"
- "a white daisy flower"

## Model

- **Architecture:** VAR (Visual AutoRegressive)
- **Training Data:** Oxford Flowers 102
- **Parameters:** ~133M
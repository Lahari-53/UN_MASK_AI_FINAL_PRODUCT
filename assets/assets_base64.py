"""
Cached Base64 Data URIs for Hero Artwork, Logo, and Thumbnails.
"""

import base64
import os
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent

def get_base64_encoded_image(filename: str) -> str:
    path = CURRENT_DIR / filename
    if path.exists():
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            ext = path.suffix.lower().replace(".", "")
            if ext == "jpg": ext = "jpeg"
            return f"data:image/{ext};base64,{encoded}"
    return ""

LOGO_BASE64 = get_base64_encoded_image("logo_mask.png")
HERO_CHARACTER_BASE64 = get_base64_encoded_image("hero_character.png")
SAMPLE_THUMB_BASE64 = get_base64_encoded_image("sample_thumb.png")
REFERENCE_HERO_BASE64 = get_base64_encoded_image("reference_hero_full.png")

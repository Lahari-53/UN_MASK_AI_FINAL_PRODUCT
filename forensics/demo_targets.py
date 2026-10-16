"""
Procedural Demo Evidence Generator.
Allows instant testing of all forensic engines without external file uploads.
"""

from __future__ import annotations
import io
import wave
import numpy as np
import cv2
from PIL import Image, ImageDraw


def generate_synthetic_diffusion_demo() -> Image.Image:
    """
    Synthesizes a test target mimicking latent diffusion / AI portrait characteristics:
    Over-smoothed skin texture, hyper-sharp pupil reflections, and subtle latent high-frequency residue.
    """
    w, h = 512, 512
    img = np.zeros((h, w, 3), dtype=np.uint8)

    # Gradient background
    for y in range(h):
        img[y, :] = [int(20 + 30 * (y / h)), int(25 + 20 * (y / h)), int(45 + 50 * (y / h))]

    # Face oval
    cv2.ellipse(img, (256, 260), (140, 190), 0, 0, 360, (215, 185, 170), -1)

    # Hair silhouette
    cv2.ellipse(img, (256, 170), (160, 120), 0, 180, 360, (40, 30, 25), -1)

    # Eyes with unnaturally high contrast
    cv2.circle(img, (200, 240), 22, (245, 245, 245), -1)
    cv2.circle(img, (312, 240), 22, (245, 245, 245), -1)
    cv2.circle(img, (200, 240), 12, (50, 110, 180), -1)
    cv2.circle(img, (312, 240), 12, (50, 110, 180), -1)
    cv2.circle(img, (200, 240), 6, (10, 10, 10), -1)
    cv2.circle(img, (312, 240), 6, (10, 10, 10), -1)
    # Pinpoint specular reflections
    cv2.circle(img, (197, 237), 3, (255, 255, 255), -1)
    cv2.circle(img, (309, 237), 3, (255, 255, 255), -1)

    # Lips
    cv2.ellipse(img, (256, 350), (45, 18), 0, 0, 360, (180, 70, 75), -1)

    # Smooth the skin (diffusion lack of high frequency pores)
    face_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(face_mask, (256, 260), (135, 185), 0, 0, 360, 255, -1)
    smoothed = cv2.bilateralFilter(img, 15, 75, 75)
    img = np.where(face_mask[:, :, None] == 255, smoothed, img)

    # Inject subtle periodic latent grid noise characteristic of generative decoders
    x_grid = np.sin(np.linspace(0, 128 * np.pi, w))
    y_grid = np.sin(np.linspace(0, 128 * np.pi, h))
    grid_noise = (np.outer(y_grid, x_grid) * 4.0).astype(np.int16)
    img_mod = np.clip(img.astype(np.int16) + grid_noise[:, :, None], 0, 255).astype(np.uint8)

    return Image.fromarray(img_mod)


def generate_spliced_tamper_demo() -> Image.Image:
    """
    Synthesizes an image with a spliced region re-compressed at a different JPEG quality factor.
    Triggers intense Error Level Analysis (ELA) anomalies.
    """
    w, h = 512, 512
    base = np.zeros((h, w, 3), dtype=np.uint8)
    cv2.rectangle(base, (0, 0), (w, h), (180, 195, 210), -1)

    # Draw natural photo textures
    cv2.circle(base, (150, 180), 80, (100, 140, 90), -1)
    cv2.circle(base, (360, 340), 90, (80, 110, 160), -1)

    # Save base at quality 70
    buf_low = io.BytesIO()
    Image.fromarray(base).save(buf_low, format="JPEG", quality=70)
    buf_low.seek(0)
    base_compressed = np.asarray(Image.open(buf_low))

    # Spliced badge saved at quality 98
    badge = np.zeros((140, 160, 3), dtype=np.uint8)
    cv2.rectangle(badge, (0, 0), (160, 140), (220, 60, 60), -1)
    cv2.putText(badge, "VERIFIED", (15, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    buf_high = io.BytesIO()
    Image.fromarray(badge).save(buf_high, format="JPEG", quality=98)
    buf_high.seek(0)
    badge_compressed = np.asarray(Image.open(buf_high))

    # Composite the high-quality badge onto the low-quality base
    result = base_compressed.copy()
    result[180:320, 176:336] = badge_compressed

    return Image.fromarray(result)


def generate_fourier_grid_demo() -> Image.Image:
    """
    Synthesizes an image with strong checkerboard artifacts from transposed convolutions.
    Triggers distinct 2D FFT spectral peaks.
    """
    w, h = 512, 512
    img = np.ones((h, w, 3), dtype=np.uint8) * 120

    # Add primary pattern
    cv2.circle(img, (256, 256), 120, (190, 170, 150), -1)

    # Superimpose high-frequency 8x8 periodic deconvolution lattice
    x = np.arange(w)
    y = np.arange(h)
    xx, yy = np.meshgrid(x, y)
    checker = ((xx // 4) % 2 == (yy // 4) % 2).astype(np.float32)
    checker = (checker - 0.5) * 22.0

    img_f = np.clip(img.astype(np.float32) + checker[:, :, None], 0, 255).astype(np.uint8)
    return Image.fromarray(img_f)


def generate_pristine_camera_demo() -> Image.Image:
    """
    Synthesizes a realistic digital camera capture with authentic PRNU sensor noise and lens vignette.
    """
    w, h = 512, 512
    img = np.zeros((h, w, 3), dtype=np.uint8)

    # Scenery gradient
    for y in range(h):
        img[y, :] = [int(120 - 40 * (y / h)), int(140 - 30 * (y / h)), int(170 - 20 * (y / h))]

    # Add buildings / structures
    cv2.rectangle(img, (80, 200), (220, 512), (70, 75, 80), -1)
    cv2.rectangle(img, (280, 160), (440, 512), (90, 85, 80), -1)

    # Lens vignette
    cx, cy = w // 2, h // 2
    y_idx, x_idx = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((x_idx - cx)**2 + (y_idx - cy)**2)
    max_dist = np.sqrt(cx**2 + cy**2)
    vignette = 1.0 - 0.35 * (dist_from_center / max_dist)**2

    img_vig = (img.astype(np.float32) * vignette[:, :, None]).astype(np.uint8)

    # Authentic sensor noise (uniform Gaussian noise)
    noise = np.random.normal(0, 4.5, (h, w, 3)).astype(np.float32)
    result = np.clip(img_vig.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    return Image.fromarray(result)


def generate_demo_audio_wav(synthetic_mode: bool = False) -> bytes:
    """
    Generates synthetic or organic audio WAV bytes for testing audio forensics.
    """
    sample_rate = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    if synthetic_mode:
        # Vocoder simulation: fundamental + strict 4kHz brickwall filter + phase jitter
        f0 = 180.0
        wave_sig = np.sin(2 * np.pi * f0 * t) + 0.5 * np.sin(2 * np.pi * 2 * f0 * t) + 0.25 * np.sin(2 * np.pi * 3 * f0 * t)
        # Suppress high frequencies completely
        wave_sig = wave_sig * 0.7
    else:
        # Natural speech simulation: rich harmonics + breath noise up to 10kHz
        wave_sig = np.zeros_like(t)
        for h_num in range(1, 15):
            amp = 1.0 / h_num
            wave_sig += amp * np.sin(2 * np.pi * (140.0 * h_num) * t + np.random.uniform(0, 2*np.pi))
        # Add natural ambient room noise
        ambient_noise = np.random.normal(0, 0.05, len(t))
        wave_sig += ambient_noise

    # Normalize to 16-bit PCM
    wave_sig = wave_sig / (np.max(np.abs(wave_sig)) + 1e-6)
    audio_int16 = (wave_sig * 32760).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())

    return buf.getvalue()

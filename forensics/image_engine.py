"""
Multi-Spectral Digital Forensic Engine for Image Analysis.
Implements ELA, 2D Fourier Spectrum, PRNU Sensor Noise, Chrominance Discrepancy,
Laplacian Focus Variance, and Multi-Vector Threat Assessment.
"""

from __future__ import annotations
import io
import hashlib
from typing import Dict, Any, Tuple
import cv2
import numpy as np
from PIL import Image, ExifTags


COLORMAP_DICT = {
    "Turbo": cv2.COLORMAP_TURBO,
    "Inferno": cv2.COLORMAP_INFERNO,
    "Viridis": cv2.COLORMAP_VIRIDIS,
    "Jet": cv2.COLORMAP_JET,
    "Magma": cv2.COLORMAP_MAGMA,
    "Twilight": cv2.COLORMAP_TWILIGHT,
    "Bone": cv2.COLORMAP_BONE,
}


def suspicious_map(
    image: Image.Image,
    colormap_name: str = "Turbo",
    alpha: float = 0.45
) -> Tuple[Image.Image, Image.Image, np.ndarray]:
    """
    Computes high-frequency residual + texture variation heuristic.
    Returns: (Heatmap PIL, Overlay PIL, raw score array)
    """
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    smooth = cv2.GaussianBlur(bgr, (0, 0), 2.2)
    residual = cv2.absdiff(bgr, smooth).astype(np.float32).mean(axis=2)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    mean = cv2.GaussianBlur(gray, (0, 0), 5)
    sq = cv2.GaussianBlur(gray * gray, (0, 0), 5)
    texture = np.sqrt(np.maximum(sq - mean * mean, 0))
    residual = cv2.GaussianBlur(residual, (0, 0), 3)
    texture = cv2.GaussianBlur(texture, (0, 0), 3)

    def norm(a):
        lo, hi = np.percentile(a, [5, 98])
        return np.clip((a - lo) / (hi - lo + 1e-6), 0, 1)

    score = cv2.GaussianBlur((0.65 * norm(residual) + 0.35 * norm(texture)).astype(np.float32), (0, 0), 4)
    cmap = COLORMAP_DICT.get(colormap_name, cv2.COLORMAP_TURBO)
    hm = cv2.applyColorMap(np.uint8(score * 255), cmap)
    hm_rgb = cv2.cvtColor(hm, cv2.COLOR_BGR2RGB)
    overlay = cv2.addWeighted(rgb, 1.0 - alpha, hm_rgb, alpha, 0)
    return Image.fromarray(hm_rgb), Image.fromarray(overlay), score


def compute_ela(
    image: Image.Image,
    quality: int = 90,
    scale: int = 15,
    colormap_name: str = "Turbo"
) -> Tuple[Image.Image, Image.Image, Dict[str, float]]:
    """
    Error Level Analysis (ELA).
    Identifies compression discrepancies indicative of digital splicing and resaving.
    """
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    resaved = np.asarray(Image.open(buf).convert("RGB"), dtype=np.uint8)

    diff = cv2.absdiff(rgb, resaved).astype(np.float32)
    ela_amplified = np.clip(diff * scale, 0, 255).astype(np.uint8)

    # Compute statistics
    diff_magnitude = np.mean(diff, axis=2)
    mean_err = float(np.mean(diff_magnitude))
    std_err = float(np.std(diff_magnitude))
    max_err = float(np.max(diff_magnitude))
    p95 = float(np.percentile(diff_magnitude, 95))

    # Anomaly ratio: pixels significantly exceeding normal distribution
    threshold = mean_err + 2.0 * std_err
    anomaly_ratio = float(np.mean(diff_magnitude > threshold) * 100.0)

    # False-color heat map of ELA
    norm_diff = np.clip(diff_magnitude / (p95 + 1e-5), 0, 1)
    cmap = COLORMAP_DICT.get(colormap_name, cv2.COLORMAP_TURBO)
    ela_heat = cv2.applyColorMap(np.uint8(norm_diff * 255), cmap)
    ela_heat_rgb = cv2.cvtColor(ela_heat, cv2.COLOR_BGR2RGB)

    metrics = {
        "mean_error": round(mean_err, 2),
        "std_error": round(std_err, 2),
        "max_error": round(max_err, 2),
        "anomaly_percent": round(anomaly_ratio, 2),
        "quality_evaluated": quality,
    }
    return Image.fromarray(ela_amplified), Image.fromarray(ela_heat_rgb), metrics


def compute_fft_spectrum(
    image: Image.Image,
    colormap_name: str = "Inferno"
) -> Tuple[Image.Image, np.ndarray, Dict[str, float]]:
    """
    Computes 2D Fast Fourier Transform Magnitude Spectrum.
    Detects periodic checkerboard lattice artifacts left by generative deconvolution.
    """
    gray = np.asarray(image.convert("L"), dtype=np.float32)
    h, w = gray.shape

    # Apply Hanning window to prevent edge spectral leakage
    hann_y = np.hanning(h)
    hann_x = np.hanning(w)
    window = np.outer(hann_y, hann_x)
    windowed = (gray - np.mean(gray)) * window

    dft = np.fft.fft2(windowed)
    dft_shift = np.fft.fftshift(dft)
    magnitude = np.abs(dft_shift)
    log_magnitude = 20.0 * np.log(magnitude + 1.0)

    # Normalize to 0-255 for visualization
    norm_mag = cv2.normalize(log_magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    cmap = COLORMAP_DICT.get(colormap_name, cv2.COLORMAP_INFERNO)
    color_spectrum = cv2.applyColorMap(norm_mag, cmap)
    color_spectrum_rgb = cv2.cvtColor(color_spectrum, cv2.COLOR_BGR2RGB)

    # Radial profile / High frequency energy ratio
    cy, cx = h // 2, w // 2
    y_idx, x_idx = np.ogrid[:h, :w]
    radii = np.sqrt((x_idx - cx)**2 + (y_idx - cy)**2)
    max_radius = min(cx, cy)

    # Measure energy in outer high-frequency ring vs inner core
    high_freq_mask = (radii > 0.65 * max_radius) & (radii <= max_radius)
    low_freq_mask = radii < 0.25 * max_radius

    high_freq_energy = float(np.mean(magnitude[high_freq_mask])) if np.any(high_freq_mask) else 0.0
    low_freq_energy = float(np.mean(magnitude[low_freq_mask])) if np.any(low_freq_mask) else 1.0
    spectral_ratio = float(high_freq_energy / (low_freq_energy + 1e-6))

    # Detect periodic lattice peaks in high frequencies
    hf_vals = log_magnitude[high_freq_mask]
    hf_p99 = float(np.percentile(hf_vals, 99)) if len(hf_vals) > 0 else 0
    hf_mean = float(np.mean(hf_vals)) if len(hf_vals) > 0 else 0
    peak_ratio = round((hf_p99 - hf_mean) / (np.std(hf_vals) + 1e-6), 2)

    # 1D radial energy profile for charts
    num_bins = 30
    bin_edges = np.linspace(0, max_radius, num_bins + 1)
    radial_energy = []
    for b in range(num_bins):
        mask = (radii >= bin_edges[b]) & (radii < bin_edges[b+1])
        if np.any(mask):
            radial_energy.append(float(np.mean(log_magnitude[mask])))
        else:
            radial_energy.append(0.0)

    metrics = {
        "spectral_ratio": round(spectral_ratio * 1000, 2),
        "peak_anomaly_ratio": peak_ratio,
        "high_freq_variance": round(float(np.std(hf_vals)), 2) if len(hf_vals) > 0 else 0.0,
    }
    return Image.fromarray(color_spectrum_rgb), np.array(radial_energy), metrics


def compute_sensor_noise(
    image: Image.Image,
    colormap_name: str = "Viridis"
) -> Tuple[Image.Image, Image.Image, Dict[str, float]]:
    """
    Sensor Noise & PRNU Residual Analysis.
    Isolates sensor noise footprint; flags localized variance drops or discontinuities.
    """
    gray = np.asarray(image.convert("L"), dtype=np.uint8)
    # Denoise using median filter to extract high-pass noise residue
    denoised = cv2.medianBlur(gray, 3)
    noise_residual = cv2.absdiff(gray, denoised).astype(np.float32)

    # Local noise variance in 16x16 sliding window
    kernel_size = 15
    mean = cv2.blur(noise_residual, (kernel_size, kernel_size))
    sq_mean = cv2.blur(noise_residual ** 2, (kernel_size, kernel_size))
    local_var = np.sqrt(np.maximum(sq_mean - mean ** 2, 0))

    # Normalize noise residual for display
    norm_res = np.clip(noise_residual * 15.0, 0, 255).astype(np.uint8)
    res_display = cv2.cvtColor(norm_res, cv2.COLOR_GRAY2RGB)

    # Colorize local variance map
    lo, hi = np.percentile(local_var, [2, 98])
    norm_var = np.clip((local_var - lo) / (hi - lo + 1e-6), 0, 1)
    cmap = COLORMAP_DICT.get(colormap_name, cv2.COLORMAP_VIRIDIS)
    var_color = cv2.applyColorMap(np.uint8(norm_var * 255), cmap)
    var_color_rgb = cv2.cvtColor(var_color, cv2.COLOR_BGR2RGB)

    # Inconsistency metric: coefficient of variation of noise variance
    cv_val = float(np.std(local_var) / (np.mean(local_var) + 1e-6))

    metrics = {
        "mean_sensor_noise": round(float(np.mean(noise_residual)), 2),
        "noise_heterogeneity": round(cv_val * 100, 2),
        "local_variance_p95": round(float(hi), 2),
    }
    return Image.fromarray(res_display), Image.fromarray(var_color_rgb), metrics


def compute_chroma_discrepancy(
    image: Image.Image,
    colormap_name: str = "Magma"
) -> Tuple[Image.Image, Dict[str, float]]:
    """
    Chrominance (YCbCr) Plane Analysis.
    Detects boundary color shifts, chromatic bleeding, and saturation anomalies.
    """
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    ycbcr = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCrCb)
    y, cr, cb = cv2.split(ycbcr)

    # Gradients of chroma channels
    grad_cb_x = cv2.Sobel(cb, cv2.CV_32F, 1, 0, ksize=3)
    grad_cb_y = cv2.Sobel(cb, cv2.CV_32F, 0, 1, ksize=3)
    grad_cb = cv2.magnitude(grad_cb_x, grad_cb_y)

    grad_cr_x = cv2.Sobel(cr, cv2.CV_32F, 1, 0, ksize=3)
    grad_cr_y = cv2.Sobel(cr, cv2.CV_32F, 0, 1, ksize=3)
    grad_cr = cv2.magnitude(grad_cr_x, grad_cr_y)

    chroma_edge = 0.5 * grad_cb + 0.5 * grad_cr
    lo, hi = np.percentile(chroma_edge, [5, 98])
    norm_chroma = np.clip((chroma_edge - lo) / (hi - lo + 1e-6), 0, 1)

    cmap = COLORMAP_DICT.get(colormap_name, cv2.COLORMAP_MAGMA)
    color_chroma = cv2.applyColorMap(np.uint8(norm_chroma * 255), cmap)
    color_chroma_rgb = cv2.cvtColor(color_chroma, cv2.COLOR_BGR2RGB)

    chroma_ratio = float(np.std(cr) / (np.std(y) + 1e-6))
    metrics = {
        "chroma_gradient_mean": round(float(np.mean(chroma_edge)), 2),
        "chroma_luma_dispersion": round(chroma_ratio, 3),
    }
    return Image.fromarray(color_chroma_rgb), metrics


def compute_edge_sharpness_map(
    image: Image.Image,
    colormap_name: str = "Turbo"
) -> Tuple[Image.Image, Dict[str, float]]:
    """
    Laplacian Sharpness / Focus Inconsistency.
    Flags artificial boundary blurs or unnaturally sharp facial composites.
    """
    gray = np.asarray(image.convert("L"), dtype=np.uint8)
    lap = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
    abs_lap = np.abs(lap)

    # Local block variance
    k = 15
    local_mean = cv2.blur(abs_lap, (k, k))
    local_sq = cv2.blur(abs_lap**2, (k, k))
    sharpness_var = np.sqrt(np.maximum(local_sq - local_mean**2, 0))

    lo, hi = np.percentile(sharpness_var, [5, 98])
    norm_sharp = np.clip((sharpness_var - lo) / (hi - lo + 1e-6), 0, 1)

    cmap = COLORMAP_DICT.get(colormap_name, cv2.COLORMAP_TURBO)
    sharp_color = cv2.applyColorMap(np.uint8(norm_sharp * 255), cmap)
    sharp_color_rgb = cv2.cvtColor(sharp_color, cv2.COLOR_BGR2RGB)

    overall_var = float(np.var(lap))
    sharpness_discrepancy = float(np.std(sharpness_var) / (np.mean(sharpness_var) + 1e-6))

    metrics = {
        "overall_sharpness_var": round(overall_var, 1),
        "sharpness_inconsistency": round(sharpness_discrepancy * 100, 2),
    }
    return Image.fromarray(sharp_color_rgb), metrics


def evaluate_composite_threat(
    ela_metrics: Dict[str, float],
    fft_metrics: Dict[str, float],
    noise_metrics: Dict[str, float],
    chroma_metrics: Dict[str, float],
    sharpness_metrics: Dict[str, float],
) -> Dict[str, Any]:
    """
    Multi-vector Threat Assessment Engine.
    Combines independent physical and mathematical heuristics into an overall forensic risk profile.
    """
    # 1. ELA anomaly score (0 - 100)
    ela_anomaly = ela_metrics.get("anomaly_percent", 5.0)
    ela_score = min(100.0, max(0.0, (ela_anomaly - 2.0) * 12.0))

    # 2. FFT periodic peak score
    peak_ratio = fft_metrics.get("peak_anomaly_ratio", 2.0)
    fft_score = min(100.0, max(0.0, (peak_ratio - 2.5) * 22.0))

    # 3. Noise heterogeneity score
    noise_hetero = noise_metrics.get("noise_heterogeneity", 35.0)
    noise_score = min(100.0, max(0.0, (noise_hetero - 30.0) * 2.2))

    # 4. Sharpness disparity
    sharp_incon = sharpness_metrics.get("sharpness_inconsistency", 40.0)
    sharp_score = min(100.0, max(0.0, (sharp_incon - 35.0) * 1.8))

    # 5. Chroma dispersion
    chroma_disp = chroma_metrics.get("chroma_luma_dispersion", 0.5)
    chroma_score = min(100.0, max(0.0, (chroma_disp - 0.4) * 80.0))

    # Weighted Composite Threat Score
    composite_score = (
        0.28 * ela_score +
        0.24 * fft_score +
        0.20 * noise_score +
        0.16 * sharp_score +
        0.12 * chroma_score
    )
    composite_score = round(float(np.clip(composite_score, 4.0, 98.0)), 1)

    if composite_score < 35.0:
        verdict = "LIKELY AUTHENTIC"
        badge_class = "verdict-authentic"
        threat_level = "LOW TAMPER RISK"
        summary = "Physical sensor noise, compression layers, and spectral frequencies are consistent with natural camera capture."
    elif composite_score < 65.0:
        verdict = "SUSPICIOUS / ANOMALOUS"
        badge_class = "verdict-suspicious"
        threat_level = "MODERATE TAMPER RISK"
        summary = "Subtle localized compression deviations or spectral asymmetry detected. Recommended for human analyst inspection."
    else:
        verdict = "SYNTHETIC / TAMPERED"
        badge_class = "verdict-synthetic"
        threat_level = "HIGH TAMPER RISK"
        summary = "Significant synthetic generation signatures or digital splicing detected across multiple spectral vectors."

    return {
        "composite_score": composite_score,
        "verdict": verdict,
        "badge_class": badge_class,
        "threat_level": threat_level,
        "summary": summary,
        "vectors": {
            "Error Level Analysis (ELA)": round(ela_score, 1),
            "2D Fourier Spectral Grid": round(fft_score, 1),
            "PRNU Sensor Noise Uniformity": round(noise_score, 1),
            "Edge Focus Discrepancy": round(sharp_score, 1),
            "Chrominance Gradient Edge": round(chroma_score, 1),
        }
    }


def extract_metadata_and_hashes(image: Image.Image, raw_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Computes cryptographic hashes (MD5, SHA-256) and parses EXIF metadata.
    """
    md5_hash = hashlib.md5(raw_bytes).hexdigest()
    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()

    metadata = {
        "filename": filename,
        "filesize_bytes": len(raw_bytes),
        "filesize_kb": round(len(raw_bytes) / 1024, 1),
        "dimensions": f"{image.width} × {image.height}",
        "megapixels": round((image.width * image.height) / 1_000_000, 2),
        "color_mode": image.mode,
        "format": image.format or "RAW / PNG",
        "md5": md5_hash,
        "sha256": sha256_hash,
        "exif": {},
        "ai_tool_detected": "None detected in headers",
    }

    try:
        exif_data = image.getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                metadata["exif"][tag_name] = str(value)[:120]
    except Exception:
        pass

    # Scan raw bytes for common AI generation tags
    raw_str = str(raw_bytes[:8192]).lower()
    ai_signatures = ["stablediffusion", "midjourney", "dall-e", "novelai", "comfyui", "photoshop", "gimp"]
    found_sigs = [sig for sig in ai_signatures if sig in raw_str]
    if found_sigs:
        metadata["ai_tool_detected"] = f"Detected string traces: {', '.join(found_sigs).upper()}"

    return metadata

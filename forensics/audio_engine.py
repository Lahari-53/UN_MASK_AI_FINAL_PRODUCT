"""
Audio Deepfake Forensics Engine.
Computes STFT Spectrogram, high-frequency cutoff analysis,
spectral flatness, and synthetic voice cloning indicators using standard wave + numpy.
"""

from __future__ import annotations
import io
import wave
from typing import Dict, Any, Tuple
import cv2
import numpy as np
from PIL import Image


def analyze_wav_audio(
    audio_bytes: bytes,
    colormap_name: str = "Viridis"
) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Parses WAV audio bytes, builds STFT Spectrogram, and evaluates synthetic voice anomalies.
    """
    buf = io.BytesIO(audio_bytes)
    with wave.open(buf, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_frames = wf.readframes(n_frames)

    # Convert to numpy array
    if sampwidth == 2:
        dtype = np.int16
    elif sampwidth == 1:
        dtype = np.uint8
    elif sampwidth == 4:
        dtype = np.int32
    else:
        dtype = np.int16

    audio_data = np.frombuffer(raw_frames, dtype=dtype).astype(np.float32)
    if n_channels > 1:
        audio_data = audio_data.reshape(-1, n_channels).mean(axis=1)

    duration_sec = float(len(audio_data) / framerate) if framerate > 0 else 0.0

    # Normalize audio
    max_amp = np.max(np.abs(audio_data)) + 1e-6
    norm_audio = audio_data / max_amp

    # STFT Spectrogram computation
    window_size = 1024
    hop_size = 256
    window = np.hanning(window_size)
    stft_list = []

    for i in range(0, len(norm_audio) - window_size, hop_size):
        chunk = norm_audio[i:i + window_size] * window
        fft_res = np.abs(np.fft.rfft(chunk))
        stft_list.append(fft_res)

    if not stft_list:
        raise ValueError("Audio duration is too short for spectral decomposition.")

    spectrogram = np.column_stack(stft_list)
    log_spec = 20.0 * np.log10(spectrogram + 1e-6)

    # Flip vertically so 0Hz is at bottom
    flipped_spec = log_spec[::-1, :]
    lo, hi = np.percentile(flipped_spec, [5, 98])
    norm_spec = np.clip((flipped_spec - lo) / (hi - lo + 1e-6), 0, 1)

    # Colormap
    cmap_val = cv2.COLORMAP_VIRIDIS if colormap_name == "Viridis" else cv2.COLORMAP_MAGMA
    spec_color = cv2.applyColorMap(np.uint8(norm_spec * 255), cmap_val)
    spec_color_rgb = cv2.cvtColor(spec_color, cv2.COLOR_BGR2RGB)
    pil_spec = Image.fromarray(spec_color_rgb)

    # Synthetic Speech Heuristics:
    # 1. High frequency energy cutoff (many vocoders drop energy above 8kHz or 12kHz)
    freq_bins = spectrogram.shape[0]
    cutoff_bin = int(freq_bins * 0.75)
    upper_band_energy = float(np.mean(spectrogram[cutoff_bin:, :]))
    total_energy = float(np.mean(spectrogram)) + 1e-6
    hf_energy_ratio = upper_band_energy / total_energy

    # 2. Spectral Flatness (ratio of geometric mean to arithmetic mean)
    geom_mean = np.exp(np.mean(np.log(spectrogram + 1e-8), axis=0))
    arith_mean = np.mean(spectrogram, axis=0) + 1e-8
    flatness = float(np.mean(geom_mean / arith_mean))

    # 3. Dynamic range
    dynamic_range_db = float(np.max(log_spec) - np.min(log_spec))

    # Synthetic likelihood estimation
    synthetic_flags = 0
    if hf_energy_ratio < 0.015:
        synthetic_flags += 1  # Unnatural high-frequency brickwall filter
    if flatness < 0.02:
        synthetic_flags += 1  # Robotic harmonic clustering
    if dynamic_range_db < 35.0:
        synthetic_flags += 1  # Over-compressed dynamic envelope

    if synthetic_flags >= 2:
        voice_verdict = "SUSPECT SYNTHETIC / VOCODER ARTIFACTS"
        voice_class = "verdict-synthetic"
    elif synthetic_flags == 1:
        voice_verdict = "UNUSUAL ACOUSTIC PROFILE"
        voice_class = "verdict-suspicious"
    else:
        voice_verdict = "NATURAL ACOUSTIC FREQUENCY SPECTRUM"
        voice_class = "verdict-authentic"

    metrics = {
        "duration_sec": round(duration_sec, 2),
        "framerate": framerate,
        "channels": n_channels,
        "hf_energy_ratio": round(hf_energy_ratio, 4),
        "spectral_flatness": round(flatness, 4),
        "dynamic_range_db": round(dynamic_range_db, 1),
        "voice_verdict": voice_verdict,
        "voice_class": voice_class,
    }

    return pil_spec, metrics

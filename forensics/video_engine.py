"""
Video Forensic Analysis Engine.
Samples temporal frames, calculates inter-frame jitter, optical fluctuation,
and localized artifact vectors across video timelines.
"""

from __future__ import annotations
import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import cv2
import numpy as np
import pandas as pd
from PIL import Image

from forensics.image_engine import suspicious_map, compute_ela


def sample_video_stream(
    upload_bytes: bytes,
    file_suffix: str = ".mp4",
    max_frames: int = 12
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Decodes video, uniformly extracts key frames, and calculates temporal continuity metrics.
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp:
            tmp.write(upload_bytes)
            tmp_path = tmp.name

        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            raise ValueError("Unable to open video stream. Please ensure video is MP4/H.264 or compatible container.")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

        if total_frames <= 0:
            raise ValueError("Video contains zero decodable frames.")

        duration = total_frames / fps if fps > 0 else 0.0
        sample_indices = np.unique(np.linspace(0, total_frames - 1, min(max_frames, total_frames), dtype=int))

        extracted_frames = []
        prev_gray = None

        for i, idx in enumerate(sample_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ok, bgr_frame = cap.read()
            if not ok:
                continue

            rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
            gray_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
            pil_img = Image.fromarray(rgb_frame)

            # Compute suspicious artifact map
            heat, overlay, score = suspicious_map(pil_img, colormap_name="Turbo")
            high_resp_area = float(np.mean(score >= np.percentile(score, 90)) * 100.0)

            # Compute ELA
            _, _, ela_meta = compute_ela(pil_img, quality=90)

            # Compute temporal difference from previous sampled frame
            temporal_jitter = 0.0
            if prev_gray is not None and prev_gray.shape == gray_frame.shape:
                diff = cv2.absdiff(prev_gray, gray_frame)
                temporal_jitter = float(np.mean(diff))
            prev_gray = gray_frame

            sec_stamp = float(idx / fps) if fps > 0 else 0.0

            # Estimate manipulation risk for frame
            frame_risk = min(98.0, max(5.0, (high_resp_area * 1.8) + (ela_meta["anomaly_percent"] * 6.0)))

            extracted_frames.append({
                "sample_id": i + 1,
                "frame_index": int(idx),
                "timestamp_sec": round(sec_stamp, 2),
                "high_response_area_pct": round(high_resp_area, 2),
                "ela_anomaly_pct": round(ela_meta["anomaly_percent"], 2),
                "temporal_jitter": round(temporal_jitter, 2),
                "estimated_risk_pct": round(frame_risk, 1),
                "pil_orig": pil_img,
                "pil_overlay": overlay,
                "pil_heat": heat,
            })

        cap.release()

        meta = {
            "total_frames": total_frames,
            "fps": round(fps, 2),
            "duration_sec": round(duration, 2),
            "resolution": f"{width} × {height}",
            "frames_analyzed": len(extracted_frames),
            "mean_temporal_jitter": round(float(np.mean([f["temporal_jitter"] for f in extracted_frames if f["temporal_jitter"] > 0] or [0])), 2),
            "max_risk_frame": max(extracted_frames, key=lambda x: x["estimated_risk_pct"]) if extracted_frames else None,
        }

        return extracted_frames, meta

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

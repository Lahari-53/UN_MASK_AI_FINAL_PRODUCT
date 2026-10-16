from __future__ import annotations
import base64
import hashlib
import io
import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import altair as alt
import cv2
import numpy as np
import pandas as pd
from PIL import ExifTags, Image
import streamlit as st

# Safe Asset Base64 Loader with Auto-Fallback
try:
    from assets.assets_base64 import (
        LOGO_BASE64,
        HERO_CHARACTER_BASE64,
        SAMPLE_THUMB_BASE64,
        REFERENCE_HERO_BASE64,
    )
except Exception:
    def _get_b64(fname: str) -> str:
        p = Path(__file__).parent / "assets" / fname
        if p.exists():
            with open(p, "rb") as f:
                ext = p.suffix.lower().replace(".", "")
                if ext == "jpg": ext = "jpeg"
                return f"data:image/{ext};base64,{base64.b64encode(f.read()).decode('utf-8')}"
        return ""
    LOGO_BASE64 = _get_b64("logo_mask.png")
    HERO_CHARACTER_BASE64 = _get_b64("hero_character.png")
    SAMPLE_THUMB_BASE64 = _get_b64("sample_thumb.png")
    REFERENCE_HERO_BASE64 = _get_b64("reference_hero_full.png")

from forensics.image_engine import (
    COLORMAP_DICT,
    suspicious_map,
    compute_ela,
    compute_fft_spectrum,
    compute_sensor_noise,
    compute_chroma_discrepancy,
    compute_edge_sharpness_map,
    evaluate_composite_threat,
    extract_metadata_and_hashes,
)
from forensics.video_engine import sample_video_stream
from forensics.audio_engine import analyze_wav_audio
from forensics.demo_targets import (
    generate_synthetic_diffusion_demo,
    generate_spliced_tamper_demo,
    generate_fourier_grid_demo,
    generate_pristine_camera_demo,
    generate_demo_audio_wav,
)
from forensics.report_engine import generate_html_dossier, generate_json_report

# ==============================================================================
# STREAMLIT CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="UnMask AI — Digital Media Authenticity & Forensics",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# HUMAN-DESIGNED PREMIUM OBSIDIAN UI STYLING
# ==============================================================================
REFERENCE_UI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-dark: #05070c;
    --card-bg: rgba(16, 21, 31, 0.72);
    --card-border: rgba(255, 255, 255, 0.08);
    --accent-purple: #818cf8;
    --accent-gradient: linear-gradient(135deg, #a78bfa 0%, #818cf8 50%, #6366f1 100%);
    --text-primary: #ffffff;
    --text-muted: #94a3b8;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-dark);
    color: #e2eafc;
}

#MainMenu, header, footer {
    visibility: hidden;
}

.stApp {
    background: radial-gradient(ellipse at 80% 25%, #111422 0%, #06080e 45%, #030508 100%) !important;
    background-attachment: fixed !important;
}

.block-container {
    max-width: 1420px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 3.5rem !important;
}

/* Navigation Bar */
.unmask-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 28px;
    background: rgba(10, 14, 22, 0.65);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 999px;
    margin-bottom: 32px;
}

.nav-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
}

.nav-brand img {
    height: 32px;
    width: auto;
    filter: drop-shadow(0 0 8px rgba(129, 140, 248, 0.5));
}

.nav-brand-text {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.04em;
    color: #ffffff;
}

.nav-brand-text span {
    color: #818cf8;
    font-weight: 700;
}

/* Hero Section */
.hero-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    min-height: 480px;
    margin-bottom: 36px;
}

.hero-left {
    flex: 1.15;
    max-width: 630px;
    z-index: 2;
}

.ai-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(24, 28, 44, 0.8);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 999px;
    padding: 6px 16px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #a78bfa;
    text-transform: uppercase;
    margin-bottom: 18px;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.15);
}

.hero-headline {
    font-size: 58px;
    font-weight: 800;
    letter-spacing: -0.035em;
    line-height: 1.08;
    color: #ffffff;
    margin: 0 0 16px 0;
}

.hero-headline .mask-text {
    background: linear-gradient(135deg, #a78bfa 0%, #818cf8 50%, #6366f1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-description {
    font-size: 16px;
    line-height: 1.6;
    color: #94a3b8;
    margin: 0 0 28px 0;
    max-width: 500px;
}

/* Upload Card Container */
.upload-card-wrapper {
    background: rgba(16, 21, 31, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 22px;
    backdrop-filter: blur(24px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08);
    padding: 18px;
    max-width: 540px;
}

.sample-thumb-card {
    border-radius: 16px;
    border: 1.5px solid rgba(255, 255, 255, 0.18);
    overflow: hidden;
    position: relative;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
    cursor: pointer;
    transition: all 0.25s ease;
}

.sample-thumb-card:hover {
    transform: scale(1.03);
    border-color: #818cf8;
    box-shadow: 0 12px 35px rgba(129, 140, 248, 0.3);
}

/* Hero Right Side Art */
.hero-right {
    flex: 1;
    position: relative;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    height: 520px;
}

.hero-character-img {
    height: 520px;
    width: auto;
    object-fit: contain;
    filter: contrast(1.05) brightness(1.02);
    mask-image: linear-gradient(to right, transparent 0%, black 18%, black 100%);
    -webkit-mask-image: linear-gradient(to right, transparent 0%, black 18%, black 100%);
}

.floating-real-fake {
    position: absolute;
    right: 250px;
    top: 40%;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    letter-spacing: 0.25em;
    color: #94a3b8;
    line-height: 1.9;
    font-weight: 700;
    text-transform: uppercase;
    text-align: left;
    text-shadow: 0 2px 10px rgba(0,0,0,0.8);
    pointer-events: none;
}

/* Bottom Feature Cards Grid */
.features-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: 20px;
    margin-bottom: 40px;
}

.feature-card {
    background: rgba(14, 19, 30, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 18px;
    padding: 20px;
    backdrop-filter: blur(16px);
    display: flex;
    align-items: flex-start;
    gap: 16px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    transition: all 0.25s ease;
}

.feature-card:hover {
    transform: translateY(-3px);
    border-color: rgba(167, 139, 250, 0.35);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5);
}

.feat-icon-box {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    flex-shrink: 0;
}

.feat-icon-purple {
    background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(129, 140, 248, 0.08));
    border: 1px solid rgba(167, 139, 250, 0.3);
    color: #c084fc;
}

.feat-icon-blue {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(14, 165, 233, 0.08));
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #38bdf8;
}

.feat-icon-pink {
    background: linear-gradient(135deg, rgba(244, 63, 94, 0.2), rgba(225, 29, 72, 0.08));
    border: 1px solid rgba(244, 63, 94, 0.3);
    color: #fb7185;
}

.feat-icon-teal {
    background: linear-gradient(135deg, rgba(45, 212, 191, 0.2), rgba(20, 184, 166, 0.08));
    border: 1px solid rgba(45, 212, 191, 0.3);
    color: #2dd4bf;
}

.feat-text-box h4 {
    margin: 0 0 4px 0;
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
}

.feat-text-box p {
    margin: 0;
    font-size: 13px;
    color: #8da2bb;
    line-height: 1.45;
}

/* Results & Intelligence Lab */
.result-section-header {
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
    margin: 40px 0 20px 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.verdict-banner-modern {
    padding: 22px 28px;
    border-radius: 18px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    border: 1px solid;
}

.verdict-real {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.4) 100%);
    border-color: rgba(52, 211, 153, 0.4);
    color: #6ee7b7;
}

.verdict-fake {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(127, 29, 29, 0.4) 100%);
    border-color: rgba(248, 113, 113, 0.4);
    color: #fca5a5;
}

.verdict-suspicious {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(120, 53, 15, 0.4) 100%);
    border-color: rgba(251, 191, 36, 0.4);
    color: #fde68a;
}
</style>
"""

st.markdown(REFERENCE_UI_CSS, unsafe_allow_html=True)

# Initialize Session State
if "media_type" not in st.session_state:
    st.session_state["media_type"] = "Image"
if "active_image" not in st.session_state:
    st.session_state["active_image"] = None
if "active_image_bytes" not in st.session_state:
    st.session_state["active_image_bytes"] = None
if "active_image_name" not in st.session_state:
    st.session_state["active_image_name"] = "evidence.png"
if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "Home"


# ==============================================================================
# TOP NAVIGATION BAR
# ==============================================================================
nav_cols = st.columns([2.4, 4.2, 1.8])

with nav_cols[0]:
    logo_src = LOGO_BASE64 if LOGO_BASE64 else ""
    st.markdown(f"""
    <div class="nav-brand">
        <img src="{logo_src}" alt="Mask Emblem">
        <div class="nav-brand-text">UNMASK <span>AI</span></div>
    </div>
    """, unsafe_allow_html=True)

with nav_cols[1]:
    n1, n2, n3, n4, n5 = st.columns(5)
    with n1:
        if st.button("Home", key="nav_home", use_container_width=True):
            st.session_state["active_nav"] = "Home"
            st.rerun()
    with n2:
        if st.button("Image Forensics", key="nav_img_forensics", use_container_width=True):
            st.session_state["active_nav"] = "Home"
            st.session_state["media_type"] = "Image"
            st.rerun()
    with n3:
        if st.button("Video Sleuth", key="nav_video_sleuth", use_container_width=True):
            st.session_state["active_nav"] = "Home"
            st.session_state["media_type"] = "Video"
            st.rerun()
    with n4:
        if st.button("How It Works", key="nav_how", use_container_width=True):
            st.session_state["active_nav"] = "How it works"
            st.rerun()
    with n5:
        if st.button("Methodology", key="nav_method", use_container_width=True):
            st.session_state["active_nav"] = "About"
            st.rerun()

with nav_cols[2]:
    if st.button("Get Started  ➔", key="nav_get_started", use_container_width=True):
        st.session_state["active_nav"] = "Home"
        st.rerun()

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# NAV VIEW: HOW IT WORKS
# ==============================================================================
if st.session_state["active_nav"] == "How it works":
    st.markdown("""
    <div style="text-align: center; margin: 20px 0 35px 0;">
        <div class="ai-badge">DIGITAL INTEGRITY PIPELINE</div>
        <h1 style="font-size: 42px; font-weight: 800; color: #fff;">How UnMask AI Verifies Media</h1>
        <p style="color: #94a3b8; max-width: 680px; margin: 0 auto; font-size: 15px;">
            A rigorous multi-spectral pipeline analyzing physical sensor noise patterns, frequency-domain artifacts, and compression quantization history.
        </p>
    </div>
    """, unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("""
        <div class="feature-card" style="flex-direction: column; text-align: left; height: 100%;">
            <div class="feat-icon-box feat-icon-purple">01</div>
            <div class="feat-text-box" style="margin-top: 12px;">
                <h4>Media Ingestion</h4>
                <p>Generates cryptographic SHA-256 fingerprints, reads EXIF camera metadata tags, and parses uncompressed raw pixels.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown("""
        <div class="feature-card" style="flex-direction: column; text-align: left; height: 100%;">
            <div class="feat-icon-box feat-icon-blue">02</div>
            <div class="feat-text-box" style="margin-top: 12px;">
                <h4>Spectral Decomposition</h4>
                <p>Computes 2D Fast Fourier Transform (FFT) power spectra to detect periodic checkerboard lattice spikes left by generative deconvolution.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown("""
        <div class="feature-card" style="flex-direction: column; text-align: left; height: 100%;">
            <div class="feat-icon-box feat-icon-pink">03</div>
            <div class="feat-text-box" style="margin-top: 12px;">
                <h4>Sensor Noise &amp; ELA</h4>
                <p>Extracts Photo Response Non-Uniformity (PRNU) sensor residue and computes Error Level Analysis to detect splicing boundaries.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with s4:
        st.markdown("""
        <div class="feature-card" style="flex-direction: column; text-align: left; height: 100%;">
            <div class="feat-icon-box feat-icon-teal">04</div>
            <div class="feat-text-box" style="margin-top: 12px;">
                <h4>Threat Assessment</h4>
                <p>Synthesizes independent mathematical vectors into an overall authenticity score and generates an exportable audit dossier.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    if st.button("← Return to Workbench", key="back_from_how"):
        st.session_state["active_nav"] = "Home"
        st.rerun()


# ==============================================================================
# NAV VIEW: METHODOLOGY & LIMITATIONS
# ==============================================================================
elif st.session_state["active_nav"] == "About":
    st.markdown("""
    <div style="text-align: center; margin: 20px 0 35px 0;">
        <div class="ai-badge">SCIENTIFIC FOUNDATIONS &amp; LIMITS</div>
        <h1 style="font-size: 42px; font-weight: 800; color: #fff;">Forensic Methodology</h1>
        <p style="color: #94a3b8; max-width: 700px; margin: 0 auto; font-size: 15px;">
            Engineered as an investigative triage workbench designed for digital forensic analysts, newsrooms, and security researchers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: rgba(14, 19, 30, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; padding: 28px; max-width: 900px; margin: 0 auto;">
        <h3 style="color: #fff; margin-top: 0;">Multi-Vector Signal Independence</h3>
        <p style="color: #94a3b8; line-height: 1.7;">
            While black-box neural classifiers frequently fail on out-of-distribution inputs, physical forensic principles (Error Level Analysis, 2D Fourier power spectra, and sensor noise consistency) measure immutable artifacts introduced during digital synthesis.
        </p>
        <h3 style="color: #fff; margin-top: 24px;">Investigative Limitations</h3>
        <p style="color: #94a3b8; line-height: 1.7;">
            - <strong>Triage Tool, Not a Courtroom Certificate:</strong> Statistical indicators surface areas warranting human scrutiny; they do not replace formal provenance chains.<br>
            - <strong>Recompression Sensitivity:</strong> Multi-generational recompression (e.g. sharing across social messaging apps) introduces quantization noise that can degrade sensor noise signals. Always seek raw camera originals where possible.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    if st.button("← Return to Workbench", key="back_from_about"):
        st.session_state["active_nav"] = "Home"
        st.rerun()


# ==============================================================================
# MAIN WORKBENCH VIEW
# ==============================================================================
else:
    hero_col_left, hero_col_right = st.columns([1.15, 1])

    # Left Column: Headline & Interactive Media Ingestion
    with hero_col_left:
        st.markdown("""
        <div class="ai-badge">DIGITAL MEDIA FORENSICS</div>
        <h1 class="hero-headline">
            See Beyond<br>
            the <span class="mask-text">Mask.</span>
        </h1>
        <p class="hero-description">
            Detect deepfakes, manipulated media and uncover the truth with advanced AI forensics.
        </p>
        """, unsafe_allow_html=True)

        # Upload Card Container
        st.markdown('<div class="upload-card-wrapper">', unsafe_allow_html=True)

        # Media Type Selection (4 Full Interactive Modes)
        m_t1, m_t2, m_t3, m_t4 = st.columns(4)
        with m_t1:
            if st.button("🖼️ Image", key="tab_btn_img", use_container_width=True):
                st.session_state["media_type"] = "Image"
                st.rerun()
        with m_t2:
            if st.button("📹 Video", key="tab_btn_vid", use_container_width=True):
                st.session_state["media_type"] = "Video"
                st.rerun()
        with m_t3:
            if st.button("👁️ Webcam", key="tab_btn_cam", use_container_width=True):
                st.session_state["media_type"] = "Webcam"
                st.rerun()
        with m_t4:
            if st.button("🎙️ Audio", key="tab_btn_aud", use_container_width=True):
                st.session_state["media_type"] = "Audio"
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Mode 1: Image Upload
        if st.session_state["media_type"] == "Image":
            c_drop, c_thumb = st.columns([2.3, 1])
            with c_drop:
                uploaded_file = st.file_uploader(
                    "Drop an image here",
                    type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
                    label_visibility="collapsed",
                    key="hero_img_uploader",
                    help="Supports PNG, JPG, JPEG, WEBP, BMP, TIFF • Max 200MB"
                )
                st.markdown("""
                <div style="text-align: center; margin-top: -10px; pointer-events: none;">
                    <div style="font-size: 11px; color: #64748b;">Supports PNG, JPG, JPEG, WEBP, BMP, TIFF • Max 200MB</div>
                </div>
                """, unsafe_allow_html=True)

            with c_thumb:
                thumb_src = SAMPLE_THUMB_BASE64 if SAMPLE_THUMB_BASE64 else ""
                st.markdown(f"""
                <div class="sample-thumb-card" title="Click to test sample evidence">
                    <img src="{thumb_src}" style="width: 100%; height: 95px; object-fit: cover; display: block;" alt="Sample Thumbnail">
                    <div style="position: absolute; bottom: 6px; right: 6px; background: rgba(0,0,0,0.6); padding: 3px 6px; border-radius: 6px; font-size: 11px; color: #fff;">Sample</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Test Sample", key="btn_sample_thumb", use_container_width=True):
                    demo_img = generate_synthetic_diffusion_demo()
                    buf = io.BytesIO()
                    demo_img.save(buf, format="PNG")
                    st.session_state["active_image"] = demo_img
                    st.session_state["active_image_bytes"] = buf.getvalue()
                    st.session_state["active_image_name"] = "sample_masked_portrait.png"
                    st.rerun()

        # Mode 2: Video Upload
        elif st.session_state["media_type"] == "Video":
            uploaded_video = st.file_uploader(
                "Drop a video here",
                type=["mp4", "mov", "avi", "mkv"],
                label_visibility="collapsed",
                key="hero_video_uploader"
            )
            st.markdown("""
            <div style="text-align: center; margin-top: -10px;">
                <div style="font-size: 11px; color: #64748b;">Supports MP4, MOV, AVI, MKV • Keyframe Temporal Analysis</div>
            </div>
            """, unsafe_allow_html=True)

        # Mode 3: Live Webcam Scanner
        elif st.session_state["media_type"] == "Webcam":
            webcam_photo = st.camera_input("Capture optical sensor target", key="webcam_input")

        # Mode 4: Audio Vocoder Analysis
        else:
            uploaded_audio = st.file_uploader("Upload audio file (.WAV)", type=["wav"], key="audio_input")
            c_aud1, c_aud2 = st.columns(2)
            with c_aud1:
                if st.button("Load Vocoder Demo", key="aud_demo_synth", use_container_width=True):
                    st.session_state["active_audio"] = generate_demo_audio_wav(synthetic_mode=True)
                    st.session_state["active_audio_label"] = "Synthetic Vocoder Simulation"
                    st.rerun()
            with c_aud2:
                if st.button("Load Organic Speech Demo", key="aud_demo_real", use_container_width=True):
                    st.session_state["active_audio"] = generate_demo_audio_wav(synthetic_mode=False)
                    st.session_state["active_audio_label"] = "Organic Human Speech"
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Right Column: Character Artwork & Floating Elements
    with hero_col_right:
        char_src = HERO_CHARACTER_BASE64 if HERO_CHARACTER_BASE64 else ""
        st.markdown(f"""
        <div class="hero-right">
            <img src="{char_src}" class="hero-character-img" alt="Unmask Character with Mask">
            <div class="floating-real-fake">
                REAL<br>OR<br>FAKE ?
            </div>
        </div>
        """, unsafe_allow_html=True)

        demo_pill_col1, demo_pill_col2 = st.columns([1.2, 1])
        with demo_pill_col2:
            if st.button("▶  Watch Demo (See in action)", key="btn_watch_demo", use_container_width=True):
                demo_img = generate_synthetic_diffusion_demo()
                buf = io.BytesIO()
                demo_img.save(buf, format="PNG")
                st.session_state["active_image"] = demo_img
                st.session_state["active_image_bytes"] = buf.getvalue()
                st.session_state["active_image_name"] = "demo_diffusion_target.png"
                st.rerun()

    # Bottom 4 Feature Cards (Interactive triggers)
    st.markdown("""
    <div class="features-grid">
        <div class="feature-card">
            <div class="feat-icon-box feat-icon-purple">🖼️</div>
            <div class="feat-text-box">
                <h4>Deepfake Detection</h4>
                <p>Identify AI-generated and edited media</p>
            </div>
        </div>
        <div class="feature-card">
            <div class="feat-icon-box feat-icon-blue">📹</div>
            <div class="feat-text-box">
                <h4>Video Analysis</h4>
                <p>Detect splices, manipulations and inconsistencies</p>
            </div>
        </div>
        <div class="feature-card">
            <div class="feat-icon-box feat-icon-pink">📊</div>
            <div class="feat-text-box">
                <h4>Multi-Spectral Analysis</h4>
                <p>Advanced ELA, frequency and noise pattern detection</p>
            </div>
        </div>
        <div class="feature-card">
            <div class="feat-icon-box feat-icon-teal">🛡️</div>
            <div class="feat-text-box">
                <h4>Detailed Reports</h4>
                <p>Get visual explanations and confidence scores</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # ==============================================================================
    # REAL-TIME FORENSIC RESULT DECK
    # ==============================================================================
    # 1. Image / Webcam Result
    current_img = None
    current_bytes = None
    current_name = "evidence.png"

    if 'uploaded_file' in locals() and uploaded_file is not None:
        current_bytes = uploaded_file.getvalue()
        current_img = Image.open(io.BytesIO(current_bytes)).convert("RGB")
        current_name = uploaded_file.name
    elif 'webcam_photo' in locals() and webcam_photo is not None:
        current_bytes = webcam_photo.getvalue()
        current_img = Image.open(io.BytesIO(current_bytes)).convert("RGB")
        current_name = "optical_webcam_capture.png"
    elif st.session_state["active_image"] is not None and st.session_state["media_type"] in ["Image", "Webcam"]:
        current_img = st.session_state["active_image"]
        current_bytes = st.session_state["active_image_bytes"]
        current_name = st.session_state["active_image_name"]

    if current_img is not None and st.session_state["media_type"] in ["Image", "Webcam"]:
        st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 30px 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="result-section-header">
            <span>FORENSIC VERIFICATION AUDIT</span>
        </div>
        """, unsafe_allow_html=True)

        t0 = time.time()
        with st.spinner("Computing Error Level Analysis, 2D Fourier decomposition, and sensor noise tensors..."):
            heat_img, overlay_img, susp_score = suspicious_map(current_img, colormap_name="Turbo", alpha=0.45)
            ela_amp_img, ela_heat_img, ela_metrics = compute_ela(current_img, quality=90, scale=15, colormap_name="Turbo")
            fft_img, radial_profile, fft_metrics = compute_fft_spectrum(current_img, colormap_name="Inferno")
            noise_res_img, noise_var_img, noise_metrics = compute_sensor_noise(current_img, colormap_name="Viridis")
            chroma_img, chroma_metrics = compute_chroma_discrepancy(current_img, colormap_name="Magma")
            sharp_img, sharp_metrics = compute_edge_sharpness_map(current_img, colormap_name="Turbo")

            threat = evaluate_composite_threat(ela_metrics, fft_metrics, noise_metrics, chroma_metrics, sharp_metrics)
            metadata = extract_metadata_and_hashes(current_img, current_bytes or b"", current_name)

        elapsed = round(time.time() - t0, 2)

        is_synthetic = threat["composite_score"] >= 60.0
        v_class = "verdict-fake" if is_synthetic else "verdict-real"
        v_label = "SYNTHETIC / AI-GENERATED MEDIA DETECTED" if is_synthetic else "VERIFIED ORGANIC SENSOR CAPTURE"

        st.markdown(f"""
        <div class="verdict-banner-modern {v_class}">
            <div>
                <div style="font-size: 11px; letter-spacing: 0.15em; font-family: 'JetBrains Mono'; opacity: 0.8; text-transform: uppercase;">
                    FORENSIC DETERMINATION
                </div>
                <div style="font-size: 24px; font-weight: 800; margin: 4px 0 6px 0;">{v_label}</div>
                <div style="font-size: 13px; max-width: 650px; opacity: 0.9; line-height: 1.5;">
                    {threat['summary']}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 11px; letter-spacing: 0.15em; font-family: 'JetBrains Mono'; opacity: 0.8;">CONFIDENCE</div>
                <div style="font-size: 40px; font-weight: 900; font-family: 'Plus Jakarta Sans';">{threat['composite_score']}%</div>
                <div style="font-size: 11px; font-weight: 700;">{threat['threat_level']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Dimensions", metadata["dimensions"], f"{metadata['megapixels']} MP")
        m2.metric("ELA Anomaly Area", f"{ela_metrics['anomaly_percent']}%", "Q=90")
        m3.metric("FFT Peak Ratio", f"{fft_metrics['peak_anomaly_ratio']}x", "Lattice grid")
        m4.metric("Noise Dispersion", f"{noise_metrics['noise_heterogeneity']}%", "PRNU variance")
        m5.metric("Scan Latency", f"{elapsed}s", "Local OpenCV / FFT")

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("#### Multi-Channel Inspection Studio")

        chan_sel = st.radio(
            "Active Channel",
            options=[
                "Multi-Spectral Heatmap Overlay",
                "Error Level Analysis (ELA Residuals)",
                "2D Fourier Spectrogram (FFT)",
                "PRNU Sensor Noise Variance",
                "Chrominance Disparity (YCbCr)",
                "Focus & Edge Sharpness Map"
            ],
            horizontal=True,
            label_visibility="collapsed"
        )

        c_view_left, c_view_right = st.columns(2)
        with c_view_left:
            st.markdown(f"**Original Evidence** · `{current_name}`")
            st.image(current_img, use_container_width=True)

        with c_view_right:
            if "Multi-Spectral" in chan_sel:
                st.markdown("**Multi-Spectral Composite Overlay** (High-frequency + Texture)")
                st.image(overlay_img, use_container_width=True)
            elif "Error Level" in chan_sel:
                st.markdown(f"**ELA Compression Heatmap** (Quality=90)")
                st.image(ela_heat_img, use_container_width=True)
            elif "2D Fourier" in chan_sel:
                st.markdown("**2D FFT Power Spectrum** (Frequency Lattice Decomposition)")
                st.image(fft_img, use_container_width=True)
            elif "Sensor Noise" in chan_sel:
                st.markdown("**PRNU Sensor Noise Variance Map** (Physical Sensor Uniformity)")
                st.image(noise_var_img, use_container_width=True)
            elif "Chrominance" in chan_sel:
                st.markdown("**YCbCr Chroma Gradient Edge Map** (Skin & Edge Color Bleed)")
                st.image(chroma_img, use_container_width=True)
            else:
                st.markdown("**Laplacian Sharpness Variance Map** (Focus Inconsistency)")
                st.image(sharp_img, use_container_width=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            st.markdown("#### Cryptographic Integrity & Provenance")
            st.code(f"SHA-256 : {metadata['sha256']}\nMD5     : {metadata['md5']}", language="bash")
            st.caption(f"File Size: {metadata['filesize_kb']} KB · Header Signatures: {metadata['ai_tool_detected']}")

        with exp_col2:
            st.markdown("#### Export Formal Evidence Dossier")
            html_dossier = generate_html_dossier(threat, metadata, current_img, overlay_img)
            st.download_button(
                label="DOWNLOAD CLASSIFIED HTML DOSSIER",
                data=html_dossier,
                file_name=f"unmask_forensic_dossier_{metadata['sha256'][:8]}.html",
                mime="text/html",
                use_container_width=True
            )
            json_report = generate_json_report(threat, metadata, {
                "ela": ela_metrics, "fft": fft_metrics, "noise": noise_metrics
            })
            st.download_button(
                label="DOWNLOAD STRUCTURED JSON REPORT",
                data=json_report,
                file_name=f"unmask_forensic_report_{metadata['sha256'][:8]}.json",
                mime="application/json",
                use_container_width=True
            )

    # 2. Video Analysis Output
    if 'uploaded_video' in locals() and uploaded_video is not None and st.session_state["media_type"] == "Video":
        st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 30px 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="result-section-header">
            <span>VIDEO TEMPORAL CONTINUITY AUDIT</span>
        </div>
        """, unsafe_allow_html=True)

        t_v0 = time.time()
        with st.spinner("Extracting keyframes and computing temporal optical continuity..."):
            frames_data, v_meta = sample_video_stream(
                uploaded_video.getvalue(),
                file_suffix=Path(uploaded_video.name).suffix or ".mp4",
                max_frames=8
            )
        elapsed_v = round(time.time() - t_v0, 2)

        vm1, vm2, vm3, vm4 = st.columns(4)
        vm1.metric("Resolution", v_meta["resolution"], f"{v_meta['fps']} FPS")
        vm2.metric("Total Frames", v_meta["total_frames"], f"{v_meta['duration_sec']}s")
        vm3.metric("Keyframes Scanned", v_meta["frames_analyzed"])
        vm4.metric("Mean Temporal Jitter", f"{v_meta['mean_temporal_jitter']}", "Inter-frame variance")

        v_df = pd.DataFrame([
            {
                "Time (s)": f["timestamp_sec"],
                "Estimated Risk (%)": f["estimated_risk_pct"],
                "Temporal Jitter": f["temporal_jitter"],
                "Artifact Area (%)": f["high_response_area_pct"]
            }
            for f in frames_data
        ])

        v_chart = alt.Chart(v_df).mark_line(
            color="#818cf8", strokeWidth=3, point=True
        ).encode(
            x=alt.X("Time (s)", title="Video Timeline (Seconds)"),
            y=alt.Y("Estimated Risk (%)", title="Estimated Risk (%)", scale=alt.Scale(domain=[0, 100])),
            tooltip=["Time (s)", "Estimated Risk (%)", "Temporal Jitter", "Artifact Area (%)"]
        ).properties(height=240)
        st.altair_chart(v_chart, use_container_width=True)

        st.markdown("#### Sampled Keyframe Diagnostics")
        film_cols = st.columns(2)
        for i, fd in enumerate(frames_data):
            with film_cols[i % 2]:
                st.markdown(f"**Keyframe #{fd['sample_id']} @ {fd['timestamp_sec']}s (Risk: {fd['estimated_risk_pct']}%)**")
                st.image(fd["pil_overlay"], use_container_width=True)

    # 3. Audio Analysis Output
    if st.session_state["media_type"] == "Audio":
        active_aud = None
        aud_label = "Audio Evidence"
        if 'uploaded_audio' in locals() and uploaded_audio is not None:
            active_aud = uploaded_audio.getvalue()
            aud_label = uploaded_audio.name
        elif "active_audio" in st.session_state:
            active_aud = st.session_state["active_audio"]
            aud_label = st.session_state.get("active_audio_label", "Demo Audio")

        if active_aud:
            st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 30px 0;'>", unsafe_allow_html=True)
            st.markdown("""
            <div class="result-section-header">
                <span>AUDIO SPECTRAL VOCODER AUDIT</span>
            </div>
            """, unsafe_allow_html=True)

            st.audio(active_aud, format="audio/wav")
            spec_img, aud_metrics = analyze_wav_audio(active_aud, colormap_name="Viridis")

            am1, am2, am3, am4 = st.columns(4)
            am1.metric("Duration", f"{aud_metrics['duration_sec']}s")
            am2.metric("Sample Rate", f"{aud_metrics['framerate']} Hz")
            am3.metric("HF Energy Ratio", f"{aud_metrics['hf_energy_ratio']*100:.2f}%", "<1.5% flags cutoff")
            am4.metric("Spectral Flatness", f"{aud_metrics['spectral_flatness']:.4f}")

            st.markdown(f"**STFT Spectrogram Decomposition** (Target: `{aud_label}`)")
            st.image(spec_img, use_container_width=True)
            st.caption(f"Determination: {aud_metrics['voice_verdict']}")

# UnMask AI // Cyber Forensics & Tamper Intelligence Suite

A state-of-the-art, defense-grade digital media forensics workbench designed to detect AI-generated synthetic media, deepfakes, spliced composites, and voice synthesis.

Built with high-performance multi-spectral frequency analysis, physical sensor noise heuristics, and zero torch dependencies for maximum speed and portability.

---

## ⚡ Quick Start

```powershell
# Activate existing virtualenv and launch Streamlit
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 🚀 Key Modules & Capabilities

### 1. 🛰️ Multi-Spectral Image Forensics
- **Error Level Analysis (ELA):** Recompression differential analysis detecting digital splicing, copy-move forgery, and localized quality anomalies.
- **2D Fast Fourier Transform (FFT) Spectrogram:** High-frequency frequency-domain decomposition detecting periodic deconvolution lattice grids left by GAN and Latent Diffusion models.
- **PRNU Sensor Noise Uniformity:** Isolates camera sensor noise residue; detects discontinuities and unnatural localized noise drops.
- **Chrominance Disparity (YCbCr):** Evaluates color gamut edges, chromatic aberration anomalies, and facial saturation bleed.
- **Laplacian Edge Focus Inconsistency:** Maps block-wise variance of sharpness to catch artificial boundary blurs or pasted facial features.
- **Multi-Vector Threat Assessment:** Synthesizes all spectral vectors into an automated Threat Index percentage and verdict banner.

### 2. 🎬 Video Temporal Sleuth & Jitter Vectoring
- Uniform keyframe extraction with customizable sampling resolution (4 to 20 frames).
- **Temporal Flicker & Inter-Frame Jitter Metric:** Detects frame-to-frame optical instability and warping.
- Interactive **Altair Temporal Timeline Chart** plotting manipulation risk over time.
- Sampled keyframe filmstrip with individual diagnostic overlays.
- Telemetry export in CSV and JSON formats.

### 3. 👁️‍🗨️ Live Cyber Webcam Scanner
- Directly captures live camera streams to perform instant biometric tamper scans and authenticity checks.

### 4. 🎙️ Audio Vocoder & Deepfake Voice Suite
- STFT Short-Time Fourier Transform Spectrogram decomposition.
- Brickwall high-frequency cutoff analysis (flags synthetic vocoders dropping frequencies >8kHz).
- Spectral flatness & dynamic range metrics for synthetic speech detection.

### 5. 🎯 Instant Demo Lab (Zero Upload Testing)
- Built-in procedural target generators:
  - **Target Alpha:** Latent Diffusion AI Artifacts (synthetic portrait)
  - **Target Beta:** Spliced Document / Tampered Region (ELA spikes)
  - **Target Gamma:** 2D Fourier Lattice Grid (upsampling deconvolution artifacts)
  - **Target Delta:** Pristine Optical Sensor (authentic camera capture)

### 6. 🛡️ Cryptographic Chain of Custody & Dossier Export
- SHA-256 and MD5 cryptographic integrity hashes.
- Embedded EXIF and AI generation signature scanner.
- One-click export of a classified, print-ready **Cyber Forensic Dossier (HTML)** and structured **JSON Report**.

---

## ⚠️ Forensic Disclaimer
This platform is an investigative triage intelligence system. Automated threat scores reflect mathematical and physical anomalies across spectral domains. Always corroborate findings with cryptographic provenance (C2PA) and human expert evaluation.

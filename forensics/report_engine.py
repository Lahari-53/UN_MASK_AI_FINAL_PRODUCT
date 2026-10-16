"""
Forensic Dossier & Intelligence Report Generator.
Exports classified-style HTML chain-of-custody dossiers and structured JSON reports.
"""

from __future__ import annotations
import json
import base64
import io
from datetime import datetime
from typing import Dict, Any
from PIL import Image


def generate_html_dossier(
    threat_info: Dict[str, Any],
    metadata: Dict[str, Any],
    preview_image: Image.Image,
    heatmap_image: Image.Image
) -> str:
    """
    Renders an official, print-ready, classified Cyber Forensics Dossier in HTML.
    """
    # Convert images to base64
    def to_b64(img: Image.Image) -> str:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    orig_b64 = to_b64(preview_image)
    heat_b64 = to_b64(heatmap_image)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    case_id = f"CYBER-EVID-{metadata.get('sha256', '000000')[:8].upper()}"

    vectors_html = ""
    for vec_name, val in threat_info.get("vectors", {}).items():
        bar_color = "#00f5d4" if val < 35 else "#ffb703" if val < 65 else "#ff0055"
        vectors_html += f"""
        <div style="margin-bottom: 12px;">
            <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
                <span>{vec_name}</span>
                <span style="font-weight:bold; color:{bar_color};">{val}%</span>
            </div>
            <div style="background:#111b2d; height:6px; border-radius:3px; overflow:hidden;">
                <div style="background:{bar_color}; width:{val}%; height:100%;"></div>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>UNMASK AI // FORENSIC DOSSIER {case_id}</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;600&display=swap');
    body {{
        background: #060b14;
        color: #e2eafc;
        font-family: 'Inter', sans-serif;
        padding: 40px;
        margin: 0;
    }}
    .dossier-card {{
        max-width: 900px;
        margin: 0 auto;
        background: #0a1222;
        border: 1px solid #00f2fe;
        box-shadow: 0 0 35px rgba(0, 242, 254, 0.2);
        border-radius: 16px;
        padding: 36px;
    }}
    .dossier-header {{
        border-bottom: 1px solid rgba(0, 242, 254, 0.3);
        padding-bottom: 20px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .stamp {{
        border: 2px solid #ff0055;
        color: #ff0055;
        font-family: 'Orbitron', monospace;
        font-weight: 800;
        font-size: 13px;
        padding: 6px 14px;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        border-radius: 6px;
        transform: rotate(-3deg);
    }}
    h1 {{
        font-family: 'Orbitron', sans-serif;
        font-size: 24px;
        margin: 0 0 6px 0;
        color: #ffffff;
        letter-spacing: 0.05em;
    }}
    .case-sub {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #00f2fe;
    }}
    .grid-2 {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 24px;
    }}
    .img-box {{
        background: #040810;
        border: 1px solid #1a2a44;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }}
    .img-box img {{
        max-width: 100%;
        border-radius: 6px;
        height: auto;
    }}
    .mono-table {{
        width: 100%;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        border-collapse: collapse;
        margin: 16px 0;
    }}
    .mono-table td {{
        padding: 8px 12px;
        border: 1px solid #19273c;
    }}
    .mono-table tr:nth-child(even) {{
        background: #08101e;
    }}
    .verdict-banner {{
        background: #0d1e38;
        border: 1px solid #00f5d4;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .footer-note {{
        font-size: 11px;
        color: #64748b;
        margin-top: 30px;
        text-align: center;
        border-top: 1px solid #1a2a44;
        padding-top: 16px;
    }}
</style>
</head>
<body>
<div class="dossier-card">
    <div class="dossier-header">
        <div>
            <h1>UNMASK AI // FORENSIC AUDIT DOSSIER</h1>
            <div class="case-sub">CASE ID: {case_id} &nbsp;·&nbsp; GENERATED: {now_str}</div>
        </div>
        <div class="stamp">CLASSIFIED EVIDENCE</div>
    </div>

    <div class="verdict-banner">
        <div>
            <div style="font-size:12px; color:#94a3b8; font-family:'JetBrains Mono';">FORENSIC VERDICT</div>
            <div style="font-family:'Orbitron'; font-size:22px; font-weight:800; color:#ffffff;">{threat_info.get('verdict')}</div>
            <div style="font-size:12px; color:#38bdf8; margin-top:4px;">{threat_info.get('summary')}</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:12px; color:#94a3b8; font-family:'JetBrains Mono';">THREAT INDEX</div>
            <div style="font-family:'Orbitron'; font-size:32px; font-weight:900; color:#00f2fe;">{threat_info.get('composite_score')}%</div>
        </div>
    </div>

    <div class="grid-2">
        <div class="img-box">
            <div style="font-size:11px; font-family:'JetBrains Mono'; color:#94a3b8; margin-bottom:8px;">ORIGINAL EVIDENCE</div>
            <img src="data:image/png;base64,{orig_b64}" alt="Original Evidence">
        </div>
        <div class="img-box">
            <div style="font-size:11px; font-family:'JetBrains Mono'; color:#00f2fe; margin-bottom:8px;">MULTI-SPECTRAL FORENSIC OVERLAY</div>
            <img src="data:image/png;base64,{heat_b64}" alt="Forensic Overlay">
        </div>
    </div>

    <h3 style="font-family:'Orbitron'; font-size:14px; margin-bottom:12px; color:#93c5fd;">SPECTRAL VECTOR BREAKDOWN</h3>
    {vectors_html}

    <h3 style="font-family:'Orbitron'; font-size:14px; margin:24px 0 12px 0; color:#93c5fd;">CRYPTOGRAPHIC CHAIN OF CUSTODY</h3>
    <table class="mono-table">
        <tr><td>FILE NAME</td><td>{metadata.get('filename')}</td></tr>
        <tr><td>DIMENSIONS</td><td>{metadata.get('dimensions')} ({metadata.get('megapixels')} MP)</td></tr>
        <tr><td>FILE SIZE</td><td>{metadata.get('filesize_kb')} KB</td></tr>
        <tr><td>SHA-256 FINGERPRINT</td><td style="color:#00f5d4; word-break:break-all;">{metadata.get('sha256')}</td></tr>
        <tr><td>MD5 HASH</td><td style="color:#67e8f9;">{metadata.get('md5')}</td></tr>
        <tr><td>AI METADATA SIGNATURE</td><td style="color:#facc15;">{metadata.get('ai_tool_detected')}</td></tr>
    </table>

    <div class="footer-note">
        UNMASK AI DEFENSE FORENSICS LAB · CONFIDENTIAL EVIDENCE PROTOCOL · PRODUCED FOR TRIAGE AND EXPERT REVIEW
    </div>
</div>
</body>
</html>
"""
    return html


def generate_json_report(
    threat_info: Dict[str, Any],
    metadata: Dict[str, Any],
    raw_metrics: Dict[str, Any]
) -> str:
    """
    Serializes complete forensic findings into structured JSON.
    """
    payload = {
        "report_type": "UnMask_AI_Forensic_Dossier",
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "case_id": f"CYBER-{metadata.get('sha256', '000000')[:8].upper()}",
        "evidence_metadata": metadata,
        "threat_assessment": threat_info,
        "spectral_diagnostics": raw_metrics,
        "audit_disclaimer": "Forensic heuristics reflect physical and mathematical anomalies; intended for human investigator triage."
    }
    return json.dumps(payload, indent=2)

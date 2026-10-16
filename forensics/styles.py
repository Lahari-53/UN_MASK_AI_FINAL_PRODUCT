"""
Pixel-Perfect UI/UX Styling Matching Reference Design for UnMask AI.
"""

REFERENCE_UI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

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
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
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

/* Custom Navigation Bar */
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

.nav-links {
    display: flex;
    align-items: center;
    gap: 36px;
    list-style: none;
    margin: 0;
    padding: 0;
}

.nav-link-item {
    font-size: 14px;
    font-weight: 500;
    color: #94a3b8;
    text-decoration: none;
    transition: color 0.2s ease;
    cursor: pointer;
    position: relative;
}

.nav-link-item:hover, .nav-link-item.active {
    color: #ffffff;
}

.nav-link-item.active::after {
    content: "";
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #818cf8;
    box-shadow: 0 0 8px #818cf8;
}

.nav-btn-started {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 999px;
    padding: 8px 22px;
    font-size: 13px;
    font-weight: 600;
    color: #ffffff;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}

.nav-btn-started:hover {
    background: rgba(255, 255, 255, 0.12);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
    color: #ffffff;
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
    flex: 1.1;
    max-width: 620px;
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
    font-size: 56px;
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
    max-width: 490px;
}

/* Hero Upload Card */
.upload-card-wrapper {
    background: rgba(16, 21, 31, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 22px;
    backdrop-filter: blur(24px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08);
    padding: 18px;
    max-width: 530px;
}

.upload-tabs {
    display: inline-flex;
    background: rgba(8, 12, 20, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    margin-bottom: 14px;
}

.tab-pill {
    padding: 7px 18px;
    border-radius: 9px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}

.tab-pill.active {
    background: rgba(255, 255, 255, 0.12);
    border-color: rgba(255, 255, 255, 0.2);
    color: #ffffff;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.tab-pill.inactive {
    background: transparent;
    color: #64748b;
}

.dropzone-box {
    border: 1.5px dashed rgba(255, 255, 255, 0.15);
    border-radius: 16px;
    background: rgba(8, 12, 19, 0.5);
    padding: 24px 18px;
    text-align: center;
    transition: all 0.25s ease;
}

.dropzone-box:hover {
    border-color: #818cf8;
    background: rgba(14, 19, 32, 0.7);
}

.drop-icon {
    font-size: 28px;
    margin-bottom: 6px;
    color: #a78bfa;
}

.drop-title {
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 3px;
}

.drop-sub {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 6px;
}

.drop-formats {
    font-size: 11px;
    color: #475569;
}

/* Sample Preview Thumbnail */
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

.watch-demo-pill {
    position: absolute;
    bottom: 40px;
    right: 30px;
    background: rgba(15, 20, 31, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 999px;
    padding: 10px 22px;
    display: flex;
    align-items: center;
    gap: 14px;
    backdrop-filter: blur(16px);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6);
    cursor: pointer;
    transition: all 0.25s ease;
    text-decoration: none;
}

.watch-demo-pill:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.3);
    box-shadow: 0 16px 45px rgba(0, 0, 0, 0.8);
}

.demo-play-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    color: #ffffff;
}

.demo-text-box {
    display: flex;
    flex-direction: column;
}

.demo-title {
    font-size: 13px;
    font-weight: 700;
    color: #ffffff;
}

.demo-sub {
    font-size: 11px;
    color: #64748b;
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

CYBER_THEME_CSS = REFERENCE_UI_CSS


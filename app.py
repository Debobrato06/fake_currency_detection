import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image
import plotly.express as px
import time
import os
import base64
from detector import analyze_currency_elite

st.set_page_config(
    page_title="AI Currency Guardian | Elite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- State Management (URL-First) ---
# This ensures state persists across reloads and sharing
if "p" in st.query_params:
    st.session_state.page = st.query_params["p"]
elif 'page' not in st.session_state:
    st.session_state.page = 'scanner'

if "theme" in st.query_params:
    st.session_state.theme = st.query_params["theme"]
elif 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

if 'font_scale' not in st.session_state:
    st.session_state.font_scale = 1.0

# Ensure current state is reflected in URL for all subsequent clicks
st.query_params["p"] = st.session_state.page
st.query_params["theme"] = st.session_state.theme

# --- Asset Helpers ---
def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

hero_base64 = get_base64_img("static/hero.png")

# --- Custom Styling (Elite Design System) ---
theme_vars = {
    'dark': {
        'bg_main': '#05060f',
        'bg_overlay': 'rgba(5, 6, 15, 0.90)',
        'bg_card': 'rgba(255, 255, 255, 0.05)',
        'border': 'rgba(255, 255, 255, 0.12)',
        'text_main': '#ffffff',
        'text_muted': '#9ca3af',
        'glass_header': 'rgba(10, 11, 23, 0.95)',
        'accent': '#10b981'
    },
    'light': {
        'bg_main': '#f8fafc',
        'bg_overlay': 'rgba(248, 250, 252, 0.93)',
        'bg_card': 'rgba(255, 255, 255, 0.85)',
        'border': 'rgba(0, 0, 0, 0.08)',
        'text_main': '#0f172a',
        'text_muted': '#64748b',
        'glass_header': 'rgba(255, 255, 255, 0.95)',
        'accent': '#059669'
    }
}[st.session_state.theme]

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100;300;400;600;800;900&family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        font-size: {st.session_state.font_scale}rem !important;
    }}

    .stApp {{
        background: linear-gradient({theme_vars['bg_overlay']}, {theme_vars['bg_overlay']}), url("data:image/png;base64,{hero_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: {theme_vars['text_main']};
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* Text Readability Enhancements */
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stHeader"] {{
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}

    /* Global Text Color Force */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div, .stApp button {{
        color: {theme_vars['text_main']};
    }}

    /* Force Widget Label & Metric Colors */
    [data-testid="stWidgetLabel"] p, 
    [data-testid="stMetricLabel"] div, 
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
    .stSlider label, .stToggle label, .stFileUploader label, .stSelectbox label, .stMetric, .stStatusWidget {{
        color: {theme_vars['text_main']} !important;
        font-weight: 600 !important;
    }}

    /* Tab Styling */
    [data-testid="stTab"] p {{
        color: {theme_vars['text_muted']} !important;
        font-weight: 600 !important;
    }}
    [data-testid="stTab"][aria-selected="true"] p {{
        color: {theme_vars['accent']} !important;
    }}
    .stTabs button {{
        border-bottom-color: {theme_vars['border']} !important;
    }}

    /* Metric Specifically */
    [data-testid="stMetricValue"] {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
    }}

    /* Global Typography Scaling */
    h1 {{ font-size: calc(2.2rem * {st.session_state.font_scale}) !important; }}
    h2 {{ font-size: calc(1.8rem * {st.session_state.font_scale}) !important; }}
    h3 {{ font-size: calc(1.4rem * {st.session_state.font_scale}) !important; }}
    .stMarkdown p, .nav-item {{ font-size: calc(0.9rem * {st.session_state.font_scale}) !important; }}

    h1, h2, h3, h4, .stMarkdown p {{
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em !important;
        color: {theme_vars['text_main']} !important;
    }}

    /* Elite Glassmorphism Card */
    .glass-card {{
        background: {theme_vars['bg_card']};
        backdrop-filter: blur(40px) saturate(200%);
        border: 1px solid {theme_vars['border']};
        border-radius: 32px;
        padding: 2.5rem;
        box-shadow: 0 10px 50px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}

    /* Custom File Uploader Style */
    .stFileUploader section {{
        background: transparent !important;
        border: 2px dashed {theme_vars['border']} !important;
        border-radius: 24px !important;
        padding: 3rem !important;
    }}
    .stFileUploader label, .stFileUploader p, .stFileUploader small, .stFileUploader span, .stFileUploader div {{
        color: {theme_vars['text_main']} !important;
    }}
    .stFileUploader button {{
        color: {theme_vars['text_main']} !important;
        background: {theme_vars['bg_card']} !important;
        border: 1px solid {theme_vars['border']} !important;
    }}
    [data-testid="stFileUploadDropzone"] svg {{
        fill: {theme_vars['text_main']} !important;
    }}

    /* Elite Custom Navbar */
    .elite-nav {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background: {theme_vars['glass_header']};
        backdrop-filter: blur(20px);
        border-bottom: 1px solid {theme_vars['border']};
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 4rem;
        z-index: 999999;
    }}
    .nav-brand {{
        display: flex;
        align-items: center;
        gap: 1rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        font-size: 1.2rem;
    }}
    .nav-links {{
        display: flex;
        align-items: center;
        gap: 2.5rem;
    }}
    .nav-item {{
        color: {theme_vars['text_muted']};
        text-decoration: none;
        font-weight: 600;
        transition: color 0.3s;
        background: none;
        border: none;
        cursor: pointer;
        padding: 0;
    }}
    .nav-item:hover, .nav-item.active {{
        color: #10b981 !important;
    }}
    .nav-item i {{ margin-right: 8px; color: white !important; }}

    .theme-btn {{
        background: rgba(255,255,255,0.05);
        border: 1px solid {theme_vars['border']};
        color: {theme_vars['text_main']};
        padding: 0.5rem;
        border-radius: 12px;
        cursor: pointer;
        font-size: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
    }}
    .theme-btn:hover {{ background: rgba(16, 185, 129, 0.1); border-color: #10b981; }}

    /* Narrow Header Style */
    .narrow-header {{
        max-width: 80%;
        margin: 0 auto;
        text-align: center;
    }}
    .narrow-header h1 {{ font-size: 1.8rem !important; margin-bottom: 0 !important; }}
    .narrow-header p {{ font-size: 0.85rem !important; opacity: 0.8; }}

    /* Scanning Radar/Laser Animation */
    .scan-field {{
        position: relative;
        width: 100%;
        height: 400px;
        background: rgba(0,0,0,0.4);
        border: 2px solid rgba(16, 185, 129, 0.2);
        border-radius: 20px;
        overflow: hidden;
        margin-top: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .laser-line {{
        position: absolute;
        width: 100%;
        height: 3px;
        background: #10b981;
        box-shadow: 0 0 15px #10b981, 0 0 30px #10b981;
        top: 0;
        animation: scan-move 4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        z-index: 10;
    }}
    @keyframes scan-move {{
        0% {{ top: 0; }}
        50% {{ top: 100%; }}
        100% {{ top: 0; }}
    }}
    .grid-pattern {{
        position: absolute;
        width: 100%;
        height: 100%;
        background-image: linear-gradient(rgba(16, 185, 129, 0.1) 1px, transparent 1px), 
                          linear-gradient(90deg, rgba(16, 185, 129, 0.1) 1px, transparent 1px);
        background-size: 40px 40px;
        z-index: 1;
    }}
    .scanner-text {{
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        color: #10b981;
        font-family: monospace;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        z-index: 20;
        animation: blink 1.5s infinite;
    }}
    @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}

    /* Layout Spacing */
    header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    #MainMenu, .stDeployButton {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}

    .gradient-text {{
        background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
    }}

    /* Verdict Boxes */
    .verdict-box {{
        padding: 3rem 2rem;
        border-radius: 32px;
        text-align: center;
        margin-bottom: 2rem;
    }}
    .verdict-real {{ background: rgba(16,185,129,0.1); border: 2px solid #10b981; }}
    .verdict-fake {{ background: rgba(239,68,68,0.1); border: 2px solid #ef4444; }}

    /* Scanning Radar/Laser Animation */
    .scan-field {{
        position: relative;
        width: 100%;
        height: 300px;
        background: radial-gradient(circle at center, rgba(16, 185, 129, 0.05) 0%, transparent 70%);
        border: 1px solid rgba(16, 185, 129, 0.1);
        border-radius: 20px;
        overflow: hidden;
        margin-top: 2rem;
    }}
    .laser-line {{
        position: absolute;
        width: 100%;
        height: 4px;
        background: linear-gradient(to right, transparent, #10b981, transparent);
        box-shadow: 0 0 20px #10b981;
        top: 0;
        animation: scan-move 3s ease-in-out infinite;
        z-index: 2;
    }}
    @keyframes scan-move {{
        0%, 100% {{ top: 0%; opacity: 0; }}
        20%, 80% {{ opacity: 1; }}
        50% {{ top: 100%; }}
    }}
    .grid-pattern {{
        position: absolute;
        width: 100%;
        height: 100%;
        background-image: linear-gradient(rgba(16, 185, 129, 0.05) 1px, transparent 1px), 
                          linear-gradient(90deg, rgba(16, 185, 129, 0.05) 1px, transparent 1px);
        background-size: 30px 30px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Navigation Logic ---
def nav_to(page):
    st.session_state.page = page
    st.rerun()

# --- Render Navbar (Global) ---
# This ensures the navbar is consistent across all pages
st.markdown(f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <div class="elite-nav">
        <div class="nav-brand">
            <i class="fas fa-shield-halved" style="color:#10b981; font-size:1.6rem;"></i>
            <span>CURRENCY GUARDIAN</span>
        </div>
        <div class="nav-links">
            <a href="?p=scanner&theme={st.session_state.theme}" target="_self" class="nav-item {"active" if st.session_state.page == 'scanner' else ""}">
                <i class="fas fa-microscope"></i> Scanner
            </a>
            <a href="?p=journal&theme={st.session_state.theme}" target="_self" class="nav-item {"active" if st.session_state.page == 'journal' else ""}">
                <i class="fas fa-book-open"></i> Journal
            </a>
            <a href="?p=manual&theme={st.session_state.theme}" target="_self" class="nav-item {"active" if st.session_state.page == 'manual' else ""}">
                <i class="fas fa-circle-info"></i> Manual
            </a>
            <a href="http://127.0.0.1:5000" target="_blank" class="nav-item">
                <i class="fas fa-external-link-alt"></i> Classic UI
            </a>
            <a href="?p={st.session_state.page}&theme={'dark' if st.session_state.theme == 'light' else 'light'}" target="_self" class="theme-btn" style="text-decoration: none;">
                {"🌙" if st.session_state.theme == "light" else "☀️"}
            </a>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Content Logic ---
if st.session_state.page == 'journal':
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    col_j1, col_j2, col_j3 = st.columns([1, 4, 1])
    with col_j2:
        st.markdown("<h1 style='text-align:center;'>TECHNICAL <span class='gradient-text'>JOURNAL</span></h1>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card' style='padding:0; overflow:hidden; height: 800px;'>", unsafe_allow_html=True)
        try:
            with open("journal/JOURNAL.html", "r") as f: html_content = f.read()
            st.components.v1.html(html_content, height=800, scrolling=True)
        except Exception as e: st.error(f"Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == 'manual':
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    col_m1, col_m2, col_m3 = st.columns([1, 4, 1])
    with col_m2:
        st.markdown("<h1 style='text-align:center;'>USER <span class='gradient-text'>MANUAL</span></h1>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card' style='padding:0; overflow:hidden; height: 800px;'>", unsafe_allow_html=True)
        try:
            with open("journal/USER_GUIDE.html", "r") as f: html_content = f.read()
            st.components.v1.html(html_content, height=800, scrolling=True)
        except Exception as e: st.error(f"Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- Scanner Page ---
    st.markdown("<div style='height: 90px;'></div>", unsafe_allow_html=True)
    
    # Header Section (Narrowed & Moved to Top)
    st.markdown(f"""
        <div class="narrow-header">
            <h1 style='margin-bottom:0;'>AI CURRENCY <span class='gradient-text'>GUARDIAN</span></h1>
            <p>Elite Forensic Counterfeit Intelligence Engine</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    col_arena, col_intel = st.columns([3, 1])
    
    with col_intel:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🧬 Analysis Core")
        watermark_enabled = st.toggle("Watermark (জলছাপ)", value=True)
        thread_enabled = st.toggle("Security Thread (সুতা)", value=True)
        intaglio_enabled = st.toggle("Intaglio (উঁচু ছাপা)", value=True)
        microprint_enabled = st.toggle("Microprint (ক্ষুদ্র লেখা)", value=True)
        ovi_enabled = st.toggle("Color Shift (রঙ পরিবর্তন)", value=True)
        st.divider()
        sensitivity = st.slider("Strictness Mode", 0, 20, 12)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🛠️ System Config")
        st.session_state.font_scale = st.slider("Text Scaling", 0.7, 1.5, st.session_state.font_scale, 0.1)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_arena:
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # --- Forensic Detection Modules ---
            def analyze_watermark(img):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (7, 7), 0)
                _, thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY)
                density = np.sum(thresh == 255) / thresh.size
                return thresh, density > 0.05

            def analyze_security_thread(img):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=100, maxLineGap=20)
                thread_img = img.copy()
                valid = False
                if lines is not None:
                    for line in lines:
                        x1, y1, x2, y2 = line[0]
                        if abs(x1 - x2) < 25: 
                            cv2.line(thread_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                            valid = True
                return thread_img, valid

            def analyze_intaglio(img):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                variance = laplacian.var()
                return cv2.convertScaleAbs(laplacian), variance > 400

            def analyze_microprint(img):
                try:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    text = pytesseract.image_to_string(gray).upper()
                    found = any(word in text for word in ["BANGLADESH", "BANK", "TAKA"])
                    return gray, found, text
                except: return img, False, "OCR FAIL"

            def analyze_ovi(img):
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
                variance = np.var(hist)
                return hsv, variance > 800

            with st.status("⚔️ Deploying Forensic Modules...", expanded=False) as status:
                st.write("Initializing AI Forensic Engine...")
                ai_results, ai_err = analyze_currency_elite(uploaded_file.getvalue(), strictness=sensitivity)
                st.write("Running Structural Analysis...")
                w_img, w_pass = analyze_watermark(image) if watermark_enabled else (None, False)
                t_img, t_pass = analyze_security_thread(image) if thread_enabled else (None, False)
                i_img, i_pass = analyze_intaglio(image) if intaglio_enabled else (None, False)
                m_img, m_pass, m_text = analyze_microprint(image) if microprint_enabled else (None, False, "")
                o_img, o_pass = analyze_ovi(image) if ovi_enabled else (None, False)
                status.update(label="Forensic Analysis Complete", state="complete")

            res_col1, res_col2 = st.columns([1.2, 1])
            with res_col1:
                st.markdown("<div class='glass-card' style='padding:0.5rem; border-radius:32px; overflow:hidden;'>", unsafe_allow_html=True)
                st.image(image_rgb, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with res_col2:
                # Combined logic
                score = ai_results['score']
                is_real = ai_results['is_real']
                st.markdown(f"<div class='verdict-box {'verdict-real' if is_real else 'verdict-fake'}'><h1 style='font-size:3rem; margin:0;'>{'GENUINE' if is_real else 'SUSPICIOUS'}</h1><p>Forensic Score: {score}/20</p></div>", unsafe_allow_html=True)
                
                # New Metrics display
                m_row1 = st.columns(3)
                m_row1[0].metric("AI Confidence", f"{ai_results['ai_confidence']}%")
                m_row1[1].metric("Anomaly Score", f"{ai_results['anomaly_score']}")
                m_row1[2].metric("Thread", "PASS" if t_pass else "FAIL")
                
                m_row2 = st.columns(2)
                m_row2[0].metric("Watermark", "PASS" if w_pass else "FAIL")
                m_row2[1].metric("OVI Color", "PASS" if o_pass else "FAIL")

            st.markdown("### 🎛️ Forensic Streams")
            tabs = st.tabs(["🧠 AI Forensic Core", "💧 Watermark", "🧵 Thread", "📐 Intaglio", "🔍 Microprint", "🌈 OVI"])
            
            with tabs[0]: 
                t_col1, t_col2 = st.columns(2)
                t_col1.image("data:image/jpeg;base64," + ai_results['visuals']['ai_attention'], caption="AI Attention Heatmap (SE-Block Focus)", use_container_width=True)
                t_col2.image("data:image/jpeg;base64," + ai_results['visuals']['reconstruction'], caption="AI Reconstruction (Forensic Decoder)", use_container_width=True)
                st.info("The AI model uses Attention Mechanisms to focus on micro-features and Anomaly Detection to flag deviations from a genuine note's distribution.")

            with tabs[1]: st.image(w_img if w_img is not None else image, caption="Texture Analysis", use_container_width=True)
            with tabs[2]: st.image(t_img if t_img is not None else image, caption="Security Thread Detection", use_container_width=True)
            with tabs[3]: st.image(i_img if i_img is not None else image, caption="Edge Sharpness (Intaglio)", use_container_width=True)
            with tabs[4]: st.code(m_text if m_text else "NO MICROPRINT DATA", language="txt")
            with tabs[5]: st.image(o_img if o_img is not None else image, caption="Color Histogram Map", use_container_width=True)

        else:
            st.markdown(f"""
                <div class='glass-card' style='text-align:center; padding: 2rem;'>
                    <div class='scan-field'>
                        <div class='grid-pattern'></div>
                        <div class='laser-line'></div>
                        <div class='scanner-text'>SYSTEM ACTIVE - READY FOR SCAN</div>
                        <div style='opacity:0.1; transform: scale(1.5);'>
                            <i class='fas fa-shield-halved' style='font-size:10rem; color:#10b981;'></i>
                        </div>
                    </div>
                    <div style='display:flex; justify-content:center; gap: 4rem; margin-top:2.5rem; opacity:0.8; font-weight:600;'>
                        <div style='color:#10b981'><i class='fas fa-broadcast-tower'></i> RADAR ON</div>
                        <div style='color:#3b82f6'><i class='fas fa-user-shield'></i> SECURE</div>
                        <div style='color:#a855f7'><i class='fas fa-microchip'></i> TPU V2</div>
                    </div>
                </div>""", unsafe_allow_html=True)

st.markdown("<br><br><br><p style='text-align:center; opacity:0.5;'>© 2026 AI CURRENCY GUARDIAN | ELITE FORENSIC SUITE</p>", unsafe_allow_html=True)

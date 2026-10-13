import streamlit as st
import os
import io
import base64
import hashlib
import datetime
from PIL import Image
from detector import analyze_image, summarize, model_info

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

# --- Scanner helpers ---
for _k, _v in {"camera_shots": [], "cam_key": 0, "history": []}.items():
    st.session_state.setdefault(_k, _v)


@st.cache_data(max_entries=48, show_spinner=False)
def analyze_cached(image_bytes):
    return analyze_image(image_bytes)


def blend(orig_b64, heat_b64, alpha):
    orig = Image.open(io.BytesIO(base64.b64decode(orig_b64))).convert("RGB")
    heat = Image.open(io.BytesIO(base64.b64decode(heat_b64))).convert("RGB").resize(orig.size)
    return Image.blend(orig, heat, alpha)


def probability_bar(p, thr):
    """Coloured P(real) scale: red below 50%, amber up to the threshold, green above, with a marker."""
    marker = "" if p is None else (
        f"<div style='position:absolute; left:calc({p * 100:.1f}% - 9px); top:-6px; width:18px; height:26px; "
        f"border-radius:6px; background:#fff; border:3px solid #111; box-shadow:0 2px 8px rgba(0,0,0,.4);'></div>")
    return f"""
    <div style='margin:0.8rem 0 1.2rem;'>
      <div style='position:relative; height:14px; border-radius:8px;
           background:linear-gradient(90deg, #ef4444 0%, #ef4444 50%, #f59e0b 50%, #f59e0b {thr * 100:.0f}%,
           #10b981 {thr * 100:.0f}%, #10b981 100%);'>{marker}</div>
      <div style='display:flex; justify-content:space-between; font-size:0.75rem; opacity:0.7; margin-top:6px;'>
        <span>Counterfeit</span><span>50%</span><span>Genuine ≥ {thr * 100:.0f}%</span>
      </div>
    </div>"""


def build_report(r):
    p_real = "-" if r["real_probability"] is None else f"{r['real_probability'] * 100:.1f}%"
    lines = ["AI CURRENCY GUARDIAN - Banknote Authentication Report",
             f"Date: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
             f"Supported notes: {r['supported_notes']}", "",
             f"VERDICT: {r['verdict']}", r["message"],
             f"P(real): {p_real}",
             f"Required confidence for GENUINE: {r['threshold'] * 100:.0f}%",
             f"Photos used: {r['photos_used']}/{r['photos_total']}", "", "Per photo:"]
    for i, p in enumerate(r["per_image"]):
        lines.append(f"  Photo {i + 1}: P(real) {p['real_probability'] * 100:.1f}%"
                     + ("" if p["in_distribution"] else "  (ignored: not a supported note)"))
    lines += ["", "Decision support only. Confirm suspicious notes at a bank."]
    return "\n".join(lines)


def render_history(box):
    with box:
        if not st.session_state.history:
            st.caption("No scans yet in this session.")
        icons = {"GENUINE": "🟢", "COUNTERFEIT": "🔴", "UNCERTAIN": "🟠", "NOT_SUPPORTED": "⚪"}
        for h in st.session_state.history:
            p = "" if h["p"] is None else f" · {h['p'] * 100:.0f}%"
            st.caption(f"{icons[h['verdict']]} **{h['verdict'].replace('_', ' ')}**{p} · {h['n']} photo(s) · {h['time']}")


# --- Content Logic ---
if st.session_state.page == 'journal':
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    col_j1, col_j2, col_j3 = st.columns([1, 4, 1])
    with col_j2:
        st.markdown("<h1 style='text-align:center;'>TECHNICAL <span class='gradient-text'>JOURNAL</span></h1>", unsafe_allow_html=True)
        try:
            with open("journal/JOURNAL.html", "r", encoding="utf-8") as f: html_content = f.read()
            st.components.v1.html(html_content, height=800, scrolling=True)
        except Exception as e: st.error(f"Error: {e}")

elif st.session_state.page == 'manual':
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    col_m1, col_m2, col_m3 = st.columns([1, 4, 1])
    with col_m2:
        st.markdown("<h1 style='text-align:center;'>USER <span class='gradient-text'>MANUAL</span></h1>", unsafe_allow_html=True)
        try:
            with open("journal/USER_GUIDE.html", "r", encoding="utf-8") as f: html_content = f.read()
            st.components.v1.html(html_content, height=800, scrolling=True)
        except Exception as e: st.error(f"Error: {e}")

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
        info = model_info()
        if info["ready"]:
            m = info["metrics"].get("test_per_note_6_views", {})
            st.success("AI model loaded")
            st.caption(f"Supported notes: {info['supported_notes']}")
            if m:
                st.caption(f"Held-out test accuracy: {m['accuracy'] * 100:.1f}% per note "
                           f"(6 photos), counterfeit detection rate {m['fake_detection_rate'] * 100:.1f}%")
        else:
            st.error(info["error"])
        st.divider()
        threshold = st.slider("Required confidence for GENUINE (%)", 50, 95, 70,
                              help="Above this P(real) the note is GENUINE, below 50% COUNTERFEIT, "
                                   "in between UNCERTAIN.") / 100
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📸 Photo Tips")
        st.caption("Upload 1-6 photos of the SAME note: front (portrait side), back, and the note "
                   "held against light (watermark). More photos = more reliable verdict. "
                   "Fill the frame with the note, avoid glare.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🕘 Recent Scans")
        history_box = st.container()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🛠️ System Config")
        st.session_state.font_scale = st.slider("Text Scaling", 0.7, 1.5, st.session_state.font_scale, 0.1)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_arena:
        # ---- input: upload or camera ----
        src_upload, src_camera = st.tabs(["📁 Upload photos", "📷 Camera"])
        with src_upload:
            uploaded_files = st.file_uploader("Upload banknote photo(s)", type=["jpg", "jpeg", "png", "webp"],
                                              accept_multiple_files=True, label_visibility="collapsed")
        with src_camera:
            shot = st.camera_input("Take a close photo of the note", key=f"cam_{st.session_state.cam_key}")
            cam_cols = st.columns([1, 1, 2])
            if cam_cols[0].button("➕ Add photo", disabled=shot is None, width="stretch"):
                if len(st.session_state.camera_shots) < 6:
                    st.session_state.camera_shots.append(shot.getvalue())
                st.session_state.cam_key += 1  # reset the camera widget for the next shot
                st.rerun()
            if cam_cols[1].button("🗑️ Clear", disabled=not st.session_state.camera_shots, width="stretch"):
                st.session_state.camera_shots = []
                st.rerun()
            cam_cols[2].caption(f"{len(st.session_state.camera_shots)}/6 camera photos added. "
                                "Take front, back and against-light shots.")

        images = ([f.getvalue() for f in (uploaded_files or [])] + st.session_state.camera_shots)[:6]
        if images:
            # per-photo AI results are cached, so moving the sliders never re-runs the model
            with st.status("⚔️ Running AI authentication...", expanded=False) as status:
                per_image, err = [], None
                for b in images:
                    r, err = analyze_cached(b)
                    if err:
                        break
                    per_image.append(r)
                status.update(label="Analysis Complete" if not err else "Analysis Failed",
                              state="complete" if not err else "error")

            if err:
                st.error(err)
                st.stop()

            results = summarize(per_image, threshold)
            verdict = results["verdict"]
            style = {"GENUINE": ("verdict-real", "✅ GENUINE"),
                     "COUNTERFEIT": ("verdict-fake", "⚠️ COUNTERFEIT"),
                     "UNCERTAIN": ("verdict-fake", "❔ UNCERTAIN"),
                     "NOT_SUPPORTED": ("verdict-fake", "🚫 NOT SUPPORTED")}[verdict]
            first_idx = next((i for i, p in enumerate(results["per_image"]) if p["in_distribution"]), 0)

            # remember this scan once per distinct set of photos
            scan_id = hashlib.sha1(b"".join(hashlib.sha1(b).digest() for b in images)).hexdigest()[:12]
            if not any(h["id"] == scan_id for h in st.session_state.history):
                st.session_state.history.insert(0, {
                    "id": scan_id, "time": datetime.datetime.now().strftime("%H:%M:%S"),
                    "verdict": verdict, "p": results["real_probability"], "n": len(images)})
                st.session_state.history = st.session_state.history[:8]

            res_col1, res_col2 = st.columns([1.2, 1])
            with res_col1:
                st.image(base64.b64decode(results["per_image"][first_idx]["visuals"]["original"]), width="stretch")
            with res_col2:
                st.markdown(f"<div class='verdict-box {style[0]}'><h1 style='font-size:2.4rem; margin:0;'>{style[1]}</h1>"
                            f"<p>{results['message']}</p></div>", unsafe_allow_html=True)
                st.markdown(probability_bar(results["real_probability"], threshold), unsafe_allow_html=True)
                m_row = st.columns(3)
                m_row[0].metric("Confidence", "-" if results["confidence"] is None else f"{results['confidence']}%")
                m_row[1].metric("P(real)", "-" if results["real_probability"] is None
                                else f"{results['real_probability'] * 100:.1f}%")
                m_row[2].metric("Photos used", f"{results['photos_used']}/{results['photos_total']}")
                st.download_button("📄 Download report", build_report(results),
                                   file_name=f"taka_report_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt",
                                   width="stretch")

            st.markdown("### 🎛️ Per-photo Analysis")
            if len(results["per_image"]) > 1:
                st.bar_chart({"P(real) %": {f"Photo {i + 1}": round(p["real_probability"] * 100, 1)
                                            for i, p in enumerate(results["per_image"])}},
                             height=180, color="#10b981")
            tabs = st.tabs([("⚠️ " if not p["in_distribution"] else "") + f"Photo {i + 1}"
                            for i, p in enumerate(results["per_image"])])
            for i, (tab, p) in enumerate(zip(tabs, results["per_image"])):
                with tab:
                    if not p["in_distribution"]:
                        st.warning("This photo does not look like a Tk 500 / Tk 1000 note and was ignored "
                                   f"(out-of-distribution score {p['ood_ratio']}).")
                    st.caption(f"P(real) = {p['real_probability'] * 100:.1f}%")
                    view = st.radio("View", ["AI focus", "Edges", "Original"], horizontal=True,
                                    key=f"view_{scan_id}_{i}", label_visibility="collapsed")
                    if view == "Edges":
                        st.image(base64.b64decode(p["visuals"]["edges"]), caption="Edge map (print sharpness)",
                                 width="stretch")
                    elif view == "Original":
                        st.image(base64.b64decode(p["visuals"]["original"]), width="stretch")
                    else:
                        alpha = st.slider("Heatmap opacity", 0, 100, 50, key=f"alpha_{scan_id}_{i}") / 100
                        st.image(blend(p["visuals"]["original"], p["visuals"]["heatmap"], alpha),
                                 caption="AI focus (Grad-CAM): red regions drove the decision most", width="stretch")
            st.info("This is decision support, not a legal verdict. Always confirm a suspicious note at a bank.")

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

if st.session_state.page not in ('journal', 'manual'):
    render_history(history_box)

st.markdown("<br><br><br><p style='text-align:center; opacity:0.5;'>© 2026 AI CURRENCY GUARDIAN | ELITE FORENSIC SUITE</p>", unsafe_allow_html=True)

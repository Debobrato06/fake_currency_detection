import base64
import datetime
import hashlib
import io
import json
from string import Template

import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from detector import analyze_image, model_info, summarize

st.set_page_config(
    page_title="Currency Guardian AI · Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

GREEN, RED, AMBER, BLUE, GREY = "#10b981", "#ef4444", "#f59e0b", "#3b82f6", "#94a3b8"
MAX_PHOTOS = 6
VIEW_HINTS = ["Front · portrait", "Front · centre", "Front · right", "Watermark", "Back side", "Against light"]
PRESETS = {"Lenient": 60, "Balanced": 70, "Strict": 85}
VERDICTS = {
    # verdict: (colour, material icon, label, font-awesome icon)
    "GENUINE": (GREEN, "verified", "Genuine", "fa-circle-check"),
    "COUNTERFEIT": (RED, "gpp_bad", "Counterfeit", "fa-triangle-exclamation"),
    "UNCERTAIN": (AMBER, "help", "Uncertain", "fa-circle-question"),
    "NOT_SUPPORTED": (GREY, "block", "Not supported", "fa-ban"),
}
SPLITS = {
    "test_per_note_6_views": "Test · per note",
    "test_per_photo": "Test · per photo",
    "val_per_photo": "Validation",
    "diagnostic_center_hidden": "Stress · centre hidden",
    "diagnostic_border_hidden": "Stress · border hidden",
}

# ---------------------------------------------------------------------
# Light / dark mode. Streamlit sends its theme config to the browser at the
# start of every run, so switching the theme options and re-running
# re-themes all native widgets, not just our own HTML.
# ---------------------------------------------------------------------
THEMES = {
    "dark": dict(base="dark", backgroundColor="#0b0f17", secondaryBackgroundColor="#161d2a",
                 textColor="#e6eaf2", borderColor="#253044"),
    "light": dict(base="light", backgroundColor="#f4f6fa", secondaryBackgroundColor="#eaeef5",
                  textColor="#0f172a", borderColor="#dbe2ec"),
}
PALETTES = {
    "dark": dict(card="#111823", soft="#161e2c", border="#222c3d", border_hi="#334055", muted="#8b97ab",
                 bar="rgba(11,15,23,.82)", grid="rgba(255,255,255,.07)",
                 shadow="0 1px 0 rgba(255,255,255,.03) inset, 0 20px 40px -26px rgba(0,0,0,.9)"),
    "light": dict(card="#ffffff", soft="#f6f8fb", border="#e3e8ef", border_hi="#cbd5e1", muted="#64748b",
                  bar="rgba(244,246,250,.86)", grid="rgba(15,23,42,.07)",
                  shadow="0 1px 2px rgba(15,23,42,.05), 0 20px 40px -28px rgba(15,23,42,.3)"),
}

if "theme" not in st.session_state:
    st.session_state.theme = st.query_params.get("theme") if st.query_params.get("theme") in THEMES else "dark"
MODE = st.session_state.theme
# The new theme reaches the browser on the *next* run, so we re-run once at the
# end of this script (after every widget has rendered, which keeps their state).
THEME_CHANGED = any(st._config.get_option(f"theme.{k}") != v for k, v in THEMES[MODE].items())
for _k, _v in THEMES[MODE].items():
    st._config.set_option(f"theme.{_k}", _v)
st.query_params["theme"] = MODE
PAL = PALETTES[MODE]


def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"


CSS = Template("""
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
header[data-testid="stHeader"] { display: none; }
.block-container { padding-top: 0 !important; padding-bottom: 1.5rem; max-width: 1360px; }
h1, h2, h3, h4, h5 { letter-spacing: -0.02em; }

/* ---------- top bar ---------- */
.st-key-topbar { position: sticky; top: 0; z-index: 990; background: $bar; backdrop-filter: blur(16px) saturate(160%);
  -webkit-backdrop-filter: blur(16px) saturate(160%); border-bottom: 1px solid $border; padding: .6rem 0; margin-bottom: .6rem;
  flex-wrap: wrap; row-gap: .4rem; }
.st-key-topbar [data-testid="stPageLink"] a { padding: .3rem .8rem; border-radius: 10px; transition: background .2s; }
.st-key-topbar [data-testid="stPageLink"] a:hover { background: $soft; }
.cg-brand { display: flex; align-items: center; gap: .65rem; margin-right: 1.2rem; white-space: nowrap; }
.cg-mark { width: 36px; height: 36px; border-radius: 11px; display: grid; place-items: center; color: #fff;
  background: linear-gradient(135deg, #10b981, #3b82f6); box-shadow: 0 8px 20px -8px rgba(16,185,129,.7); }
.cg-brand b { font-family: Outfit, sans-serif; font-size: 1.08rem; font-weight: 600; }
.cg-brand b em { font-style: normal; font-weight: 800; color: #10b981; }
.cg-brand small { font-size: .62rem; font-weight: 700; letter-spacing: .08em; padding: .12rem .45rem; border-radius: 999px;
  color: #10b981; border: 1px solid rgba(16,185,129,.4); background: rgba(16,185,129,.1); }
.cg-status { display: inline-flex; align-items: center; gap: .45rem; font-size: .76rem; font-weight: 600; white-space: nowrap;
  padding: .32rem .75rem; border-radius: 999px; border: 1px solid $border; background: $soft; }
.cg-status i { width: 7px; height: 7px; border-radius: 50%; background: #10b981; animation: cgPing 2s infinite; }
.cg-status.err i { background: #ef4444; animation: none; }

/* ---------- page header ---------- */
.cg-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 1.2rem; flex-wrap: wrap; margin: .6rem 0 1.1rem; }
.cg-eyebrow { font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #10b981; }
.cg-head h1 { font-size: 2rem; margin: .1rem 0 0; padding: 0; line-height: 1.15; }
.cg-head p { margin: .3rem 0 0; color: $muted; font-size: .95rem; }
.cg-grad { background: linear-gradient(135deg, #10b981 10%, #3b82f6); -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; }
.cg-kpis { display: flex; gap: .55rem; flex-wrap: wrap; }
.cg-kpi { padding: .5rem .9rem; border-radius: 12px; border: 1px solid $border; background: $card; min-width: 108px; box-shadow: $shadow; }
.cg-kpi b { display: block; font-family: Outfit, sans-serif; font-size: 1.2rem; line-height: 1.25; }
.cg-kpi span { font-size: .66rem; font-weight: 600; text-transform: uppercase; letter-spacing: .07em; color: $muted; }

/* ---------- cards ---------- */
[class*="st-key-card"] { background: $card; border: 1px solid $border; border-radius: 18px; padding: 1.1rem 1.2rem 1.2rem;
  box-shadow: $shadow; transition: border-color .25s; }
[class*="st-key-card"]:hover { border-color: $border_hi; }
.cg-ch { display: flex; align-items: center; gap: .7rem; }
.cg-ci { width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center; flex: none;
  background: rgba(16,185,129,.12); color: #10b981; font-size: .9rem; }
.cg-ch b { font-family: Outfit, sans-serif; font-size: 1.05rem; font-weight: 700; display: block; line-height: 1.2; }
.cg-ch small { color: $muted; font-size: .78rem; }

/* ---------- photo tray ---------- */
.cg-tray { display: grid; grid-template-columns: repeat(6, 1fr); gap: .55rem; }
.cg-slot { position: relative; aspect-ratio: 1; border-radius: 12px; overflow: hidden; border: 1.5px dashed $border_hi;
  background: $soft; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .25rem;
  color: $muted; font-size: .66rem; text-align: center; padding: .3rem; line-height: 1.2; }
.cg-slot i { font-size: .9rem; opacity: .6; }
.cg-slot.on { border: 1px solid $border; padding: 0; animation: cgPop .35s cubic-bezier(.22,1,.36,1); }
.cg-slot.on img { width: 100%; height: 100%; object-fit: cover; transition: transform .4s; }
.cg-slot.on:hover img { transform: scale(1.07); }
.cg-slot .n { position: absolute; left: 5px; bottom: 5px; font-size: .62rem; font-weight: 700; color: #fff;
  background: rgba(0,0,0,.6); padding: .05rem .4rem; border-radius: 6px; }
.cg-cov { display: flex; align-items: center; gap: .8rem; margin-top: .75rem; font-size: .78rem; color: $muted; }
.cg-cov .bar { flex: 1; height: 5px; border-radius: 5px; background: $soft; overflow: hidden; }
.cg-cov .bar i { display: block; height: 100%; background: linear-gradient(90deg, #f59e0b, #10b981); transition: width .5s; }

/* ---------- verdict ---------- */
.cg-verdict { display: flex; gap: 1rem; align-items: center; border-radius: 16px; padding: 1rem 1.1rem; position: relative; overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--c) 55%, transparent);
  background: linear-gradient(120deg, color-mix(in srgb, var(--c) 18%, transparent), color-mix(in srgb, var(--c) 3%, transparent));
  animation: cgPop .45s cubic-bezier(.22,1,.36,1); }
.cg-vicon { width: 52px; height: 52px; border-radius: 15px; flex: none; display: grid; place-items: center; font-size: 1.4rem;
  color: #fff; background: var(--c); box-shadow: 0 10px 24px -10px var(--c); }
.cg-verdict.fake .cg-vicon i { animation: cgShake .6s .3s; }
.cg-verdict .lbl { font-size: .68rem; text-transform: uppercase; letter-spacing: .12em; color: $muted; font-weight: 700; }
.cg-verdict h2 { margin: 0; padding: 0; font-size: 1.75rem; color: var(--c); line-height: 1.15; }
.cg-verdict p { margin: .2rem 0 0; font-size: .85rem; opacity: .85; }
.cg-await { text-align: center; padding: 1.6rem 1rem; border-radius: 16px; border: 1.5px dashed $border_hi; color: $muted; }
.cg-await i { font-size: 2rem; color: #10b981; opacity: .7; margin-bottom: .5rem; }
.cg-await b { display: block; color: inherit; font-size: 1rem; margin-bottom: .2rem; }
.cg-tiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: .55rem; }
.cg-tile { background: $soft; border: 1px solid $border; border-radius: 12px; padding: .6rem .75rem; }
.cg-tile span { display: block; font-size: .64rem; color: $muted; text-transform: uppercase; letter-spacing: .07em; font-weight: 700; }
.cg-tile b { display: block; font-family: Outfit, sans-serif; font-size: 1.35rem; line-height: 1.3; font-variant-numeric: tabular-nums; }
.cg-tile small { font-size: .7rem; color: $muted; }
.cg-why { list-style: none; margin: 0; padding: 0; display: grid; gap: .45rem; }
.cg-why li { display: flex; gap: .6rem; align-items: flex-start; font-size: .84rem; margin: 0; }
.cg-why li i { margin-top: .2rem; width: 16px; text-align: center; }
.cg-chips { display: flex; gap: .4rem; flex-wrap: wrap; }
.cg-chip { font-size: .74rem; font-weight: 600; padding: .22rem .65rem; border-radius: 999px; border: 1px solid $border; background: $soft; }
.cg-chip b { color: var(--c, inherit); }

/* ---------- idle ---------- */
.cg-field { position: relative; height: 260px; border-radius: 14px; overflow: hidden; display: grid; place-items: center;
  background: radial-gradient(circle at center, rgba(16,185,129,.12), transparent 70%); border: 1px solid rgba(16,185,129,.2); }
.cg-grid { position: absolute; inset: 0; background-size: 28px 28px;
  background-image: linear-gradient(rgba(16,185,129,.09) 1px, transparent 1px), linear-gradient(90deg, rgba(16,185,129,.09) 1px, transparent 1px); }
.cg-laser { position: absolute; left: 0; width: 100%; height: 3px; top: 0;
  background: linear-gradient(90deg, transparent, #10b981, transparent); box-shadow: 0 0 18px #10b981; animation: cgScan 3s ease-in-out infinite; }
.cg-field i.big { font-size: 5.5rem; color: #10b981; opacity: .2; }
.cg-field .txt { position: absolute; bottom: 14px; left: 0; right: 0; text-align: center; font-family: ui-monospace, monospace;
  font-size: .72rem; letter-spacing: .25em; color: #10b981; animation: cgBlink 1.6s infinite; }
.cg-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: .7rem; margin-top: .9rem; }
.cg-step { display: flex; gap: .7rem; align-items: flex-start; padding: .8rem; border-radius: 12px; background: $soft; border: 1px solid $border; }
.cg-step i { width: 32px; height: 32px; flex: none; border-radius: 9px; display: grid; place-items: center; background: rgba(16,185,129,.13); color: #10b981; }
.cg-step b { display: block; font-size: .86rem; }
.cg-step span { font-size: .76rem; color: $muted; }

/* ---------- history ---------- */
.cg-hist { display: flex; align-items: center; gap: .65rem; padding: .45rem; border-radius: 12px; background: $soft;
  border: 1px solid $border; border-left: 3px solid var(--c); margin-bottom: .45rem; }
.cg-hist img { width: 40px; height: 40px; object-fit: cover; border-radius: 8px; flex: none; }
.cg-hist b { font-size: .82rem; display: block; color: var(--c); }
.cg-hist small { font-size: .72rem; color: $muted; }
.cg-empty { font-size: .84rem; color: $muted; padding: .4rem 0; }

.cg-footer { text-align: center; color: $muted; font-size: .78rem; padding-top: 1.2rem; border-top: 1px solid $border; margin-top: 1.6rem; }

@keyframes cgPop { from { opacity: 0; transform: scale(.97); } to { opacity: 1; transform: none; } }
@keyframes cgScan { 0%, 100% { top: 0; opacity: 0; } 15%, 85% { opacity: 1; } 50% { top: calc(100% - 3px); } }
@keyframes cgBlink { 0%, 100% { opacity: 1; } 50% { opacity: .35; } }
@keyframes cgPing { 0% { box-shadow: 0 0 0 0 rgba(16,185,129,.6); } 70%, 100% { box-shadow: 0 0 0 6px transparent; } }
@keyframes cgShake { 0%, 100% { transform: none; } 25%, 75% { transform: rotate(-12deg); } 50% { transform: rotate(12deg); } }
@media (max-width: 760px) {
  .cg-steps { grid-template-columns: 1fr; } .cg-head h1 { font-size: 1.55rem; }
  .cg-tray { grid-template-columns: repeat(3, 1fr); } .cg-brand b, .cg-brand small, .cg-status span { display: none; }
}
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; } }
</style>
""")
st.html(CSS.substitute(PAL))

# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------
for _k, _v in {"camera_shots": [], "cam_key": 0, "up_key": 0, "history": [], "thr": 70,
               "preset": "Balanced", "last_sel": None}.items():
    st.session_state.setdefault(_k, _v)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
@st.cache_data(max_entries=48, show_spinner=False)
def analyze_cached(image_bytes):
    return analyze_image(image_bytes)


@st.cache_data(show_spinner=False)
def get_model_info():
    return model_info()


@st.cache_data(max_entries=64, show_spinner=False)
def thumb_b64(image_bytes, side=240):
    try:
        im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        im.thumbnail((side, side))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=78)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ""


def b64img(b64):
    return base64.b64decode(b64)


def blend(orig_b64, heat_b64, alpha):
    orig = Image.open(io.BytesIO(b64img(orig_b64))).convert("RGB")
    heat = Image.open(io.BytesIO(b64img(heat_b64))).convert("RGB").resize(orig.size)
    return Image.blend(orig, heat, alpha)


def zone_colour(p, thr, in_dist=True):
    if not in_dist:
        return GREY
    return GREEN if p >= thr else (AMBER if p >= 0.5 else RED)


def apply_preset():
    if st.session_state.preset:
        st.session_state.thr = PRESETS[st.session_state.preset]


def sync_preset():
    st.session_state.preset = next((k for k, v in PRESETS.items() if v == st.session_state.thr), None)


def clear_photos():
    st.session_state.camera_shots = []
    st.session_state.up_key += 1  # fresh file_uploader widget


def card_head(icon, title, sub=None):
    st.html(f"<div class='cg-ch'><span class='cg-ci'><i class='fas {icon}'></i></span>"
            f"<div><b>{title}</b>{f'<small>{sub}</small>' if sub else ''}</div></div>")


def style_fig(fig, height):
    fig.update_layout(height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(gridcolor=PAL["grid"], zerolinecolor=PAL["grid"])
    fig.update_yaxes(gridcolor=PAL["grid"], zerolinecolor=PAL["grid"])
    return fig


def gauge_figure(p, thr, colour):
    value = 0 if p is None else p * 100
    fig = go.Figure(go.Indicator(
        mode="gauge+number" if p is not None else "gauge",
        value=value,
        number={"suffix": "%", "valueformat": ".1f", "font": {"size": 40, "color": colour}},
        gauge={
            "shape": "angular",
            "axis": {"range": [0, 100], "ticksuffix": "%", "tickvals": [0, 50, round(thr * 100), 100], "tickwidth": 1},
            "bar": {"color": colour, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50], "color": "rgba(239,68,68,.26)"},
                {"range": [50, thr * 100], "color": "rgba(245,158,11,.28)"},
                {"range": [thr * 100, 100], "color": "rgba(16,185,129,.28)"},
            ],
            "threshold": {"line": {"color": colour, "width": 5}, "thickness": 0.95, "value": value},
        },
    ))
    fig.update_layout(margin=dict(l=35, r=40, t=20, b=0))
    return style_fig(fig, 210)


def photo_chart(per_image, thr, sel):
    xs = [f"Photo {i + 1}" for i in range(len(per_image))]
    ys = [round(p["real_probability"] * 100, 1) for p in per_image]
    status = ["ignored (not a Tk 500/1000 note)" if not p["in_distribution"] else
              ("looks real" if p["real_probability"] >= 0.5 else "looks fake") for p in per_image]
    fig = go.Figure(go.Bar(
        x=xs, y=ys, customdata=status,
        marker_color=[zone_colour(p["real_probability"], thr, p["in_distribution"]) for p in per_image],
        marker_opacity=[1 if i == sel else 0.45 for i in range(len(xs))],
        text=[f"{y:.0f}%" for y in ys], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>P(real) %{y:.1f}%<br>%{customdata}<extra></extra>",
    ))
    fig.add_hline(y=thr * 100, line_dash="dash", line_color=GREEN, line_width=1.5,
                  annotation_text=f"Genuine ≥ {thr * 100:.0f}%", annotation_position="top left",
                  annotation_font_color=GREEN)
    fig.add_hline(y=50, line_dash="dot", line_color=RED, line_width=1.2,
                  annotation_text="50%", annotation_position="bottom left", annotation_font_color=RED)
    fig.update_layout(margin=dict(l=5, r=5, t=15, b=5), showlegend=False, bargap=0.45, dragmode=False,
                      yaxis=dict(range=[0, 114], ticksuffix="%", title=None), xaxis=dict(title=None),
                      clickmode="event+select")
    return style_fig(fig, 220)


def build_report(r):
    p_real = "-" if r["real_probability"] is None else f"{r['real_probability'] * 100:.1f}%"
    lines = ["AI CURRENCY GUARDIAN - Banknote Authentication Report",
             f"Date: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
             f"Supported notes: {r['supported_notes']}", "",
             f"VERDICT: {r['verdict'].replace('_', ' ')}", r["message"],
             f"P(real): {p_real}",
             f"Confidence: {'-' if r['confidence'] is None else str(r['confidence']) + '%'}",
             f"Required confidence for GENUINE: {r['threshold'] * 100:.0f}%",
             f"Photos used: {r['photos_used']}/{r['photos_total']}", "", "Per photo:"]
    for i, p in enumerate(r["per_image"]):
        lines.append(f"  Photo {i + 1}: P(real) {p['real_probability'] * 100:.1f}%"
                     + ("" if p["in_distribution"] else "  (ignored: not a supported note)"))
    lines += ["", "Decision support only. Confirm suspicious notes at a bank."]
    return "\n".join(lines)


def build_json(r):
    slim = {k: v for k, v in r.items() if k != "per_image"}
    slim["generated"] = datetime.datetime.now().isoformat(timespec="seconds")
    slim["per_image"] = [{k: v for k, v in p.items() if k != "visuals"} for p in r["per_image"]]
    return json.dumps(slim, indent=2)


def explain(results, thr):
    """Plain-language reasons behind the verdict."""
    per = results["per_image"]
    used = [p["real_probability"] for p in per if p["in_distribution"]]
    ignored = len(per) - len(used)
    if not used:
        return [("fa-ban", GREY, "None of the photos look like a Tk 500 / Tk 1000 note, so no verdict is given.")]
    p = float(np.mean(used))
    out = [("fa-images", BLUE, f"{len(used)} photo(s) analysed"
            + (f", {ignored} ignored as not a supported note." if ignored else "."))]
    if len(used) > 1:
        sd = float(np.std(used)) * 100
        out.append(("fa-circle-check", GREEN, f"Photos agree closely (spread ±{sd:.0f}%).") if sd < 12 else
                   ("fa-triangle-exclamation", AMBER, f"Photos disagree (spread ±{sd:.0f}%): retake unclear shots."))
    else:
        out.append(("fa-circle-info", AMBER, "Only one photo: add the back and an against-light shot for a firmer verdict."))
    if results["verdict"] == "GENUINE":
        out.append(("fa-arrow-up", GREEN, f"P(real) is {(p - thr) * 100:.1f} pts above the {thr * 100:.0f}% genuine threshold."))
    elif results["verdict"] == "COUNTERFEIT":
        out.append(("fa-arrow-down", RED, f"P(real) is {(0.5 - p) * 100:.1f} pts below 50%."))
    else:
        out.append(("fa-arrows-left-right", AMBER, f"P(real) falls between 50% and the {thr * 100:.0f}% genuine threshold."))
    return out


# ---------------------------------------------------------------------
# Layout chrome
# ---------------------------------------------------------------------
def topbar():
    info = get_model_info()
    with st.container(key="topbar", horizontal=True, vertical_alignment="center", gap="small"):
        st.html("<div class='cg-brand'><span class='cg-mark'><i class='fas fa-shield-halved'></i></span>"
                "<b>Currency<em>Guardian</em></b><small>PRO</small></div>", width="content")
        st.page_link(PAGES["scanner"], label="Scanner", icon=":material/document_scanner:")
        st.page_link(PAGES["model"], label="Model insights", icon=":material/insights:")
        st.page_link(PAGES["journal"], label="Journal", icon=":material/menu_book:")
        st.page_link(PAGES["manual"], label="Manual", icon=":material/help:")
        st.space("stretch")
        st.html("<span class='cg-status'><i></i><span>Model online</span></span>" if info["ready"] else
                "<span class='cg-status err'><i></i><span>Model not ready</span></span>", width="content")
        st.button("", key="theme_btn", on_click=toggle_theme,
                  icon=":material/light_mode:" if MODE == "dark" else ":material/dark_mode:",
                  help="Switch to light mode" if MODE == "dark" else "Switch to dark mode")
        st.link_button("Classic UI", "http://127.0.0.1:5000", icon=":material/open_in_new:")


def page_head(eyebrow, title_html, subtitle, info):
    m = info.get("metrics", {}).get("test_per_note_6_views", {}) if info["ready"] else {}
    kpis = "".join(f"<div class='cg-kpi'><b>{v}</b><span>{k}</span></div>" for k, v in [
        ("Test accuracy", f"{m['accuracy'] * 100:.1f}%" if m else "–"),
        ("Fakes caught", f"{m['fake_detection_rate'] * 100:.1f}%" if m else "–"),
        ("ROC AUC", f"{m['auc']:.3f}" if m else "–"),
    ])
    st.html(f"<div class='cg-head'><div><div class='cg-eyebrow'>{eyebrow}</div><h1>{title_html}</h1>"
            f"<p>{subtitle}</p></div><div class='cg-kpis'>{kpis}</div></div>")


def footer():
    st.html("<div class='cg-footer'>© 2026 AI Currency Guardian · Pro forensic suite · "
            "Decision support only. Confirm suspicious notes at a bank.</div>")


# ---------------------------------------------------------------------
# Scanner page
# ---------------------------------------------------------------------
@st.dialog("Photo inspector", width="large")
def photo_dialog(p, i):
    st.caption(f"Photo {i + 1} · P(real) {p['real_probability'] * 100:.1f}% · OOD score {p['ood_ratio']}")
    t1, t2, t3, t4 = st.tabs(["AI focus", "Grad-CAM overlay", "Edges", "Original"])
    alpha = t1.slider("Heatmap opacity", 0, 100, 50, format="%d%%", key="dlg_alpha") / 100
    t1.image(blend(p["visuals"]["original"], p["visuals"]["heatmap"], alpha), width="stretch")
    t2.image(b64img(p["visuals"]["gradcam"]), width="stretch")
    t3.image(b64img(p["visuals"]["edges"]), width="stretch")
    t4.image(b64img(p["visuals"]["original"]), width="stretch")


def scanner_page():
    topbar()
    info = get_model_info()
    page_head("Forensic workspace", "Banknote <span class='cg-grad'>scanner</span>",
              "Explainable counterfeit detection for Bangladeshi Tk 500 &amp; Tk 1000 notes", info)
    if not info["ready"]:
        st.error(info["error"], icon=":material/error:")

    thr = st.session_state.thr / 100
    left, right = st.columns([1.55, 1], gap="large")

    # ---- input ----
    with left:
        with st.container(key="card_photos"):
            h_l, h_r = st.columns([3, 1.2], vertical_alignment="center")
            with h_l:
                card_head("fa-images", "Photos of one note", "Upload or capture 1–6 views of the SAME note")
            with h_r:
                with st.popover("Photo tips", icon=":material/lightbulb:", width="stretch"):
                    st.markdown("""
- :material/crop_free: **Get close**, the note should fill the frame
- :material/person: **Front**: portrait and security thread
- :material/flip: **Back** side of the note
- :material/light_mode: **Against light** to show the watermark
- :material/block: Avoid glare, blur and scanned images
- :material/account_balance: Confirm suspicious notes at a bank""")
            src_upload, src_camera = st.tabs([":material/upload: Upload", ":material/photo_camera: Camera"])
            with src_upload:
                uploaded_files = st.file_uploader(
                    "Upload banknote photo(s)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True,
                    label_visibility="collapsed", key=f"up_{st.session_state.up_key}")
            with src_camera:
                n_cam = len(st.session_state.camera_shots)
                shot = st.camera_input(f"Shot {n_cam + 1}: {VIEW_HINTS[min(n_cam, 5)]}",
                                       key=f"cam_{st.session_state.cam_key}")
                cam_cols = st.columns([1, 1, 2], vertical_alignment="center")
                if cam_cols[0].button("Add photo", icon=":material/add:", type="primary", width="stretch",
                                      disabled=shot is None or n_cam >= MAX_PHOTOS):
                    st.session_state.camera_shots.append(shot.getvalue())
                    st.session_state.cam_key += 1  # reset the camera widget for the next shot
                    st.rerun()
                if cam_cols[1].button("Clear", icon=":material/delete:", disabled=not n_cam, width="stretch"):
                    st.session_state.camera_shots = []
                    st.rerun()
                cam_cols[2].caption(f"{n_cam}/6 camera photos added.")

            all_images = [f.getvalue() for f in (uploaded_files or [])] + st.session_state.camera_shots
            if len(all_images) > MAX_PHOTOS:
                st.toast("Only 6 photos per note are used; extra photos were skipped.", icon=":material/warning:")
            images = all_images[:MAX_PHOTOS]
            n = len(images)

            slots = []
            for i in range(MAX_PHOTOS):
                if i < n:
                    slots.append(f"<div class='cg-slot on' title='{VIEW_HINTS[i]}'>"
                                 f"<img src='data:image/jpeg;base64,{thumb_b64(images[i])}'><span class='n'>{i + 1}</span></div>")
                else:
                    slots.append(f"<div class='cg-slot'><i class='fas fa-plus'></i>{VIEW_HINTS[i]}</div>")
            cov = ("No photos yet" if n == 0 else "Add more views for a reliable result" if n < 3
                   else "Good coverage" if n < 6 else "Maximum coverage")
            st.html(f"<div class='cg-tray'>{''.join(slots)}</div><div class='cg-cov'><div class='bar'>"
                    f"<i style='width:{n / MAX_PHOTOS * 100:.0f}%'></i></div><span>{n}/6 · {cov}</span></div>")
            if n:
                st.button("Clear all photos", icon=":material/delete_sweep:", on_click=clear_photos, type="tertiary")

        # ---- analysis ----
        results, scan_id = None, None
        if images:
            with st.status("Running AI authentication…", expanded=False) as status:
                per_image, err = [], None
                for i, b in enumerate(images):
                    status.update(label=f"Analyzing photo {i + 1}/{n}…")
                    r, err = analyze_cached(b)
                    if err:
                        break
                    per_image.append(r)
                status.update(label=f"Analysis complete · {n} photo(s)" if not err else "Analysis failed",
                              state="complete" if not err else "error")
            if err:
                st.error(err, icon=":material/error:")
            else:
                results = summarize(per_image, thr)
                scan_id = hashlib.sha1(b"".join(hashlib.sha1(b).digest() for b in images)).hexdigest()[:12]
                remember(results, scan_id, images)

    # ---- right pane: verdict, chart, history ----
    with right:
        verdict_card(results, thr, scan_id)
        if results:
            chart_card(results, thr, scan_id)
        history_card()

    # ---- inspector / idle ----
    with left:
        if results:
            inspector_card(results, thr, scan_id)
        elif not images:
            with st.container(key="card_idle"):
                st.html("""
                <div class='cg-field'><div class='cg-grid'></div><div class='cg-laser'></div>
                  <i class='fas fa-shield-halved big'></i><div class='txt'>SYSTEM READY · AWAITING NOTE</div></div>
                <div class='cg-steps'>
                  <div class='cg-step'><i class='fas fa-images'></i><div><b>1 · Add photos</b><span>Upload or shoot 1–6 views of the same note</span></div></div>
                  <div class='cg-step'><i class='fas fa-microchip'></i><div><b>2 · AI analysis</b><span>EfficientNet checks the print texture of each photo</span></div></div>
                  <div class='cg-step'><i class='fas fa-fire'></i><div><b>3 · Explainable verdict</b><span>Grad-CAM shows what drove the decision</span></div></div>
                </div>""")
    footer()


def remember(results, scan_id, images):
    """Add this scan to the session history once per distinct set of photos."""
    if any(h["id"] == scan_id for h in st.session_state.history):
        return
    verdict = results["verdict"]
    st.session_state.history.insert(0, {
        "id": scan_id, "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "verdict": verdict, "p": results["real_probability"], "n": len(images), "thumb": thumb_b64(images[0], 80)})
    st.session_state.history = st.session_state.history[:10]
    st.toast(f"Verdict: {VERDICTS[verdict][2]}", icon=f":material/{VERDICTS[verdict][1]}:")


def verdict_card(results, thr, scan_id):
    with st.container(key="card_verdict"):
        card_head("fa-gavel", "Verdict", "Updates instantly when you change the strictness")
        if results is None:
            st.html("<div class='cg-await'><i class='fas fa-hourglass-half'></i><b>Awaiting photos</b>"
                    "Add photos of a note to see the verdict here.</div>")
        else:
            colour, _, label, fa = VERDICTS[results["verdict"]]
            cls = "fake" if results["verdict"] == "COUNTERFEIT" else ""
            st.html(f"<div class='cg-verdict {cls}' style='--c:{colour}'><div class='cg-vicon'><i class='fas {fa}'></i></div>"
                    f"<div><div class='lbl'>AI verdict</div><h2>{label.upper()}</h2><p>{results['message']}</p></div></div>")
            st.plotly_chart(gauge_figure(results["real_probability"], thr, colour), width="stretch",
                            config={"displayModeBar": False}, key=f"gauge_{scan_id}")
            p = results["real_probability"]
            conf = results["confidence"]
            delta = "" if p is None else f"{(p - thr) * 100:+.1f} pts vs {thr * 100:.0f}%"
            st.html(f"""<div class='cg-tiles'>
                <div class='cg-tile'><span>Confidence</span><b>{'–' if conf is None else f'{conf}%'}</b><small>in this verdict</small></div>
                <div class='cg-tile'><span>P(real)</span><b style='color:{colour}'>{'–' if p is None else f'{p * 100:.1f}%'}</b><small>{delta}</small></div>
                <div class='cg-tile'><span>Photos used</span><b>{results['photos_used']}/{results['photos_total']}</b><small>supported views</small></div>
            </div>""")
            st.html("<ul class='cg-why'>" + "".join(
                f"<li><i class='fas {ic}' style='color:{c}'></i><span>{txt}</span></li>"
                for ic, c, txt in explain(results, thr)) + "</ul>")

        st.divider()
        st.markdown("**:material/tune: Strictness**")
        st.segmented_control("Preset", list(PRESETS), key="preset", on_change=apply_preset,
                             label_visibility="collapsed", width="stretch")
        st.slider("Required P(real) for GENUINE", 50, 95, key="thr", format="%d%%", on_change=sync_preset,
                  help="Above this P(real) the note is GENUINE, below 50% COUNTERFEIT, in between UNCERTAIN.")
        st.caption(f":red[■] < 50% counterfeit · :orange[■] 50–{thr * 100:.0f}% uncertain · :green[■] ≥ {thr * 100:.0f}% genuine")

        if results is not None:
            ts = f"{datetime.datetime.now():%Y%m%d_%H%M%S}"
            d1, d2 = st.columns(2)
            d1.download_button("Report", build_report(results), file_name=f"taka_report_{ts}.txt",
                               icon=":material/description:", width="stretch", help="Plain-text report (.txt)")
            d2.download_button("Data", build_json(results), file_name=f"taka_report_{ts}.json",
                               mime="application/json", icon=":material/data_object:", width="stretch",
                               help="Machine-readable results (.json)")


def chart_card(results, thr, scan_id):
    per = results["per_image"]
    sel_key = f"photo_{scan_id}"
    st.session_state.setdefault(sel_key, next((i for i, p in enumerate(per) if p["in_distribution"]), 0))
    with st.container(key="card_chart"):
        card_head("fa-chart-column", "Per-photo analysis", "Click a bar to inspect that photo")
        event = st.plotly_chart(photo_chart(per, thr, st.session_state[sel_key] or 0), width="stretch",
                                on_select="rerun", selection_mode="points", key=f"bars_{scan_id}",
                                config={"displayModeBar": False})
        pts = event.selection.points if event and event.selection else []
        if pts:
            idx = pts[0].get("point_index", pts[0].get("point_number"))
            if idx is not None and st.session_state.last_sel != (scan_id, idx):
                st.session_state.last_sel = (scan_id, idx)
                st.session_state[sel_key] = idx
                st.rerun()


def inspector_card(results, thr, scan_id):
    per = results["per_image"]
    first_idx = next((i for i, p in enumerate(per) if p["in_distribution"]), 0)
    sel_key = f"photo_{scan_id}"
    with st.container(key="card_inspector"):
        h_l, h_r = st.columns([3, 1], vertical_alignment="center")
        with h_l:
            card_head("fa-magnifying-glass", "Visual inspector", "See what the AI looked at")
        t_l, t_r = st.columns([1.2, 1], vertical_alignment="bottom")
        with t_l:
            sel = st.segmented_control(
                "Photo", list(range(len(per))), key=sel_key, width="stretch",
                format_func=lambda i: ("⚪" if not per[i]["in_distribution"] else
                                       "🟢" if per[i]["real_probability"] >= thr else
                                       "🟠" if per[i]["real_probability"] >= 0.5 else "🔴") + f" {i + 1}")
        with t_r:
            view = st.segmented_control("View", ["AI focus", "Compare", "Edges", "Original"], default="AI focus",
                                        key=f"view_{scan_id}", width="stretch")
        sel = first_idx if sel is None else sel
        view = view or "AI focus"
        p = per[sel]
        if h_r.button("Enlarge", icon=":material/open_in_full:", width="stretch", key=f"enlarge_{scan_id}"):
            photo_dialog(p, sel)

        colour = zone_colour(p["real_probability"], thr, p["in_distribution"])
        call = ("Ignored" if not p["in_distribution"] else
                "Looks real" if p["real_probability"] >= 0.5 else "Looks fake")
        st.html(f"<div class='cg-chips'><span class='cg-chip' style='--c:{colour}'>P(real) <b>{p['real_probability'] * 100:.1f}%</b></span>"
                f"<span class='cg-chip' style='--c:{colour}'>Call <b>{call}</b></span>"
                f"<span class='cg-chip'>OOD score <b>{p['ood_ratio']}</b></span>"
                f"<span class='cg-chip'>View <b>{VIEW_HINTS[sel]}</b></span></div>")
        if not p["in_distribution"]:
            st.warning("This photo does not look like a Tk 500 / Tk 1000 note and was ignored.", icon=":material/block:")

        if view == "Compare":
            c1, c2 = st.columns(2)
            c1.image(b64img(p["visuals"]["original"]), caption="Original", width="stretch")
            c2.image(b64img(p["visuals"]["gradcam"]), caption="AI focus (Grad-CAM)", width="stretch")
        elif view == "Edges":
            st.image(b64img(p["visuals"]["edges"]), width="stretch",
                     caption="Edge map: sharp, continuous lines suggest genuine intaglio print")
        elif view == "Original":
            st.image(b64img(p["visuals"]["original"]), width="stretch")
        else:
            alpha = st.slider("Heatmap opacity", 0, 100, 50, key=f"alpha_{scan_id}", format="%d%%") / 100
            st.image(blend(p["visuals"]["original"], p["visuals"]["heatmap"], alpha), width="stretch",
                     caption="Red regions drove the decision most")
    st.info("This is decision support, not a legal verdict. Always confirm a suspicious note at a bank.",
            icon=":material/account_balance:")


def history_card():
    hist = st.session_state.history
    with st.container(key="card_history"):
        h_l, h_r = st.columns([4, 1], vertical_alignment="center")
        with h_l:
            card_head("fa-clock-rotate-left", "Recent scans", "This session only")
        if hist and h_r.button("", icon=":material/delete:", help="Clear history", type="tertiary", key="hist_clear"):
            st.session_state.history = []
            st.rerun()
        if not hist:
            st.html("<div class='cg-empty'>No scans yet.</div>")
            return
        tally = {}
        for h in hist:
            tally[h["verdict"]] = tally.get(h["verdict"], 0) + 1
        items = []
        for h in hist:
            colour, _, label, _ = VERDICTS[h["verdict"]]
            p = "" if h["p"] is None else f" · {h['p'] * 100:.0f}%"
            img = f"<img src='data:image/jpeg;base64,{h['thumb']}'>" if h.get("thumb") else ""
            items.append(f"<div class='cg-hist' style='--c:{colour}'>{img}<div><b>{label}{p}</b>"
                         f"<small>{h['time']} · {h['n']} photo(s)</small></div></div>")
        st.html("<div class='cg-chips' style='margin-bottom:.6rem'>" + "".join(
            f"<span class='cg-chip' style='--c:{VERDICTS[v][0]}'><b>{VERDICTS[v][2]}</b> · {k}</span>"
            for v, k in tally.items()) + "</div>" + "".join(items))


# ---------------------------------------------------------------------
# Model insights page
# ---------------------------------------------------------------------
def model_page():
    topbar()
    info = get_model_info()
    page_head("Evaluation", "Model <span class='cg-grad'>insights</span>",
              "How the EfficientNet-B0 authenticator performs on data it never saw during training", info)
    if not info["ready"]:
        st.error(info["error"], icon=":material/error:")
        return
    metrics = info["metrics"]
    splits = [k for k in SPLITS if k in metrics]
    split = st.segmented_control("Evaluation set", splits, format_func=SPLITS.get,
                                 default=splits[0], key="split") or splits[0]
    m = metrics[split]

    tiles = "".join(f"<div class='cg-tile'><span>{name}</span><b>{val}</b><small>{sub}</small></div>" for name, val, sub in [
        ("Accuracy", f"{m['accuracy'] * 100:.1f}%", "all samples"),
        ("Counterfeits detected", f"{m['fake_detection_rate'] * 100:.1f}%", "recall on fakes"),
        ("Genuine accepted", f"{m['real_acceptance_rate'] * 100:.1f}%", "recall on real notes"),
        ("ROC AUC", f"{m['auc']:.3f}", "threshold-independent"),
    ])
    st.html(f"<div class='cg-tiles' style='grid-template-columns:repeat(auto-fit,minmax(180px,1fr));margin:.3rem 0 1rem'>{tiles}</div>")

    c1, c2 = st.columns([1, 1.3], gap="large")
    with c1, st.container(key="card_cm"):
        card_head("fa-table-cells", "Confusion matrix", f"{m['n']} samples · {SPLITS[split]}")
        c = m["confusion"]
        z = [[c["real_as_real"], c["real_as_fake"]], [c["fake_as_real"], c["fake_as_fake"]]]
        rows = [sum(r) or 1 for r in z]
        txt = [[f"<b>{v}</b><br>{v / rows[i] * 100:.1f}%" for v in r] for i, r in enumerate(z)]
        good = [[1, 0], [0, 1]]
        fig = go.Figure(go.Heatmap(
            z=[[(v / rows[i]) * (1 if good[i][j] else -1) for j, v in enumerate(r)] for i, r in enumerate(z)],
            x=["Predicted real", "Predicted fake"], y=["Actual real", "Actual fake"], text=txt,
            texttemplate="%{text}", textfont={"size": 16}, showscale=False, zmin=-1, zmax=1,
            colorscale=[[0, RED], [0.5, PAL["soft"]], [1, GREEN]],
            hovertemplate="%{y} → %{x}<br>%{text}<extra></extra>", xgap=5, ygap=5))
        fig.update_layout(margin=dict(l=5, r=5, t=5, b=5), yaxis=dict(autorange="reversed", showgrid=False),
                          xaxis=dict(showgrid=False))
        st.plotly_chart(style_fig(fig, 320), width="stretch", config={"displayModeBar": False})
    with c2, st.container(key="card_sets"):
        card_head("fa-chart-simple", "All evaluation sets", "Click legend items to toggle a metric")
        fig = go.Figure()
        for name, key, col in [("Accuracy", "accuracy", BLUE), ("Fakes caught", "fake_detection_rate", GREEN),
                               ("Genuine accepted", "real_acceptance_rate", AMBER)]:
            fig.add_bar(name=name, x=[SPLITS[s] for s in splits], y=[metrics[s][key] * 100 for s in splits],
                        marker_color=col, hovertemplate="%{x}<br>" + name + ": %{y:.1f}%<extra></extra>")
        fig.update_layout(barmode="group", margin=dict(l=5, r=5, t=5, b=5),
                          yaxis=dict(range=[0, 105], ticksuffix="%"), legend=dict(orientation="h", y=1.12))
        st.plotly_chart(style_fig(fig, 320), width="stretch", config={"displayModeBar": False})
        st.caption("Stress sets hide part of the note to test robustness.")

    if "split" in metrics:
        st.space("small")
        with st.container(key="card_data"):
            card_head("fa-database", "Dataset & splits", metrics.get("dataset", ""))
            st.dataframe([{"Split": s.title(), "Photos": v["photos"], "Notes": v["notes"]}
                          for s, v in metrics["split"].items()], hide_index=True, width="stretch")
    footer()


def html_page(eyebrow, title_html, path):
    topbar()
    info = get_model_info()
    page_head(eyebrow, title_html, "Reference documentation for the Currency Guardian system", info)
    with st.container(key="card_doc"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                components.html(f.read(), height=900, scrolling=True)
        except OSError as e:
            st.error(f"Could not open {path}: {e}")
    footer()


PAGES = {
    "scanner": st.Page(scanner_page, title="Scanner", icon=":material/document_scanner:", url_path="scanner", default=True),
    "model": st.Page(model_page, title="Model insights", icon=":material/insights:", url_path="model"),
    "journal": st.Page(lambda: html_page("Research", "Technical <span class='cg-grad'>journal</span>", "journal/JOURNAL.html"),
                       title="Journal", icon=":material/menu_book:", url_path="journal"),
    "manual": st.Page(lambda: html_page("Help", "User <span class='cg-grad'>manual</span>", "journal/USER_GUIDE.html"),
                      title="Manual", icon=":material/help:", url_path="manual"),
}
st.navigation(list(PAGES.values()), position="hidden").run()
if THEME_CHANGED:
    st.rerun()

"""
ASR Paper Report — Streamlit App
5 Models × 4 Notations × 4 Clips
"""
import re
import html as html_lib
from pathlib import Path
import pandas as pd
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ASR Transcription Comparison",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ─────────────────────────────────────────────────────────────────
MODELS = ["Gemini", "GeminiFlash", "GPTAudio", "GPTAudioMini", "WhisperX"]
MODEL_LABELS = {
    "Gemini":       "Gemini 2.5 Pro",
    "GeminiFlash":  "Gemini 2.5 Flash",
    "GPTAudio":     "GPT-audio",
    "GPTAudioMini": "GPT-audio Mini",
    "WhisperX":     "WhisperX medium",
}
MODEL_COLORS = {
    "Gemini":       "#4285F4",
    "GeminiFlash":  "#0097A7",
    "GPTAudio":     "#34A853",
    "GPTAudioMini": "#E8A838",
    "WhisperX":     "#F5A623",
}

NOTATIONS = ["Jefferson", "Poland", "BraunClarke", "Muller"]
NOTATION_LABELS = {
    "Jefferson":   "Jefferson (CA)",
    "Poland":      "Poland (2001)",
    "BraunClarke": "Braun & Clarke (2021)",
    "Muller":      "Müller & Guendouzi (2005)",
}
NOTATION_COLORS = {
    "Jefferson":   "#4FC3F7",
    "Poland":      "#81C784",
    "BraunClarke": "#FFB74D",
    "Muller":      "#CE93D8",
}
NOTATION_REF = {
    "Jefferson":   "Jefferson (1984/2004) — Conversation Analysis",
    "Poland":      "Poland (2001) Table 30.4 — Denzin & Lincoln",
    "BraunClarke": "Braun & Clarke (2021) — Thematic Analysis",
    "Muller":      "Guendouzi & Müller (2005) Ch.2 — Orthographic Transcription",
}
NOTATION_KEYS = {
    "Jefferson":   "[ overlap  |  = latching  |  (.) micro-pause  |  (1.2) timed pause  |  ↑↓ pitch  |  :: lengthening  |  .hhh breath  |  _word_ emphasis  |  ¿ weak rising  |  → marked  |  ((…)) paralinguistic",
    "Poland":      ".. short pause  |  ... ~1s pause  |  (overlapping)  |  CAPS emphasis  |  (laughing) non-verbal  |  xxxxx inaudible  |  \"quoted\" reported speech",
    "BraunClarke": "(.) micro  |  (..) short  |  (...) long  |  (( )) paralinguistic  |  [unclear]  |  [overlap]  |  *word* emphasis  |  CAPS stress",
    "Muller":      "¿ rising  |  ↑↓ pitch  |  :: lengthening  |  __word__ emphasis  |  word- cutoff  |  CAPS loud  |  (.) beat pause  |  (2.5) timed  |  = latching  |  [ overlap start  |  * overlap end  |  {B} breathy  |  {W} whisper  |  {piano} quiet  |  {forte} loud  |  (xXx) syllables  |  (( )) non-verbal",
}

CLIPS = ["Apollo13", "PaperChain", "Primer", "TheMeyerowitzStories"]
CLIP_LABELS = {
    "Apollo13":             "Apollo 13 (1995)",
    "PaperChain":           "PaperChain",
    "Primer":               "Primer (2004)",
    "TheMeyerowitzStories": "The Meyerowitz Stories",
}
CLIP_INFO = {
    "Apollo13":             "77 sec · 3–4 speakers · Technical problem-solving, overlapping crosstalk",
    "PaperChain":           "41 sec · 2–3 speakers · Formal discussion, clear turn-taking",
    "Primer":               "90 sec · 4–5 speakers · Fast-paced engineering dialogue, dense overlap",
    "TheMeyerowitzStories": "26 sec · 2 speakers · Casual conversation, low overlap",
}
CLIP_STEMS = {
    "Apollo13":             "Apollo13_1995__trim0000_0117",
    "PaperChain":           "PaperChain_trim0323_0404",
    "Primer":               "Primer_2004__trim0000_0130",
    "TheMeyerowitzStories": "TheMeyerowitzStories_trim0149_0215",
}

DATA_DIR = Path(__file__).parent / "data"
TX_DIR   = DATA_DIR / "transcripts"

# ── Load metrics ──────────────────────────────────────────────────────────────
@st.cache_data
def load_metrics():
    df = pd.read_excel(DATA_DIR / "ASR_Paper_Data.xlsx", sheet_name="AllData")
    return df

@st.cache_data
def load_transcript(clip, model, notation):
    stem = CLIP_STEMS[clip]
    path = TX_DIR / f"{stem}_{model}_{notation}_Indexed.txt"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r'^##.*\n?', '', text, flags=re.MULTILINE).strip()
    return text

# ── Highlighting ──────────────────────────────────────────────────────────────
def highlight(text, notation):
    e = html_lib.escape(text)
    if notation == "Jefferson":
        e = re.sub(r'(Speaker [A-Z]:)', r'<span style="color:#4285F4;font-weight:700">\1</span>', e)
        e = re.sub(r'(\(\d+\.\d+\)|\(\.\))', r'<span style="color:#A5D6A7">\1</span>', e)
        e = re.sub(r'(:{2,}|\.hhh+|[↑↓¿→]|_\w[\w\s]*?_|°[^°]+°|={1,2}|\(\([^)]+\)\))', r'<span style="color:#A5D6A7">\1</span>', e)
        e = re.sub(r'(\[\s)', r'<span style="color:#A5D6A7">[</span> ', e)
    elif notation == "Poland":
        e = re.sub(r'(Speaker [A-Z]:)', r'<span style="color:#4285F4;font-weight:700">\1</span>', e)
        e = re.sub(r'(\.\.\.\.*|\.\.)(?!\.)', r'<span style="color:#A5D6A7">\1</span>', e)
        e = re.sub(r'(\(overlapping\)|\(long pause\)|\(pause\)|\(laugh[^)]*\)|\(cough[^)]*\)|\(sigh[^)]*\))', r'<span style="color:#A5D6A7">\1</span>', e, flags=re.IGNORECASE)
        e = re.sub(r'(\b[A-Z]{2,}\b)', r'<span style="color:#A5D6A7">\1</span>', e)
        e = re.sub(r'(\bx{3,}\b)', r'<span style="color:#A5D6A7">\1</span>', e, flags=re.IGNORECASE)
    elif notation == "BraunClarke":
        e = re.sub(r'(Speaker [A-Z]:)', r'<span style="color:#4285F4;font-weight:700">\1</span>', e)
        e = re.sub(r'(\(\.\.\.\)|\(\.\.\)|\(\.\)|\(\([^)]+\)\)|\*\w[\w\s]*?\*|\[unclear\]|\[overlap\])', r'<span style="color:#A5D6A7">\1</span>', e, flags=re.IGNORECASE)
        e = re.sub(r'(\b[A-Z]{2,}\b)', r'<span style="color:#A5D6A7">\1</span>', e)
    elif notation == "Muller":
        e = re.sub(r'(Speaker [A-Z]:)', r'<span style="color:#4285F4;font-weight:700">\1</span>', e)
        e = re.sub(r'(\(\d+\.?\d*\)|\(\.{1,3}\))', r'<span style="color:#A5D6A7">\1</span>', e)
        e = re.sub(r'(:{2,}|__\S+__|[↑↓¿]|\{[A-Za-z ]+\}|\([xX]+\)|\(\([^)]+\)\)|={1,2})', r'<span style="color:#A5D6A7">\1</span>', e)
        e = re.sub(r'(\b[A-Z]{2,}\b)', r'<span style="color:#A5D6A7">\1</span>', e)
    return e.replace('\n', '<br>')

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0a0a18; }
[data-testid="stSidebar"] * { color: #ccc !important; }
.block-container { padding-top: 1rem; }
.tx-panel {
    background: #131330; border: 1px solid #1e2a4a; border-radius: 8px;
    padding: 10px; font-family: 'Cascadia Code','Fira Code',monospace;
    font-size: 11.5px; line-height: 1.9; color: #ccc;
    height: 500px; overflow-y: auto;
}
.mp-header {
    padding: 8px 10px; margin-bottom: 6px;
    background: #0a0a18; border-radius: 6px;
}
.wx-note {
    background: #2a1a08; border-left: 3px solid #ffb74d;
    padding: 6px 8px; font-size: 11px; color: #cc9922;
    border-radius: 4px; margin-bottom: 6px; line-height: 1.5;
}
.nota-key {
    background: #0a0a18; border-radius: 6px;
    padding: 8px 12px; font-size: 11px; color: #666;
    margin-bottom: 12px; line-height: 1.8;
}
.metric-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.metric-table th { background: #1a1a3a; color: #888; padding: 6px 12px; text-align: left; }
.metric-table td { padding: 6px 12px; border-bottom: 1px solid #1a2236; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎙️ ASR Paper Report")
    st.markdown('<div style="font-size:11px;color:#555">5 Models · 4 Notations · 4 Clips</div>', unsafe_allow_html=True)
    st.divider()

    clip = st.radio(
        "**Clip**",
        CLIPS,
        format_func=lambda c: CLIP_LABELS[c],
    )
    st.divider()

    notation = st.radio(
        "**Notation System**",
        NOTATIONS,
        format_func=lambda n: NOTATION_LABELS[n],
    )
    st.divider()
    st.markdown(f'<div style="font-size:10px;color:#444">Speaker labels ON<br>Timestamps OFF<br>No GPT-4o Diarize</div>', unsafe_allow_html=True)

# ── Main ──────────────────────────────────────────────────────────────────────
nc = NOTATION_COLORS[notation]

# Breadcrumb
st.markdown(
    f"**{CLIP_LABELS[clip]}** &rsaquo; "
    f"<span style='color:{nc};font-weight:700'>{NOTATION_LABELS[notation]}</span>"
    f"<span style='color:#555;font-size:12px;margin-left:12px'>{CLIP_INFO[clip]}</span>",
    unsafe_allow_html=True,
)

# Reference + key
st.markdown(
    f'<div class="nota-key">'
    f'<span style="color:{nc};font-weight:700">{NOTATION_REF[notation]}</span><br>'
    f'{NOTATION_KEYS[notation]}'
    f'</div>',
    unsafe_allow_html=True,
)

# Metrics table
df = load_metrics()
mask = (
    (df["Clip"] == CLIP_LABELS[clip]) &
    (df["Notation"] == NOTATION_LABELS[notation])
)
sub = df[mask][["Model", "Word Count", "Speakers", "Total Markers"]].copy()
sub = sub.set_index("Model")

rows = ""
for model in MODELS:
    lbl = MODEL_LABELS[model]
    mc  = MODEL_COLORS[model]
    wx_tag = ' <span style="font-size:9px;background:#2a1a08;color:#ffb74d;border:1px solid #ffb74d44;padding:1px 5px;border-radius:8px">2-step</span>' if model == "WhisperX" else ""
    if lbl in sub.index:
        wc = sub.loc[lbl, "Word Count"]
        sp = sub.loc[lbl, "Speakers"]
        tm = sub.loc[lbl, "Total Markers"]
    else:
        wc = sp = tm = "–"
    rows += (
        f'<tr><td style="color:{mc};font-weight:700">{lbl}{wx_tag}</td>'
        f'<td style="text-align:center">{wc}</td>'
        f'<td style="text-align:center">{sp}</td>'
        f'<td style="text-align:center;color:{nc};font-weight:700">{tm}</td></tr>'
    )

st.markdown(
    f'<table class="metric-table">'
    f'<thead><tr><th>Model</th><th style="text-align:center">Words</th>'
    f'<th style="text-align:center">Speakers</th>'
    f'<th style="text-align:center;color:{nc}">Markers</th></tr></thead>'
    f'<tbody>{rows}</tbody></table>',
    unsafe_allow_html=True,
)

st.divider()

# Transcript panels — 5 columns
cols = st.columns(5)
for i, (model, col) in enumerate(zip(MODELS, cols)):
    lbl  = MODEL_LABELS[model]
    mc   = MODEL_COLORS[model]
    text = load_transcript(clip, model, notation)

    # Metrics for this model
    if lbl in sub.index:
        wc = sub.loc[lbl, "Word Count"]
        sp = sub.loc[lbl, "Speakers"]
        tm = sub.loc[lbl, "Total Markers"]
    else:
        wc = sp = tm = "–"

    with col:
        st.markdown(
            f'<div class="mp-header" style="border-top:3px solid {mc}">'
            f'<span style="color:{mc};font-weight:700;font-size:12px">{lbl}</span><br>'
            f'<span style="font-size:10px;color:#666">'
            f'Words: <b style="color:#aaa">{wc}</b> &nbsp;'
            f'Spk: <b style="color:#aaa">{sp}</b> &nbsp;'
            f'<span style="color:{nc}">Markers: <b>{tm}</b></span></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if model == "WhisperX":
            st.markdown(
                '<div class="wx-note">⚠ <b>2-step:</b> WhisperX ASR → plain text → '
                'Gemini 2.5 Pro applies notation. Prosodic markers (pitch, breath, '
                'timed pauses) <b>cannot be observed from text alone.</b></div>',
                unsafe_allow_html=True,
            )

        if text:
            body = highlight(text, notation)
        else:
            body = '<span style="color:#444;font-style:italic">— transcript not found —</span>'

        st.markdown(
            f'<div class="tx-panel">{body}</div>',
            unsafe_allow_html=True,
        )

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="ASR Paper Report — Full HTML",
    page_icon="🎙️",
    layout="wide",
)

st.markdown("""
<style>
.block-container { padding: 0 !important; }
header { display: none !important; }
</style>
""", unsafe_allow_html=True)

html_path = Path(__file__).parent.parent / "data" / "ASR_Paper_Report.html"

if html_path.exists():
    html_content = html_path.read_text(encoding="utf-8")
    st.components.v1.html(html_content, height=900, scrolling=False)
else:
    st.error("ASR_Paper_Report.html not found. Run: cp ~/ASR-Benchmarking/ASR_Paper_Report.html streamlit_app/data/")

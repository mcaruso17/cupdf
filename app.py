import streamlit as st
import pandas as pd
import os
import base64
import urllib.request
from datetime import datetime
from urllib.parse import quote
from pathlib import Path

start_time = datetime.now()
start_time_str = start_time.strftime("%d/%m/%Y %H:%M:%S")

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    IMPOSTAZIONI                                     ║
# ╚══════════════════════════════════════════════════════════════════════╝

AT_EXCEL = "data/file pulito per ricerca.xlsx"

RN_CSV_FILES = [
    "data/risultati_puliti_dir.csv",
    "data/risultati_puliti_dirett.csv",
    "data/risultati_puliti_interm.csv",
    "data/risultati_puliti_minist.csv",
]

SHAREPOINT_BASE = "https://mefgovit-my.sharepoint.com/my"

ONEDRIVE_PATH_BASE = (
    "/personal/matteo_caruso_rgs_tesoro_it"
    "/Documents/Documenti/data analysis/at mit"
)

AT_ONEDRIVE_PATH = ONEDRIVE_PATH_BASE + "/allegati at"
RN_ONEDRIVE_PATH = ONEDRIVE_PATH_BASE + "/output_mit_normativa/allegati"

# ── RGS Logo ─────────────────────────────────────────────────────────
# Primary source: raw GitHub URL.
# ⚠️  Replace the value below with the actual raw URL of your file, e.g.:
#   https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/Logo_RGS_orizzontale.png
GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/"
    "Logo_RGS_orizzontale.png"
)

# Local fallback (used if the GitHub fetch fails or during local dev)
_LOGO_LOCAL_CANDIDATES = [
    Path(__file__).parent / "Logo_RGS_orizzontale.png",
    Path("Logo_RGS_orizzontale.png"),
    Path("assets/Logo_RGS_orizzontale.png"),
]

@st.cache_data(show_spinner=False)
def _load_logo_b64() -> str | None:
    # 1. Try GitHub (raw URL, no auth needed for public repos)
    try:
        with urllib.request.urlopen(GITHUB_LOGO_URL, timeout=5) as resp:
            return base64.b64encode(resp.read()).decode()
    except Exception:
        pass
    # 2. Fallback: local file
    for p in _LOGO_LOCAL_CANDIDATES:
        if p.exists():
            return base64.b64encode(p.read_bytes()).decode()
    return None

RGS_LOGO_B64 = _load_logo_b64()

# ╔══════════════════════════════════════════════════════════════════════╗
# ║          FINE IMPOSTAZIONI                                          ║
# ╚══════════════════════════════════════════════════════════════════════╝

st.set_page_config(
    page_title="CUPDF — Ragioneria Generale dello Stato",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════
#  MEF / RGS VISUAL IDENTITY — CSS
#  All custom elements carry explicit hardcoded colors so that
#  Streamlit's dark-mode theme cannot bleed through.
# ═══════════════════════════════════════════════════════════════════════
MEF_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');

/* ── Design tokens ── */
:root {
    --mef-blue:       #1D3D8F;
    --mef-blue-dark:  #132B6B;
    --mef-blue-light: #E8EDF7;
    --mef-gold:       #C49B1D;
    --mef-border:     #CED5E8;
    --font: 'Segoe UI', 'Source Sans 3', sans-serif;
}

/* ══════════════════════════════════════════════════════════
   DARK-MODE NEUTRALISATION
   Re-force all Streamlit dark overrides back to white/light.
   ══════════════════════════════════════════════════════════ */
[data-theme="dark"] .main,
[data-theme="dark"] .block-container,
[data-theme="dark"] section[data-testid="stMain"],
[data-theme="dark"] section[data-testid="stMain"] > div,
[data-theme="dark"] [data-testid="stAppViewContainer"] {
    background-color: #FFFFFF !important;
    color: #17203A !important;
}
[data-theme="dark"] p,
[data-theme="dark"] span:not([class*="mef-"]):not([class*="sb-"]):not([class*="doc-"]):not([class*="tag-"]),
[data-theme="dark"] div:not([class*="mef-"]):not([class*="sb-"]):not([class*="doc-"]):not([class*="card-"]),
[data-theme="dark"] li { color: #17203A !important; }
/* Expanders */
[data-theme="dark"] .streamlit-expanderHeader,
[data-theme="dark"] details summary {
    background-color: #FFFFFF !important;
    color: #17203A !important;
    border-color: #CED5E8 !important;
}
[data-theme="dark"] .streamlit-expanderContent,
[data-theme="dark"] details > div {
    background-color: #FFFFFF !important;
    color: #17203A !important;
    border-color: #CED5E8 !important;
}
/* Inputs */
[data-theme="dark"] input,
[data-theme="dark"] .stTextInput input {
    background-color: #FFFFFF !important;
    color: #17203A !important;
    border-color: #CED5E8 !important;
}
[data-theme="dark"] .stTextInput label,
[data-theme="dark"] .stSelectbox label,
[data-theme="dark"] label { color: #556080 !important; }
/* Tabs */
[data-theme="dark"] [data-baseweb="tab-list"],
[data-theme="dark"] [data-baseweb="tab"],
[data-theme="dark"] [data-baseweb="tab-panel"] {
    background-color: #FFFFFF !important;
    color: #17203A !important;
}
[data-theme="dark"] [aria-selected="true"] {
    color: #1D3D8F !important;
    border-bottom-color: #1D3D8F !important;
}
/* Tables */
[data-theme="dark"] table,
[data-theme="dark"] tbody,
[data-theme="dark"] tr,
[data-theme="dark"] td {
    background-color: #FFFFFF !important;
    color: #17203A !important;
    border-color: #CED5E8 !important;
}
[data-theme="dark"] th {
    background-color: #1D3D8F !important;
    color: #FFFFFF !important;
}
[data-theme="dark"] tr:nth-child(even) td {
    background-color: #F5F6F8 !important;
}
/* Alerts */
[data-theme="dark"] .stAlert,
[data-theme="dark"] .stAlert > div {
    background-color: #E8EDF7 !important;
    color: #17203A !important;
}
/* Selectbox dropdown */
[data-theme="dark"] [data-baseweb="select"] div,
[data-theme="dark"] [data-baseweb="popover"] * {
    background-color: #FFFFFF !important;
    color: #17203A !important;
}
/* Keep sidebar dark */
[data-theme="dark"] [data-testid="stSidebar"],
[data-theme="dark"] [data-testid="stSidebar"] * {
    background-color: #132B6B !important;
    color: rgba(255,255,255,0.82) !important;
}
[data-theme="dark"] [data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

/* ══════════════════════════════════════════════════════════
   BASE
   ══════════════════════════════════════════════════════════ */
html, body, [class*="css"] { font-family: var(--font) !important; }
.main,
section[data-testid="stMain"],
[data-testid="stAppViewContainer"] {
    background-color: #FFFFFF !important;
    color: #17203A !important;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
    background-color: #FFFFFF !important;
}

/* ══════════════════════════════════════════════════════════
   INSTITUTIONAL HEADER
   ══════════════════════════════════════════════════════════ */
.mef-header {
    background: #1D3D8F;
    border-bottom: 4px solid #C49B1D;
    margin: -1rem -1rem 0 -1rem;
}
.mef-header-inner {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 14px 40px;
}
/* The logo PNG has a black background; invert it to white for the blue band */
.mef-logo-img {
    height: 46px;
    width: auto;
    filter: brightness(0) invert(1);
    flex-shrink: 0;
}
.mef-logo-fallback {
    width: 52px; height: 52px;
    border: 2.5px solid #C49B1D; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; font-weight: 700; color: #FFFFFF;
    letter-spacing: -1px; flex-shrink: 0;
}
.mef-header-ministry {
    font-size: 11px; font-weight: 300;
    color: rgba(255,255,255,0.62); letter-spacing: .04em;
}
.mef-header-dept {
    font-size: 16px; font-weight: 700;
    color: #FFFFFF; line-height: 1.2;
}
.mef-header-sub {
    font-size: 10px; font-weight: 300;
    color: rgba(255,255,255,0.48);
    letter-spacing: .07em; text-transform: uppercase; margin-top: 3px;
}
.mef-header-right { margin-left: auto; text-align: right; }
.mef-app-name {
    font-size: 22px; font-weight: 700;
    color: #FFFFFF; letter-spacing: .03em; line-height: 1;
}
.mef-app-tagline {
    font-size: 10px; color: rgba(255,255,255,0.48);
    font-weight: 300; letter-spacing: .08em;
    text-transform: uppercase; margin-top: 3px;
}

/* ══════════════════════════════════════════════════════════
   PAGE TITLE / DIVIDER
   ══════════════════════════════════════════════════════════ */
.mef-rule { border: none; border-top: 1px solid #CED5E8; margin: 1.25rem 0; }
.mef-page-title {
    font-size: 21px; font-weight: 700; color: #1D3D8F;
    margin: 1.5rem 0 .2rem 0; letter-spacing: -.01em;
    font-family: var(--font);
}
.mef-page-subtitle {
    font-size: 13px; color: #556080;
    margin-bottom: 1.25rem; line-height: 1.5;
    font-family: var(--font);
}

/* ══════════════════════════════════════════════════════════
   TAGS
   ══════════════════════════════════════════════════════════ */
.mef-tag {
    display: inline-block; padding: 2px 7px; border-radius: 2px;
    font-size: 10px; font-weight: 700; letter-spacing: .07em;
    text-transform: uppercase; font-family: var(--font); line-height: 1.6;
}
.tag-at { background-color: #1D3D8F; color: #FFFFFF; }
.tag-rn { background-color: #C49B1D; color: #FFFFFF; }

/* ══════════════════════════════════════════════════════════
   STATUS CARDS
   ══════════════════════════════════════════════════════════ */
.mef-status-row { display: flex; gap: 10px; margin-bottom: 1.5rem; flex-wrap: wrap; }
.mef-status-card {
    flex: 1; min-width: 200px; border-radius: 3px;
    padding: 9px 14px; font-size: 13px; font-family: var(--font);
    display: flex; align-items: center; gap: 10px; border: 1px solid;
    background-color: #EDF2FF; border-color: #1D3D8F; color: #132B6B;
}
.mef-status-card.error {
    background-color: #FFF3F3; border-color: #CC2222; color: #8B0000;
}
.mef-status-dot {
    width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
    background: #1D3D8F;
}
.mef-status-card.error .mef-status-dot { background: #CC2222; }
.mef-status-tag {
    font-size: 9px; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; padding: 2px 6px; border-radius: 2px;
    margin-left: auto; flex-shrink: 0;
    background: #1D3D8F; color: #FFFFFF;
}
.mef-status-card.error .mef-status-tag { background: #CC2222; }

/* ══════════════════════════════════════════════════════════
   SEARCH INPUT
   ══════════════════════════════════════════════════════════ */
.stTextInput > div > div > input {
    border: 1.5px solid #CED5E8 !important;
    border-radius: 3px !important; font-size: 14px !important;
    padding: 10px 14px !important; font-family: var(--font) !important;
    background-color: #FFFFFF !important; color: #17203A !important;
    transition: border-color .2s;
}
.stTextInput > div > div > input:focus {
    border-color: #1D3D8F !important;
    box-shadow: 0 0 0 3px rgba(29,61,143,.10) !important;
}
.stTextInput > label {
    font-size: 11px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: .07em !important;
    color: #556080 !important; font-family: var(--font) !important;
}

/* ══════════════════════════════════════════════════════════
   RESULT BANNER
   ══════════════════════════════════════════════════════════ */
.mef-result-banner {
    background-color: #EDF2FF; border-left: 4px solid #1D3D8F;
    border-radius: 0 3px 3px 0; padding: 10px 16px;
    margin-bottom: 1.25rem; font-size: 13.5px; font-family: var(--font);
    color: #132B6B; display: flex; align-items: center;
    gap: 16px; flex-wrap: wrap;
}
.mef-result-banner strong { font-weight: 700; }

/* ══════════════════════════════════════════════════════════
   SELECTBOX
   ══════════════════════════════════════════════════════════ */
.stSelectbox > label {
    font-size: 11px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: .07em !important;
    color: #556080 !important; font-family: var(--font) !important;
}
.stSelectbox [data-baseweb="select"] div {
    background-color: #FFFFFF !important; color: #17203A !important;
}

/* ══════════════════════════════════════════════════════════
   TABS
   ══════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid #CED5E8 !important;
    gap: 0 !important; background-color: #FFFFFF !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font) !important; font-size: 13px !important;
    font-weight: 600 !important; color: #556080 !important;
    padding: 10px 20px !important; border-radius: 0 !important;
    border-bottom: 3px solid transparent !important;
    margin-bottom: -2px !important; background-color: #FFFFFF !important;
}
.stTabs [aria-selected="true"] {
    color: #1D3D8F !important;
    border-bottom-color: #1D3D8F !important;
    background-color: #FFFFFF !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.25rem !important; background-color: #FFFFFF !important;
}

/* ══════════════════════════════════════════════════════════
   EXPANDER / DOCUMENT CARDS
   ══════════════════════════════════════════════════════════ */
.streamlit-expanderHeader, details summary {
    background-color: #FFFFFF !important;
    border: 1px solid #CED5E8 !important; border-radius: 3px !important;
    font-family: var(--font) !important; font-size: 13.5px !important;
    font-weight: 600 !important; color: #132B6B !important;
    padding: 11px 16px !important;
}
.streamlit-expanderHeader:hover, details summary:hover {
    background-color: #E8EDF7 !important;
}
.streamlit-expanderContent, details > div {
    border: 1px solid #CED5E8 !important; border-top: none !important;
    border-radius: 0 0 3px 3px !important; padding: 16px 20px !important;
    background-color: #FFFFFF !important; color: #17203A !important;
}

/* ══════════════════════════════════════════════════════════
   DOCUMENT FIELDS
   ══════════════════════════════════════════════════════════ */
.doc-label {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .07em; color: #556080; margin-bottom: 2px;
    font-family: var(--font);
}
.doc-value {
    font-size: 13.5px; color: #17203A;
    margin-bottom: 12px; font-family: var(--font);
}
.doc-cup {
    font-family: 'Courier New', monospace; font-size: 12.5px;
    background-color: #EDF2FF; color: #132B6B;
    padding: 3px 8px; border-radius: 2px;
    font-weight: 700; letter-spacing: .05em;
}

/* ══════════════════════════════════════════════════════════
   LINK BUTTON
   ══════════════════════════════════════════════════════════ */
.mef-link-btn {
    display: inline-flex; align-items: center; gap: 6px;
    background-color: #1D3D8F; color: #FFFFFF !important;
    font-size: 12px; font-weight: 600; letter-spacing: .04em;
    text-decoration: none !important; padding: 7px 14px;
    border-radius: 3px; margin-top: 8px; font-family: var(--font);
    transition: background .15s;
}
.mef-link-btn:hover {
    background-color: #132B6B !important; color: #FFFFFF !important;
}

/* ══════════════════════════════════════════════════════════
   CARD FOOTER
   ══════════════════════════════════════════════════════════ */
.card-footer {
    font-size: 10.5px; color: #556080;
    margin-top: 10px; padding-top: 8px;
    border-top: 1px solid #CED5E8;
    font-family: var(--font); background-color: #FFFFFF;
}

/* ══════════════════════════════════════════════════════════
   TABLE
   ══════════════════════════════════════════════════════════ */
table {
    font-size: 12.5px !important; border-collapse: collapse !important;
    width: 100% !important; font-family: var(--font) !important;
    background-color: #FFFFFF !important;
}
th {
    background-color: #1D3D8F !important; color: #FFFFFF !important;
    font-size: 10.5px !important; font-weight: 700 !important;
    letter-spacing: .07em !important; text-transform: uppercase !important;
    padding: 8px 12px !important; border: none !important;
}
td {
    padding: 7px 12px !important; border-bottom: 1px solid #CED5E8 !important;
    vertical-align: top !important; color: #17203A !important;
    background-color: #FFFFFF !important;
}
tr:nth-child(even) td { background-color: #F5F6F8 !important; }

/* ══════════════════════════════════════════════════════════
   SIDEBAR  (intentionally dark — institutional blue band)
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background-color: #132B6B !important;
    border-right: 3px solid #C49B1D !important;
}
[data-testid="stSidebar"] * {
    font-family: var(--font) !important;
    color: rgba(255,255,255,.82) !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #FFFFFF !important; font-size: 11px !important;
    font-weight: 700 !important; text-transform: uppercase !important;
    letter-spacing: .08em !important;
    border-bottom: 1px solid rgba(255,255,255,.15) !important;
    padding-bottom: 5px !important; margin-top: 14px !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    font-size: 20px !important; font-weight: 700 !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    font-size: 9.5px !important; text-transform: uppercase !important;
    letter-spacing: .07em !important; color: rgba(255,255,255,.50) !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.12) !important; }
.sb-type-badge {
    display: inline-block; background-color: #C49B1D; color: #FFFFFF;
    font-size: 9px; font-weight: 700; letter-spacing: .07em;
    text-transform: uppercase; padding: 2px 5px; border-radius: 2px; margin-right: 4px;
}

/* ══════════════════════════════════════════════════════════
   FOOTER
   ══════════════════════════════════════════════════════════ */
.mef-footer {
    border-top: 1px solid #CED5E8; margin-top: 3rem; padding-top: 1rem;
    font-size: 11px; color: #556080; font-family: var(--font);
    display: flex; justify-content: space-between;
    flex-wrap: wrap; gap: 4px; background-color: #FFFFFF;
}

/* ── Hide Streamlit chrome (keep sidebar toggle arrows visible) ── */
#MainMenu                              { visibility: hidden; }
footer                                 { visibility: hidden; }
[data-testid="stToolbar"]             { visibility: hidden; }
[data-testid="stDecoration"]          { display: none; }
[data-testid="stStatusWidget"]        { visibility: hidden; }
</style>
"""

st.markdown(MEF_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  FUNZIONI URL ONEDRIVE
# ═══════════════════════════════════════════════════════════════════════

def encode_path(path):
    return quote(path, safe="")

def onedrive_link_at(filename):
    file_path = AT_ONEDRIVE_PATH + "/" + filename
    return (
        f"{SHAREPOINT_BASE}"
        f"?id={encode_path(file_path)}"
        f"&parent={encode_path(AT_ONEDRIVE_PATH)}"
    )

def onedrive_link_rn(cartella, filename):
    if not cartella or not filename:
        return None
    file_path = RN_ONEDRIVE_PATH + "/" + cartella + "/" + filename
    return (
        f"{SHAREPOINT_BASE}"
        f"?id={encode_path(file_path)}"
        f"&parent={encode_path(RN_ONEDRIVE_PATH + '/' + cartella)}"
    )


# ═══════════════════════════════════════════════════════════════════════
#  CARICAMENTO DATI
# ═══════════════════════════════════════════════════════════════════════

@st.cache_data
def load_at_data():
    if not os.path.exists(AT_EXCEL):
        return pd.DataFrame()
    df = pd.read_excel(AT_EXCEL)
    df["cup"] = df["cup"].astype(str).str.strip().str.upper()
    df["_fonte"] = "AT"
    return df

@st.cache_data
def load_rn_data():
    frames = []
    for csv_file in RN_CSV_FILES:
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file, sep=";", encoding="utf-8-sig", dtype=str)
                df = df.fillna("")
                df["_csv_origine"] = os.path.basename(csv_file)
                frames.append(df)
            except Exception as e:
                st.warning(f"Errore nel leggere {csv_file}: {e}")
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df = df[df["CUP"].str.strip() != ""].copy()
    if df.empty:
        return pd.DataFrame()
    df["CUP"] = df["CUP"].str.strip().str.upper()
    df["_fonte"] = "RN"
    return df.reset_index(drop=True)


df_at = load_at_data()
df_rn = load_rn_data()
at_disponibile = not df_at.empty
rn_disponibile = not df_rn.empty


# ═══════════════════════════════════════════════════════════════════════
#  INSTITUTIONAL HEADER
# ═══════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="mef-header">
  <div class="mef-header-inner">
    <div>
      <div class="mef-header-ministry">Ministero dell'Economia e delle Finanze</div>
      <div class="mef-header-dept">Ragioneria Generale dello Stato</div>
      <div class="mef-header-sub">Sistema di ricerca documentale</div>
    </div>
    <div class="mef-header-right">
      <div class="mef-app-name">CUPDF</div>
      <div class="mef-app-tagline">CUP Document Finder</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  PAGE HEADING
# ═══════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="mef-page-title">Ricerca per CUP</div>
<div class="mef-page-subtitle">
  Consultazione integrata di&nbsp;
  <span class="mef-tag tag-at">AT</span>&nbsp;Amministrazione Trasparente
  &nbsp;e&nbsp;
  <span class="mef-tag tag-rn">RN</span>&nbsp;Ricerca Normativa — MIT
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  STATUS INDICATORS
# ═══════════════════════════════════════════════════════════════════════

at_class = "ok" if at_disponibile else "error"
rn_class = "ok" if rn_disponibile else "error"
at_text = (
    f"Amministrazione Trasparente — {len(df_at):,} record"
    if at_disponibile else "Amministrazione Trasparente — dati non trovati"
)
rn_text = (
    f"Ricerca Normativa — {len(df_rn):,} record ({df_rn['_csv_origine'].nunique()} file)"
    if rn_disponibile else "Ricerca Normativa — dati non trovati"
)

st.markdown(f"""
<div class="mef-status-row">
  <div class="mef-status-card {at_class}">
    <div class="mef-status-dot"></div>
    <span>{at_text}</span>
    <span class="mef-status-tag">AT</span>
  </div>
  <div class="mef-status-card {rn_class}">
    <div class="mef-status-dot"></div>
    <span>{rn_text}</span>
    <span class="mef-status-tag">RN</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="mef-rule">', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════

def field(label: str, value: str, mono: bool = False) -> str:
    if not value or str(value).strip() in ("", "nan", "None"):
        return ""
    val_class = "doc-cup" if mono else ""
    return (
        f'<div class="doc-label">{label}</div>'
        f'<div class="doc-value {val_class}">{value}</div>'
    )

def open_link_html(url: str) -> str:
    return (
        f'<a class="mef-link-btn" href="{url}" target="_blank">'
        f'&#8599;&nbsp; Apri documento su OneDrive</a>'
    )

def card_footer(tag: str, tag_class: str, source_name: str, extra: str = "") -> str:
    return (
        f'<div class="card-footer">'
        f'<span class="mef-tag {tag_class}" style="font-size:9px">{tag}</span>'
        f'&nbsp; Fonte: {source_name}'
        + (f' &nbsp;|&nbsp; {extra}' if extra else "")
        + "</div>"
    )


# ═══════════════════════════════════════════════════════════════════════
#  SEARCH INPUT
# ═══════════════════════════════════════════════════════════════════════

query = st.text_input(
    "Codice CUP (o parte di esso)",
    placeholder="es. J31B20000050001",
)


# ═══════════════════════════════════════════════════════════════════════
#  SEARCH & RESULTS
# ═══════════════════════════════════════════════════════════════════════

if query:
    query_clean = query.strip().upper()

    results_at = pd.DataFrame()
    if at_disponibile:
        results_at = df_at[df_at["cup"].str.contains(query_clean, na=False)]

    results_rn = pd.DataFrame()
    if rn_disponibile:
        results_rn = df_rn[df_rn["CUP"].str.contains(query_clean, na=False)]

    tot = len(results_at) + len(results_rn)

    if tot == 0:
        st.warning("Nessun documento trovato. Verificare il CUP o provare una ricerca parziale.")
    else:
        st.markdown(f"""
        <div class="mef-result-banner">
          <span>Risultati per &nbsp;<strong>{query_clean}</strong></span>
          <span><strong>{tot}</strong> documento/i trovato/i</span>
          <span><span class="mef-tag tag-at">AT</span>&nbsp; {len(results_at)} da Amm. Trasparente</span>
          <span><span class="mef-tag tag-rn">RN</span>&nbsp; {len(results_rn)} da Ricerca Normativa</span>
        </div>
        """, unsafe_allow_html=True)

        all_cups = []
        if not results_at.empty:
            all_cups.extend(results_at["cup"].unique().tolist())
        if not results_rn.empty:
            all_cups.extend(results_rn["CUP"].unique().tolist())
        unique_cups = sorted(set(all_cups))

        if len(unique_cups) > 1:
            selected_cup = st.selectbox(
                f"CUP multipli trovati ({len(unique_cups)}) — selezionarne uno:",
                options=unique_cups,
            )
            if not results_at.empty:
                results_at = results_at[results_at["cup"] == selected_cup]
            if not results_rn.empty:
                results_rn = results_rn[results_rn["CUP"] == selected_cup]

        tab_at, tab_rn, tab_all = st.tabs([
            f"Amm. Trasparente  ({len(results_at)})",
            f"Ricerca Normativa  ({len(results_rn)})",
            f"Riepilogo  ({len(results_at) + len(results_rn)})",
        ])

        # ═══ TAB AT ═══════════════════════════════════════════════
        with tab_at:
            if results_at.empty:
                st.info("Nessun risultato da Amministrazione Trasparente.")
            else:
                for _, row in results_at.iterrows():
                    with st.expander(f"[AT]  {row['file']}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(
                                field("CUP", row["cup"], mono=True)
                                + field("Capitolo", str(row.get("cap", "")))
                                + field("Piano Gestionale", str(row.get("pg", "")))
                                + field("Stato — Cap. — Piano", str(row.get("stacappg", ""))),
                                unsafe_allow_html=True,
                            )
                        with col2:
                            st.markdown(
                                field("N. Decreto",   str(row.get("n_decreto",   "")))
                                + field("Data Decreto", str(row.get("data_decreto", "")))
                                + field("Decreto",      str(row.get("decreto",      ""))),
                                unsafe_allow_html=True,
                            )
                        link = onedrive_link_at(row["file"])
                        st.markdown(open_link_html(link), unsafe_allow_html=True)
                        st.markdown(
                            card_footer("AT", "tag-at", "Amministrazione Trasparente"),
                            unsafe_allow_html=True,
                        )

        # ═══ TAB RN ═══════════════════════════════════════════════
        with tab_rn:
            if results_rn.empty:
                st.info("Nessun risultato da Ricerca Normativa.")
            else:
                for _, row in results_rn.iterrows():
                    doc_name  = row.get("Documento",  "Documento sconosciuto")
                    tipologia = row.get("Tipologia",  "")
                    cartella  = row.get("Cartella",   "")
                    with st.expander(f"[RN]  {doc_name}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(
                                field("CUP", row["CUP"], mono=True)
                                + field("Capitolo di Spesa", str(row.get("Capitolo_di_Spesa", "")))
                                + field("Piano Gestionale",  str(row.get("Piano_Gestionale",  "")))
                                + field("Importo (EUR)",     str(row.get("Importo_EUR",        ""))),
                                unsafe_allow_html=True,
                            )
                        with col2:
                            st.markdown(
                                field("N. Decreto",  str(row.get("Numero_Decreto", "")))
                                + field("Data Decreto", str(row.get("Data_Decreto",  "")))
                                + field("Tipologia",    tipologia)
                                + field("Ministero",    str(row.get("Ministero",     ""))),
                                unsafe_allow_html=True,
                            )
                        link = onedrive_link_rn(cartella, doc_name)
                        if link:
                            st.markdown(open_link_html(link), unsafe_allow_html=True)
                        src = row.get("_csv_origine", "")
                        extra = f"Cartella: {cartella}" if cartella else ""
                        st.markdown(
                            card_footer("RN", "tag-rn", f"Ricerca Normativa ({src})", extra),
                            unsafe_allow_html=True,
                        )

        # ═══ TAB RIEPILOGO ════════════════════════════════════════
        with tab_all:
            st.markdown(
                "<p style='font-size:13px;color:#556080;margin-bottom:1rem;"
                "font-family:Segoe UI,sans-serif'>"
                "Riepilogo combinato di tutti i risultati trovati.</p>",
                unsafe_allow_html=True,
            )
            if not results_at.empty:
                st.markdown(
                    "<div style='font-size:11px;font-weight:700;text-transform:uppercase;"
                    "letter-spacing:.07em;color:#1D3D8F;margin-bottom:8px;"
                    "font-family:Segoe UI,sans-serif'>"
                    "<span class='mef-tag tag-at' style='font-size:9px'>AT</span>"
                    "&nbsp; Amministrazione Trasparente</div>",
                    unsafe_allow_html=True,
                )
                display_at = results_at[
                    ["cup", "cap", "pg", "n_decreto", "data_decreto", "file"]
                ].copy()
                display_at.columns = ["CUP", "Capitolo", "Piano Gest.", "N. Decreto", "Data Decreto", "Documento"]
                display_at.insert(0, "Fonte", "AT")
                st.table(display_at.reset_index(drop=True))

            if not results_rn.empty:
                st.markdown(
                    "<div style='font-size:11px;font-weight:700;text-transform:uppercase;"
                    "letter-spacing:.07em;color:#C49B1D;margin-bottom:8px;margin-top:16px;"
                    "font-family:Segoe UI,sans-serif'>"
                    "<span class='mef-tag tag-rn' style='font-size:9px'>RN</span>"
                    "&nbsp; Ricerca Normativa</div>",
                    unsafe_allow_html=True,
                )
                cols_rn = ["CUP", "Tipologia", "Numero_Decreto", "Data_Decreto",
                           "Capitolo_di_Spesa", "Documento"]
                cols_present = [c for c in cols_rn if c in results_rn.columns]
                display_rn = results_rn[cols_present].copy()
                display_rn.insert(0, "Fonte", "RN")
                st.table(display_rn.reset_index(drop=True))


# ═══════════════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════════════

_logo_footer = (
    f'<img src="data:image/png;base64,{RGS_LOGO_B64}" '
    f'alt="MEF — Ragioneria Generale dello Stato" '
    f'style="height:36px;width:auto;margin-top:8px;display:block" />'
    if RGS_LOGO_B64 else ""
)

st.markdown(
    f'<div class="mef-footer">'
    f'  <div>'
    f'    <div>Ministero dell\'Economia e delle Finanze — Ragioneria Generale dello Stato</div>'
    f'    {_logo_footer}'
    f'  </div>'
    f'  <span style="align-self:flex-end">Avviato: {start_time_str} &nbsp;|&nbsp;'
    f'    <span class="mef-tag tag-at" style="font-size:9px">AT</span>'
    f'    &nbsp;Amm. Trasparente&nbsp;&nbsp;'
    f'    <span class="mef-tag tag-rn" style="font-size:9px">RN</span>'
    f'    &nbsp;Ricerca Normativa MIT'
    f'  </span>'
    f'</div>',
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        "<div style='padding:14px 0 8px 0;font-size:14px;font-weight:700;"
        "color:#FFFFFF;font-family:Segoe UI,sans-serif;"
        "border-bottom:1px solid rgba(255,255,255,.15);margin-bottom:4px'>"
        "MEF &nbsp;<span style='color:#C49B1D'>·</span>&nbsp; RGS"
        "<br><span style='font-size:9.5px;font-weight:300;opacity:.55;"
        "letter-spacing:.07em;text-transform:uppercase'>"
        "Statistiche Database</span></div>",
        unsafe_allow_html=True,
    )

    st.subheader("Amm. Trasparente")
    if at_disponibile:
        st.metric("Record totali", f"{len(df_at):,}")
        st.metric("CUP unici",     f"{df_at['cup'].nunique():,}")
        st.metric("Documenti",     f"{df_at['file'].nunique():,}")
    else:
        st.caption("Non disponibile")

    st.markdown("---")
    st.subheader("Ricerca Normativa")
    if rn_disponibile:
        st.metric("Record con CUP", f"{len(df_rn):,}")
        st.metric("CUP unici",      f"{df_rn['CUP'].nunique():,}")
        for csv_name in df_rn["_csv_origine"].unique():
            subset = df_rn[df_rn["_csv_origine"] == csv_name]
            tipo = csv_name.replace("risultati_puliti_", "").replace(".csv", "")
            st.markdown(
                f"<div style='font-size:11px;opacity:.72;padding:2px 0;"
                f"font-family:Segoe UI,sans-serif'>"
                f"<span class='sb-type-badge'>{tipo}</span>"
                f"{len(subset):,} rec &nbsp;·&nbsp; {subset['CUP'].nunique():,} CUP"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.caption("Non disponibile")

    if at_disponibile and rn_disponibile:
        st.markdown("---")
        st.subheader("Riepilogo combinato")
        cup_at     = set(df_at["cup"].unique())
        cup_rn     = set(df_rn["CUP"].unique())
        cup_comuni = cup_at & cup_rn
        cup_totali = cup_at | cup_rn
        st.metric("CUP totali (unici)",   f"{len(cup_totali):,}")
        st.metric("In entrambe le fonti", f"{len(cup_comuni):,}")
        st.metric("Solo AT",              f"{len(cup_at - cup_rn):,}")
        st.metric("Solo RN",              f"{len(cup_rn - cup_at):,}")

    st.markdown("---")
    st.markdown(
        f"<div style='font-size:10px;opacity:.40;padding-bottom:8px;"
        f"font-family:Segoe UI,sans-serif'>"
        f"Avviato: {start_time_str}<br>"
        f"&#9888; Accesso PDF richiede OneDrive condiviso."
        f"</div>",
        unsafe_allow_html=True,
    )

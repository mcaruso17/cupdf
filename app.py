import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from urllib.parse import quote

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


# ╔══════════════════════════════════════════════════════════════════════╗
# ║          FINE IMPOSTAZIONI                                          ║
# ╚══════════════════════════════════════════════════════════════════════╝

st.set_page_config(
    page_title="CUPDF — Ragioneria Generale dello Stato",
    layout="wide",
    initial_sidebar_state="expanded",
)

MEF_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');

/* -- Design tokens -- */
:root {
    --mef-blue:       #1D3D8F;
    --mef-blue-dark:  #132B6B;
    --mef-blue-light: #E8EDF7;
    --mef-gold:       #C49B1D;
    --mef-border:     #CED5E8;
    --font: 'Segoe UI', 'Source Sans 3', sans-serif;
}

/* ---- DARK-MODE NEUTRALISATION ---- */
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
[data-theme="dark"] div:not([class*="mef-"]):not([class*="sb-"]):not([class*="card-"]),
[data-theme="dark"] li { color: #17203A !important; }
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
[data-theme="dark"] input,
[data-theme="dark"] .stTextInput input {
    background-color: #FFFFFF !important;
    color: #17203A !important;
    border-color: #CED5E8 !important;
}
[data-theme="dark"] .stTextInput label,
[data-theme="dark"] .stSelectbox label,
[data-theme="dark"] label { color: #556080 !important; }
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
[data-theme="dark"] .stAlert,
[data-theme="dark"] .stAlert > div {
    background-color: #E8EDF7 !important;
    color: #17203A !important;
}
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

/* ---- BASE ---- */
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

/* ---- INSTITUTIONAL HEADER ---- */
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

/* ---- PAGE TITLE / DIVIDER ---- */
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

/* ---- TAGS ---- */
.mef-tag {
    display: inline-block; padding: 2px 7px; border-radius: 2px;
    font-size: 10px; font-weight: 700; letter-spacing: .07em;
    text-transform: uppercase; font-family: var(--font); line-height: 1.6;
}
.tag-at { background-color: #1D3D8F; color: #FFFFFF; }
.tag-rn { background-color: #C49B1D; color: #FFFFFF; }

/* ---- STATUS CARDS ---- */
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

/* ---- SEARCH INPUT ---- */
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

/* ---- RESULT BANNER ---- */
.mef-result-banner {
    background-color: #EDF2FF; border-left: 4px solid #1D3D8F;
    border-radius: 0 3px 3px 0; padding: 10px 16px;
    margin-bottom: 1.25rem; font-size: 13.5px; font-family: var(--font);
    color: #132B6B; display: flex; align-items: center;
    gap: 16px; flex-wrap: wrap;
}
.mef-result-banner strong { font-weight: 700; }

/* ---- SELECTBOX ---- */
.stSelectbox > label {
    font-size: 11px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: .07em !important;
    color: #556080 !important; font-family: var(--font) !important;
}
.stSelectbox [data-baseweb="select"] div {
    background-color: #FFFFFF !important; color: #17203A !important;
}

/* ---- TABS ---- */
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

/* ---- EXPANDER / DOCUMENT CARDS ---- */
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

/* ---- DOCUMENT FIELDS ---- */
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

/* ---- MULTI-CUP LIST ---- */
.cup-list { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px; }
.cup-list .doc-cup { display: inline-block; }

/* ---- LINK BUTTON ---- */
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

/* ---- CARD FOOTER ---- */
.card-footer {
    font-size: 10.5px; color: #556080;
    margin-top: 10px; padding-top: 8px;
    border-top: 1px solid #CED5E8;
    font-family: var(--font); background-color: #FFFFFF;
}

/* ---- TABLE ---- */
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

/* ---- SIDEBAR ---- */
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

/* ---- SIDEBAR ALWAYS VISIBLE ---- */
[data-testid="stSidebar"] {
    margin-left: 0 !important;
    transform: none !important;
    width: 300px !important;
    min-width: 300px !important;
}
[data-testid="stSidebar"][aria-expanded="false"] {
    margin-left: 0 !important;
    transform: none !important;
    width: 300px !important;
    min-width: 300px !important;
}
/* Hide collapse/expand buttons */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* ---- FIX: STREAMLIT NATIVE HEADER BAR (white stripe) ---- */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    pointer-events: none !important;
}
header[data-testid="stHeader"] * {
    pointer-events: auto !important;
}
header[data-testid="stHeader"] [data-testid="stToolbar"] {
    display: none !important;
}

/* ---- HIDE STREAMLIT CHROME ---- */
#MainMenu                              { display: none !important; }
footer                                 { display: none !important; }
[data-testid="stToolbar"]             { display: none !important; }
[data-testid="stDecoration"]          { display: none !important; }
[data-testid="stStatusWidget"]        { display: none !important; }

/* ---- FOOTER ---- */
.mef-footer {
    border-top: 1px solid #CED5E8; margin-top: 3rem; padding-top: 1rem;
    font-size: 11px; color: #556080; font-family: var(--font);
    display: flex; justify-content: space-between;
    flex-wrap: wrap; gap: 4px; background-color: #FFFFFF;
}
</style>
"""

st.markdown(MEF_CSS, unsafe_allow_html=True)


# ===================================================================
#  FUNZIONI URL ONEDRIVE
# ===================================================================

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


# ===================================================================
#  UTILITÀ — pulizia valori numerici interi (7000.0 → 7000)
# ===================================================================

def clean_int(val):
    """Converte stringhe tipo '7000.0' o float in '7000'.
    Restituisce stringa vuota se il valore è nullo/invalido."""
    if val is None:
        return ""
    s = str(val).strip()
    if s in ("", "nan", "None", "NaT"):
        return ""
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
        return s
    except (ValueError, OverflowError):
        return s


# ===================================================================
#  CARICAMENTO DATI
# ===================================================================

@st.cache_data
def load_at_data():
    if not os.path.exists(AT_EXCEL):
        return pd.DataFrame()
    df = pd.read_excel(AT_EXCEL)
    df["cup"] = df["cup"].astype(str).str.strip().str.upper()
    # Pulizia colonne numeriche intere
    for col in ("cap", "pg"):
        if col in df.columns:
            df[col] = df[col].apply(clean_int)
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
    # Pulizia colonne numeriche intere
    for col in ("Capitolo_di_Spesa", "Piano_Gestionale"):
        if col in df.columns:
            df[col] = df[col].apply(clean_int)
    df["_fonte"] = "RN"
    return df.reset_index(drop=True)


df_at = load_at_data()
df_rn = load_rn_data()
at_disponibile = not df_at.empty
rn_disponibile = not df_rn.empty


# ===================================================================
#  INSTITUTIONAL HEADER
# ===================================================================

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


# ===================================================================
#  PAGE HEADING
# ===================================================================

st.markdown("""
<div class="mef-page-title">Ricerca Documentale</div>
<div class="mef-page-subtitle">
  Consultazione integrata di&nbsp;
  <span class="mef-tag tag-at">AT</span>&nbsp;Amministrazione Trasparente
  &nbsp;e&nbsp;
  <span class="mef-tag tag-rn">RN</span>&nbsp;Ricerca Normativa — MIT
  &nbsp;&#8212;&nbsp; Ricerca per CUP o Capitolo di Spesa (con filtro opzionale per Piano di Gestione)
</div>
""", unsafe_allow_html=True)


# ===================================================================
#  STATUS INDICATORS
# ===================================================================

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


# ===================================================================
#  HELPERS
# ===================================================================

def field(label, value, mono=False):
    if not value or str(value).strip() in ("", "nan", "None"):
        return ""
    val_class = "doc-cup" if mono else ""
    return (
        f'<div class="doc-label">{label}</div>'
        f'<div class="doc-value {val_class}">{value}</div>'
    )

def open_link_html(url):
    return (
        f'<a class="mef-link-btn" href="{url}" target="_blank">'
        f'&#8599;&nbsp; Apri documento su OneDrive</a>'
    )

def card_footer(tag, tag_class, source_name, extra=""):
    return (
        f'<div class="card-footer">'
        f'<span class="mef-tag {tag_class}" style="font-size:9px">{tag}</span>'
        f'&nbsp; Fonte: {source_name}'
        + (f' &nbsp;|&nbsp; {extra}' if extra else "")
        + "</div>"
    )


def field_cups(cups):
    """Rende una lista di CUP come badge monospace."""
    if not cups:
        return ""
    badges = " ".join(f'<span class="doc-cup">{c}</span>' for c in cups)
    label = "CUP" if len(cups) == 1 else f"CUP ({len(cups)})"
    return (
        f'<div class="doc-label">{label}</div>'
        f'<div class="cup-list">{badges}</div>'
    )


def group_at(df):
    """Raggruppa righe AT per documento (file), aggregando i CUP."""
    if df.empty:
        return []
    groups = []
    for doc_name, grp in df.groupby("file", sort=False):
        cups = sorted(grp["cup"].unique())
        first = grp.iloc[0]
        groups.append({
            "file": doc_name,
            "cups": cups,
            "cap": clean_int(first.get("cap", "")),
            "pg": clean_int(first.get("pg", "")),
            "stacappg": str(first.get("stacappg", "")),
            "n_decreto": str(first.get("n_decreto", "")),
            "data_decreto": str(first.get("data_decreto", "")),
            "decreto": str(first.get("decreto", "")),
        })
    return groups


def group_rn(df):
    """Raggruppa righe RN per documento (Documento), aggregando i CUP."""
    if df.empty:
        return []
    groups = []
    for doc_name, grp in df.groupby("Documento", sort=False):
        cups = sorted(grp["CUP"].unique())
        first = grp.iloc[0]
        groups.append({
            "Documento": doc_name,
            "cups": cups,
            "Capitolo_di_Spesa": clean_int(first.get("Capitolo_di_Spesa", "")),
            "Piano_Gestionale": clean_int(first.get("Piano_Gestionale", "")),
            "Importo_EUR": str(first.get("Importo_EUR", "")),
            "Numero_Decreto": str(first.get("Numero_Decreto", "")),
            "Data_Decreto": str(first.get("Data_Decreto", "")),
            "Tipologia": str(first.get("Tipologia", "")),
            "Ministero": str(first.get("Ministero", "")),
            "Cartella": str(first.get("Cartella", "")),
            "_csv_origine": str(first.get("_csv_origine", "")),
        })
    return groups


# ===================================================================
#  SEARCH INPUT — criterio di ricerca selezionabile
# ===================================================================

SEARCH_MODES = {
    "CUP":               "Codice CUP (o parte di esso)",
    "Capitolo di Spesa": "Capitolo di Spesa (es. 7000)",
}

col_mode, col_query = st.columns([1, 3])
with col_mode:
    search_mode = st.selectbox(
        "Criterio di ricerca",
        options=list(SEARCH_MODES.keys()),
    )
with col_query:
    if search_mode == "CUP":
        query = st.text_input(
            "Codice CUP (o parte di esso)",
            placeholder="es. J31B20000050001",
        )
    else:
        query = st.text_input(
            "Capitolo di Spesa",
            placeholder="es. 7000",
        )

# Campo opzionale PG — visibile solo quando si cerca per Capitolo
query_pg = ""
if search_mode == "Capitolo di Spesa":
    query_pg = st.text_input(
        "Piano di Gestione (facoltativo — filtra ulteriormente per PG)",
        placeholder="es. 1  (lasciare vuoto per vedere tutti i PG del capitolo)",
    )


# ===================================================================
#  FUNZIONI DI RICERCA PER CRITERIO
# ===================================================================

def search_at(df, mode, q, pg=None):
    """Filtra il DataFrame AT in base al criterio selezionato."""
    if df.empty:
        return pd.DataFrame()
    if mode == "CUP":
        return df[df["cup"].str.contains(q, na=False)]
    elif mode == "Capitolo di Spesa":
        if "cap" not in df.columns:
            return pd.DataFrame()
        mask = df["cap"].astype(str).str.strip().str.upper() == q
        if pg and "pg" in df.columns:
            mask = mask & (df["pg"].astype(str).str.strip().str.upper() == pg)
        return df[mask]
    return pd.DataFrame()

def search_rn(df, mode, q, pg=None):
    """Filtra il DataFrame RN in base al criterio selezionato."""
    if df.empty:
        return pd.DataFrame()
    if mode == "CUP":
        return df[df["CUP"].str.contains(q, na=False)]
    elif mode == "Capitolo di Spesa":
        if "Capitolo_di_Spesa" not in df.columns:
            return pd.DataFrame()
        mask = df["Capitolo_di_Spesa"].astype(str).str.strip().str.upper() == q
        if pg and "Piano_Gestionale" in df.columns:
            mask = mask & (df["Piano_Gestionale"].astype(str).str.strip().str.upper() == pg)
        return df[mask]
    return pd.DataFrame()


# ===================================================================
#  SEARCH & RESULTS
# ===================================================================

if query:
    query_clean = query.strip().upper()
    pg_clean = query_pg.strip().upper() if query_pg else None

    results_at = search_at(df_at, search_mode, query_clean, pg_clean) if at_disponibile else pd.DataFrame()
    results_rn = search_rn(df_rn, search_mode, query_clean, pg_clean) if rn_disponibile else pd.DataFrame()

    # Raggruppa per documento unico
    docs_at = group_at(results_at)
    docs_rn = group_rn(results_rn)
    n_docs_at = len(docs_at)
    n_docs_rn = len(docs_rn)
    tot_docs = n_docs_at + n_docs_rn

    # Etichetta ricerca per il banner
    search_label = f"{search_mode}: {query_clean}"
    if search_mode == "Capitolo di Spesa" and pg_clean:
        search_label += f" / PG: {pg_clean}"

    if tot_docs == 0:
        st.warning(
            f"Nessun documento trovato per {search_label}. "
            "Verificare il valore o provare una ricerca diversa."
        )
    else:
        tot_rows = len(results_at) + len(results_rn)
        extra_note = ""
        if tot_rows != tot_docs:
            extra_note = (
                f"<span style='font-size:12px;color:#556080'>"
                f"({tot_rows} righe totali, deduplicate per documento)</span>"
            )
        st.markdown(f"""
        <div class="mef-result-banner">
          <span>Risultati per &nbsp;<strong>{search_label}</strong></span>
          <span><strong>{tot_docs}</strong> documento/i unico/i {extra_note}</span>
          <span><span class="mef-tag tag-at">AT</span>&nbsp; {n_docs_at} da Amm. Trasparente</span>
          <span><span class="mef-tag tag-rn">RN</span>&nbsp; {n_docs_rn} da Ricerca Normativa</span>
        </div>
        """, unsafe_allow_html=True)

        tab_at, tab_rn, tab_all = st.tabs([
            f"Amm. Trasparente  ({n_docs_at})",
            f"Ricerca Normativa  ({n_docs_rn})",
            f"Riepilogo  ({tot_docs})",
        ])

        # === TAB AT ===
        with tab_at:
            if not docs_at:
                st.info("Nessun risultato da Amministrazione Trasparente.")
            else:
                for doc in docs_at:
                    with st.expander(f"[AT]  {doc['file']}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(
                                field_cups(doc["cups"])
                                + field("Capitolo", doc["cap"])
                                + field("Piano Gestionale", doc["pg"])
                                + field("Stato - Cap. - Piano", doc["stacappg"]),
                                unsafe_allow_html=True,
                            )
                        with col2:
                            st.markdown(
                                field("N. Decreto",   doc["n_decreto"])
                                + field("Data Decreto", doc["data_decreto"])
                                + field("Decreto",      doc["decreto"]),
                                unsafe_allow_html=True,
                            )
                        link = onedrive_link_at(doc["file"])
                        st.markdown(open_link_html(link), unsafe_allow_html=True)
                        st.markdown(
                            card_footer("AT", "tag-at", "Amministrazione Trasparente"),
                            unsafe_allow_html=True,
                        )

        # === TAB RN ===
        with tab_rn:
            if not docs_rn:
                st.info("Nessun risultato da Ricerca Normativa.")
            else:
                for doc in docs_rn:
                    doc_name  = doc["Documento"]
                    cartella  = doc["Cartella"]
                    with st.expander(f"[RN]  {doc_name}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(
                                field_cups(doc["cups"])
                                + field("Capitolo di Spesa", doc["Capitolo_di_Spesa"])
                                + field("Piano Gestionale",  doc["Piano_Gestionale"])
                                + field("Importo (EUR)",     doc["Importo_EUR"]),
                                unsafe_allow_html=True,
                            )
                        with col2:
                            st.markdown(
                                field("N. Decreto",   doc["Numero_Decreto"])
                                + field("Data Decreto", doc["Data_Decreto"])
                                + field("Tipologia",    doc["Tipologia"])
                                + field("Ministero",    doc["Ministero"]),
                                unsafe_allow_html=True,
                            )
                        link = onedrive_link_rn(cartella, doc_name)
                        if link:
                            st.markdown(open_link_html(link), unsafe_allow_html=True)
                        src = doc["_csv_origine"]
                        extra = f"Cartella: {cartella}" if cartella else ""
                        st.markdown(
                            card_footer("RN", "tag-rn", f"Ricerca Normativa ({src})", extra),
                            unsafe_allow_html=True,
                        )

        # === TAB RIEPILOGO ===
        with tab_all:
            st.markdown(
                "<p style='font-size:13px;color:#556080;margin-bottom:1rem;"
                "font-family:Segoe UI,sans-serif'>"
                "Riepilogo combinato — ogni documento appare una sola volta.</p>",
                unsafe_allow_html=True,
            )
            if docs_at:
                st.markdown(
                    "<div style='font-size:11px;font-weight:700;text-transform:uppercase;"
                    "letter-spacing:.07em;color:#1D3D8F;margin-bottom:8px;"
                    "font-family:Segoe UI,sans-serif'>"
                    "<span class='mef-tag tag-at' style='font-size:9px'>AT</span>"
                    "&nbsp; Amministrazione Trasparente</div>",
                    unsafe_allow_html=True,
                )
                rows_at = []
                for doc in docs_at:
                    rows_at.append({
                        "Fonte": "AT",
                        "Documento": doc["file"],
                        "CUP": ", ".join(doc["cups"]),
                        "Capitolo": doc["cap"],
                        "Piano Gest.": doc["pg"],
                        "N. Decreto": doc["n_decreto"],
                        "Data Decreto": doc["data_decreto"],
                    })
                st.table(pd.DataFrame(rows_at))

            if docs_rn:
                st.markdown(
                    "<div style='font-size:11px;font-weight:700;text-transform:uppercase;"
                    "letter-spacing:.07em;color:#C49B1D;margin-bottom:8px;margin-top:16px;"
                    "font-family:Segoe UI,sans-serif'>"
                    "<span class='mef-tag tag-rn' style='font-size:9px'>RN</span>"
                    "&nbsp; Ricerca Normativa</div>",
                    unsafe_allow_html=True,
                )
                rows_rn = []
                for doc in docs_rn:
                    rows_rn.append({
                        "Fonte": "RN",
                        "Documento": doc["Documento"],
                        "CUP": ", ".join(doc["cups"]),
                        "Tipologia": doc["Tipologia"],
                        "N. Decreto": doc["Numero_Decreto"],
                        "Capitolo": doc["Capitolo_di_Spesa"],
                        "Piano Gest.": doc["Piano_Gestionale"],
                    })
                st.table(pd.DataFrame(rows_rn))


# ===================================================================
#  FOOTER
# ===================================================================

st.markdown(
    f'<div class="mef-footer">'
    f'  <span>Ministero dell\'Economia e delle Finanze — Ragioneria Generale dello Stato</span>'
    f'  <span>Avviato: {start_time_str} &nbsp;|&nbsp;'
    f'    <span class="mef-tag tag-at" style="font-size:9px">AT</span>'
    f'    &nbsp;Amm. Trasparente&nbsp;&nbsp;'
    f'    <span class="mef-tag tag-rn" style="font-size:9px">RN</span>'
    f'    &nbsp;Ricerca Normativa MIT'
    f'  </span>'
    f'</div>',
    unsafe_allow_html=True,
)


# ===================================================================
#  SIDEBAR
# ===================================================================

with st.sidebar:
    st.markdown(
        "<div style='padding:14px 0 8px 0;font-size:14px;font-weight:700;"
        "color:#FFFFFF;font-family:Segoe UI,sans-serif;"
        "border-bottom:1px solid rgba(255,255,255,.15);margin-bottom:4px'>"
        "MEF &nbsp;<span style='color:#C49B1D'>&#183;</span>&nbsp; RGS"
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
                f"{len(subset):,} rec &nbsp;&#183;&nbsp; {subset['CUP'].nunique():,} CUP"
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

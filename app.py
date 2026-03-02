import streamlit as st
import pandas as pd
import os
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

BADGE_AT = "AT"
BADGE_RN = "RN"

# ═══════════════════════════════════════════════════════════════════════
#  MEF / RGS VISUAL IDENTITY — CSS
#  Colors from the manual:
#    Blue  Pantone 287 C  →  #1D3D8F  (approx.)
#    Gold  Pantone 131 CVC → #C49B1D  (approx.)
# ═══════════════════════════════════════════════════════════════════════
MEF_CSS = """
<style>
/* ── Google Fonts fallback: Segoe UI is the spec font ── */
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');

:root {
    --mef-blue:       #1D3D8F;
    --mef-blue-dark:  #132B6B;
    --mef-blue-light: #E8EDF7;
    --mef-gold:       #C49B1D;
    --mef-gold-light: #F7F1DC;
    --mef-white:      #FFFFFF;
    --mef-off-white:  #F5F6F8;
    --mef-border:     #D1D9EC;
    --mef-text:       #1A1A2E;
    --mef-text-muted: #5A6585;
    --mef-at-tag:     #1D3D8F;
    --mef-rn-tag:     #C49B1D;
    --font:           'Segoe UI', 'Source Sans 3', sans-serif;
}

/* ── Base reset ── */
html, body, [class*="css"] {
    font-family: var(--font) !important;
    color: var(--mef-text);
}

/* ── Remove default Streamlit padding ── */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}

/* ── INSTITUTIONAL HEADER BAND ── */
.mef-header {
    background: var(--mef-blue);
    color: white;
    padding: 0;
    margin: -1rem -1rem 0 -1rem;
    border-bottom: 4px solid var(--mef-gold);
}
.mef-header-inner {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 18px 40px;
}
.mef-logo-circle {
    width: 52px;
    height: 52px;
    border: 2.5px solid var(--mef-gold);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 700;
    color: white;
    letter-spacing: -1px;
    flex-shrink: 0;
    position: relative;
}
.mef-logo-arc {
    position: absolute;
    right: -4px;
    top: -4px;
    width: 26px;
    height: 26px;
    border: 2.5px solid var(--mef-gold);
    border-radius: 50%;
    border-left-color: transparent;
    border-bottom-color: transparent;
    transform: rotate(45deg);
}
.mef-header-text {}
.mef-header-title {
    font-size: 13px;
    font-weight: 300;
    letter-spacing: 0.05em;
    color: rgba(255,255,255,0.75);
    line-height: 1.2;
    margin-bottom: 2px;
}
.mef-header-dept {
    font-size: 16px;
    font-weight: 600;
    color: white;
    line-height: 1.2;
}
.mef-header-sub {
    font-size: 11px;
    font-weight: 300;
    color: rgba(255,255,255,0.6);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 3px;
}
.mef-header-right {
    margin-left: auto;
    text-align: right;
}
.mef-app-name {
    font-size: 20px;
    font-weight: 700;
    color: white;
    letter-spacing: 0.02em;
}
.mef-app-desc {
    font-size: 11px;
    color: rgba(255,255,255,0.6);
    font-weight: 300;
    letter-spacing: 0.05em;
}

/* ── DIVIDER ── */
.mef-rule {
    border: none;
    border-top: 1px solid var(--mef-border);
    margin: 1.5rem 0;
}

/* ── PAGE TITLE ── */
.mef-page-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--mef-blue);
    margin: 1.5rem 0 0.25rem 0;
    letter-spacing: -0.01em;
}
.mef-page-subtitle {
    font-size: 13px;
    color: var(--mef-text-muted);
    margin-bottom: 1.5rem;
}

/* ── STATUS BADGES ── */
.mef-status-row {
    display: flex;
    gap: 12px;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.mef-status-card {
    flex: 1;
    min-width: 220px;
    border-radius: 4px;
    padding: 10px 16px;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 10px;
    border: 1px solid;
}
.mef-status-card.ok {
    background: #EDF2FF;
    border-color: var(--mef-blue);
    color: var(--mef-blue-dark);
}
.mef-status-card.error {
    background: #FFF3F3;
    border-color: #CC2222;
    color: #8B0000;
}
.mef-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.mef-status-card.ok   .mef-status-dot { background: var(--mef-blue); }
.mef-status-card.error .mef-status-dot { background: #CC2222; }
.mef-status-tag {
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 2px;
    margin-left: auto;
    flex-shrink: 0;
}
.mef-status-card.ok   .mef-status-tag { background: var(--mef-blue); color: white; }
.mef-status-card.error .mef-status-tag { background: #CC2222; color: white; }

/* ── SEARCH BOX ── */
.stTextInput > div > div > input {
    border: 1.5px solid var(--mef-border) !important;
    border-radius: 3px !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s;
    font-family: var(--font) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--mef-blue) !important;
    box-shadow: 0 0 0 3px rgba(29,61,143,0.12) !important;
}
.stTextInput > label {
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: var(--mef-text-muted) !important;
}

/* ── RESULT BANNER ── */
.mef-result-banner {
    background: var(--mef-blue-light);
    border-left: 4px solid var(--mef-blue);
    border-radius: 0 3px 3px 0;
    padding: 10px 16px;
    margin-bottom: 1.25rem;
    font-size: 13.5px;
    color: var(--mef-blue-dark);
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
}
.mef-result-banner strong { font-weight: 700; }
.mef-tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 2px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.tag-at { background: var(--mef-blue);  color: white; }
.tag-rn { background: var(--mef-gold);  color: white; }

/* ── SELECT BOX ── */
.stSelectbox > label {
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: var(--mef-text-muted) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid var(--mef-border) !important;
    gap: 0 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--mef-text-muted) !important;
    padding: 10px 20px !important;
    border-radius: 0 !important;
    border-bottom: 3px solid transparent !important;
    margin-bottom: -2px !important;
    letter-spacing: 0.01em;
    background: transparent !important;
    text-transform: none !important;
}
.stTabs [aria-selected="true"] {
    color: var(--mef-blue) !important;
    border-bottom-color: var(--mef-blue) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.25rem !important;
}

/* ── EXPANDERS (document cards) ── */
.streamlit-expanderHeader {
    background: var(--mef-white) !important;
    border: 1px solid var(--mef-border) !important;
    border-radius: 3px !important;
    font-family: var(--font) !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    color: var(--mef-blue-dark) !important;
    padding: 12px 16px !important;
    transition: background 0.15s;
}
.streamlit-expanderHeader:hover {
    background: var(--mef-blue-light) !important;
}
.streamlit-expanderContent {
    border: 1px solid var(--mef-border) !important;
    border-top: none !important;
    border-radius: 0 0 3px 3px !important;
    padding: 16px 20px !important;
    background: var(--mef-white) !important;
}

/* ── DOCUMENT FIELD LABELS ── */
.doc-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--mef-text-muted);
    margin-bottom: 2px;
}
.doc-value {
    font-size: 13.5px;
    color: var(--mef-text);
    margin-bottom: 12px;
}
.doc-cup {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    background: var(--mef-blue-light);
    color: var(--mef-blue-dark);
    padding: 3px 8px;
    border-radius: 2px;
    font-weight: 700;
    letter-spacing: 0.05em;
}

/* ── LINK BUTTON ── */
.mef-link-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--mef-blue);
    color: white !important;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-decoration: none !important;
    padding: 7px 14px;
    border-radius: 3px;
    margin-top: 8px;
    transition: background 0.15s;
}
.mef-link-btn:hover { background: var(--mef-blue-dark) !important; }

/* ── TABLE ── */
table {
    font-size: 12.5px !important;
    border-collapse: collapse !important;
    width: 100% !important;
}
th {
    background: var(--mef-blue) !important;
    color: white !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 8px 12px !important;
    border: none !important;
}
td {
    padding: 7px 12px !important;
    border-bottom: 1px solid var(--mef-border) !important;
    vertical-align: top;
}
tr:nth-child(even) td { background: var(--mef-off-white) !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--mef-blue-dark) !important;
    border-right: 3px solid var(--mef-gold) !important;
}
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
    font-family: var(--font) !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: white !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    border-bottom: 1px solid rgba(255,255,255,0.15) !important;
    padding-bottom: 6px !important;
    margin-top: 16px !important;
}
[data-testid="stSidebar"] .stMetric {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 3px !important;
    padding: 8px 10px !important;
    margin-bottom: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: white !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: rgba(255,255,255,0.55) !important;
}
[data-testid="stSidebar"] .stMarkdown caption,
[data-testid="stSidebar"] small {
    color: rgba(255,255,255,0.45) !important;
    font-size: 10.5px !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.12) !important;
}

/* ── SIDEBAR GOLD DETAIL TAGS ── */
.sb-type-badge {
    display: inline-block;
    background: var(--mef-gold);
    color: white;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 2px;
    margin-right: 4px;
}

/* ── FOOTER ── */
.mef-footer {
    border-top: 1px solid var(--mef-border);
    margin-top: 3rem;
    padding-top: 1rem;
    font-size: 11px;
    color: var(--mef-text-muted);
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 4px;
}
.mef-footer a { color: var(--mef-blue); text-decoration: none; }

/* ── WARNINGS ── */
.stAlert {
    border-radius: 3px !important;
    font-size: 13px !important;
    font-family: var(--font) !important;
}

/* ── Hide Streamlit default elements ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
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
    parent_path = AT_ONEDRIVE_PATH
    return (
        f"{SHAREPOINT_BASE}"
        f"?id={encode_path(file_path)}"
        f"&parent={encode_path(parent_path)}"
    )


def onedrive_link_rn(cartella, filename):
    if not cartella or not filename:
        return None
    file_path = RN_ONEDRIVE_PATH + "/" + cartella + "/" + filename
    parent_path = RN_ONEDRIVE_PATH + "/" + cartella
    return (
        f"{SHAREPOINT_BASE}"
        f"?id={encode_path(file_path)}"
        f"&parent={encode_path(parent_path)}"
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
                df = pd.read_csv(
                    csv_file, sep=";", encoding="utf-8-sig", dtype=str
                )
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
    <div class="mef-logo-circle">
      MEF
      <div class="mef-logo-arc"></div>
    </div>
    <div class="mef-header-text">
      <div class="mef-header-title">Ministero dell'Economia e delle Finanze</div>
      <div class="mef-header-dept">Ragioneria Generale dello Stato</div>
      <div class="mef-header-sub">Sistema di ricerca documentale</div>
    </div>
    <div class="mef-header-right">
      <div class="mef-app-name">CUPDF</div>
      <div class="mef-app-desc">CUP Document Finder</div>
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
  Consultazione integrata di 
  <span class="mef-tag tag-at">AT</span> Amministrazione Trasparente &nbsp;e&nbsp;
  <span class="mef-tag tag-rn">RN</span> Ricerca Normativa — MIT
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  STATUS INDICATORS
# ═══════════════════════════════════════════════════════════════════════

at_label  = (f"Amministrazione Trasparente — {len(df_at):,} record &nbsp;"
             f"<span class='mef-status-tag'>AT</span>") if at_disponibile \
            else "Amministrazione Trasparente — dati non trovati &nbsp;<span class='mef-status-tag'>AT</span>"

rn_label  = (f"Ricerca Normativa — {len(df_rn):,} record ({df_rn['_csv_origine'].nunique()} file) &nbsp;"
             f"<span class='mef-status-tag'>RN</span>") if rn_disponibile \
            else "Ricerca Normativa — dati non trovati &nbsp;<span class='mef-status-tag'>RN</span>"

at_class  = "ok"    if at_disponibile else "error"
rn_class  = "ok"    if rn_disponibile else "error"

st.markdown(f"""
<div class="mef-status-row">
  <div class="mef-status-card {at_class}">
    <div class="mef-status-dot"></div>
    <span>{at_label}</span>
  </div>
  <div class="mef-status-card {rn_class}">
    <div class="mef-status-dot"></div>
    <span>{rn_label}</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="mef-rule">', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  SEARCH INPUT
# ═══════════════════════════════════════════════════════════════════════

query = st.text_input(
    "Codice CUP (o parte di esso)",
    placeholder="es. J31B20000050001",
)


# ═══════════════════════════════════════════════════════════════════════
#  HELPER: render a field row with institutional label style
# ═══════════════════════════════════════════════════════════════════════

def field(label: str, value: str, mono: bool = False) -> str:
    """Return HTML for a labelled document field."""
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

        # --- CUP unici combinati ---
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

        # ─── TABS ─────────────────────────────────────────────────
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
                for i, row in results_at.iterrows():
                    with st.expander(
                        f"[AT]  {row['file']}",
                        expanded=True,
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(
                                field("CUP", row["cup"], mono=True)
                                + field("Capitolo", str(row.get("cap", "")))
                                + field("Piano Gestionale", str(row.get("pg", "")))
                                + field("Stato — Capitolo — Piano", str(row.get("stacappg", ""))),
                                unsafe_allow_html=True,
                            )
                        with col2:
                            st.markdown(
                                field("N. Decreto",  str(row.get("n_decreto",  "")))
                                + field("Data Decreto", str(row.get("data_decreto", "")))
                                + field("Decreto",      str(row.get("decreto",      ""))),
                                unsafe_allow_html=True,
                            )
                        link = onedrive_link_at(row["file"])
                        st.markdown(open_link_html(link), unsafe_allow_html=True)
                        st.markdown(
                            '<div style="font-size:10.5px;color:var(--mef-text-muted);'
                            'margin-top:10px;padding-top:8px;border-top:1px solid var(--mef-border)">'
                            '<span class="mef-tag tag-at" style="font-size:9px">AT</span>'
                            '&nbsp; Fonte: Amministrazione Trasparente</div>',
                            unsafe_allow_html=True,
                        )

        # ═══ TAB RN ═══════════════════════════════════════════════
        with tab_rn:
            if results_rn.empty:
                st.info("Nessun risultato da Ricerca Normativa.")
            else:
                for i, row in results_rn.iterrows():
                    doc_name  = row.get("Documento",  "Documento sconosciuto")
                    tipologia = row.get("Tipologia",  "")
                    cartella  = row.get("Cartella",   "")
                    with st.expander(
                        f"[RN]  {doc_name}",
                        expanded=True,
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(
                                field("CUP", row["CUP"], mono=True)
                                + field("Capitolo di Spesa",  str(row.get("Capitolo_di_Spesa", "")))
                                + field("Piano Gestionale",   str(row.get("Piano_Gestionale",  "")))
                                + field("Importo (EUR)",      str(row.get("Importo_EUR",       ""))),
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
                        st.markdown(
                            f'<div style="font-size:10.5px;color:var(--mef-text-muted);'
                            f'margin-top:10px;padding-top:8px;border-top:1px solid var(--mef-border)">'
                            f'<span class="mef-tag tag-rn" style="font-size:9px">RN</span>'
                            f'&nbsp; Fonte: Ricerca Normativa ({src})'
                            + (f' &nbsp;|&nbsp; Cartella: {cartella}' if cartella else "")
                            + "</div>",
                            unsafe_allow_html=True,
                        )

        # ═══ TAB TUTTI ════════════════════════════════════════════
        with tab_all:
            st.markdown(
                "<p style='font-size:13px;color:var(--mef-text-muted);margin-bottom:1rem'>"
                "Riepilogo combinato di tutti i risultati trovati.</p>",
                unsafe_allow_html=True,
            )
            if not results_at.empty:
                st.markdown(
                    "<div style='font-size:11px;font-weight:700;text-transform:uppercase;"
                    "letter-spacing:.07em;color:var(--mef-blue);margin-bottom:8px'>"
                    "<span class='mef-tag tag-at' style='font-size:9px'>AT</span>"
                    "&nbsp; Amministrazione Trasparente</div>",
                    unsafe_allow_html=True,
                )
                display_at = results_at[
                    ["cup", "cap", "pg", "n_decreto", "data_decreto", "file"]
                ].copy()
                display_at.columns = [
                    "CUP", "Capitolo", "Piano Gest.", "N. Decreto", "Data Decreto", "Documento"
                ]
                display_at.insert(0, "Fonte", "AT")
                st.table(display_at.reset_index(drop=True))

            if not results_rn.empty:
                st.markdown(
                    "<div style='font-size:11px;font-weight:700;text-transform:uppercase;"
                    "letter-spacing:.07em;color:var(--mef-gold);margin-bottom:8px;margin-top:16px'>"
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

st.markdown(
    f'<div class="mef-footer">'
    f'  <span>Ministero dell\'Economia e delle Finanze — Ragioneria Generale dello Stato</span>'
    f'  <span>Avviato: {start_time_str} &nbsp;|&nbsp; '
    f'    <span class="mef-tag tag-at" style="font-size:9px">AT</span> Amm. Trasparente &nbsp;&nbsp;'
    f'    <span class="mef-tag tag-rn" style="font-size:9px">RN</span> Ricerca Normativa MIT'
    f'  </span>'
    f'</div>',
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        "<div style='padding:16px 0 8px 0;font-size:15px;font-weight:700;"
        "color:white;letter-spacing:.01em;border-bottom:1px solid rgba(255,255,255,.15);"
        "margin-bottom:4px'>"
        "MEF &nbsp;<span style='color:var(--mef-gold)'>·</span>&nbsp; RGS"
        "<br><span style='font-size:10px;font-weight:300;opacity:.6;letter-spacing:.06em;text-transform:uppercase'>"
        "Statistiche Database</span></div>",
        unsafe_allow_html=True,
    )

    st.subheader("Amm. Trasparente")
    if at_disponibile:
        st.metric("Record totali",  f"{len(df_at):,}")
        st.metric("CUP unici",      f"{df_at['cup'].nunique():,}")
        st.metric("Documenti",      f"{df_at['file'].nunique():,}")
    else:
        st.caption("Non disponibile")

    st.markdown("---")
    st.subheader("Ricerca Normativa")
    if rn_disponibile:
        st.metric("Record con CUP", f"{len(df_rn):,}")
        st.metric("CUP unici",      f"{df_rn['CUP'].nunique():,}")
        for csv_name in df_rn["_csv_origine"].unique():
            subset = df_rn[df_rn["_csv_origine"] == csv_name]
            tipo = (
                csv_name
                .replace("risultati_puliti_", "")
                .replace(".csv", "")
            )
            st.markdown(
                f"<div style='font-size:11px;opacity:.7;padding:2px 0'>"
                f"<span class='sb-type-badge'>{tipo}</span> "
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
        f"<div style='font-size:10px;opacity:.45;padding-bottom:8px'>"
        f"Avviato: {start_time_str}<br>"
        f"⚠️ Accesso PDF richiede OneDrive condiviso."
        f"</div>",
        unsafe_allow_html=True,
    )

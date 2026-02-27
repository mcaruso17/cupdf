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

# --- Fonte 1: Amministrazione Trasparente ---
AT_EXCEL = "data/file pulito per ricerca.xlsx"

# --- Fonte 2: Ricerca Normativa ---
RN_CSV_FILES = [
    "data/risultati_puliti_dir.csv",
    "data/risultati_puliti_dirett.csv",
    "data/risultati_puliti_interm.csv",
    "data/risultati_puliti_minist.csv",
]

# --- OneDrive URL Config ---
# Base URL di SharePoint
SHAREPOINT_BASE = "https://mefgovit-my.sharepoint.com/my"

# Percorso base su OneDrive (dalla root di Documents)
ONEDRIVE_PATH_BASE = (
    "/personal/matteo_caruso_rgs_tesoro_it"
    "/Documents/Documenti/data analysis/at mit"
)

# Percorsi relativi delle cartelle PDF
AT_ONEDRIVE_PATH = ONEDRIVE_PATH_BASE + "/allegati at"
RN_ONEDRIVE_PATH = ONEDRIVE_PATH_BASE + "/output_mit_normativa/allegati"

# ╔══════════════════════════════════════════════════════════════════════╗
# ║          FINE IMPOSTAZIONI                                          ║
# ╚══════════════════════════════════════════════════════════════════════╝

st.set_page_config(page_title="CUP Document Finder", layout="wide")

BADGE_AT = "🟦"
BADGE_RN = "🟧"


# ═══════════════════════════════════════════════════════════════════════
#  FUNZIONI URL ONEDRIVE
# ═══════════════════════════════════════════════════════════════════════

def encode_path(path):
    """Codifica un percorso per URL SharePoint."""
    return quote(path, safe="")


def onedrive_link_at(filename):
    """Genera link diretto al PDF su OneDrive per AT."""
    file_path = AT_ONEDRIVE_PATH + "/" + filename
    parent_path = AT_ONEDRIVE_PATH
    return (
        f"{SHAREPOINT_BASE}"
        f"?id={encode_path(file_path)}"
        f"&parent={encode_path(parent_path)}"
    )


def onedrive_link_rn(cartella, filename):
    """Genera link diretto al PDF su OneDrive per RN."""
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


# ═══════════════════════════════════════════════════════════════════════
#  CARICA TUTTO
# ═══════════════════════════════════════════════════════════════════════

df_at = load_at_data()
df_rn = load_rn_data()

at_disponibile = not df_at.empty
rn_disponibile = not df_rn.empty


# ═══════════════════════════════════════════════════════════════════════
#  INTERFACCIA
# ═══════════════════════════════════════════════════════════════════════

st.title("CUP Document Finder (CUPDF)")
st.markdown(
    "Ricerca documentazione relativa al CUP da "
    f"**{BADGE_AT} Amministrazione Trasparente** e "
    f"**{BADGE_RN} Ricerca Normativa** del MIT."
)

# --- Indicatori fonti ---
col_s1, col_s2 = st.columns(2)
with col_s1:
    if at_disponibile:
        st.success(f"{BADGE_AT} Amministrazione Trasparente — caricata")
    else:
        st.error("❌ Amm. Trasparente — dati non trovati")
with col_s2:
    if rn_disponibile:
        st.success(
            f"{BADGE_RN} Ricerca Normativa — caricata "
            f"({len(df_rn):,} record con CUP da "
            f"{df_rn['_csv_origine'].nunique()} file)"
        )
    else:
        st.error("❌ Ricerca Normativa — dati non trovati")

st.markdown("---")
st.caption(
    f"{BADGE_AT} = Amministrazione Trasparente  |  "
    f"{BADGE_RN} = Ricerca Normativa"
)

# --- Ricerca ---
query = st.text_input(
    "Inserire CUP (o parte di esso):",
    placeholder="es. J31B20000050001",
)

if query:
    query_clean = query.strip().upper()

    results_at = pd.DataFrame()
    if at_disponibile:
        results_at = df_at[
            df_at["cup"].str.contains(query_clean, na=False)
        ]

    results_rn = pd.DataFrame()
    if rn_disponibile:
        results_rn = df_rn[
            df_rn["CUP"].str.contains(query_clean, na=False)
        ]

    tot = len(results_at) + len(results_rn)

    if tot == 0:
        st.warning(
            "Nessun documento trovato per questo CUP. "
            "Prova una ricerca parziale."
        )
    else:
        st.success(
            f"Trovati **{tot}** risultato/i per \"{query_clean}\"  —  "
            f"{BADGE_AT} **{len(results_at)}** da Amm. Trasparente, "
            f"{BADGE_RN} **{len(results_rn)}** da Ricerca Normativa"
        )

        # --- CUP unici combinati ---
        all_cups = []
        if not results_at.empty:
            all_cups.extend(results_at["cup"].unique().tolist())
        if not results_rn.empty:
            all_cups.extend(results_rn["CUP"].unique().tolist())
        unique_cups = sorted(set(all_cups))

        selected_cup = None
        if len(unique_cups) > 1:
            selected_cup = st.selectbox(
                f"CUP multipli trovati ({len(unique_cups)}). "
                "Selezionane uno:",
                options=unique_cups,
            )
            if not results_at.empty:
                results_at = results_at[
                    results_at["cup"] == selected_cup
                ]
            if not results_rn.empty:
                results_rn = results_rn[
                    results_rn["CUP"] == selected_cup
                ]

        # ─── TABS ─────────────────────────────────────────────────
        tab_at, tab_rn, tab_all = st.tabs([
            f"{BADGE_AT} Amm. Trasparente ({len(results_at)})",
            f"{BADGE_RN} Ricerca Normativa ({len(results_rn)})",
            f"📋 Tutti i risultati "
            f"({len(results_at) + len(results_rn)})",
        ])

        # ═══ TAB AT ═══════════════════════════════════════════════
        with tab_at:
            if results_at.empty:
                st.info(
                    "Nessun risultato da Amministrazione Trasparente."
                )
            else:
                for i, row in results_at.iterrows():
                    with st.expander(
                        f"{BADGE_AT} 📄 {row['file']}",
                        expanded=True,
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**CUP:** `{row['cup']}`")
                            st.markdown(f"**Capitolo:** {row['cap']}")
                            st.markdown(
                                f"**Piano Gestionale:** {row['pg']}"
                            )
                            st.markdown(
                                f"**Stato - Capitolo - Piano:** "
                                f"{row['stacappg']}"
                            )
                        with col2:
                            st.markdown(
                                f"**N. Decreto:** {row['n_decreto']}"
                            )
                            st.markdown(
                                f"**Data Decreto:** "
                                f"{row['data_decreto']}"
                            )
                            st.markdown(
                                f"**Decreto:** {row['decreto']}"
                            )

                        st.caption(
                            f"Fonte: {BADGE_AT} "
                            f"Amministrazione Trasparente"
                        )

                        # Link diretto al PDF su OneDrive
                        link = onedrive_link_at(row["file"])
                        st.markdown(
                            f"📥 [**Apri documento su OneDrive**]"
                            f"({link})"
                        )

        # ═══ TAB RN ═══════════════════════════════════════════════
        with tab_rn:
            if results_rn.empty:
                st.info("Nessun risultato da Ricerca Normativa.")
            else:
                for i, row in results_rn.iterrows():
                    doc_name = row.get(
                        "Documento", "Documento sconosciuto"
                    )
                    tipologia = row.get("Tipologia", "")
                    with st.expander(
                        f"{BADGE_RN} 📜 {doc_name}",
                        expanded=True,
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**CUP:** `{row['CUP']}`")
                            if row.get("Capitolo_di_Spesa", ""):
                                st.markdown(
                                    f"**Capitolo di Spesa:** "
                                    f"{row['Capitolo_di_Spesa']}"
                                )
                            if row.get("Piano_Gestionale", ""):
                                st.markdown(
                                    f"**Piano Gestionale:** "
                                    f"{row['Piano_Gestionale']}"
                                )
                            if row.get("Importo_EUR", ""):
                                st.markdown(
                                    f"**Importo (EUR):** "
                                    f"{row['Importo_EUR']}"
                                )
                        with col2:
                            if row.get("Numero_Decreto", ""):
                                st.markdown(
                                    f"**N. Decreto:** "
                                    f"{row['Numero_Decreto']}"
                                )
                            if row.get("Data_Decreto", ""):
                                st.markdown(
                                    f"**Data Decreto:** "
                                    f"{row['Data_Decreto']}"
                                )
                            if tipologia:
                                st.markdown(
                                    f"**Tipologia:** {tipologia}"
                                )
                            if row.get("Ministero", ""):
                                st.markdown(
                                    f"**Ministero:** "
                                    f"{row['Ministero']}"
                                )

                        cartella = row.get("Cartella", "")
                        if cartella:
                            st.caption(f"Cartella: {cartella}")
                        st.caption(
                            f"Fonte: {BADGE_RN} Ricerca Normativa "
                            f"({row.get('_csv_origine', '')})"
                        )

                        # Link diretto al PDF su OneDrive
                        link = onedrive_link_rn(cartella, doc_name)
                        if link:
                            st.markdown(
                                f"📥 [**Apri documento su OneDrive**]"
                                f"({link})"
                            )

        # ═══ TAB TUTTI ════════════════════════════════════════════
        with tab_all:
            st.markdown("Riepilogo combinato di tutti i risultati.")

            if not results_at.empty:
                st.subheader(
                    f"{BADGE_AT} Amministrazione Trasparente"
                )
                display_at = results_at[
                    ["cup", "cap", "pg", "n_decreto",
                     "data_decreto", "file"]
                ].copy()
                display_at.columns = [
                    "CUP", "Capitolo", "Piano Gest.",
                    "N. Decreto", "Data Decreto", "Documento",
                ]
                display_at.insert(0, "Fonte", BADGE_AT)
                st.table(display_at.reset_index(drop=True))

            if not results_rn.empty:
                st.subheader(f"{BADGE_RN} Ricerca Normativa")
                cols_rn = [
                    "CUP", "Tipologia", "Numero_Decreto",
                    "Data_Decreto", "Capitolo_di_Spesa", "Documento",
                ]
                cols_present = [
                    c for c in cols_rn if c in results_rn.columns
                ]
                display_rn = results_rn[cols_present].copy()
                display_rn.insert(0, "Fonte", BADGE_RN)
                st.table(display_rn.reset_index(drop=True))


# ═══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("📊 Statistiche Database")

    st.subheader(f"{BADGE_AT} Amm. Trasparente")
    if at_disponibile:
        st.metric("Record totali", f"{len(df_at):,}")
        st.metric("CUP unici", f"{df_at['cup'].nunique():,}")
        st.metric("Documenti", f"{df_at['file'].nunique():,}")
    else:
        st.caption("Non disponibile")

    st.markdown("---")

    st.subheader(f"{BADGE_RN} Ricerca Normativa")
    if rn_disponibile:
        st.metric("Record con CUP", f"{len(df_rn):,}")
        st.metric("CUP unici", f"{df_rn['CUP'].nunique():,}")
        st.markdown("**Dettaglio per tipo:**")
        for csv_name in df_rn["_csv_origine"].unique():
            subset = df_rn[df_rn["_csv_origine"] == csv_name]
            tipo = (
                csv_name
                .replace("risultati_puliti_", "")
                .replace(".csv", "")
            )
            st.caption(
                f"  • {tipo}: {len(subset):,} record, "
                f"{subset['CUP'].nunique():,} CUP unici"
            )
    else:
        st.caption("Non disponibile")

    st.markdown("---")

    if at_disponibile and rn_disponibile:
        st.subheader("📊 Riepilogo combinato")
        cup_at = set(df_at["cup"].unique())
        cup_rn = set(df_rn["CUP"].unique())
        cup_comuni = cup_at & cup_rn
        cup_totali = cup_at | cup_rn

        st.metric("CUP totali (unici)", f"{len(cup_totali):,}")
        st.metric(
            "CUP in entrambe le fonti", f"{len(cup_comuni):,}"
        )
        st.metric(
            f"CUP solo in {BADGE_AT}",
            f"{len(cup_at - cup_rn):,}",
        )
        st.metric(
            f"CUP solo in {BADGE_RN}",
            f"{len(cup_rn - cup_at):,}",
        )

    st.markdown("---")
    st.caption(f"Avviato: {start_time_str}")
    st.caption(
        f"Fonti: {BADGE_AT} MIT Amm. Trasparente  |  "
        f"{BADGE_RN} MIT Ricerca Normativa"
    )
    st.markdown("---")
    st.caption(
        "⚠️ Per accedere ai PDF è necessario avere accesso "
        "alla cartella OneDrive condivisa."
    )

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import re

# Sideoppsett
st.set_page_config(page_title="Kalkulator for Nedbetaling & Innbytte", layout="wide")
st.title("📱 Nedbetalingskalkulator")

# --- INITIALISER DEFAULT-VERDIER I SESSION STATE (SETT TIL 0 NÅR APPEN STARTER) ---
if "gammel_mnd_pris" not in st.session_state:
    st.session_state["gammel_mnd_pris"] = 0.0
if "innbytteverdi" not in st.session_state:
    st.session_state["innbytteverdi"] = 0.0
if "gjenstaende_mnd" not in st.session_state:
    st.session_state["gjenstaende_mnd"] = 0

# --- FUNKSJON FOR TEKST-PARSING ---
def parse_kopiert_tekst(tekst):
    mnd_pris = None
    innbytte = None
    mnd_igjen = None

    # 1. Månedspris (f.eks. "228,75 /md.")
    mnd_match = re.search(r'(\d+[\.,]\d+)\s*/?\s*md', tekst, re.IGNORECASE)
    if mnd_match:
        mnd_pris = float(mnd_match.group(1).replace(',', '.'))

    # 2. Innbytteverdi (f.eks. "opptil 4368,- kr")
    innbytte_match = re.search(r'opptil\s*(\d+)', tekst, re.IGNORECASE)
    if not innbytte_match:
        innbytte_match = re.search(r'(\d+)\s*[\.,-]?\s*kr', tekst, re.IGNORECASE)
    if innbytte_match:
        innbytte = float(innbytte_match.group(1))

    # 3. Beregn gjenstående måneder ut fra datoperiode (f.eks. "05.09.2025 - 05.09.2027")
    dato_match = re.search(r'(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})', tekst)
    if dato_match:
        try:
            sluttdato = datetime.strptime(dato_match.group(2), "%d.%m.%Y")
            idag = datetime.now()
            differanse_mnd = (sluttdato.year - idag.year) * 12 + (sluttdato.month - idag.month)
            mnd_igjen = max(1, differanse_mnd)
        except Exception:
            pass

    # Backup: Regn ut fra Gjenstående beløp / Månedspris
    if mnd_igjen is None and mnd_pris and mnd_pris > 0:
        gjen_match = re.search(r'Gjenstående[^\d]*(\d+[\.,]\d+|\d+)', tekst, re.IGNORECASE)
        if gjen_match:
            gjenstaende_belop = float(gjen_match.group(1).replace(',', '.'))
            mnd_igjen = round(gjenstaende_belop / mnd_pris)

    return mnd_pris, innbytte, mnd_igjen

# --- SIDEMENY: Inndata ---
st.sidebar.header("1. Ny Telefon")
ny_tlf_pris = st.sidebar.number_input("Totalpris på ny telefon (kr)", min_value=0, value=15000, step=500)
ny_nedbetaling_mnd = st.sidebar.selectbox("Nedbetalingstid ny telefon (mnd)", [24, 36], index=0)

st.sidebar.markdown("---")
st.sidebar.header("2. Eksisterende Avtale & Innbytte")

# Tekstområde for å lim inn fra kundebilde
lim_inn_tekst = st.sidebar.text_area("Lim inn tekst fra kundebildet:", height=130)

if st.sidebar.button("📋 Hent ut informasjonen"):
    if lim_inn_tekst.strip():
        m_pris, i_verdi, m_igjen = parse_kopiert_tekst(lim_inn_tekst)
        funnet = False
        
        if m_pris is not None:
            st.session_state["gammel_mnd_pris"] = m_pris
            funnet = True
        if i_verdi is not None:
            st.session_state["innbytteverdi"] = i_verdi
            funnet = True
        if m_igjen is not None:
            st.session_state["gjenstaende_mnd"] = m_igjen
            funnet = True
        
        if funnet:
            st.sidebar.success("Oppdatert!")
            st.rerun()
        else:
            st.sidebar.warning("Fant ikke alle tall i teksten.")
    else:
        st.sidebar.error("Vennligst lim inn teksten først.")

# Felter koblet direkte til session_state (starter nå på 0)
gammel_mnd_pris = st.sidebar.number_input(
    "Gammel månedspris (kr/md)", 
    min_value=0.0, 
    key="gammel_mnd_pris",
    step=10.0
)
gjenstaende_mnd = st.sidebar.number_input(
    "Gjenstående måneder på gammel avtale", 
    min_value=0, 
    key="gjenstaende_mnd",
    step=1
)
innbytteverdi = st.sidebar.number_input(
    "Innbytteverdi på gammel telefon (kr)", 
    min_value=0.0, 
    key="innbytteverdi",
    step=100.0
)

# --- BEREGNINGER ---
effektiv_ny_totalpris = max(0.0, ny_tlf_pris - innbytteverdi)
ny_mnd_pris_ren = effektiv_ny_totalpris / ny_nedbetaling_mnd if ny_nedbetaling_mnd > 0 else 0

mnd_fase_1 = min(gjenstaende_mnd, ny_nedbetaling_mnd)
mnd_fase_2 = max(0, ny_nedbetaling_mnd - mnd_fase_1)

total_mnd_fase_1 = ny_mnd_pris_ren + gammel_mnd_pris
total_mnd_fase_2 = ny_mnd_pris_ren

# --- NØKKELTALL (KOMPAKT) ---
col1, col2, col3 = st.columns(3)
col1.metric("Månedspris ny tlf", f"{ny_mnd_pris_ren:.2f} kr/md")
col2.metric("Innbytteverdi", f"{innbytteverdi:,.0f} kr")
col3.metric("Effektiv ny totalpris", f"{effektiv_ny_totalpris:,.0f} kr")

st.markdown("---")

# --- HORISONTAL DELE-VISNING ---
st.subheader("💳 Månedlig nedbetalingsplan")

if gammel_mnd_pris > 0 and gjenstaende_mnd > 0 and mnd_fase_2 > 0:
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.error(f"### Del 1 ({mnd_fase_1} mnd)")
        st.markdown(f"# **{total_mnd_fase_1:,.2f} kr/md**")
        st.caption(f"*(Ny tlf: {ny_mnd_pris_ren:.2f} kr + Gammel avtale: {gammel_mnd_pris:.2f} kr)*")

    with col_p2:
        st.success(f"### Del 2 ({mnd_fase_2} mnd)")
        st.markdown(f"# **{total_mnd_fase_2:,.2f} kr/md**")
        st.caption("*(Kun ny tlf etter gammel avtale er utløpt)*")

else:
    st.success(f"### Hele perioden ({ny_nedbetaling_mnd} mnd)")
    st.markdown(f"# **{ny_mnd_pris_ren:,.2f} kr/md**")

st.markdown("---")

# --- TETTSITTENDE GRAF / STOLPER ---
tidslinje_data = []
for mnd in range(1, ny_nedbetaling_mnd + 1):
    er_fase_1 = mnd <= gjenstaende_mnd
    gammel_del = gammel_mnd_pris if er_fase_1 else 0
    tidslinje_data.append({"Måned": f"Mnd {mnd}", "Del": "Ny Telefon", "Beløp": ny_mnd_pris_ren})
    if gammel_del > 0:
        tidslinje_data.append({"Måned": f"Mnd {mnd}", "Del": "Gammel Avtale", "Beløp": gammel_del})

df = pd.DataFrame(tidslinje_data)

fig = px.bar(
    df, 
    x="Måned", 
    y="Beløp", 
    color="Del", 
    labels={"Beløp": "Kr/md", "Måned": ""},
    color_discrete_map={"Ny Telefon": "#0083B0", "Gammel Avtale": "#FF6B6B"}
)

fig.update_layout(
    barmode='stack', 
    bargap=0.0,
    xaxis_tickangle=-45,
    margin=dict(l=10, r=10, t=10, b=10),
    legend_title_text=""
)

st.plotly_chart(fig, use_container_width=True)

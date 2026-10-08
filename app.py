import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import re

# Sideoppsett med mørkt tema
st.set_page_config(page_title="Innbyttekalkulator", layout="centered")

# --- CSS STYLING ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b1329;
        color: #e2e8f0;
    }
    
    .main-title {
        color: #f59e0b;
        font-weight: 700;
        font-size: 26px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    label, div[data-widget="radio"] label p, .stWidgetLabel p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }

    div[data-baseweb="input"] {
        background-color: #111d38 !important;
        border-color: #1e293b !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="input"] input {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    .result-box {
        background-color: #0b1736;
        border: 1px solid #1d3557;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
    }

    .result-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        font-size: 16px;
    }

    .border-bottom-dash {
        border-bottom: 1px dashed #2a3a5e;
        margin: 10px 0;
    }

    .text-light { color: #94a3b8; }
    .text-white-bold { color: #ffffff; font-weight: bold; font-size: 20px; }
    .text-green-bold { color: #10b981; font-weight: bold; font-size: 20px; }
    .text-yellow-bold { color: #f59e0b; font-weight: bold; font-size: 20px; }

    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #1e293b;
        color: white;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISER DEFAULT-VERDIER I SESSION STATE ---
if "ny_tlf_pris" not in st.session_state:
    st.session_state["ny_tlf_pris"] = 15990
if "innbytteverdi" not in st.session_state:
    st.session_state["innbytteverdi"] = 4368
if "innbyttebonus" not in st.session_state:
    st.session_state["innbyttebonus"] = 0
if "gammel_mnd_pris" not in st.session_state:
    st.session_state["gammel_mnd_pris"] = 0.0
if "gjenstaende_mnd" not in st.session_state:
    st.session_state["gjenstaende_mnd"] = 0
if "nedbetalingsmnd" not in st.session_state:
    st.session_state["nedbetalingsmnd"] = 24

# --- FUNKSJON FOR TEKST-PARSING ---
def parse_kopiert_tekst(tekst):
    mnd_pris = None
    innbytte = None
    mnd_igjen = None

    mnd_match = re.search(r'(\d+[\.,]\d+)\s*/?\s*md', tekst, re.IGNORECASE)
    if mnd_match:
        mnd_pris = float(mnd_match.group(1).replace(',', '.'))

    innbytte_match = re.search(r'opptil\s*(\d+)', tekst, re.IGNORECASE)
    if not innbytte_match:
        innbytte_match = re.search(r'(\d+)\s*[\.,-]?\s*kr', tekst, re.IGNORECASE)
    if innbytte_match:
        innbytte = float(innbytte_match.group(1))

    dato_match = re.search(r'(\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})', tekst)
    if dato_match:
        try:
            sluttdato = datetime.strptime(dato_match.group(2), "%d.%m.%Y")
            idag = datetime.now()
            differanse_mnd = (sluttdato.year - idag.year) * 12 + (sluttdato.month - idag.month)
            mnd_igjen = max(1, differanse_mnd)
        except Exception:
            pass

    if mnd_igjen is None and mnd_pris and mnd_pris > 0:
        gjen_match = re.search(r'Gjenstående[^\d]*(\d+[\.,]\d+|\d+)', tekst, re.IGNORECASE)
        if gjen_match:
            gjenstaende_belop = float(gjen_match.group(1).replace(',', '.'))
            mnd_igjen = round(gjenstaende_belop / mnd_pris)

    return mnd_pris, innbytte, mnd_igjen


# --- HOVED-GRENSESNITT ---

# TOPPBAR
col_title, col_mnd_select = st.columns([2, 1])

with col_title:
    st.markdown('<div class="main-title">🔵 Innbyttekalkulator</div>', unsafe_allow_html=True)

with col_mnd_select:
    mnd_valg = st.radio(
        "",
        options=[24, 36],
        index=0 if st.session_state["nedbetalingsmnd"] == 24 else 1,
        format_func=lambda x: f"{x} mnd",
        horizontal=True,
        key="nedbetalingsmnd"
    )

st.markdown("---")

# EKSPANDERBAR FOR HENTING AV TEKST (PLASSERT FØR NUMBER_INPUT WIDGETENE)
with st.expander("▶ Har kunden gjenstående gammel Splitt? (Lim inn tekst)"):
    lim_inn_tekst = st.text_area("Lim inn tekst fra kundebildet:", height=100)
    
    if st.button("📋 Hent ut fra tekst"):
        if lim_inn_tekst.strip():
            m_pris, i_verdi, m_igjen = parse_kopiert_tekst(lim_inn_tekst)
            if m_pris is not None:
                st.session_state["gammel_mnd_pris"] = float(m_pris)
            if i_verdi is not None:
                st.session_state["innbytteverdi"] = int(i_verdi)
            if m_igjen is not None:
                st.session_state["gjenstaende_mnd"] = int(m_igjen)
            st.rerun()

# INNDATAFELTER (TEGNES NÅ OPP ETTER AT PARSING ER HÅNDTERT)
ny_tlf_pris = st.number_input(
    "1. NY MOBIL PRIS (KONTANT)", 
    min_value=0, 
    key="ny_tlf_pris", 
    step=500
)

col_in1, col_in2 = st.columns(2)
with col_in1:
    innbytteverdi = st.number_input(
        "2. INNBYTTEVERDI GAMMEL MOBIL", 
        min_value=0, 
        key="innbytteverdi", 
        step=100
    )

with col_in2:
    innbyttebonus = st.number_input(
        "3. INNBYTTEBONUS", 
        min_value=0, 
        key="innbyttebonus", 
        step=100
    )

c_g1, c_g2 = st.columns(2)
with c_g1:
    gammel_mnd_pris = st.number_input("Gammel månedspris (kr/md)", min_value=0.0, key="gammel_mnd_pris", step=10.0)
with c_g2:
    gjenstaende_mnd = st.number_input("Gjenstående måneder", min_value=0, key="gjenstaende_mnd", step=1)

# --- BEREGNINGER ---
total_rabatt = st.session_state["innbytteverdi"] + st.session_state["innbyttebonus"]
effektiv_ny_totalpris = max(0.0, st.session_state["ny_tlf_pris"] - total_rabatt)
ny_mnd_pris_ren = effektiv_ny_totalpris / mnd_valg if mnd_valg > 0 else 0

mnd_fase_1 = min(st.session_state["gjenstaende_mnd"], mnd_valg)
mnd_fase_2 = max(0, mnd_valg - mnd_fase_1)

total_mnd_fase_1 = ny_mnd_pris_ren + st.session_state["gammel_mnd_pris"]
total_mnd_fase_2 = ny_mnd_pris_ren


# --- RESULTATKORT ---
st.markdown('<div class="result-box">', unsafe_allow_html=True)

st.markdown(f'''
<div class="result-row">
    <span class="text-light">Effektiv ny mobil-sum etter innbytte:</span>
    <span class="text-white-bold">{effektiv_ny_totalpris:,.0f} kr</span>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="result-row">
    <span class="text-light">Ny mobil per mnd ({mnd_valg} mnd Splitt):</span>
    <span class="text-green-bold">{ny_mnd_pris_ren:,.0f} kr/mnd</span>
</div>
''', unsafe_allow_html=True)

st.markdown('<div class="border-bottom-dash"></div>', unsafe_allow_html=True)

if st.session_state["gammel_mnd_pris"] > 0 and st.session_state["gjenstaende_mnd"] > 0 and mnd_fase_2 > 0:
    st.markdown(f'''
    <div class="result-row">
        <span class="text-light">Totalpris i første periode (inkl gammel Splitt avtale):</span>
        <span class="text-yellow-bold">{total_mnd_fase_1:,.0f} kr/mnd (første {mnd_fase_1} mnd)</span>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="result-row">
        <span class="text-light">Pris i resterende periode:</span>
        <span class="text-green-bold">{total_mnd_fase_2:,.0f} kr/mnd (deretter i {mnd_fase_2} mnd)</span>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('<div class="border-bottom-dash"></div>', unsafe_allow_html=True)

# VISUELL TIDSLINJE NEDERST
st.markdown('<span class="text-light" style="font-size: 12px; font-weight: bold; letter-spacing: 1px;">VISUELL OVERSIKT OVER TIDSFORLØPET:</span>', unsafe_allow_html=True)

if st.session_state["gammel_mnd_pris"] > 0 and st.session_state["gjenstaende_mnd"] > 0 and mnd_fase_2 > 0:
    tidslinje_faser = [
        {"Fase": "F1", "Måneder": mnd_fase_1, "Farge": "Fase1", "Tekst": f"{total_mnd_fase_1:,.0f} kr/mnd<br><span style='font-size:11px;'>Første {mnd_fase_1} mnd</span>"},
        {"Fase": "F2", "Måneder": mnd_fase_2, "Farge": "Fase2", "Tekst": f"{total_mnd_fase_2:,.0f} kr/mnd<br><span style='font-size:11px;'>Deretter {mnd_fase_2} mnd</span>"}
    ]
else:
    tidslinje_faser = [
        {"Fase": "F2", "Måneder": mnd_valg, "Farge": "Fase2", "Tekst": f"{ny_mnd_pris_ren:,.0f} kr/mnd<br><span style='font-size:11px;'>Hele perioden ({mnd_valg} mnd)</span>"}
    ]

df_tidslinje = pd.DataFrame(tidslinje_faser)

fig = px.bar(
    df_tidslinje,
    x="Måneder",
    y=[""] * len(df_tidslinje),
    color="Farge",
    orientation='h',
    text="Tekst",
    color_discrete_map={"Fase1": "#f59e0b", "Fase2": "#10b981"}
)

fig.update_traces(
    textposition='inside',
    textfont=dict(size=14, color='black', family="Arial Black"),
    insidetextanchor='middle'
)

fig.update_layout(
    barmode='stack',
    showlegend=False,
    xaxis=dict(showgrid=False, showticklabels=False, title=""),
    yaxis=dict(showgrid=False, showticklabels=False, title=""),
    height=80,
    margin=dict(l=0, r=0, t=5, b=5),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

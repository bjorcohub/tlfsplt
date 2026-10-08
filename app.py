import streamlit as st
from datetime import datetime
import re

# Sideoppsett med mørkt tema og komprimert layout
st.set_page_config(page_title="Innbyttekalkulator", layout="centered")

# --- ULTRA-MODERNE PREMIUM CSS STYLING ---
st.markdown("""
<style>
    /* Hovedbakgrunn */
    .stApp {
        background: linear-gradient(135deg, #070c1e 0%, #0d162d 100%);
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Skjul uønskede Streamlit-elementer */
    #MainMenu, header, footer {visibility: hidden;}

    /* Tittel-styling */
    .main-title {
        color: #fbbf24;
        font-weight: 800;
        font-size: 28px;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.5px;
    }

    /* Form-labels */
    label, div[data-widget="radio"] label p, .stWidgetLabel p {
        color: #94a3b8 !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-bottom: 6px !important;
    }

    /* Input-felter styling */
    div[data-baseweb="input"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        transition: all 0.2s ease-in-out;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }

    div[data-baseweb="input"] input {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }

    /* Radioknapper (24 mnd / 36 mnd velger) */
    div[role="radiogroup"] {
        background-color: #1e293b;
        padding: 4px;
        border-radius: 10px;
        border: 1px solid #334155;
    }

    div[role="radiogroup"] label {
        margin-right: 0px !important;
        padding: 6px 12px !important;
        border-radius: 8px !important;
    }

    div[data-testid="stMarkdownContainer"] p {
        color: #f8fafc !important;
        font-size: 14px !important;
    }

    /* Expander styling */
    .stExpander {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        margin-top: 15px !important;
        margin-bottom: 15px !important;
    }

    /* Resultat-kort */
    .result-box {
        background: linear-gradient(180deg, #0f172a 0%, #0b1329 100%);
        border: 1.5px solid #1d3557;
        border-radius: 16px;
        padding: 24px;
        margin-top: 20px;
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05), 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }

    .result-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        font-size: 15px;
    }

    .border-bottom-dash {
        border-bottom: 1px dashed #2a3a5e;
        margin: 14px 0;
    }

    /* Farger på tall og nøkkelverdier */
    .text-light { color: #94a3b8; font-weight: 500; }
    .text-white-bold { color: #ffffff; font-weight: 800; font-size: 20px; }
    .text-green-bold { color: #10b981; font-weight: 800; font-size: 20px; }
    .text-yellow-bold { color: #fbbf24; font-weight: 800; font-size: 20px; }

    /* Custom HTML Tidslinje Styling */
    .timeline-container {
        display: flex;
        width: 100%;
        height: 54px;
        border-radius: 10px;
        overflow: hidden;
        margin-top: 10px;
        background-color: #1e293b;
    }

    .timeline-bar-fase1 {
        background-color: #fbbf24;
        color: #0f172a;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-weight: 800;
        font-size: 13px;
        line-height: 1.15;
        white-space: nowrap;
        padding: 0 4px;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .timeline-bar-fase2 {
        background-color: #10b981;
        color: #0f172a;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-weight: 800;
        font-size: 13px;
        line-height: 1.15;
        white-space: nowrap;
        padding: 0 4px;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .timeline-subtext {
        font-size: 10px;
        font-weight: 600;
        opacity: 0.85;
    }

    /* Knappestyling */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        font-weight: 700;
        border: 1px solid #475569;
        padding: 6px 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        transition: all 0.2s;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
        border-color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISER DEFAULT-VERDIER I SESSION STATE ---
if "ny_tlf_pris" not in st.session_state:
    st.session_state["ny_tlf_pris"] = 15990
if "innbytteverdi" not in st.session_state:
    st.session_state["innbytteverdi"] = 0
if "innbyttebonus" not in st.session_state:
    st.session_state["innbyttebonus"] = 0
if "gammel_mnd_pris" not in st.session_state:
    st.session_state["gammel_mnd_pris"] = 0.0
if "gjenstaende_mnd" not in st.session_state:
    st.session_state["gjenstaende_mnd"] = 0
if "nedbetalingsmnd" not in st.session_state:
    st.session_state["nedbetalingsmnd"] = 24

# --- CALLBACK-FUNKSJONER FOR NULLSTILLING ---
def reset_felt(nokkel, verdi=0):
    st.session_state[nokkel] = verdi

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

# TOPPBAR (TITTEL + KNAPPER)
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

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# EXPANDER FOR TEKST-LIMING
with st.expander("▶ Har kunden gjenstående gammel Splitt? (Lim inn tekst)"):
    lim_inn_tekst = st.text_area("Lim inn tekst fra kundebildet:", height=90)
    
    if st.button("📋 Hent ut informasjonen fra teksten"):
        if lim_inn_tekst.strip():
            m_pris, i_verdi, m_igjen = parse_kopiert_tekst(lim_inn_tekst)
            if m_pris is not None:
                st.session_state["gammel_mnd_pris"] = float(m_pris)
            if i_verdi is not None:
                st.session_state["innbytteverdi"] = int(i_verdi)
            if m_igjen is not None:
                st.session_state["gjenstaende_mnd"] = int(m_igjen)
            st.rerun()

# INNDATAFELTER MED LINJERING OGSÅ PÅ TOPP-FELTET

# 1. NY MOBIL PRIS (KORRIGERT FORHOLD SLIK AT DET FLUKTER HERT MED DE TODELEDE FELTENE UNDER)
col_p1, col_p2 = st.columns([11, 1])
with col_p1:
    ny_tlf_pris = st.number_input(
        "1. NY MOBIL PRIS (KONTANT)", 
        min_value=0, 
        key="ny_tlf_pris", 
        step=500
    )
with col_p2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    st.button("🗑️", key="reset_ny_tlf", on_click=reset_felt, args=("ny_tlf_pris", 0))

# 2. INNBYTTEVERDI OG 3. INNBYTTEBONUS
col_in1, col_btn1, col_in2, col_btn2 = st.columns([5, 1, 5, 1])

with col_in1:
    innbytteverdi = st.number_input(
        "2. INNBYTTEVERDI", 
        min_value=0, 
        key="innbytteverdi", 
        step=100
    )
with col_btn1:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    st.button("🗑️", key="reset_innbytte", on_click=reset_felt, args=("innbytteverdi", 0))

with col_in2:
    innbyttebonus = st.number_input(
        "3. INNBYTTEBONUS", 
        min_value=0, 
        key="innbyttebonus", 
        step=100
    )
with col_btn2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    st.button("🗑️", key="reset_bonus", on_click=reset_felt, args=("innbyttebonus", 0))

# GAMMEL SPLITT
c_g1, c_gbtn1, c_g2, c_gbtn2 = st.columns([5, 1, 5, 1])
with c_g1:
    gammel_mnd_pris = st.number_input("Gammel månedspris (kr/md)", min_value=0.0, key="gammel_mnd_pris", step=10.0)
with c_gbtn1:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    st.button("🗑️", key="reset_gammel_pris", on_click=reset_felt, args=("gammel_mnd_pris", 0.0))

with c_g2:
    gjenstaende_mnd = st.number_input("Gjenstående måneder", min_value=0, key="gjenstaende_mnd", step=1)
with c_gbtn2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    st.button("🗑️", key="reset_gjenstaende", on_click=reset_felt, args=("gjenstaende_mnd", 0))


# --- BEREGNINGER ---
total_rabatt = st.session_state["innbytteverdi"] + st.session_state["innbyttebonus"]
effektiv_ny_totalpris = max(0.0, st.session_state["ny_tlf_pris"] - total_rabatt)
ny_mnd_pris_ren = effektiv_ny_totalpris / mnd_valg if mnd_valg > 0 else 0

mnd_fase_1 = min(st.session_state["gjenstaende_mnd"], mnd_valg)
mnd_fase_2 = max(0, mnd_valg - mnd_fase_1)

total_mnd_fase_1 = ny_mnd_pris_ren + st.session_state["gammel_mnd_pris"]
total_mnd_fase_2 = ny_mnd_pris_ren


# --- RESULTATKORT UTEN INNRYKK PÅ HTML ---

har_fase1 = st.session_state["gammel_mnd_pris"] > 0 and st.session_state["gjenstaende_mnd"] > 0 and mnd_fase_2 > 0

fase1_rad = ""
if har_fase1:
    fase1_rad = f"""<div class="result-row">
<span class="text-light">Totalpris i første periode (inkl gammel Splitt):</span>
<span class="text-yellow-bold">{total_mnd_fase_1:,.0f} kr/mnd (første {mnd_fase_1} mnd)</span>
</div>
<div class="result-row">
<span class="text-light">Pris i resterende periode:</span>
<span class="text-green-bold">{total_mnd_fase_2:,.0f} kr/mnd (deretter i {mnd_fase_2} mnd)</span>
</div>
<div class="border-bottom-dash"></div>"""

if har_fase1:
    p1 = (mnd_fase_1 / mnd_valg) * 100
    p2 = (mnd_fase_2 / mnd_valg) * 100
    
    # Sørg for at smale/korte perioder (f.eks. 1 mnd) har nok plass til teksten eller en ultrakompakt visning
    tekst_fase1 = f"<span>{total_mnd_fase_1:,.0f} kr/mnd</span><span class=\"timeline-subtext\">Første {mnd_fase_1} mnd</span>" if p1 >= 18 else f"<span>{total_mnd_fase_1:,.0f}kr</span><span class=\"timeline-subtext\">{mnd_fase_1}m</span>"
    tekst_fase2 = f"<span>{total_mnd_fase_2:,.0f} kr/mnd</span><span class=\"timeline-subtext\">Deretter {mnd_fase_2} mnd</span>" if p2 >= 18 else f"<span>{total_mnd_fase_2:,.0f}kr</span><span class=\"timeline-subtext\">{mnd_fase_2}m</span>"
    
    # Sätt min-width på minst 8% så teksten ikke skvises om det er f.eks. 1 mnd
    p1_vis = max(8.0, p1) if p2 > 8 else min(92.0, p1)
    p2_vis = 100.0 - p1_vis

    tidslinje_innhold = f"""<div class="timeline-container">
<div class="timeline-bar-fase1" style="width: {p1_vis}%;">
{tekst_fase1}
</div>
<div class="timeline-bar-fase2" style="width: {p2_vis}%;">
{tekst_fase2}
</div>
</div>"""
else:
    tidslinje_innhold = f"""<div class="timeline-container">
<div class="timeline-bar-fase2" style="width: 100%;">
<span>{ny_mnd_pris_ren:,.0f} kr/mnd</span>
<span class="timeline-subtext">Hele perioden ({mnd_valg} mnd)</span>
</div>
</div>"""

full_html = f"""<div class="result-box">
<div class="result-row">
<span class="text-light">Effektiv ny mobil-sum etter innbytte:</span>
<span class="text-white-bold">{effektiv_ny_totalpris:,.0f} kr</span>
</div>
<div class="result-row">
<span class="text-light">Ny mobil per mnd ({mnd_valg} mnd Splitt):</span>
<span class="text-green-bold">{ny_mnd_pris_ren:,.0f} kr/mnd</span>
</div>
<div class="border-bottom-dash"></div>
{fase1_rad}
<div style="margin-top: 6px; margin-bottom: 4px;">
<span class="text-light" style="font-size: 11px; font-weight: 700; letter-spacing: 1px;">VISUELL OVERSIKT OVER TIDSFORLØPET:</span>
</div>
{tidslinje_innhold}
</div>"""

st.markdown(full_html, unsafe_allow_html=True)

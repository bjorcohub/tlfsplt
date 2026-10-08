import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import pytesseract
import re

# Sideoppsett
st.set_page_config(page_title="Kalkulator for Nedbetaling & Innbytte", layout="wide")
st.title("📱 Kalkulator for Nedbetaling & Innbytte (Splitt/SWAP)")

# --- INITIALISER DEFAULT-VERDIER I SESSION STATE ---
if "gammel_mnd_pris" not in st.session_state:
    st.session_state["gammel_mnd_pris"] = 228.75
if "innbytteverdi" not in st.session_state:
    st.session_state["innbytteverdi"] = 4368.0
if "gjenstaende_mnd" not in st.session_state:
    st.session_state["gjenstaende_mnd"] = 11

# --- FUNKSJON FOR GRATIS OCR-UTLESING ---
def les_skjermbilde(bilde):
    img = Image.open(bilde)
    # Hent ut råtekst fra bildet
    tekst = pytesseract.image_to_string(img, lang="nor+eng")
    
    mnd_pris = None
    innbytte = None
    gjenstaende_belop = None
    
    # 1. Månedspris (f.eks. "228,75 /md." eller "228.75/md")
    mnd_match = re.search(r'(\d+[\.,]\d+)\s*/?\s*md', tekst, re.IGNORECASE)
    if mnd_match:
        mnd_pris = float(mnd_match.group(1).replace(',', '.'))

    # 2. Innbytteverdi (f.eks. "opptil 4368" eller "4368,- kr")
    innbytte_match = re.search(r'opptil\s*(\d+)', tekst, re.IGNORECASE)
    if not innbytte_match:
        innbytte_match = re.search(r'(\d+)\s*[\.,-]?\s*kr', tekst, re.IGNORECASE)
    if innbytte_match:
        innbytte = float(innbytte_match.group(1).replace('.', ''))

    # 3. Gjenstående beløp (f.eks. "Gjenstående beløp i Splitt-avtalen: 2516,25")
    gjen_match = re.search(r'Gjenstående[^\d]*(\d+[\.,]\d+|\d+)', tekst, re.IGNORECASE)
    if gjen_match:
        gjenstaende_belop = float(gjen_match.group(1).replace(',', '.'))

    # Beregn anslåtte gjenstående måneder basert på beløp / månedspris
    mnd_igjen = None
    if gjenstaende_belop and mnd_pris and mnd_pris > 0:
        mnd_igjen = round(gjenstaende_belop / mnd_pris)

    return mnd_pris, innbytte, mnd_igjen

# --- SIDEMENY: Inndata ---
st.sidebar.header("1. Ny Telefon")
ny_tlf_navn = st.sidebar.text_input("Navn på ny telefon", "Ny Smarttelefon")
ny_tlf_pris = st.sidebar.number_input("Totalpris på ny telefon (kr)", min_value=0, value=15000, step=500)
ny_nedbetaling_mnd = st.sidebar.selectbox("Nedbetalingstid ny telefon (mnd)", [24, 36], index=0)

st.sidebar.markdown("---")
st.sidebar.header("2. Eksisterende Avtale & Innbytte")

# Bilde-opplasting for OCR
uploaded_file = st.sidebar.file_uploader("Lim inn / Last opp skjermbilde", type=["png", "jpg", "jpeg"])

if uploaded_file:
    if st.sidebar.button("🔍 Les av skjermbilde (Gratis OCR)"):
        with st.spinner("Analyserer bilde..."):
            m_pris, i_verdi, m_igjen = les_skjermbilde(uploaded_file)
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
                st.sidebar.success("Tallene ble hentet ut!")
                st.rerun()  # Tvinger Streamlit til å laste inn feltene på nytt med de nye verdiene
            else:
                st.sidebar.warning("Fant ikke tallene automatisk. Sjekk bildet eller legg inn manuelt.")

# Felter koblet direkte til session_state via key
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
total_mnd_fase_1 = ny_mnd_pris_ren + gammel_mnd_pris
total_mnd_fase_2 = ny_mnd_pris_ren

# --- VISNING AV NØKKELTALL ---
col1, col2, col3 = st.columns(3)
col1.metric("Ny Månedspris (Selve telefonen)", f"{ny_mnd_pris_ren:.2f} kr/md")
col2.metric("Innbytterabatt", f"{innbytteverdi:,.0f} kr")
col3.metric("Effektiv pris på ny telefon", f"{effektiv_ny_totalpris:,.0f} kr")

st.markdown("---")

st.subheader("📊 Månedlig kostnadsoversikt for kunden")

if gammel_mnd_pris > 0 and gjenstaende_mnd > 0:
    st.info(f"""
    * **Periode 1 (Måned 1 – {mnd_fase_1}):** **{total_mnd_fase_1:.2f} kr/md** 
      *(Ny telefon: {ny_mnd_pris_ren:.2f} kr + Gammel avtale: {gammel_mnd_pris:.2f} kr)*
    * **Periode 2 (Måned {mnd_fase_1 + 1} – {ny_nedbetaling_mnd}):** **{total_mnd_fase_2:.2f} kr/md** 
      *(Når den gamle avtalen er ferdig nedbetalt)*
    """)
else:
    st.info(f"**Månedspris hele perioden (1 – {ny_nedbetaling_mnd} mnd):** **{ny_mnd_pris_ren:.2f} kr/md**")

# Lag datasett for graf
tidslinje_data = []
for mnd in range(1, ny_nedbetaling_mnd + 1):
    er_fase_1 = mnd <= gjenstaende_mnd
    gammel_del = gammel_mnd_pris if er_fase_1 else 0
    tidslinje_data.append({"Måned": f"Mnd {mnd}", "Del": "Ny Telefon", "Beløp": ny_mnd_pris_ren})
    if gammel_del > 0:
        tidslinje_data.append({"Måned": f"Mnd {mnd}", "Del": "Gammel Avtale", "Beløp": gammel_del})

df = pd.DataFrame(tidslinje_data)

# Stolpediagram
fig = px.bar(
    df, 
    x="Måned", 
    y="Beløp", 
    color="Del", 
    title="Månedlig Belastning Over Tid (kr)",
    labels={"Beløp": "Kroner per måned", "Måned": "Måned i ny avtale"},
    color_discrete_map={"Ny Telefon": "#0083B0", "Gammel Avtale": "#FF6B6B"}
)
fig.update_layout(barmode='stack', xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

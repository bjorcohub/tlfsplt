import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import base64
from openai import OpenAI

# Tittel og sideoppsett
st.set_page_config(page_title="Kalkulator for Telefonkjøp & Innbytte", layout="wide")
st.title("📱 Kalkulator for Nedbetaling & Innbytte (Splitt/SWAP)")

# API-nøkkel fra Streamlit Secrets eller brukermating for GPT-4 Vision OCR
openai_api_key = st.secrets.get("OPENAI_API_KEY", None)

# --- SIDEBAR: Inndata ---
st.sidebar.header("1. Ny Telefon")
ny_tlf_navn = st.sidebar.text_input("Navn på ny telefon", "Ny Smarttelefon")
ny_tlf_pris = st.sidebar.number_input("Totalpris på ny telefon (kr)", min_value=0, value=15000, step=500)
ny_nedbetaling_mnd = st.sidebar.selectbox("Nedbetalingstid ny telefon (mnd)", [24, 36], index=0)

st.sidebar.markdown("---")
st.sidebar.header("2. Eksisterende Avtale & Innbytte")

# Bilde-opplasting for automatisk utlesing
uploaded_file = st.sidebar.file_uploader("Lim inn / Last opp skjermbilde fra kundebildet", type=["png", "jpg", "jpeg"])

gammel_mnd_pris_default = 0.0
gjenstaende_mnd_default = 0
innbytteverdi_default = 0.0

if uploaded_file and openai_api_key:
    if st.sidebar.button("🤖 Les av skjermbilde automatisk"):
        with st.spinner("Analyserer skjermbilde..."):
            client = OpenAI(api_key=openai_api_key)
            base64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            
            prompt = """
            Analyser dette skjermbildet fra et kundebilde på telefonnedbetaling.
            Returner et gyldig JSON-objekt med følgende felter:
            - "mnd_pris": månedsprisen på eksisterende avtale (tall/float).
            - "innbytteverdi": innbytteverdi i kr (tall/float).
            - "gjenstaende_belop": gjenstående beløp i kroner (tall/float).
            - "mnd_igjen": anslått antall gjenstående måneder ut fra datoer eller gjenstående beløp/mnd_pris (heltall).
            Svar KUN med JSON uten markdown-formatering.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                max_tokens=300,
            )
            try:
                res_json = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", "").strip())
                gammel_mnd_pris_default = float(res_json.get("mnd_pris", 0.0))
                innbytteverdi_default = float(res_json.get("innbytteverdi", 0.0))
                gjenstaende_mnd_default = int(res_json.get("mnd_igjen", 0))
                st.sidebar.success("Bilde avlest!")
            except Exception as e:
                st.sidebar.error("Klarte ikke tolke bildet helt automatisk.")

# Manuelt justerbare felter
gammel_mnd_pris = st.sidebar.number_input("Gammel månedspris (kr/md)", min_value=0.0, value=gammel_mnd_pris_default, step=10.0)
gjenstaende_mnd = st.sidebar.number_input("Gjenstående måneder på gammel avtale", min_value=0, value=gjenstaende_mnd_default, step=1)
innbytteverdi = st.sidebar.number_input("Innbytteverdi (kr)", min_value=0.0, value=innbytteverdi_default, step=500.0)

# --- BEREGNINGER ---
effektiv_ny_totalpris = max(0.0, ny_tlf_pris - innbytteverdi)
ny_mnd_pris_ren = effektiv_ny_totalpris / ny_nedbetaling_mnd if ny_nedbetaling_mnd > 0 else 0

mnd_fase_1 = min(gjenstaende_mnd, ny_nedbetaling_mnd)
mnd_fase_2 = max(0, ny_nedbetaling_mnd - mnd_fase_1)

total_mnd_fase_1 = ny_mnd_pris_ren + gammel_mnd_pris
total_mnd_fase_2 = ny_mnd_pris_ren

# --- REPRESENTASJON & VISUALISERING ---
col1, col2, col3 = st.columns(3)
col1.metric("Ny Månedspris (Selve telefonen)", f"{ny_mnd_pris_ren:.2f} kr/md")
col2.metric("Innbytterabatt gitt", f"{innbytteverdi:,.0f} kr")
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

# Lag datasett for nedbetalingsgraf
tidslinje_data = []
for mnd in range(1, ny_nedbetaling_mnd + 1):
    er_fase_1 = mnd <= gjenstaende_mnd
    gammel_del = gammel_mnd_pris if er_fase_1 else 0
    tidslinje_data.append({"Måned": f"Mnd {mnd}", "Del": "Ny Telefon", "Beløp": ny_mnd_pris_ren})
    if gammel_del > 0:
        tidslinje_data.append({"Måned": f"Mnd {mnd}", "Del": "Gammel Avtale", "Beløp": gammel_del})

df = pd.DataFrame(tidslinje_data)

# Visualisering med stolpediagram
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

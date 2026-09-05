import streamlit as st
import pandas as pd
import datetime

# Impostazioni pagina
st.set_page_config(page_title="Gestione Spese", page_icon="💶", layout="wide")

st.title("Gestione Spese - Mirko e Selene")

# Menu laterale che riprende i fogli del tuo Excel
menu = [
    "🏠 Dashboard Riassuntiva", 
    "🛒 Spesa Quotidiana", 
    "⚡ Bollette Elettriche", 
    "🚗 Telepedaggio e Parcheggi", 
    "💳 Rate (Klarna + Cofidis)", 
    "🏦 Libretto Postale"
]
scelta = st.sidebar.radio("Sezioni", menu)

if scelta == "🏠 Dashboard Riassuntiva":
    st.header("Riepilogo Mensile")
    st.write("Qui potrai inserire i grafici per monitorare l'andamento delle uscite.")
    
    # Esempio di metriche fittizie
    col1, col2, col3 = st.columns(3)
    col1.metric("Totale Spesa (Mese)", "320 €", "-15 €")
    col2.metric("Bollette (Mese)", "110 €")
    col3.metric("Rate Attive", "150 €")

elif scelta == "🛒 Spesa Quotidiana":
    st.header("Registra una nuova Spesa")
    with st.form("form_spesa"):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data", datetime.date.today())
        importo = col2.number_input("Importo (€)", min_value=0.0, format="%.2f")
        
        dove = st.text_input("Negozio / Supermercato (es. Conad, Iperal)")
        # Riprende la suddivisione "Ricarica Posta/Buoni" vista nell'Excel
        metodo = st.selectbox("Metodo di pagamento", ["Ricarica Posta/Buoni", "Carta di Credito", "Contanti"])
        
        submit = st.form_submit_button("Aggiungi Spesa")
        if submit:
            # Qui andrà la logica per salvare il dato nel database
            st.success(f"Registrata spesa di {importo}€ presso {dove}.")

elif scelta == "🚗 Telepedaggio e Parcheggi":
    st.header("Tracciamento Pedaggi e Parcheggi")
    with st.form("form_auto"):
        data = st.date_input("Data transito/sosta", datetime.date.today())
        importo = st.number_input("Importo (€)", min_value=0.0, format="%.2f")
        tipo = st.selectbox("Tipologia", ["Pedaggio autostradale", "Parcheggio"])
        
        veicolo = st.text_input("Veicolo", value="Peugeot 2008 GT") 
        competenza = st.selectbox("Competenza", ["Mirko", "Mirko + Selene"])
        
        submit_auto = st.form_submit_button("Salva Spesa Auto")
        if submit_auto:
            st.success("Transazione registrata con successo!")

elif scelta == "💳 Rate (Klarna + Cofidis)":
    st.header("Gestione Pagamenti Dilazionati")
    st.write("Tieni traccia dei piani di ammortamento e dei pagamenti residui.")
    
    # Esempio di tabella visiva
    dati_rate = pd.DataFrame({
        "Servizio": ["Klarna", "Cofidis"],
        "Importo Totale (€)": [300, 800],
        "Rata Mensile (€)": [100, 50],
        "Rate Rimanenti": [2, 10]
    })
    st.dataframe(dati_rate, use_container_width=True)

elif scelta == "⚡ Bollette Elettriche":
    st.header("Bollette Elettriche")
    with st.form("form_bollette"):
        mese_riferimento = st.selectbox("Mese di riferimento", ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"])
        importo_bolletta = st.number_input("Importo (€)", min_value=0.0, format="%.2f")
        scadenza = st.date_input("Data Scadenza")
        pagato = st.checkbox("Segna come Pagata")
        
        if st.form_submit_button("Registra Bolletta"):
            st.success("Bolletta salvata!")

elif scelta == "🏦 Libretto Postale":
    st.header("Gestione Libretto Postale")
    st.info("Sezione dedicata ai versamenti e alla giacenza del libretto.")

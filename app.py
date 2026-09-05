import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Gestione Spese", page_icon="💶", layout="wide")
st.title("Gestione Spese - Mirko e Selene")

# --- 1. INIZIALIZZAZIONE DELLA MEMORIA (SESSION STATE) ---
# Creiamo dei dati di partenza solo se non esistono già nella sessione
if 'df_spese' not in st.session_state:
    st.session_state.df_spese = pd.DataFrame({
        "Data": [datetime.date(2026, 9, 1), datetime.date(2026, 9, 3)],
        "Tipo": ["Ricarica Postepay", "Spesa"],
        "Importo (€)": [500.00, 45.50],
        "Dettaglio/Negozio": ["Stipendio", "Conad"]
    })

if 'df_bollette' not in st.session_state:
    st.session_state.df_bollette = pd.DataFrame({
        "Mese Riferimento": ["Agosto", "Settembre"],
        "Fornitore": ["Enel", "Eni"],
        "Importo (€)": [65.20, 0.00],
        "Pagato": [True, False]
    })

if 'df_auto' not in st.session_state:
    st.session_state.df_auto = pd.DataFrame({
        "Data": [datetime.date(2026, 9, 2)],
        "Tipologia": ["Pedaggio"],
        "Veicolo": ["Peugeot 2008 GT"],
        "Competenza": ["Mirko + Selene"],
        "Importo (€)": [12.40]
    })

if 'df_rate' not in st.session_state:
    st.session_state.df_rate = pd.DataFrame({
        "Servizio": ["Klarna", "Cofidis"],
        "Importo Totale (€)": [300.00, 800.00],
        "Rata Mensile (€)": [100.00, 50.00],
        "Rate Rimanenti": [2, 10]
    })

if 'df_libretto' not in st.session_state:
    st.session_state.df_libretto = pd.DataFrame({
        "Data": [datetime.date(2026, 9, 1)],
        "Operazione": ["Versamento"],
        "Importo (€)": [150.00]
    })


# --- 2. MENU LATERALE ---
menu = [
    "🏠 Dashboard", 
    "🛒 Spesa e Ricariche", 
    "⚡ Bollette Elettriche", 
    "🚗 Telepedaggio e Parcheggi", 
    "💳 Rate (Klarna + Cofidis)", 
    "🏦 Libretto Postale"
]
scelta = st.sidebar.radio("Navigazione", menu)


# --- 3. SEZIONI DELL'APP (CON DATA EDITOR) ---

if scelta == "🏠 Dashboard":
    st.header("Dashboard Riassuntiva")
    st.info("Qui i grafici si aggiorneranno in base ai dati modificati nelle altre sezioni.")
    
    # Calcoli dinamici basati sul DataFrame modificabile
    totale_uscite = st.session_state.df_spese[st.session_state.df_spese["Tipo"] == "Spesa"]["Importo (€)"].sum()
    totale_entrate = st.session_state.df_spese[st.session_state.df_spese["Tipo"].str.contains("Ricarica|Buoni")]["Importo (€)"].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Totale Entrate", f"{totale_entrate:.2f} €")
    col2.metric("Totale Uscite", f"{totale_uscite:.2f} €")
    col3.metric("Bilancio", f"{totale_entrate - totale_uscite:.2f} €")

elif scelta == "🛒 Spesa e Ricariche":
    st.header("Spesa Quotidiana e Ricariche")
    st.write("Fai doppio clic su una cella per modificarla. Usa la colonna all'estrema sinistra per selezionare ed eliminare le righe o clicca in basso per aggiungerne di nuove.")
    
    # st.data_editor sostituisce st.dataframe e permette le modifiche
    st.session_state.df_spese = st.data_editor(
        st.session_state.df_spese,
        num_rows="dynamic", # Permette di aggiungere/eliminare righe
        use_container_width=True,
        key="editor_spese"
    )

elif scelta == "⚡ Bollette Elettriche":
    st.header("Gestione Bollette")
    st.write("Modifica gli importi o spunta la casella 'Pagato'.")
    
    st.session_state.df_bollette = st.data_editor(
        st.session_state.df_bollette,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_bollette"
    )

elif scelta == "🚗 Telepedaggio e Parcheggi":
    st.header("Tracciamento Pedaggi e Parcheggi")
    
    st.session_state.df_auto = st.data_editor(
        st.session_state.df_auto,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_auto"
    )

elif scelta == "💳 Rate (Klarna + Cofidis)":
    st.header("Piani di Ammortamento")
    st.write("Aggiorna le rate rimanenti mano a mano che vengono scalate.")
    
    st.session_state.df_rate = st.data_editor(
        st.session_state.df_rate,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_rate"
    )

elif scelta == "🏦 Libretto Postale":
    st.header("Movimenti Libretto Postale")
    
    st.session_state.df_libretto = st.data_editor(
        st.session_state.df_libretto,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_libretto"
    )

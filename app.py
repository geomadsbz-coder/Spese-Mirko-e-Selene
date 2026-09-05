import streamlit as st
import pandas as pd
import datetime

# Impostazioni pagina (più larga per far respirare i grafici)
st.set_page_config(page_title="Gestione Spese", page_icon="💶", layout="wide")

st.title("Gestione Spese - Mirko e Selene")

# --- 1. DATI SIMULATI PER MOSTRARE LO STORICO ---
# (Questi verranno sostituiti dal vero database quando lo collegheremo)
@st.cache_data
def carica_dati_storici():
    dati = {
        "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set"],
        "Ricarica Posta/Buoni (€)": [500, 450, 480, 520, 500, 490, 550, 510, 530],
        "Spese (€)": [420, 380, 490, 410, 390, 450, 600, 420, 350]
    }
    df = pd.DataFrame(dati)
    df["Bilancio"] = df["Ricarica Posta/Buoni (€)"] - df["Spese (€)"]
    return df

df_storico = carica_dati_storici()

# --- 2. MENU LATERALE ---
menu = [
    "🏠 Dashboard e Grafici", 
    "🛒 Spesa e Ricariche", 
    "⚡ Bollette Elettriche", 
    "🚗 Telepedaggio e Parcheggi", 
    "💳 Rate (Klarna + Cofidis)", 
    "🏦 Libretto Postale"
]
scelta = st.sidebar.radio("Navigazione", menu)

# --- 3. SEZIONE DASHBOARD E GRAFICI ---
if scelta == "🏠 Dashboard e Grafici":
    st.header("Dashboard Interattiva")
    
    # Selettore interattivo per scegliere il mese da analizzare
    mese_selezionato = st.selectbox("Seleziona il mese da analizzare", df_storico["Mese"].tolist(), index=8)
    
    # Estrae i dati del mese selezionato
    dati_mese = df_storico[df_storico["Mese"] == mese_selezionato].iloc[0]
    
    # Metriche riassuntive
    col1, col2, col3 = st.columns(3)
    col1.metric("Entrate / Buoni", f"{dati_mese['Ricarica Posta/Buoni (€)']} €")
    col2.metric("Uscite / Spesa", f"{dati_mese['Spese (€)']} €")
    
    bilancio = dati_mese['Bilancio']
    col3.metric("Risparmio del mese", f"{bilancio} €", 
                delta="In attivo" if bilancio >= 0 else "In passivo", 
                delta_color="normal" if bilancio >= 0 else "inverse")

    st.divider()

    # Grafico interattivo a barre
    st.subheader("Andamento Storico: Entrate vs Uscite")
    # Prepariamo i dati per il grafico in modo che mostri due barre affiancate
    df_grafico = df_storico.set_index("Mese")[["Ricarica Posta/Buoni (€)", "Spese (€)"]]
    # Usa un grafico nativo (puoi passarci sopra con il mouse per vedere i valori esatti)
    st.bar_chart(df_grafico, color=["#2e7b32", "#d32f2f"]) # Verde per entrate, rosso per uscite


# --- 4. SEZIONE SPESA E RICARICHE (CON TABS E TABELLA) ---
elif scelta == "🛒 Spesa e Ricariche":
    st.header("Gestione Quotidiana")
    
    # Creiamo due schede (Tabs) per separare entrate e uscite senza fare confusione
    tab1, tab2 = st.tabs(["📉 Registra Spesa", "📈 Registra Ricarica/Buoni"])
    
    with tab1:
        with st.form("form_spesa"):
            col1, col2 = st.columns(2)
            data_spesa = col1.date_input("Data della spesa", datetime.date.today())
            importo_spesa = col2.number_input("Importo (€)", min_value=0.0, format="%.2f")
            
            dove = st.text_input("Negozio / Supermercato (es. Conad, Iperal, ecc.)")
            
            submit_spesa = st.form_submit_button("Aggiungi Spesa", type="primary")
            if submit_spesa:
                st.success(f"Spesa di {importo_spesa}€ registrata in data {data_spesa}.")

    with tab2:
        with st.form("form_ricarica"):
            col1, col2 = st.columns(2)
            data_ric = col1.date_input("Data Accredito", datetime.date.today())
            importo_ric = col2.number_input("Importo Ricarica/Buoni (€)", min_value=0.0, format="%.2f")
            
            origine = st.selectbox("Tipologia", ["Ricarica Postepay", "Buoni Pasto", "Altro"])
            
            submit_ric = st.form_submit_button("Aggiungi Entrata", type="primary")
            if submit_ric:
                st.success(f"Entrata di {importo_ric}€ ({origine}) registrata con successo.")
                
    st.divider()
    
    # Tabella dello storico (è interattiva: si può ordinare cliccando sulle colonne)
    st.subheader("Storico Mensile")
    st.dataframe(df_storico, use_container_width=True, hide_index=True)


# --- 5. ALTRE SEZIONI ---
elif scelta == "⚡ Bollette Elettriche":
    st.header("Bollette Elettriche")
    st.info("Qui potremo inserire un grafico dedicato solo ai consumi elettrici.")

elif scelta == "🚗 Telepedaggio e Parcheggi":
    st.header("Telepedaggio e Parcheggi")
    st.info("Qui terremo traccia dei passaggi autostradali e dei parcheggi.")

elif scelta == "💳 Rate (Klarna + Cofidis)":
    st.header("Rate (Klarna + Cofidis)")
    st.info("Monitoraggio del piano di rientro delle rate attive.")

elif scelta == "🏦 Libretto Postale":
    st.header("Libretto Postale")
    st.info("Registro dei versamenti e giacenza totale.")

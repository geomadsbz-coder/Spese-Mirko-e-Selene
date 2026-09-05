import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Gestione Spese", page_icon="💶", layout="wide")
st.title("Gestione Spese - Mirko e Selene")

# --- FUNZIONE PER LEGGERE IL TUO EXCEL E TRADURLO ---
@st.cache_data
def carica_dati_da_excel():
    try:
        file_path = "Spese Mirko e Selene.xlsx"
        xls = pd.ExcelFile(file_path)
        
        # 1. ESTREZIONE FOGLIO "SPESA"
        df_spesa = pd.read_excel(xls, sheet_name="Spesa", header=None)
        spese_list = []
        
        # Il tuo Excel ha 12 mesi affiancati (6 colonne per ogni mese = 72 colonne totali)
        for i in range(0, 72, 6):
            chunk = df_spesa.iloc[4:, i:i+6].copy() # I dati iniziano dalla riga 4 in poi
            chunk.columns = ["Label", "LabelVal", "Entrata", "Uscita", "Data", "Dove"]
            chunk = chunk.dropna(subset=["Data"]) # Prende solo le righe dove c'è una data compilata
            
            for _, row in chunk.iterrows():
                date_val = row["Data"]
                entrata = row["Entrata"]
                uscita = row["Uscita"]
                dove = row["Dove"]
                
                # Se la cella è una data valida
                if pd.notna(date_val) and isinstance(date_val, datetime.datetime):
                    # Se c'è un'entrata nella colonna "Ricarica Posta/Buoni"
                    if pd.notna(entrata) and float(entrata) > 0:
                        spese_list.append({
                            "Data": date_val.date(),
                            "Tipo": "Ricarica/Buoni",
                            "Importo (€)": float(entrata),
                            "Dettaglio/Negozio": dove if pd.notna(dove) else ""
                        })
                    # Se c'è un'uscita nella colonna "Spesa"
                    if pd.notna(uscita) and float(uscita) > 0:
                        spese_list.append({
                            "Data": date_val.date(),
                            "Tipo": "Spesa",
                            "Importo (€)": float(uscita),
                            "Dettaglio/Negozio": dove if pd.notna(dove) else ""
                        })
        
        df_spese_estratte = pd.DataFrame(spese_list).sort_values(by="Data").reset_index(drop=True)
        
        # 2. ESTRAZIONE FOGLIO "BOLLETTE ELETTRICHE"
        df_bollette_excel = pd.read_excel(xls, sheet_name="Bollette elettriche", header=None)
        bollette_list = []
        
        # Nelle bollette, i dati veri e propri iniziano alla riga 6
        for _, row in df_bollette_excel.iloc[6:].iterrows():
            num_doc = row[0]
            distr = row[1]
            importo = row[3]
            consumo = row[4]
            costo_kw = row[5]
            
            if pd.notna(num_doc) and pd.notna(distr):
                bollette_list.append({
                    "Numero Documento": str(num_doc),
                    "Distributore": distr,
                    "Importo (€)": float(importo) if pd.notna(importo) else 0.0,
                    "Consumo (KW)": float(consumo) if pd.notna(consumo) else 0.0,
                    "Costo al KW (€)": round(float(costo_kw), 4) if pd.notna(costo_kw) else 0.0,
                    "Pagato": True # Impostato come pagato di default per lo storico
                })
        
        df_bollette_estratte = pd.DataFrame(bollette_list)
        return df_spese_estratte, df_bollette_estratte

    except Exception as e:
        # Se c'è un errore (es. file non trovato), crea tabelle vuote con la giusta struttura
        st.error("Sto aspettando che carichi il file 'Spese Mirko e Selene.xlsx' su GitHub...")
        return pd.DataFrame(columns=["Data", "Tipo", "Importo (€)", "Dettaglio/Negozio"]), pd.DataFrame(columns=["Numero Documento", "Distributore", "Importo (€)", "Consumo (KW)", "Costo al KW (€)", "Pagato"])

# --- INIZIALIZZAZIONE MEMORIA (CARICAMENTO UNA TANTUM) ---
df_spese_iniziali, df_bollette_iniziali = carica_dati_da_excel()

if 'df_spese' not in st.session_state or st.session_state.df_spese.empty:
    st.session_state.df_spese = df_spese_iniziali

if 'df_bollette' not in st.session_state or st.session_state.df_bollette.empty:
    st.session_state.df_bollette = df_bollette_iniziali

# --- MENU LATERALE ---
menu = ["🏠 Dashboard", "🛒 Spesa e Ricariche", "⚡ Bollette Elettriche"]
scelta = st.sidebar.radio("Navigazione", menu)

# --- SEZIONI ---
if scelta == "🏠 Dashboard":
    st.header("Dashboard Riassuntiva")
    st.info("I dati che vedi sono stati estratti automaticamente dal tuo file Excel!")
    
    if not st.session_state.df_spese.empty:
        totale_uscite = st.session_state.df_spese[st.session_state.df_spese["Tipo"] == "Spesa"]["Importo (€)"].sum()
        totale_entrate = st.session_state.df_spese[st.session_state.df_spese["Tipo"] == "Ricarica/Buoni"]["Importo (€)"].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Totale Entrate", f"{totale_entrate:.2f} €")
        col2.metric("Totale Uscite", f"{totale_uscite:.2f} €")
        
        bilancio = totale_entrate - totale_uscite
        col3.metric("Bilancio Attuale", f"{bilancio:.2f} €", delta=f"{bilancio:.2f} €", delta_color="normal" if bilancio >= 0 else "inverse")

elif scelta == "🛒 Spesa e Ricariche":
    st.header("Spesa Quotidiana e Ricariche")
    st.write("Fai doppio clic sulle celle per correggere gli importi o i negozi (es. Iperpoli, Conad).")
    
    st.session_state.df_spese = st.data_editor(
        st.session_state.df_spese,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_spese"
    )

elif scelta == "⚡ Bollette Elettriche":
    st.header("Gestione Bollette (Enel/Engie)")
    st.write("Ecco i dati estratti dal tuo foglio Excel. Doppio clic per modificare.")
    
    st.session_state.df_bollette = st.data_editor(
        st.session_state.df_bollette,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_bollette"
    )

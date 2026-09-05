import streamlit as st
import pandas as pd
import datetime

# Impostazioni della pagina
st.set_page_config(page_title="Gestione Spese", page_icon="💶", layout="wide")
st.title("Gestione Spese - Mirko e Selene")

# --- FUNZIONE POTENZIATA PER LEGGERE TUTTI I FOGLI DELL'EXCEL ---
@st.cache_data
def carica_tutti_i_dati():
    file_path = "Spese Mirko e Selene.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
    except Exception as e:
        st.error(f"Errore di lettura! Assicurati di aver caricato il file Excel correttamente e di avere 'openpyxl' in requirements.txt. Dettaglio: {e}")
        return None, None, None, None, None

    # 1. SPESA (Estrazione Mese per Mese)
    df_spesa_excel = pd.read_excel(xls, sheet_name="Spesa", header=None)
    spese_list = []
    for i in range(0, 72, 6):
        chunk = df_spesa_excel.iloc[4:, i:i+6].copy()
        chunk.columns = ["Label", "LabelVal", "Entrata", "Uscita", "Data", "Dove"]
        chunk = chunk.dropna(subset=["Data"])
        for _, row in chunk.iterrows():
            date_val, entrata, uscita, dove = row["Data"], row["Entrata"], row["Uscita"], row["Dove"]
            if pd.notna(date_val) and isinstance(date_val, datetime.datetime):
                if pd.notna(entrata) and float(entrata) > 0:
                    spese_list.append({"Data": date_val.date(), "Tipo": "Ricarica/Buoni", "Importo (€)": float(entrata), "Dettaglio/Negozio": dove if pd.notna(dove) else ""})
                if pd.notna(uscita) and float(uscita) > 0:
                    spese_list.append({"Data": date_val.date(), "Tipo": "Spesa", "Importo (€)": float(uscita), "Dettaglio/Negozio": dove if pd.notna(dove) else ""})
    df_spese = pd.DataFrame(spese_list).sort_values(by="Data").reset_index(drop=True)

    # 2. BOLLETTE ELETTRICHE
    df_bollette_excel = pd.read_excel(xls, sheet_name="Bollette elettriche", header=None)
    bollette_list = []
    for _, row in df_bollette_excel.iloc[6:].iterrows():
        if pd.notna(row[0]) and pd.notna(row[1]):
            bollette_list.append({
                "Numero Documento": str(row[0]), "Distributore": row[1], 
                "Importo (€)": float(row[3]) if pd.notna(row[3]) else 0.0, 
                "Consumo (KW)": float(row[4]) if pd.notna(row[4]) else 0.0, 
                "Costo al KW (€)": round(float(row[5]), 4) if pd.notna(row[5]) else 0.0, 
                "Pagato": True
            })
    df_bollette = pd.DataFrame(bollette_list)

    # 3. TELEPEDAGGIO
    df_tele_excel = pd.read_excel(xls, sheet_name="Telepedaggio", header=None)
    tele_list = []
    for _, row in df_tele_excel.iloc[3:15].iterrows(): # Dati da Gennaio a Dicembre
        mese = row[1]
        if pd.notna(mese):
            tele_list.append({
                "Mese": mese, "Importo Totale (€)": float(row[2]) if pd.notna(row[2]) else 0.0, 
                "Quota Mirko (€)": float(row[3]) if pd.notna(row[3]) else 0.0, 
                "Quota Condivisa (€)": float(row[4]) if pd.notna(row[4]) else 0.0, 
                "Parcheggi (€)": float(row[5]) if pd.notna(row[5]) else 0.0
            })
    df_tele = pd.DataFrame(tele_list)

    # 4. LIBRETTO POSTALE
    df_lib_excel = pd.read_excel(xls, sheet_name="Libretto Postale", header=None)
    lib_list = []
    for _, row in df_lib_excel.iloc[5:17].iterrows():
        data_val = row[0]
        if pd.notna(data_val) and isinstance(data_val, datetime.datetime):
            lib_list.append({
                "Data": data_val.date(), 
                "Versamento Mirko (€)": float(row[1]) if pd.notna(row[1]) else 0.0, 
                "Versamento Selene (€)": float(row[2]) if pd.notna(row[2]) else 0.0
            })
    df_lib = pd.DataFrame(lib_list)

    # 5. RATE (KLARNA + COFIDIS)
    df_rate_excel = pd.read_excel(xls, sheet_name="Klarna + Cofidis", header=None)
    rate_list = []
    for _, row in df_rate_excel.iloc[6:15].iterrows():
        prodotto = row[0]
        if pd.notna(prodotto) and isinstance(prodotto, str) and prodotto.strip() != "":
            rate_list.append({
                "Prodotto/Servizio": prodotto, 
                "Importo Totale (€)": float(row[1]) if pd.notna(row[1]) else 0.0, 
                "Rata Mensile (€)": float(row[2]) if pd.notna(row[2]) else 0.0
            })
    df_rate = pd.DataFrame(rate_list)

    return df_spese, df_bollette, df_tele, df_lib, df_rate

# --- CARICAMENTO E SALVATAGGIO IN MEMORIA ---
dfs = carica_tutti_i_dati()

# Salviamo i dati nella sessione, in modo da poterli editare senza perderli navigando tra le pagine
if dfs[0] is not None:
    if 'df_spese' not in st.session_state: st.session_state.df_spese = dfs[0]
    if 'df_bollette' not in st.session_state: st.session_state.df_bollette = dfs[1]
    if 'df_tele' not in st.session_state: st.session_state.df_tele = dfs[2]
    if 'df_lib' not in st.session_state: st.session_state.df_lib = dfs[3]
    if 'df_rate' not in st.session_state: st.session_state.df_rate = dfs[4]

# --- MENU LATERALE ---
menu = [
    "📊 Output Mensile & Grafici", 
    "🛒 Modifica Spese e Ricariche", 
    "⚡ Modifica Bollette", 
    "🚗 Modifica Telepedaggio", 
    "🏦 Modifica Libretto", 
    "💳 Modifica Rate (Klarna)"
]
scelta = st.sidebar.radio("Scegli la Sezione", menu)


# --- DASHBOARD GRAFICA ---
if scelta == "📊 Output Mensile & Grafici":
    st.header("Analisi Grafica Mensile")
    
    if 'df_spese' in st.session_state and not st.session_state.df_spese.empty:
        # Prepariamo i dati per raggrupparli per mese
        df = st.session_state.df_spese.copy()
        
        # Converte le date in "Anno-Mese" (es. 2026-01) per il grafico
        df['Mese'] = pd.to_datetime(df['Data']).dt.to_period('M').astype(str)
        
        # Somma Entrate e Uscite per ogni mese
        df_mensile = df.groupby(['Mese', 'Tipo'])['Importo (€)'].sum().unstack(fill_value=0)
        
        # Assicuriamoci che esistano le colonne
        if 'Ricarica/Buoni' not in df_mensile.columns: df_mensile['Ricarica/Buoni'] = 0
        if 'Spesa' not in df_mensile.columns: df_mensile['Spesa'] = 0
        
        # 1. GRAFICO A BARRE INTERATTIVO
        st.subheader("Andamento: Ricariche vs Spese")
        st.write("Passa il mouse sulle barre per vedere l'importo esatto del mese.")
        st.bar_chart(df_mensile)
        
        # 2. TABELLA RIASSUNTIVA CON IL BILANCIO
        st.subheader("Riepilogo Tabellare e Risparmio Netto")
        df_mensile["Risparmio/Bilancio (€)"] = df_mensile['Ricarica/Buoni'] - df_mensile['Spesa']
        
        # Mostra la tabella formattata bene
        st.dataframe(df_mensile.style.format("{:.2f} €"), use_container_width=True)
    else:
        st.warning("Non ci sono dati sufficienti per generare il grafico.")


# --- SEZIONI DI EDITING ---
elif scelta == "🛒 Modifica Spese e Ricariche":
    st.header("Spese Quotidiane e Ricariche")
    st.write("Fai **doppio clic** per modificare date, importi e negozi. Clicca la riga vuota in fondo per aggiungere.")
    st.session_state.df_spese = st.data_editor(st.session_state.df_spese, num_rows="dynamic", use_container_width=True, key="editor_sp")

elif scelta == "⚡ Modifica Bollette":
    st.header("Bollette Elettriche")
    st.session_state.df_bollette = st.data_editor(st.session_state.df_bollette, num_rows="dynamic", use_container_width=True, key="editor_bol")

elif scelta == "🚗 Modifica Telepedaggio":
    st.header("Telepedaggio e Parcheggi")
    st.session_state.df_tele = st.data_editor(st.session_state.df_tele, num_rows="dynamic", use_container_width=True, key="editor_tel")

elif scelta == "🏦 Modifica Libretto":
    st.header("Libretto Postale")
    st.session_state.df_lib = st.data_editor(st.session_state.df_lib, num_rows="dynamic", use_container_width=True, key="editor_lib")

elif scelta == "💳 Modifica Rate (Klarna)":
    st.header("Rate: Klarna + Cofidis")
    st.session_state.df_rate = st.data_editor(st.session_state.df_rate, num_rows="dynamic", use_container_width=True, key="editor_rat")

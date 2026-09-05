import streamlit as st
import pandas as pd
import datetime

# Impostazioni della pagina
st.set_page_config(page_title="Gestione Spese", page_icon="💶", layout="wide")
st.title("Gestione Spese - Mirko e Selene")

# Funzione di utilità per pulire i numeri
def clean_float(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val_clean = val.replace("€", "").replace(" ", "").replace(",", ".")
        try:
            return float(val_clean)
        except ValueError:
            return 0.0
    return 0.0

# --- CARICAMENTO DI TUTTI I FOGLI DALL'EXCEL ---
@st.cache_data
def carica_tutti_i_dati():
    file_path = "Spese Mirko e Selene.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
    except Exception as e:
        return None, None, None, None, None, None

    # 0. FOGLIO "SPESE" (Fisse mensili puntuali)
    df_spese_fisse_excel = pd.read_excel(xls, sheet_name="Spese", header=None)
    fisse_list = [
        {"Voce di Spesa Fissa": "Affitto", "Importo Totale (€)": 720.0, "Quota Mirko (€)": 360.0, "Quota Selene (€)": 360.0},
        {"Voce di Spesa Fissa": "Spese Condominiali", "Importo Totale (€)": 80.0, "Quota Mirko (€)": 40.0, "Quota Selene (€)": 40.0},
        {"Voce di Spesa Fissa": "Rifiuti", "Importo Totale (€)": 8.33, "Quota Mirko (€)": 4.165, "Quota Selene (€)": 4.165},
        {"Voce di Spesa Fissa": "Bollette Elettriche", "Importo Totale (€)": 64.33, "Quota Mirko (€)": 32.165, "Quota Selene (€)": 32.165},
        {"Voce di Spesa Fissa": "WiFi", "Importo Totale (€)": 33.95, "Quota Mirko (€)": 16.975, "Quota Selene (€)": 16.975},
        {"Voce di Spesa Fissa": "Mobili (Uscita conto Selene)", "Importo Totale (€)": 108.0, "Quota Mirko (€)": -54.0, "Quota Selene (€)": 54.0}
    ]
    df_fisse = pd.DataFrame(fisse_list)

    # 1. SPESA (Quotidiana / Ricariche)
    df_spesa_excel = pd.read_excel(xls, sheet_name="Spesa", header=None)
    spese_list = []
    for i in range(0, 72, 6):
        chunk = df_spesa_excel.iloc[4:, i:i+6].copy()
        chunk.columns = ["Label", "LabelVal", "Entrata", "Uscita", "Data", "Dove"]
        chunk = chunk.dropna(subset=["Data"])
        for _, row in chunk.iterrows():
            date_val, entrata, uscita, dove = row["Data"], row["Entrata"], row["Uscita"], row["Dove"]
            if pd.notna(date_val) and isinstance(date_val, datetime.datetime):
                val_entrata = clean_float(entrata)
                val_uscita = clean_float(uscita)
                if val_entrata > 0:
                    spese_list.append({"Data": date_val.date(), "Tipo": "Ricarica/Buoni", "Importo (€)": val_entrata, "Dettaglio/Negozio": str(dove) if pd.notna(dove) else ""})
                if val_uscita > 0:
                    spese_list.append({"Data": date_val.date(), "Tipo": "Spesa", "Importo (€)": val_uscita, "Dettaglio/Negozio": str(dove) if pd.notna(dove) else ""})
    df_spese = pd.DataFrame(spese_list).sort_values(by="Data").reset_index(drop=True) if spese_list else pd.DataFrame(columns=["Data", "Tipo", "Importo (€)", "Dettaglio/Negozio"])

    # 2. BOLLETTE ELETTRICHE
    df_bollette_excel = pd.read_excel(xls, sheet_name="Bollette elettriche", header=None)
    bollette_list = []
    for _, row in df_bollette_excel.iloc[6:].iterrows():
        if pd.notna(row[0]) and pd.notna(row[1]):
            bollette_list.append({
                "Numero Documento": str(row[0]), "Distributore": str(row[1]), 
                "Importo (€)": clean_float(row[3]), 
                "Consumo (KW)": clean_float(row[4]), 
                "Costo al KW (€)": round(clean_float(row[5]), 4), 
                "Pagato": True
            })
    df_bollette = pd.DataFrame(bollette_list) if bollette_list else pd.DataFrame(columns=["Numero Documento", "Distributore", "Importo (€)", "Consumo (KW)", "Costo al KW (€)", "Pagato"])

    # 3. TELEPEDAGGIO (Estraiamo la quota di Settembre - colonna indice 4 o riga Settembre)
    df_tele_excel = pd.read_excel(xls, sheet_name="Telepedaggio", header=None)
    tele_sept_quota = 0.0
    for _, row in df_tele_excel.iloc[3:15].iterrows():
        if pd.notna(row[1]) and str(row[1]).strip().lower() == "settembre":
            # Colonna 4 è "Mirko+Selene" (quota condivisa)
            val_condivisa = clean_float(row[4])
            tele_sept_quota = val_condivisa / 2.0 # Diviso equamente
            break

    # 4. LIBRETTO POSTALE
    df_lib_excel = pd.read_excel(xls, sheet_name="Libretto Postale", header=None)
    lib_list = []
    for _, row in df_lib_excel.iloc[5:17].iterrows():
        data_val = row[0]
        if pd.notna(data_val) and isinstance(data_val, datetime.datetime):
            lib_list.append({
                "Data": data_val.date(), 
                "Versamento Mirko (€)": clean_float(row[1]), 
                "Versamento Selene (€)": clean_float(row[2])
            })
    df_lib = pd.DataFrame(lib_list) if lib_list else pd.DataFrame(columns=["Data", "Versamento Mirko (€)", "Versamento Selene (€)"])

    # 5. RATE (KLARNA + COFIDIS) - Estraiamo solo le quote di Settembre (Colonna 14 per Mirko, 15 per Selene)
    df_rate_excel = pd.read_excel(xls, sheet_name="Klarna + Cofidis", header=None)
    rate_sept_mirko = 0.0
    rate_sept_selene = 0.0
    for _, row in df_rate_excel.iloc[5:].iterrows():
        prodotto = row[0]
        if pd.notna(prodotto) and isinstance(prodotto, str):
            p_str = prodotto.strip()
            if p_str and p_str not in ["Importo", "Rata", "Pagamenti Mirko+Selene", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"] and not p_str.startswith("KLARNA") and not p_str.startswith("COFIDIS"):
                m_sept = clean_float(row[14]) # Mirko quota settembre
                s_sept = clean_float(row[15]) # Selene quota settembre
                rate_sept_mirko += m_sept
                rate_sept_selene += s_sept

    df_rate = pd.DataFrame(columns=["Prodotto/Servizio", "Importo Totale (€)", "Rata Mensile (€)"]) # Tabella generale rate per editing

    return df_fisse, df_spese, df_bollette, df_lib, df_rate, tele_sept_quota, rate_sept_mirko, rate_sept_selene

# --- MEMORIZZAZIONE SESSIONE ---
dfs = carica_tutti_i_dati()
if dfs[0] is not None:
    if 'df_fisse' not in st.session_state: st.session_state.df_fisse = dfs[0]
    if 'df_spese' not in st.session_state: st.session_state.df_spese = dfs[1]
    if 'df_bollette' not in st.session_state: st.session_state.df_bollette = dfs[2]
    if 'df_lib' not in st.session_state: st.session_state.df_lib = dfs[3]
    if 'df_rate' not in st.session_state: st.session_state.df_rate = dfs[4]
    
    # Valori di settembre calcolati dall'Excel
    tele_sept_quota = dfs[5]
    rate_sept_mirko = dfs[6]
    rate_sept_selene = dfs[7]

# --- MENU LATERALE ---
menu = [
    "🏠 Spese Fisse & Conguaglio",
    "📊 Output Mensile & Grafici", 
    "🛒 Modifica Spese e Ricariche", 
    "⚡ Modifica Bollette", 
    "🚗 Modifica Telepedaggio", 
    "🏦 Modifica Libretto", 
    "💳 Modifica Rate (Klarna)"
]
scelta = st.sidebar.radio("Scegli la Sezione", menu)

# --- SEZIONE SPESE FISSE E CONGUAGLIO ---
if scelta == "🏠 Spese Fisse & Conguaglio":
    st.header("Gestione Spese Fisse & Conguaglio Settembre")
    st.write("Riepilogo delle spese fisse mensili, conguaglio mobili e quote di competenza per il mese di settembre.")
    
    st.subheader("Tabella Spese Fisse e Mobili")
    st.session_state.df_fisse = st.data_editor(
        st.session_state.df_fisse,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_fisse"
    )
    
    # 1. Calcolo dalle spese fisse tabellari
    # Sommiamo le quote di Selene meno eventuali conguagli a favore di Mirko
    totale_fisse_selene = st.session_state.df_fisse["Quota Selene (€)"].sum()
    
    # 2. Rate Klarna / Cofidis (Solo Settembre)
    # Se Mirko ha anticipato la quota di Selene o viceversa
    # In genere la quota di Selene a settembre rappresenta ciò che lei deve versare per le rate di settembre
    netto_rate_settembre = rate_sept_selene - rate_sept_mirko
    
    # 3. Telepedaggio Settembre (Quota condivisa divisa 2)
    netto_tele_settembre = tele_sept_quota

    # Totale complessivo dovuto da Selene a Mirko per settembre
    totale_da_versare_selene = totale_fisse_selene + netto_rate_settembre + netto_tele_settembre

    st.divider()
    st.subheader("Riepilogo Competenze di Settembre")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Quote Fisse Selene", f"{totale_fisse_selene:.2f} €")
    col2.metric("Rate Klarna/Cofidis (Set)", f"{rate_sept_selene:.2f} €")
    col3.metric("Telepedaggio (Set)", f"{tele_sept_quota:.2f} €")
    col4.metric("Totale da versare da Selene", f"{totale_da_versare_selene:.2f} €", delta="Aggiornato")

# --- SEZIONE GRAFICA ---
elif scelta == "📊 Output Mensile & Grafici":
    st.header("Analisi Grafica Mensile")
    
    if 'df_spese' in st.session_state and not st.session_state.df_spese.empty:
        df = st.session_state.df_spese.copy()
        df['Mese'] = pd.to_datetime(df['Data']).dt.to_period('M').astype(str)
        df_mensile = df.groupby(['Mese', 'Tipo'])['Importo (€)'].sum().unstack(fill_value=0)
        
        if 'Ricarica/Buoni' not in df_mensile.columns: df_mensile['Ricarica/Buoni'] = 0
        if 'Spesa' not in df_mensile.columns: df_mensile['Spesa'] = 0
        
        st.subheader("Andamento: Ricariche vs Spese")
        st.bar_chart(df_mensile)
        
        st.subheader("Riepilogo Tabellare e Risparmio Netto")
        df_mensile["Risparmio/Bilancio (€)"] = df_mensile['Ricarica/Buoni'] - df_mensile['Spesa']
        st.dataframe(df_mensile.style.format("{:.2f} €"), use_container_width=True)
    else:
        st.warning("Nessun dato di spesa disponibile.")

# --- SEZIONI DI EDITING ---
elif scelta == "🛒 Modifica Spese e Ricariche":
    st.header("Spese Quotidiane e Ricariche")
    st.session_state.df_spese = st.data_editor(st.session_state.df_spese, num_rows="dynamic", use_container_width=True, key="editor_sp")

elif scelta == "⚡ Modifica Bollette":
    st.header("Bollette Elettriche")
    st.session_state.df_bollette = st.data_editor(st.session_state.df_bollette, num_rows="dynamic", use_container_width=True, key="editor_bol")

elif scelta == "🚗 Modifica Telepedaggio":
    st.header("Telepedaggio e Parcheggi")
    # Facciamo caricare il df telepedaggio standard per modifica
    xls = pd.ExcelFile("Spese Mirko e Selene.xlsx")
    df_tele_raw = pd.read_excel(xls, sheet_name="Telepedaggio", header=None)
    st.session_state.df_tele = st.data_editor(df_tele_raw.iloc[2:15], num_rows="dynamic", use_container_width=True, key="editor_tel")

elif scelta == "🏦 Modifica Libretto":
    st.header("Libretto Postale")
    st.session_state.df_lib = st.data_editor(st.session_state.df_lib, num_rows="dynamic", use_container_width=True, key="editor_lib")

elif scelta == "💳 Modifica Rate (Klarna)":
    st.header("Rate: Klarna + Cofidis")
    xls = pd.ExcelFile("Spese Mirko e Selene.xlsx")
    df_rate_raw = pd.read_excel(xls, sheet_name="Klarna + Cofidis", header=None)
    st.session_state.df_rate = st.data_editor(df_rate_raw.iloc[5:], num_rows="dynamic", use_container_width=True, key="editor_rat")

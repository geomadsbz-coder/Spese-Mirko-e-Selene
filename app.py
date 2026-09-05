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

    # 0. FOGLIO "SPESE" (Spese fisse mensili)
    df_spese_fisse_excel = pd.read_excel(xls, sheet_name="Spese", header=None)
    fisse_list = []
    # Estraiamo le principali voci fisse note dalla struttura (es. righe 5 a 17)
    for idx, row in df_spese_fisse_excel.iloc[5:17].iterrows():
        voce = row[0]
        totale = row[1]
        if pd.notna(voce) and str(voce).strip() != "":
            fisse_list.append({
                "Voce di Spesa Fissa": str(voce),
                "Importo Totale (€)": clean_float(totale),
                "Quota Mirko (€)": clean_float(row[2]),
                "Quota Selene (€)": clean_float(row[4])
            })
    df_fisse = pd.DataFrame(fisse_list) if fisse_list else pd.DataFrame(columns=["Voce di Spesa Fissa", "Importo Totale (€)", "Quota Mirko (€)", "Quota Selene (€)"])

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

    # 3. TELEPEDAGGIO
    df_tele_excel = pd.read_excel(xls, sheet_name="Telepedaggio", header=None)
    tele_list = []
    for _, row in df_tele_excel.iloc[3:15].iterrows():
        mese = row[1]
        if pd.notna(mese):
            tele_list.append({
                "Mese": str(mese), "Importo Totale (€)": clean_float(row[2]), 
                "Quota Mirko (€)": clean_float(row[3]), 
                "Quota Condivisa (€)": clean_float(row[4]), 
                "Parcheggi (€)": clean_float(row[5])
            })
    df_tele = pd.DataFrame(tele_list) if tele_list else pd.DataFrame(columns=["Mese", "Importo Totale (€)", "Quota Mirko (€)", "Quota Condivisa (€)", "Parcheggi (€)"])

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

    # 5. RATE (KLARNA + COFIDIS)
    df_rate_excel = pd.read_excel(xls, sheet_name="Klarna + Cofidis", header=None)
    rate_list = []
    for _, row in df_rate_excel.iloc[5:].iterrows():
        prodotto = row[0]
        if pd.notna(prodotto) and isinstance(prodotto, str):
            p_str = prodotto.strip()
            if p_str and p_str not in ["Importo", "Rata", "Pagamenti Mirko+Selene", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"] and not p_str.startswith("KLARNA") and not p_str.startswith("COFIDIS"):
                imp = clean_float(row[1])
                rat = clean_float(row[2])
                if imp > 0 or rat > 0:
                    rate_list.append({"Prodotto/Servizio": p_str, "Importo Totale (€)": imp, "Rata Mensile (€)": rat})
    df_rate = pd.DataFrame(rate_list) if rate_list else pd.DataFrame(columns=["Prodotto/Servizio", "Importo Totale (€)", "Rata Mensile (€)"])

    return df_fisse, df_spese, df_bollette, df_tele, df_lib, df_rate

# --- MEMORIZZAZIONE SESSIONE ---
dfs = carica_tutti_i_dati()
if dfs[0] is not None:
    if 'df_fisse' not in st.session_state: st.session_state.df_fisse = dfs[0]
    if 'df_spese' not in st.session_state: st.session_state.df_spese = dfs[1]
    if 'df_bollette' not in st.session_state: st.session_state.df_bollette = dfs[2]
    if 'df_tele' not in st.session_state: st.session_state.df_tele = dfs[3]
    if 'df_lib' not in st.session_state: st.session_state.df_lib = dfs[4]
    if 'df_rate' not in st.session_state: st.session_state.df_rate = dfs[5]

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
    st.header("Gestione Spese Fisse Mensili & Quota Selene")
    st.write("Qui puoi visualizzare e modificare le spese fisse (escluse spesa quotidiana e ricariche). Le quote sono divise equamente al 50%.")
    
    # Tabella editabile delle spese fisse
    st.session_state.df_fisse = st.data_editor(
        st.session_state.df_fisse,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_fisse"
    )
    
    st.divider()
    
    # Calcoli automatici della quota parte
    totale_fisse = st.session_state.df_fisse["Importo Totale (€)"].sum()
    quota_selene_totale = totale_fisse / 2.0  # Divisione al 50%
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Totale Spese Fisse Mensili", f"{totale_fisse:.2f} €")
    col2.metric("Quota di Mirko (50%)", f"{totale_fisse - quota_selene_totale:.2f} €")
    col3.metric("Quota da versare da parte di Selene", f"{quota_selene_totale:.2f} €", delta="Diviso equamente")

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
    st.session_state.df_tele = st.data_editor(st.session_state.df_tele, num_rows="dynamic", use_container_width=True, key="editor_tel")

elif scelta == "🏦 Modifica Libretto":
    st.header("Libretto Postale")
    st.session_state.df_lib = st.data_editor(st.session_state.df_lib, num_rows="dynamic", use_container_width=True, key="editor_lib")

elif scelta == "💳 Modifica Rate (Klarna)":
    st.header("Rate: Klarna + Cofidis")
    st.session_state.df_rate = st.data_editor(st.session_state.df_rate, num_rows="dynamic", use_container_width=True, key="editor_rat")

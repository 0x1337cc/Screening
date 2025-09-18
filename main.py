import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuración de página - DEBE SER PRIMERO
st.set_page_config(
    page_title="BQuant Screener Pro | @Gsnchez",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para modo oscuro profesional
dark_mode_css = """
<style>
    /* Fondo principal */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1f2e 100%);
        color: #e0e0e0;
    }
    
    /* Sidebar con estilo premium */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #262730 100%);
        border-right: 1px solid #2a2d3a;
    }
    
    /* Cards de métricas con efecto glass */
    div[data-testid="metric-container"] {
        background: rgba(26, 31, 46, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
    }
    
    /* Headers con gradiente */
    h1 {
        background: linear-gradient(90deg, #00d4ff 0%, #0099ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    
    h2, h3 {
        color: #00d4ff !important;
    }
    
    /* Inputs estilizados */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > div {
        background: rgba(26, 31, 46, 0.9);
        color: #e0e0e0;
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 5px;
    }
    
    /* Tabs mejorados */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(26, 31, 46, 0.5);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #0099ff 0%, #00d4ff 100%);
        color: white !important;
        border-radius: 5px;
    }
    
    /* Botones con estilo */
    .stButton > button {
        background: linear-gradient(90deg, #0099ff 0%, #00d4ff 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 153, 255, 0.3);
    }
    
    /* Expander premium */
    .streamlit-expanderHeader {
        background: rgba(26, 31, 46, 0.9);
        color: #00d4ff;
        border-radius: 10px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* Success/Info boxes */
    .stAlert {
        background: rgba(26, 31, 46, 0.9);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 10px;
    }
    
    /* Dataframe mejorado */
    .dataframe {
        font-size: 13px;
        background: rgba(26, 31, 46, 0.7);
    }
    
    /* Footer credits */
    .footer-credits {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(26, 31, 46, 0.95);
        padding: 10px;
        text-align: center;
        border-top: 1px solid rgba(0, 212, 255, 0.3);
        z-index: 999;
    }
</style>
"""

st.markdown(dark_mode_css, unsafe_allow_html=True)

# Funciones auxiliares con caché optimizado
@st.cache_data(persist="disk", ttl=3600)  # Cache por 1 hora
def load_and_preprocess_data():
    """Carga y preprocesa los datos con caché persistente"""
    df = pd.read_csv('screenerstocks20250918.csv')
    
    # Convertir columnas de porcentaje de string a float
    percentage_columns = []
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = df[col].dropna().head(10)
            if sample.astype(str).str.contains('%', na=False).any():
                percentage_columns.append(col)
    
    for col in percentage_columns:
        df[col] = df[col].astype(str).str.replace('%', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Precalcular algunas métricas útiles
    df['Value_Score'] = 0
    if 'PE Ratio' in df.columns:
        df.loc[df['PE Ratio'] < df['PE Ratio'].quantile(0.3), 'Value_Score'] += 1
    if 'PB Ratio' in df.columns:
        df.loc[df['PB Ratio'] < df['PB Ratio'].quantile(0.3), 'Value_Score'] += 1
    if 'PS Ratio' in df.columns:
        df.loc[df['PS Ratio'] < df['PS Ratio'].quantile(0.3), 'Value_Score'] += 1
    if 'Div. Yield' in df.columns:
        df.loc[df['Div. Yield'] > df['Div. Yield'].quantile(0.7), 'Value_Score'] += 1
    
    # Growth Score
    df['Growth_Score'] = 0
    if 'Rev. Growth' in df.columns:
        df.loc[df['Rev. Growth'] > 15, 'Growth_Score'] += 1
    if 'EPS Growth' in df.columns:
        df.loc[df['EPS Growth'] > 15, 'Growth_Score'] += 1
    if 'Rev Gr. Next Y' in df.columns:
        df.loc[df['Rev Gr. Next Y'] > 10, 'Growth_Score'] += 1
    
    # Quality Score
    df['Quality_Score'] = 0
    if 'ROE' in df.columns:
        df.loc[df['ROE'] > 15, 'Quality_Score'] += 1
    if 'ROA' in df.columns:
        df.loc[df['ROA'] > 5, 'Quality_Score'] += 1
    if 'Profit Margin' in df.columns:
        df.loc[df['Profit Margin'] > 10, 'Quality_Score'] += 1
    if 'Debt / Equity' in df.columns:
        df.loc[df['Debt / Equity'] < 1, 'Quality_Score'] += 1
    
    return df

@st.cache_data(persist="disk")
def get_sector_stats(df):
    """Calcula estadísticas por sector con caché"""
    return df.groupby('Sector').agg({
        'Market Cap': 'sum',
        'PE Ratio': 'median',
        'Div. Yield': 'mean',
        'ROE': 'mean',
        'Rev. Growth': 'mean'
    }).round(2)

def format_large_number(num):
    """Formatea números grandes con sufijos apropiados"""
    if pd.isna(num):
        return "N/D"
    if abs(num) >= 1e12:
        return f"${num/1e12:.2f}T"
    elif abs(num) >= 1e9:
        return f"${num/1e9:.2f}B"
    elif abs(num) >= 1e6:
        return f"${num/1e6:.2f}M"
    elif abs(num) >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"

def parse_market_cap(value_str):
    """Convierte string de market cap a número"""
    if not value_str:
        return None
    value_str = value_str.upper().replace(',', '').strip()
    multipliers = {'K': 1e3, 'M': 1e6, 'B': 1e9, 'T': 1e12}
    for suffix, multiplier in multipliers.items():
        if value_str.endswith(suffix):
            return float(value_str[:-1]) * multiplier
    try:
        return float(value_str)
    except:
        return None

# Cargar datos
with st.spinner("⚡ Cargando base de datos optimizada..."):
    df = load_and_preprocess_data()
    sector_stats = get_sector_stats(df)

# Header con créditos
col1, col2, col3 = st.columns([2, 3, 2])
with col1:
    st.markdown("### 🏆 **BQuant Finance**")
    st.caption("bquantfinance.com")
with col2:
    st.title("📊 Screener Profesional de Acciones")
    st.markdown("*5,500+ acciones | 230+ métricas | Análisis institucional*")
with col3:
    st.markdown("### 👨‍💻 **Desarrollado por**")
    st.caption("@Gsnchez")

# Sidebar - Filtros
st.sidebar.markdown("## 🎯 **Screeners Inteligentes**")
st.sidebar.markdown("---")

# Screeners predefinidos con explicaciones
screener_descriptions = {
    "🎯 Personalizado": "Crea tu propio screener",
    "💎 Warren Buffett Style": "Empresas infravaloradas con moats económicos: P/E < 20, ROE > 15%, Deuda/Capital < 0.5",
    "🚀 Peter Lynch Growth": "PEG < 1, Crecimiento EPS > 15%, ROE > 15% - Crecimiento a precio razonable",
    "📈 CANSLIM (William O'Neil)": "Momentum + Crecimiento: EPS Growth > 25%, RS > 80, Volumen alto",
    "💰 Aristocratas del Dividendo": "Yield > 3%, Payout < 60%, 10+ años pagando dividendos crecientes",
    "🔥 Hipercrecimiento Tech": "Rev Growth > 30%, Gross Margin > 60%, Sector Tecnología",
    "🏦 Bancos Infravalorados": "P/B < 1, ROE > 10%, Sector Financiero, Dividend Yield > 3%",
    "🛡️ Defensive Quality": "Beta < 1, FCF Yield > 5%, Profit Margin > 15%, Low volatility",
    "📊 Small Cap Gems": "Market Cap 100M-2B, ROE > 20%, Insider buying, Rev Growth > 20%",
    "🎲 Turnaround Plays": "52W desde mínimos > 50%, mejora en márgenes, Z-Score > 3",
    "🌟 GARP Profesional": "P/E 10-25, EPS Growth 15-30%, PEG 0.5-1.5, ROE > 15%",
    "⚡ Momentum Institucional": "RSI 50-70, Volumen > promedio, Inst. Ownership > 60%"
}

selected_screener = st.sidebar.selectbox(
    "Selecciona un Screener Predefinido",
    options=list(screener_descriptions.keys())
)

st.sidebar.info(f"**📝 Descripción:** {screener_descriptions[selected_screener]}")

# Aplicar configuraciones del screener seleccionado
screener_filters = {}

if selected_screener == "💎 Warren Buffett Style":
    screener_filters = {
        'pe_max': 20, 'pe_min': 0,
        'roe_min': 15,
        'debt_equity_max': 0.5,
        'profit_margin_min': 10,
        'current_ratio_min': 1.5
    }
elif selected_screener == "🚀 Peter Lynch Growth":
    screener_filters = {
        'peg_max': 1, 'peg_min': 0,
        'eps_growth_min': 15,
        'roe_min': 15,
        'rev_growth_min': 10
    }
elif selected_screener == "📈 CANSLIM (William O'Neil)":
    screener_filters = {
        'eps_growth_min': 25,
        'rev_growth_min': 20,
        'rsi_min': 80,
        'roe_min': 17
    }
elif selected_screener == "💰 Aristocratas del Dividendo":
    screener_filters = {
        'div_yield_min': 3,
        'payout_max': 60,
        'years_min': 10,
        'market_cap_min': 10e9
    }
elif selected_screener == "🔥 Hipercrecimiento Tech":
    screener_filters = {
        'sectors': ['Technology'],
        'rev_growth_min': 30,
        'gross_margin_min': 60,
        'ps_max': 15
    }
elif selected_screener == "🏦 Bancos Infravalorados":
    screener_filters = {
        'sectors': ['Financials'],
        'pb_max': 1,
        'roe_min': 10,
        'div_yield_min': 3
    }
elif selected_screener == "🛡️ Defensive Quality":
    screener_filters = {
        'beta_max': 1,
        'fcf_yield_min': 5,
        'profit_margin_min': 15,
        'current_ratio_min': 2
    }
elif selected_screener == "📊 Small Cap Gems":
    screener_filters = {
        'market_cap_min': 100e6,
        'market_cap_max': 2e9,
        'roe_min': 20,
        'rev_growth_min': 20
    }
elif selected_screener == "🌟 GARP Profesional":
    screener_filters = {
        'pe_min': 10, 'pe_max': 25,
        'eps_growth_min': 15, 'eps_growth_max': 30,
        'peg_min': 0.5, 'peg_max': 1.5,
        'roe_min': 15
    }

# Filtros manuales
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔧 **Filtros Personalizados**")

with st.sidebar.expander("🏢 **Filtros de Empresa**", expanded=True):
    search_term = st.text_input("🔍 Buscar (Símbolo o Nombre)", "")
    
    sectors = st.multiselect(
        "📊 Sectores",
        options=sorted(df['Sector'].dropna().unique().tolist()),
        default=screener_filters.get('sectors', [])
    )
    
    exchanges = st.multiselect(
        "🏛️ Bolsas",
        options=sorted(df['Exchange'].dropna().unique().tolist()),
        default=[]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        min_mcap = st.text_input(
            "Cap. Min", 
            value=f"{screener_filters.get('market_cap_min', 1e6)/1e6:.0f}M"
        )
    with col2:
        max_mcap = st.text_input(
            "Cap. Max", 
            value=f"{screener_filters.get('market_cap_max', 1e12)/1e9:.0f}B" if 'market_cap_max' in screener_filters else ""
        )

with st.sidebar.expander("💰 **Métricas de Valoración**"):
    col1, col2 = st.columns(2)
    with col1:
        min_pe = st.number_input("P/E Min", value=float(screener_filters.get('pe_min', 0)), step=1.0)
        min_pb = st.number_input("P/B Min", value=float(screener_filters.get('pb_min', 0)), step=0.1)
    with col2:
        max_pe = st.number_input("P/E Max", value=float(screener_filters.get('pe_max', 50)), step=1.0)
        max_pb = st.number_input("P/B Max", value=float(screener_filters.get('pb_max', 10)), step=0.1)
    
    col1, col2 = st.columns(2)
    with col1:
        min_peg = st.number_input("PEG Min", value=float(screener_filters.get('peg_min', 0)), step=0.1)
    with col2:
        max_peg = st.number_input("PEG Max", value=float(screener_filters.get('peg_max', 3)), step=0.1)

with st.sidebar.expander("📈 **Crecimiento**"):
    rev_growth_min = st.number_input(
        "Crec. Ingresos Min (%)", 
        value=float(screener_filters.get('rev_growth_min', -50)), 
        step=5.0
    )
    eps_growth_min = st.number_input(
        "Crec. EPS Min (%)", 
        value=float(screener_filters.get('eps_growth_min', -50)), 
        step=5.0
    )
    eps_growth_max = st.number_input(
        "Crec. EPS Max (%)", 
        value=float(screener_filters.get('eps_growth_max', 200)), 
        step=5.0
    )

with st.sidebar.expander("💵 **Dividendos**"):
    div_yield_min = st.number_input(
        "Yield Min (%)", 
        value=float(screener_filters.get('div_yield_min', 0)), 
        step=0.5
    )
    payout_max = st.number_input(
        "Payout Max (%)", 
        value=float(screener_filters.get('payout_max', 100)), 
        step=10.0
    )
    years_min = st.number_input(
        "Años Dividendos Min", 
        value=int(screener_filters.get('years_min', 0)), 
        step=1
    )

with st.sidebar.expander("📊 **Rentabilidad**"):
    roe_min = st.number_input(
        "ROE Min (%)", 
        value=float(screener_filters.get('roe_min', -100)), 
        step=5.0
    )
    profit_margin_min = st.number_input(
        "Margen Neto Min (%)", 
        value=float(screener_filters.get('profit_margin_min', -100)), 
        step=5.0
    )
    gross_margin_min = st.number_input(
        "Margen Bruto Min (%)", 
        value=float(screener_filters.get('gross_margin_min', 0)), 
        step=5.0
    )

with st.sidebar.expander("📉 **Indicadores Técnicos**"):
    col1, col2 = st.columns(2)
    with col1:
        rsi_min = st.number_input(
            "RSI Min", 
            value=float(screener_filters.get('rsi_min', 0)), 
            max_value=100.0, 
            step=5.0
        )
    with col2:
        rsi_max = st.number_input("RSI Max", value=100.0, max_value=100.0, step=5.0)
    
    beta_max = st.number_input(
        "Beta Max", 
        value=float(screener_filters.get('beta_max', 3)), 
        step=0.1
    )

# Botón de aplicar filtros
st.sidebar.markdown("---")
apply_button = st.sidebar.button("🚀 **APLICAR FILTROS**", type="primary", use_container_width=True)

# Aplicar filtros al dataframe
filtered_df = df.copy()

# Búsqueda
if search_term:
    filtered_df = filtered_df[
        (filtered_df['Symbol'].str.contains(search_term.upper(), na=False)) |
        (filtered_df['Company Name'].str.contains(search_term, case=False, na=False))
    ]

# Sectores
if sectors:
    filtered_df = filtered_df[filtered_df['Sector'].isin(sectors)]

# Exchanges
if exchanges:
    filtered_df = filtered_df[filtered_df['Exchange'].isin(exchanges)]

# Market Cap
min_mc = parse_market_cap(min_mcap)
max_mc = parse_market_cap(max_mcap)
if min_mc:
    filtered_df = filtered_df[filtered_df['Market Cap'] >= min_mc]
if max_mc:
    filtered_df = filtered_df[filtered_df['Market Cap'] <= max_mc]

# Valoración
filtered_df = filtered_df[(filtered_df['PE Ratio'] >= min_pe) & (filtered_df['PE Ratio'] <= max_pe)]
filtered_df = filtered_df[(filtered_df['PB Ratio'] >= min_pb) & (filtered_df['PB Ratio'] <= max_pb)]
if 'PEG Ratio' in filtered_df.columns:
    filtered_df = filtered_df[(filtered_df['PEG Ratio'] >= min_peg) & (filtered_df['PEG Ratio'] <= max_peg)]

# Crecimiento
if 'Rev. Growth' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Rev. Growth'] >= rev_growth_min]
if 'EPS Growth' in filtered_df.columns:
    filtered_df = filtered_df[(filtered_df['EPS Growth'] >= eps_growth_min) & 
                             (filtered_df['EPS Growth'] <= eps_growth_max)]

# Dividendos
if 'Div. Yield' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Div. Yield'] >= div_yield_min]
if 'Payout Ratio' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Payout Ratio'] <= payout_max]
if 'Years' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Years'] >= years_min]

# Rentabilidad
if 'ROE' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['ROE'] >= roe_min]
if 'Profit Margin' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Profit Margin'] >= profit_margin_min]
if 'Gross Margin' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Gross Margin'] >= gross_margin_min]

# Técnicos
if 'RSI' in filtered_df.columns:
    filtered_df = filtered_df[(filtered_df['RSI'] >= rsi_min) & (filtered_df['RSI'] <= rsi_max)]
if 'Beta (5Y)' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Beta (5Y)'] <= beta_max]

# FCF Yield para Defensive Quality
if 'fcf_yield_min' in screener_filters and 'FCF Yield' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['FCF Yield'] >= screener_filters['fcf_yield_min']]

# Current Ratio
if 'current_ratio_min' in screener_filters and 'Current Ratio' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Current Ratio'] >= screener_filters['current_ratio_min']]

# Debt/Equity
if 'debt_equity_max' in screener_filters and 'Debt / Equity' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Debt / Equity'] <= screener_filters['debt_equity_max']]

# Área principal - Métricas resumen
st.markdown("---")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("📊 Total Acciones", f"{len(filtered_df):,}")
with col2:
    total_mcap = filtered_df['Market Cap'].sum()
    st.metric("💰 Cap. Total", format_large_number(total_mcap))
with col3:
    avg_pe = filtered_df['PE Ratio'].median()
    st.metric("📈 P/E Mediano", f"{avg_pe:.1f}" if not pd.isna(avg_pe) else "N/D")
with col4:
    avg_yield = filtered_df['Div. Yield'].mean()
    st.metric("💵 Yield Prom", f"{avg_yield:.2f}%" if not pd.isna(avg_yield) else "N/D")
with col5:
    avg_roe = filtered_df['ROE'].median()
    st.metric("💎 ROE Mediano", f"{avg_roe:.1f}%" if not pd.isna(avg_roe) else "N/D")
with col6:
    avg_growth = filtered_df['Rev. Growth'].median()
    st.metric("🚀 Crec. Mediano", f"{avg_growth:.1f}%" if not pd.isna(avg_growth) else "N/D")

# Tabs principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 **Tabla de Resultados**", 
    "📈 **Análisis Visual**", 
    "🏆 **Top Performers**", 
    "🎯 **Análisis Sectorial**",
    "💾 **Exportar Datos**"
])

with tab1:
    st.subheader(f"🎯 Resultados del Screener: {selected_screener}")
    
    # Columnas predefinidas según el screener
    if selected_screener == "💎 Warren Buffett Style":
        default_cols = ['Symbol', 'Company Name', 'Sector', 'Market Cap', 'PE Ratio', 
                       'ROE', 'Debt / Equity', 'Profit Margin', 'Current Ratio', 'FCF Yield']
    elif selected_screener == "🚀 Peter Lynch Growth":
        default_cols = ['Symbol', 'Company Name', 'PEG Ratio', 'EPS Growth', 'Rev. Growth',
                       'ROE', 'Market Cap', 'PE Ratio', 'PS Ratio']
    elif selected_screener == "💰 Aristocratas del Dividendo":
        default_cols = ['Symbol', 'Company Name', 'Div. Yield', 'Payout Ratio', 'Years',
                       'Div. Growth 5Y', 'Market Cap', 'PE Ratio', 'FCF Yield']
    else:
        default_cols = ['Symbol', 'Company Name', 'Sector', 'Market Cap', 'PE Ratio',
                       'Div. Yield', 'ROE', 'Rev. Growth', 'EPS Growth', 'PEG Ratio']
    
    available_cols = [col for col in default_cols if col in filtered_df.columns]
    
    # Selector de columnas
    with st.expander("⚙️ **Personalizar Columnas**"):
        selected_columns = st.multiselect(
            "Selecciona las columnas a mostrar:",
            options=filtered_df.columns.tolist(),
            default=available_cols
        )
    
    if not selected_columns:
        selected_columns = available_cols
    
    # Configuración de ordenamiento
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        sort_column = st.selectbox(
            "📊 Ordenar por:",
            options=selected_columns,
            index=0 if selected_columns else 0
        )
    with col2:
        sort_order = st.radio("📈 Orden:", ["Descendente", "Ascendente"], horizontal=True)
    with col3:
        rows_to_show = st.selectbox("📋 Mostrar:", [50, 100, 200, 500], index=1)
    
    # Ordenar y mostrar datos
    display_df = filtered_df[selected_columns].sort_values(
        by=sort_column,
        ascending=(sort_order == "Ascendente")
    )
    
    # Aplicar formato condicional
    def highlight_values(val):
        if pd.isna(val):
            return ''
        if isinstance(val, (int, float)):
            if 'Growth' in str(val) or 'ROE' in str(val):
                if val > 20:
                    return 'color: #00ff00'
                elif val > 10:
                    return 'color: #90EE90'
                elif val < 0:
                    return 'color: #ff4444'
        return ''
    
    # Mostrar dataframe con estilo
    st.dataframe(
        display_df.head(rows_to_show).style.format({
            col: lambda x: format_large_number(x) if 'Market Cap' in col or 'Revenue' in col else
                          f"{x:.2f}%" if any(metric in col for metric in ['Yield', 'Growth', 'ROE', 'ROA', 'Margin']) else
                          f"{x:.2f}" if isinstance(x, float) else x
            for col in selected_columns
        }),
        use_container_width=True,
        height=600
    )
    
    st.success(f"✅ Mostrando {min(rows_to_show, len(display_df))} de {len(display_df)} resultados totales")

with tab2:
    st.subheader("📈 Dashboard de Análisis Visual")
    
    # Crear figura con subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=[
            '🥧 Distribución por Sector', 
            '📊 P/E vs Capitalización', 
            '📈 Matriz Crecimiento-Valor',
            '💰 Análisis de Dividendos',
            '🎯 Score de Calidad',
            '📉 Mapa de Calor de Retornos'
        ],
        specs=[[{'type': 'pie'}, {'type': 'scatter'}],
               [{'type': 'scatter'}, {'type': 'box'}],
               [{'type': 'bar'}, {'type': 'scatter'}]],
        vertical_spacing=0.1,
        horizontal_spacing=0.15
    )
    
    # 1. Distribución por sector
    sector_data = filtered_df['Sector'].value_counts().head(10)
    fig.add_trace(
        go.Pie(
            labels=sector_data.index, 
            values=sector_data.values,
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Set3),
            textposition='auto',
            textinfo='label+percent'
        ),
        row=1, col=1
    )
    
    # 2. P/E vs Market Cap
    scatter_df = filtered_df.dropna(subset=['PE Ratio', 'Market Cap']).head(200)
    fig.add_trace(
        go.Scatter(
            x=scatter_df['Market Cap'],
            y=scatter_df['PE Ratio'],
            mode='markers+text',
            text=scatter_df['Symbol'],
            textposition="top center",
            textfont=dict(size=8),
            marker=dict(
                size=scatter_df['ROE'] if 'ROE' in scatter_df.columns else 8,
                color=scatter_df['Rev. Growth'] if 'Rev. Growth' in scatter_df.columns else 'blue',
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Crec.<br>Ingresos %", x=1.15),
                line=dict(width=1, color='white')
            ),
            hovertemplate='<b>%{text}</b><br>P/E: %{y:.1f}<br>MCap: %{x:.0f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Matriz Crecimiento-Valor
    growth_value_df = filtered_df.dropna(subset=['Rev. Growth', 'PE Ratio']).head(100)
    fig.add_trace(
        go.Scatter(
            x=growth_value_df['PE Ratio'],
            y=growth_value_df['Rev. Growth'],
            mode='markers+text',
            text=growth_value_df['Symbol'],
            textposition="top center",
            textfont=dict(size=8),
            marker=dict(
                size=10,
                color=growth_value_df['Market Cap'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Market<br>Cap", x=0.45, y=0.5)
            ),
            hovertemplate='<b>%{text}</b><br>P/E: %{x:.1f}<br>Crec: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. Análisis de dividendos por sector
    div_sectors = filtered_df.groupby('Sector')['Div. Yield'].apply(list).head(5)
    for sector in div_sectors.index:
        fig.add_trace(
            go.Box(
                y=div_sectors[sector],
                name=sector[:10],
                marker_color=px.colors.qualitative.Set3[list(div_sectors.index).index(sector)]
            ),
            row=2, col=2
        )
    
    # 5. Top 10 por Quality Score
    top_quality = filtered_df.nlargest(10, 'Quality_Score')[['Symbol', 'Quality_Score']]
    fig.add_trace(
        go.Bar(
            x=top_quality['Symbol'],
            y=top_quality['Quality_Score'],
            marker_color='lightblue',
            text=top_quality['Quality_Score'],
            textposition='auto',
        ),
        row=3, col=1
    )
    
    # 6. Scatter de Beta vs Retorno
    beta_return_df = filtered_df.dropna(subset=['Beta (5Y)', 'Return 1Y']).head(100)
    fig.add_trace(
        go.Scatter(
            x=beta_return_df['Beta (5Y)'],
            y=beta_return_df['Return 1Y'],
            mode='markers',
            text=beta_return_df['Symbol'],
            marker=dict(
                size=8,
                color=beta_return_df['Market Cap'],
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(title="MCap", x=1.15, y=0.15)
            ),
            hovertemplate='<b>%{text}</b><br>Beta: %{x:.2f}<br>Ret 1Y: %{y:.1f}%<extra></extra>'
        ),
        row=3, col=2
    )
    
    # Actualizar diseño
    fig.update_layout(
        height=1200,
        showlegend=False,
        template='plotly_dark',
        title={
            'text': f"<b>Análisis Visual - {selected_screener}</b>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#00d4ff'}
        },
        paper_bgcolor='rgba(26, 31, 46, 0.8)',
        plot_bgcolor='rgba(26, 31, 46, 0.9)'
    )
    
    fig.update_xaxes(type="log", row=1, col=2)
    fig.update_xaxes(title_text="P/E Ratio", row=2, col=1)
    fig.update_yaxes(title_text="Crecimiento Ingresos %", row=2, col=1)
    fig.update_xaxes(title_text="Beta", row=3, col=2)
    fig.update_yaxes(title_text="Retorno 1 Año %", row=3, col=2)
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("🏆 Ranking de Top Performers")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📈 **Mayor Retorno Anual**")
        if 'Return 1Y' in filtered_df.columns:
            top_returns = filtered_df.nlargest(10, 'Return 1Y')[
                ['Symbol', 'Company Name', 'Return 1Y', 'Market Cap', 'Sector']
            ]
            for idx, row in top_returns.iterrows():
                with st.container():
                    st.markdown(f"**{row['Symbol']}** | {row['Sector']}")
                    st.caption(f"{row['Company Name'][:40]}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Retorno", f"{row['Return 1Y']:.1f}%")
                    with col_b:
                        st.metric("MCap", format_large_number(row['Market Cap']))
                    st.markdown("---")
    
    with col2:
        st.markdown("### 💎 **Mejor Valor (P/E Bajo)**")
        best_value = filtered_df[(filtered_df['PE Ratio'] > 0) & (filtered_df['PE Ratio'] < 100)].nsmallest(10, 'PE Ratio')[
            ['Symbol', 'Company Name', 'PE Ratio', 'PB Ratio', 'Div. Yield']
        ]
        for idx, row in best_value.iterrows():
            with st.container():
                st.markdown(f"**{row['Symbol']}**")
                st.caption(f"{row['Company Name'][:40]}")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("P/E", f"{row['PE Ratio']:.1f}")
                with col_b:
                    st.metric("P/B", f"{row['PB Ratio']:.2f}")
                with col_c:
                    st.metric("Yield", f"{row['Div. Yield']:.2f}%")
                st.markdown("---")
    
    with col3:
        st.markdown("### 🚀 **Mayor Crecimiento**")
        if 'Rev. Growth' in filtered_df.columns:
            high_growth = filtered_df[filtered_df['Rev. Growth'] > 0].nlargest(10, 'Rev. Growth')[
                ['Symbol', 'Company Name', 'Rev. Growth', 'EPS Growth', 'Market Cap']
            ]
            for idx, row in high_growth.iterrows():
                with st.container():
                    st.markdown(f"**{row['Symbol']}**")
                    st.caption(f"{row['Company Name'][:40]}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Crec. Ing.", f"{row['Rev. Growth']:.1f}%")
                    with col_b:
                        st.metric("Crec. EPS", f"{row['EPS Growth']:.1f}%")
                    st.markdown("---")

with tab4:
    st.subheader("🎯 Análisis Sectorial Detallado")
    
    # Estadísticas por sector
    sector_metrics = filtered_df.groupby('Sector').agg({
        'Symbol': 'count',
        'Market Cap': 'sum',
        'PE Ratio': 'median',
        'Div. Yield': 'mean',
        'ROE': 'median',
        'Rev. Growth': 'median',
        'Return 1Y': 'mean'
    }).round(2)
    
    sector_metrics.columns = ['Acciones', 'Cap. Total', 'P/E Med.', 'Yield Prom.', 
                              'ROE Med.', 'Crec. Med.', 'Ret. 1Y Prom.']
    sector_metrics = sector_metrics.sort_values('Cap. Total', ascending=False)
    
    # Mostrar tabla
    st.markdown("### 📊 Métricas Clave por Sector")
    st.dataframe(
        sector_metrics.style.format({
            'Cap. Total': lambda x: format_large_number(x),
            'P/E Med.': '{:.1f}',
            'Yield Prom.': '{:.2f}%',
            'ROE Med.': '{:.1f}%',
            'Crec. Med.': '{:.1f}%',
            'Ret. 1Y Prom.': '{:.1f}%'
        }).background_gradient(cmap='RdYlGn', subset=['ROE Med.', 'Crec. Med.', 'Ret. 1Y Prom.']),
        use_container_width=True
    )
    
    # Gráfico de burbujas por sector
    st.markdown("### 🎯 Mapa de Oportunidades por Sector")
    
    bubble_data = sector_metrics.reset_index()
    bubble_data = bubble_data[bubble_data['Acciones'] > 5]  # Sectores con más de 5 acciones
    
    fig_bubble = go.Figure()
    
    fig_bubble.add_trace(go.Scatter(
        x=bubble_data['P/E Med.'],
        y=bubble_data['ROE Med.'],
        mode='markers+text',
        text=bubble_data['Sector'],
        textposition="top center",
        marker=dict(
            size=bubble_data['Cap. Total']/1e10,  # Tamaño proporcional al market cap
            color=bubble_data['Ret. 1Y Prom.'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Retorno<br>1Y %"),
            line=dict(width=2, color='white'),
            sizemode='diameter',
            sizeref=2.*max(bubble_data['Cap. Total']/1e10)/(40.**2),
            sizemin=4
        ),
        hovertemplate='<b>%{text}</b><br>P/E: %{x:.1f}<br>ROE: %{y:.1f}%<br><extra></extra>'
    ))
    
    fig_bubble.update_layout(
        title="Sectores: P/E vs ROE (tamaño = Market Cap)",
        xaxis_title="P/E Mediano",
        yaxis_title="ROE Mediano (%)",
        height=600,
        template='plotly_dark',
        paper_bgcolor='rgba(26, 31, 46, 0.8)',
        plot_bgcolor='rgba(26, 31, 46, 0.9)'
    )
    
    # Añadir líneas de referencia
    fig_bubble.add_hline(y=15, line_dash="dash", line_color="gray", annotation_text="ROE 15%")
    fig_bubble.add_vline(x=20, line_dash="dash", line_color="gray", annotation_text="P/E 20")
    
    st.plotly_chart(fig_bubble, use_container_width=True)

with tab5:
    st.subheader("💾 Exportar Resultados del Screener")
    
    st.info("📝 **Selecciona las columnas que deseas exportar y descarga tu análisis personalizado**")
    
    # Presets de exportación
    export_preset = st.selectbox(
        "📋 Preset de Exportación:",
        ["Personalizado", "Análisis Fundamental", "Métricas de Crecimiento", 
         "Análisis de Dividendos", "Indicadores Técnicos", "Todo"]
    )
    
    if export_preset == "Análisis Fundamental":
        export_cols = ['Symbol', 'Company Name', 'Sector', 'Market Cap', 'PE Ratio', 
                      'PB Ratio', 'PS Ratio', 'ROE', 'ROA', 'Profit Margin']
    elif export_preset == "Métricas de Crecimiento":
        export_cols = ['Symbol', 'Company Name', 'Rev. Growth', 'EPS Growth', 
                      'Rev Gr. Next Y', 'EPS Gr. Next Y', 'Rev. Growth 5Y']
    elif export_preset == "Análisis de Dividendos":
        export_cols = ['Symbol', 'Company Name', 'Div. Yield', 'Payout Ratio', 
                      'Years', 'Div. Growth 5Y', 'Ex-Div Date']
    elif export_preset == "Indicadores Técnicos":
        export_cols = ['Symbol', 'Company Name', 'RSI', 'Beta (5Y)', 'ATR', 
                      'Return 1Y', 'Return YTD', '52W High', '52W Low']
    elif export_preset == "Todo":
        export_cols = filtered_df.columns.tolist()
    else:
        export_cols = st.multiselect(
            "Selecciona columnas para exportar:",
            options=filtered_df.columns.tolist(),
            default=['Symbol', 'Company Name', 'Sector', 'Market Cap', 
                    'PE Ratio', 'Div. Yield', 'ROE']
        )
    
    # Filtrar solo columnas existentes
    export_cols = [col for col in export_cols if col in filtered_df.columns]
    
    if export_cols:
        export_df = filtered_df[export_cols]
        
        # Preview
        st.markdown("### 👁️ Vista Previa (primeras 10 filas)")
        st.dataframe(export_df.head(10), use_container_width=True)
        
        # Estadísticas de exportación
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total de Filas", f"{len(export_df):,}")
        with col2:
            st.metric("📋 Total de Columnas", len(export_cols))
        with col3:
            st.metric("💾 Tamaño Estimado", f"{len(export_df) * len(export_cols) * 8 / 1024:.1f} KB")
        
        # Botones de descarga
        col1, col2 = st.columns(2)
        
        with col1:
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="📥 **Descargar como CSV**",
                data=csv,
                file_name=f"bquant_screener_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            # Crear archivo Excel (requiere openpyxl)
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    export_df.to_excel(writer, sheet_name='Screener Results', index=False)
                    
                    # Agregar hoja de estadísticas
                    stats_df = pd.DataFrame({
                        'Métrica': ['Total Acciones', 'Screener Usado', 'Fecha'],
                        'Valor': [len(export_df), selected_screener, pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')]
                    })
                    stats_df.to_excel(writer, sheet_name='Info', index=False)
                
                st.download_button(
                    label="📗 **Descargar como Excel**",
                    data=buffer.getvalue(),
                    file_name=f"bquant_screener_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="secondary",
                    use_container_width=True
                )
            except ImportError:
                st.warning("⚠️ Instala 'openpyxl' para exportar a Excel: pip install openpyxl")
        
        st.success(f"✅ **Listo para exportar:** {len(export_df)} acciones con {len(export_cols)} métricas")

# Footer con créditos
st.markdown("---")
footer_html = """
<div style='text-align: center; padding: 20px; background: rgba(26, 31, 46, 0.9); border-radius: 10px; margin-top: 30px;'>
    <h4 style='color: #00d4ff;'>📊 BQuant Finance Screener Profesional</h4>
    <p style='color: #888;'>
        Desarrollado por <a href='https://twitter.com/Gsnchez' style='color: #00d4ff;'>@Gsnchez</a> | 
        <a href='https://bquantfinance.com' style='color: #00d4ff;'>bquantfinance.com</a><br>
        Base de datos: 5,500+ acciones | 230+ métricas | Actualización: Sept 2025<br>
        <small>Powered by Streamlit | Data cached for optimal performance</small>
    </p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; padding: 10px;'>
    <small style='color: #888;'>
        💡 <b>Pro Tip:</b> Usa los screeners predefinidos<br>
        para entender el poder de la herramienta<br><br>
        🔥 Creado por <b>@Gsnchez</b><br>
        🌐 <b>bquantfinance.com</b>
    </small>
</div>
""", unsafe_allow_html=True)

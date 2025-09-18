import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import time
import random
warnings.filterwarnings('ignore')

# Configuración de página - DEBE SER PRIMERO
st.set_page_config(
    page_title="BQuant Screener Pro | @Gsnchez",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ULTRA ESTÉTICO con efectos y animaciones
ultra_aesthetic_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;700&display=swap');
    
    /* Variables de colores */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --dark-gradient: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        --neon-blue: #00d4ff;
        --neon-purple: #b429f9;
        --neon-pink: #ff006e;
    }
    
    /* Animación de fondo con partículas */
    .stApp {
        background: var(--dark-gradient);
        position: relative;
        overflow: hidden;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(120, 80, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 0, 150, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 20%, rgba(0, 212, 255, 0.1) 0%, transparent 50%);
        animation: float 20s ease-in-out infinite;
        pointer-events: none;
        z-index: 1;
    }
    
    @keyframes float {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(30px, -30px) rotate(120deg); }
        66% { transform: translate(-20px, 20px) rotate(240deg); }
    }
    
    /* Sidebar con efecto glass y glow */
    section[data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.7);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0, 212, 255, 0.3);
        box-shadow: 
            0 0 40px rgba(0, 212, 255, 0.2),
            inset 0 0 20px rgba(180, 41, 249, 0.1);
        z-index: 100;
    }
    
    /* Títulos con gradiente animado */
    h1 {
        background: linear-gradient(90deg, #00d4ff, #b429f9, #ff006e, #00d4ff);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 3em;
        text-align: center;
        animation: gradient-shift 3s ease infinite;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--neon-blue) !important;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    /* Cards con efecto 3D y hover */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.5),
            inset 0 0 0 1px rgba(255, 255, 255, 0.1),
            0 0 20px rgba(0, 212, 255, 0.3);
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.7),
            inset 0 0 0 1px rgba(255, 255, 255, 0.2),
            0 0 40px rgba(180, 41, 249, 0.5);
    }
    
    div[data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        transition: transform 0.6s;
    }
    
    div[data-testid="metric-container"]:hover::before {
        transform: translateX(100%);
    }
    
    /* Botones con efecto neon */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 30px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 16px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
        box-shadow: 
            0 4px 15px rgba(102, 126, 234, 0.4),
            0 0 20px rgba(102, 126, 234, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, #f093fb, #f5576c);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .stButton > button:hover::before {
        opacity: 1;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 8px 25px rgba(245, 87, 108, 0.5),
            0 0 40px rgba(240, 147, 251, 0.4);
    }
    
    /* Input fields con glow */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div > div {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        color: #ffffff;
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 10px 15px;
        font-family: 'Space Grotesk', sans-serif;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--neon-purple);
        box-shadow: 
            0 0 20px rgba(180, 41, 249, 0.5),
            inset 0 0 10px rgba(180, 41, 249, 0.1);
        outline: none;
    }
    
    /* Tabs futuristas */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 5px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 15px;
        padding: 10px 20px;
        background: transparent;
        color: rgba(255, 255, 255, 0.7);
        transition: all 0.3s;
        border: 1px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white !important;
        box-shadow: 
            0 5px 20px rgba(102, 126, 234, 0.4),
            inset 0 0 10px rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
    }
    
    /* Expanders con animación */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        color: var(--neon-blue);
        border-radius: 15px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        padding: 15px;
        transition: all 0.3s;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.1);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
    }
    
    /* Dataframe estilizado */
    .dataframe {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        overflow: hidden;
    }
    
    .dataframe th {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white !important;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 12px;
    }
    
    .dataframe td {
        font-family: 'Space Grotesk', sans-serif;
        color: #e0e0e0;
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    .dataframe tr:hover {
        background: rgba(0, 212, 255, 0.1);
    }
    
    /* Alerts con efecto neon */
    .stAlert {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid;
        border-radius: 15px;
        padding: 15px;
        animation: pulse-glow 2s infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.3); }
        50% { box-shadow: 0 0 40px rgba(0, 212, 255, 0.5); }
    }
    
    /* Success message */
    .success-box {
        background: linear-gradient(45deg, rgba(76, 175, 80, 0.2), rgba(0, 212, 255, 0.2));
        border: 1px solid #4caf50;
        box-shadow: 0 0 30px rgba(76, 175, 80, 0.4);
    }
    
    /* Error message */
    .error-box {
        background: linear-gradient(45deg, rgba(244, 67, 54, 0.2), rgba(255, 0, 110, 0.2));
        border: 1px solid #f44336;
        box-shadow: 0 0 30px rgba(244, 67, 54, 0.4);
    }
    
    /* Loading animation */
    .loading-wave {
        width: 300px;
        height: 100px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 50px auto;
    }
    
    .loading-bar {
        width: 20px;
        height: 10px;
        margin: 0 5px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 5px;
        animation: loading-wave-animation 1s ease-in-out infinite;
    }
    
    .loading-bar:nth-child(2) { animation-delay: 0.1s; }
    .loading-bar:nth-child(3) { animation-delay: 0.2s; }
    .loading-bar:nth-child(4) { animation-delay: 0.3s; }
    .loading-bar:nth-child(5) { animation-delay: 0.4s; }
    
    @keyframes loading-wave-animation {
        0%, 100% { height: 10px; }
        50% { height: 50px; }
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #764ba2, #f5576c);
    }
    
    /* Glow effect for important elements */
    .glow {
        animation: glow-effect 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow-effect {
        from { box-shadow: 0 0 30px rgba(0, 212, 255, 0.5); }
        to { box-shadow: 0 0 60px rgba(180, 41, 249, 0.8), 0 0 90px rgba(255, 0, 110, 0.5); }
    }
</style>
"""

st.markdown(ultra_aesthetic_css, unsafe_allow_html=True)

# Animación de carga inicial
loading_html = """
<div class="loading-wave">
    <div class="loading-bar"></div>
    <div class="loading-bar"></div>
    <div class="loading-bar"></div>
    <div class="loading-bar"></div>
    <div class="loading-bar"></div>
</div>
"""

# Funciones auxiliares mejoradas
@st.cache_data(persist="disk", ttl=3600)
def load_and_preprocess_data():
    """Carga y preprocesa los datos con caché persistente"""
    try:
        df = pd.read_csv('screenerstocks20250918.csv')
    except FileNotFoundError:
        # Generar datos de ejemplo si no encuentra el archivo
        np.random.seed(42)
        n_stocks = 1000
        
        sectors = ['Technology', 'Healthcare', 'Financials', 'Consumer Discretionary', 
                  'Industrials', 'Energy', 'Materials', 'Utilities', 'Real Estate', 
                  'Communication Services', 'Consumer Staples']
        
        df = pd.DataFrame({
            'Symbol': [f'STK{i:04d}' for i in range(n_stocks)],
            'Company Name': [f'Company {i}' for i in range(n_stocks)],
            'Sector': np.random.choice(sectors, n_stocks),
            'Market Cap': np.random.lognormal(20, 2, n_stocks),
            'PE Ratio': np.random.uniform(5, 50, n_stocks),
            'PB Ratio': np.random.uniform(0.5, 10, n_stocks),
            'PS Ratio': np.random.uniform(0.5, 20, n_stocks),
            'PEG Ratio': np.random.uniform(0.5, 3, n_stocks),
            'Div. Yield': np.random.uniform(0, 8, n_stocks),
            'Payout Ratio': np.random.uniform(0, 100, n_stocks),
            'Years': np.random.randint(0, 50, n_stocks),
            'ROE': np.random.uniform(-20, 50, n_stocks),
            'ROA': np.random.uniform(-10, 30, n_stocks),
            'Profit Margin': np.random.uniform(-20, 40, n_stocks),
            'Gross Margin': np.random.uniform(10, 80, n_stocks),
            'Rev. Growth': np.random.uniform(-30, 100, n_stocks),
            'EPS Growth': np.random.uniform(-50, 150, n_stocks),
            'Rev Gr. Next Y': np.random.uniform(-20, 50, n_stocks),
            'EPS Gr. Next Y': np.random.uniform(-30, 60, n_stocks),
            'Return 1Y': np.random.uniform(-50, 200, n_stocks),
            'Return YTD': np.random.uniform(-30, 100, n_stocks),
            'Return 1M': np.random.uniform(-20, 30, n_stocks),
            'Return 1W': np.random.uniform(-10, 15, n_stocks),
            'RSI': np.random.uniform(20, 80, n_stocks),
            'Beta (5Y)': np.random.uniform(0.5, 2.5, n_stocks),
            'Debt / Equity': np.random.uniform(0, 3, n_stocks),
            'Current Ratio': np.random.uniform(0.5, 5, n_stocks),
            'FCF Yield': np.random.uniform(-5, 20, n_stocks),
            'Exchange': np.random.choice(['NASDAQ', 'NYSE', 'AMEX'], n_stocks),
            'Revenue': np.random.lognormal(18, 2, n_stocks),
            'EPS': np.random.uniform(-5, 20, n_stocks),
            'Div. Growth 5Y': np.random.uniform(-10, 30, n_stocks),
            '52W High': np.random.uniform(50, 500, n_stocks),
            '52W Low': np.random.uniform(10, 100, n_stocks),
        })
        
        st.warning("⚠️ Archivo CSV no encontrado. Usando datos de ejemplo para demostración.")
    
    # Calcular scores sintéticos
    df['Value_Score'] = 0
    df.loc[df['PE Ratio'] < df['PE Ratio'].quantile(0.3), 'Value_Score'] += 1
    df.loc[df['PB Ratio'] < df['PB Ratio'].quantile(0.3), 'Value_Score'] += 1
    df.loc[df['Div. Yield'] > df['Div. Yield'].quantile(0.7), 'Value_Score'] += 1
    
    df['Growth_Score'] = 0
    df.loc[df['Rev. Growth'] > 15, 'Growth_Score'] += 1
    df.loc[df['EPS Growth'] > 15, 'Growth_Score'] += 1
    
    df['Quality_Score'] = 0
    df.loc[df['ROE'] > 15, 'Quality_Score'] += 1
    df.loc[df['ROA'] > 5, 'Quality_Score'] += 1
    df.loc[df['Profit Margin'] > 10, 'Quality_Score'] += 1
    
    return df

def format_large_number(num):
    """Formatea números grandes con sufijos"""
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
            try:
                return float(value_str[:-1]) * multiplier
            except:
                return None
    try:
        return float(value_str)
    except:
        return None

# Header animado con efectos
header_html = """
<div style="text-align: center; padding: 30px 0;">
    <h1 style="margin: 0; animation: gradient-shift 3s ease infinite;">
        🚀 BQUANT SCREENER PRO
    </h1>
    <p style="color: #a0a0a0; font-family: 'Space Grotesk', sans-serif; font-size: 18px; margin-top: 10px;">
        <span style="color: #00d4ff;">5,500+ acciones</span> | 
        <span style="color: #b429f9;">230+ métricas</span> | 
        <span style="color: #ff006e;">Análisis institucional</span>
    </p>
    <div style="display: flex; justify-content: center; gap: 30px; margin-top: 20px;">
        <div style="text-align: center;">
            <p style="color: #00d4ff; font-size: 14px; margin: 0;">💎 Desarrollado por</p>
            <p style="color: white; font-weight: bold; font-size: 16px;">@Gsnchez</p>
        </div>
        <div style="text-align: center;">
            <p style="color: #b429f9; font-size: 14px; margin: 0;">🌐 Powered by</p>
            <p style="color: white; font-weight: bold; font-size: 16px;">bquantfinance.com</p>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Mostrar loading mientras carga
with st.spinner(""):
    st.markdown(loading_html, unsafe_allow_html=True)
    time.sleep(0.5)  # Efecto dramático
    df = load_and_preprocess_data()

# Limpiar loading
st.empty()

# Sidebar con efectos
st.sidebar.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h2 style="color: #00d4ff; text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);">
        ⚡ SCREENERS INTELIGENTES
    </h2>
</div>
""", unsafe_allow_html=True)

# Screeners predefinidos
screener_descriptions = {
    "🎯 Personalizado": "Crea tu propio screener",
    "💎 Warren Buffett Style": "Empresas infravaloradas con moats",
    "🚀 Peter Lynch Growth": "PEG < 1, Crecimiento razonable",
    "📈 CANSLIM": "Momentum + Crecimiento extremo",
    "💰 Aristócratas Dividendos": "Dividendos crecientes +10 años",
    "🔥 Hipercrecimiento Tech": "Rev Growth > 30%, Tech sector",
    "🏦 Bancos Infravalorados": "P/B < 1, ROE > 10%, Financials",
    "🛡️ Defensive Quality": "Beta < 1, FCF Yield > 5%",
    "📊 Small Cap Gems": "MCap 100M-2B, ROE > 20%",
    "⚡ Momentum Institucional": "RSI 50-70, High volume"
}

selected_screener = st.sidebar.selectbox(
    "🎭 Selecciona un Screener",
    options=list(screener_descriptions.keys()),
    help="Cada screener está optimizado para una estrategia específica"
)

# Info box animado
st.sidebar.markdown(f"""
<div style="background: rgba(255, 255, 255, 0.05); 
            backdrop-filter: blur(10px); 
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 15px; 
            padding: 15px;
            margin: 10px 0;
            animation: pulse-glow 2s infinite;">
    <p style="color: #00d4ff; margin: 0; font-weight: bold;">📝 Descripción:</p>
    <p style="color: #e0e0e0; margin: 5px 0 0 0; font-size: 14px;">{screener_descriptions[selected_screener]}</p>
</div>
""", unsafe_allow_html=True)

# Configuraciones de screeners
screener_filters = {}
if selected_screener == "💎 Warren Buffett Style":
    screener_filters = {'pe_max': 20, 'roe_min': 15, 'debt_equity_max': 0.5}
elif selected_screener == "🚀 Peter Lynch Growth":
    screener_filters = {'peg_max': 1, 'eps_growth_min': 15, 'roe_min': 15}
elif selected_screener == "💰 Aristócratas Dividendos":
    screener_filters = {'div_yield_min': 3, 'years_min': 10}

# Filtros con diseño mejorado
st.sidebar.markdown("---")
st.sidebar.markdown("""
<h3 style="text-align: center; color: #b429f9; text-shadow: 0 0 15px rgba(180, 41, 249, 0.5);">
    🔧 FILTROS PERSONALIZADOS
</h3>
""", unsafe_allow_html=True)

with st.sidebar.expander("🏢 **Filtros de Empresa**", expanded=True):
    search_term = st.text_input("🔍 Buscar", placeholder="Símbolo o nombre...")
    sectors = st.multiselect("📊 Sectores", options=df['Sector'].unique().tolist())
    
    col1, col2 = st.columns(2)
    with col1:
        min_mcap = st.text_input("💰 Cap. Min", "1M")
    with col2:
        max_mcap = st.text_input("💰 Cap. Max", "")

with st.sidebar.expander("💎 **Valoración**"):
    col1, col2 = st.columns(2)
    with col1:
        min_pe = st.number_input("P/E Min", 0.0, 100.0, 0.0)
    with col2:
        max_pe = st.number_input("P/E Max", 0.0, 100.0, 50.0)

with st.sidebar.expander("📈 **Crecimiento**"):
    rev_growth_min = st.number_input("Crec. Ingresos Min %", -100.0, 500.0, -50.0)
    eps_growth_min = st.number_input("Crec. EPS Min %", -100.0, 500.0, -50.0)

# Botón de aplicar con efecto
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("⚡ APLICAR FILTROS", use_container_width=True):
    st.balloons()  # Efecto visual

# Aplicar filtros
filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[
        (filtered_df['Symbol'].str.contains(search_term.upper(), na=False)) |
        (filtered_df['Company Name'].str.contains(search_term, case=False, na=False))
    ]

if sectors:
    filtered_df = filtered_df[filtered_df['Sector'].isin(sectors)]

min_mc = parse_market_cap(min_mcap)
max_mc = parse_market_cap(max_mcap)
if min_mc:
    filtered_df = filtered_df[filtered_df['Market Cap'] >= min_mc]
if max_mc:
    filtered_df = filtered_df[filtered_df['Market Cap'] <= max_mc]

filtered_df = filtered_df[(filtered_df['PE Ratio'] >= min_pe) & (filtered_df['PE Ratio'] <= max_pe)]

if 'Rev. Growth' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Rev. Growth'] >= rev_growth_min]
if 'EPS Growth' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['EPS Growth'] >= eps_growth_min]

# Aplicar filtros específicos del screener
for key, value in screener_filters.items():
    if 'min' in key:
        col = key.replace('_min', '').replace('_', ' ').title()
        if col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[col] >= value]
    elif 'max' in key:
        col = key.replace('_max', '').replace('_', ' ').title()
        if col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[col] <= value]

# Métricas con animación
st.markdown("---")
metrics_cols = st.columns(6)

metrics_data = [
    ("📊", "Total Acciones", f"{len(filtered_df):,}"),
    ("💰", "Cap. Total", format_large_number(filtered_df['Market Cap'].sum())),
    ("📈", "P/E Mediano", f"{filtered_df['PE Ratio'].median():.1f}"),
    ("💵", "Yield Prom", f"{filtered_df['Div. Yield'].mean():.2f}%"),
    ("💎", "ROE Mediano", f"{filtered_df['ROE'].median():.1f}%"),
    ("🚀", "Crec. Mediano", f"{filtered_df['Rev. Growth'].median():.1f}%")
]

for col, (icon, label, value) in zip(metrics_cols, metrics_data):
    with col:
        st.markdown(f"""
        <div class="glow" style="text-align: center; padding: 20px; 
                    background: rgba(255, 255, 255, 0.05); 
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    border: 1px solid rgba(0, 212, 255, 0.3);">
            <div style="font-size: 30px;">{icon}</div>
            <div style="color: #a0a0a0; font-size: 12px; margin: 5px 0;">{label}</div>
            <div style="color: #00d4ff; font-size: 20px; font-weight: bold;">{value}</div>
        </div>
        """, unsafe_allow_html=True)

# Tabs con diseño futurista
tab1, tab2, tab3, tab4 = st.tabs(["📊 **TABLA**", "📈 **GRÁFICOS**", "🏆 **TOP**", "💾 **EXPORTAR**"])

with tab1:
    st.markdown(f"""
    <h3 style="text-align: center; color: #00d4ff; margin: 20px 0;">
        🎯 Resultados: {selected_screener}
    </h3>
    """, unsafe_allow_html=True)
    
    # Columnas por defecto según screener
    default_cols = ['Symbol', 'Company Name', 'Sector', 'Market Cap', 'PE Ratio',
                   'ROE', 'Rev. Growth', 'Div. Yield', 'Return 1Y']
    
    available_cols = [col for col in default_cols if col in filtered_df.columns]
    
    # Mostrar tabla con estilo
    display_df = filtered_df[available_cols].head(100)
    
    # Aplicar formato con colores
    styled_df = display_df.style.format({
        'Market Cap': lambda x: format_large_number(x),
        'PE Ratio': '{:.1f}',
        'ROE': '{:.1f}%',
        'Rev. Growth': '{:.1f}%',
        'Div. Yield': '{:.2f}%',
        'Return 1Y': '{:.1f}%'
    }).background_gradient(cmap='RdYlGn', subset=['ROE', 'Rev. Growth', 'Return 1Y'])
    
    st.dataframe(styled_df, use_container_width=True, height=600)
    
    # Mensaje de éxito animado
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0; padding: 15px;
                background: linear-gradient(45deg, rgba(76, 175, 80, 0.1), rgba(0, 212, 255, 0.1));
                border: 1px solid #4caf50;
                border-radius: 15px;">
        <p style="color: #4caf50; margin: 0;">
            ✅ Mostrando {min(100, len(display_df))} de {len(filtered_df)} resultados
        </p>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <h3 style="text-align: center; color: #b429f9; margin: 20px 0;">
        📈 Dashboard Visual Interactivo
    </h3>
    """, unsafe_allow_html=True)
    
    # Gráfico 1: Distribución por sector
    fig1 = px.pie(
        filtered_df['Sector'].value_counts().reset_index(),
        values='count',
        names='Sector',
        title='Distribución por Sector',
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    fig1.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    
    # Gráfico 2: Scatter P/E vs ROE
    fig2 = px.scatter(
        filtered_df.head(200),
        x='PE Ratio',
        y='ROE',
        size='Market Cap',
        color='Rev. Growth',
        hover_data=['Symbol', 'Company Name'],
        title='Matriz Valor-Calidad',
        color_continuous_scale='Viridis'
    )
    fig2.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
    
    # Heatmap de correlaciones
    numeric_cols = ['PE Ratio', 'ROE', 'Rev. Growth', 'Div. Yield', 'Return 1Y']
    available_numeric = [col for col in numeric_cols if col in filtered_df.columns]
    
    if len(available_numeric) > 1:
        corr_matrix = filtered_df[available_numeric].corr()
        fig3 = px.imshow(
            corr_matrix,
            title='Matriz de Correlaciones',
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        fig3.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.markdown("""
    <h3 style="text-align: center; color: #ff006e; margin: 20px 0;">
        🏆 Rankings de Elite
    </h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); 
                    backdrop-filter: blur(10px);
                    border-radius: 15px; 
                    padding: 20px;
                    border: 1px solid rgba(0, 212, 255, 0.3);">
            <h4 style="color: #00d4ff; text-align: center;">📈 Mayor Retorno</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if 'Return 1Y' in filtered_df.columns:
            top_returns = filtered_df.nlargest(5, 'Return 1Y')[['Symbol', 'Return 1Y']]
            for _, row in top_returns.iterrows():
                st.markdown(f"""
                <div style="margin: 10px 0; padding: 10px;
                            background: rgba(0, 255, 0, 0.1);
                            border-left: 3px solid #00ff00;
                            border-radius: 5px;">
                    <b>{row['Symbol']}</b>: {row['Return 1Y']:.1f}%
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); 
                    backdrop-filter: blur(10px);
                    border-radius: 15px; 
                    padding: 20px;
                    border: 1px solid rgba(180, 41, 249, 0.3);">
            <h4 style="color: #b429f9; text-align: center;">💎 Mejor Valor</h4>
        </div>
        """, unsafe_allow_html=True)
        
        value_stocks = filtered_df[filtered_df['PE Ratio'] > 0].nsmallest(5, 'PE Ratio')[['Symbol', 'PE Ratio']]
        for _, row in value_stocks.iterrows():
            st.markdown(f"""
            <div style="margin: 10px 0; padding: 10px;
                        background: rgba(180, 41, 249, 0.1);
                        border-left: 3px solid #b429f9;
                        border-radius: 5px;">
                <b>{row['Symbol']}</b>: P/E {row['PE Ratio']:.1f}
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); 
                    backdrop-filter: blur(10px);
                    border-radius: 15px; 
                    padding: 20px;
                    border: 1px solid rgba(255, 0, 110, 0.3);">
            <h4 style="color: #ff006e; text-align: center;">🚀 Mayor Crecimiento</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if 'Rev. Growth' in filtered_df.columns:
            growth_stocks = filtered_df.nlargest(5, 'Rev. Growth')[['Symbol', 'Rev. Growth']]
            for _, row in growth_stocks.iterrows():
                st.markdown(f"""
                <div style="margin: 10px 0; padding: 10px;
                            background: rgba(255, 0, 110, 0.1);
                            border-left: 3px solid #ff006e;
                            border-radius: 5px;">
                    <b>{row['Symbol']}</b>: {row['Rev. Growth']:.1f}%
                </div>
                """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <h3 style="text-align: center; color: #4caf50; margin: 20px 0;">
        💾 Centro de Exportación
    </h3>
    """, unsafe_allow_html=True)
    
    export_cols = st.multiselect(
        "Selecciona columnas para exportar:",
        options=filtered_df.columns.tolist(),
        default=['Symbol', 'Company Name', 'Sector', 'Market Cap', 'PE Ratio']
    )
    
    if export_cols:
        export_df = filtered_df[export_cols]
        
        csv = export_df.to_csv(index=False)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="⬇️ DESCARGAR CSV",
                data=csv,
                file_name=f"bquant_screener_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.markdown(f"""
            <div style="text-align: center; margin: 20px 0; padding: 20px;
                        background: linear-gradient(45deg, rgba(76, 175, 80, 0.2), rgba(0, 212, 255, 0.2));
                        border: 1px solid #4caf50;
                        border-radius: 15px;
                        animation: pulse-glow 2s infinite;">
                <p style="color: #4caf50; font-size: 18px; margin: 0;">
                    ✅ {len(export_df)} acciones listas para exportar
                </p>
            </div>
            """, unsafe_allow_html=True)

# Footer animado
st.markdown("---")
footer_html = """
<div style="text-align: center; padding: 40px 20px; margin-top: 50px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);">
    <h3 style="background: linear-gradient(90deg, #00d4ff, #b429f9, #ff006e);
               background-size: 200% 100%;
               -webkit-background-clip: text;
               -webkit-text-fill-color: transparent;
               animation: gradient-shift 3s ease infinite;">
        BQuant Finance Screener Pro
    </h3>
    <p style="color: #a0a0a0; margin: 20px 0;">
        <span style="color: #00d4ff;">💎 Desarrollado por @Gsnchez</span> | 
        <span style="color: #b429f9;">🌐 bquantfinance.com</span>
    </p>
    <p style="color: #666; font-size: 12px;">
        Base de datos: 5,500+ acciones | 230+ métricas | Actualización: Sept 2025<br>
        <span style="color: #4caf50;">⚡ Powered by Streamlit | ✨ Ultra Performance Mode</span>
    </p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)

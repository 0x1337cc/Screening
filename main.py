import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="BQuant Professional Screener | @Gsnchez",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Profesional Minimalista
professional_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #1c1f26;
        border-right: 1px solid #2e3139;
        width: 320px;
    }
    
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    div[data-testid="metric-container"] {
        background-color: #1c1f26;
        border: 1px solid #2e3139;
        padding: 16px;
        border-radius: 8px;
    }
    
    div[data-testid="metric-container"]:hover {
        border-color: #4a9eff;
    }
    
    .stButton > button {
        background-color: #4a9eff;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #3a8eef;
        transform: translateY(-1px);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4a9eff;
    }
    
    .streamlit-expanderHeader {
        background-color: #1c1f26;
        border: 1px solid #2e3139;
        border-radius: 6px;
        font-weight: 500;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #4a9eff;
    }
    
    .filter-container {
        background-color: #1c1f26;
        border: 1px solid #2e3139;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .screener-card {
        background: linear-gradient(135deg, #1c1f26 0%, #262b36 100%);
        border: 1px solid #2e3139;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s;
    }
    
    .screener-card:hover {
        border-color: #4a9eff;
        transform: translateX(5px);
    }
</style>
"""

st.markdown(professional_css, unsafe_allow_html=True)

# =============================================================================
# FUNCIONES DE CARGA Y UTILIDAD
# =============================================================================

@st.cache_data(persist="disk", show_spinner=False, ttl=3600)
def load_and_preprocess_data():
    """Carga y preprocesa los datos con caché persistente"""
    try:
        # Nombre correcto del archivo
        df = pd.read_csv('screener-stocks-2025-09-18.csv')
        
        # Convertir columnas de porcentaje de string a float si es necesario
        for col in df.columns:
            if df[col].dtype == 'object':
                sample = df[col].dropna().head(100)
                if sample.astype(str).str.contains('%', na=False).any():
                    df[col] = df[col].astype(str).str.replace('%', '').astype(float, errors='ignore')
        
        # Crear métricas compuestas
        df = create_composite_metrics(df)
        
        return df
        
    except FileNotFoundError:
        st.error("❌ **No se encontró el archivo 'screener-stocks-2025-09-18.csv'**")
        st.info("Por favor, asegúrate de que el archivo CSV esté en el mismo directorio que la aplicación.")
        st.stop()

def create_composite_metrics(df):
    """Crea métricas compuestas y scores avanzados"""
    
    # Quality Score (0-100)
    df['Quality_Score'] = 0
    if 'ROE' in df.columns:
        df['Quality_Score'] += np.where(df['ROE'] > df['ROE'].quantile(0.7), 25, 0)
    if 'ROA' in df.columns:
        df['Quality_Score'] += np.where(df['ROA'] > df['ROA'].quantile(0.7), 25, 0)
    if 'ROIC' in df.columns:
        df['Quality_Score'] += np.where(df['ROIC'] > df['ROIC'].quantile(0.7), 25, 0)
    if 'Profit Margin' in df.columns:
        df['Quality_Score'] += np.where(df['Profit Margin'] > df['Profit Margin'].quantile(0.7), 25, 0)
    
    # Value Score (0-100)
    df['Value_Score'] = 0
    if 'PE Ratio' in df.columns:
        df['Value_Score'] += np.where(
            (df['PE Ratio'] > 0) & (df['PE Ratio'] < df['PE Ratio'].quantile(0.3)), 25, 0)
    if 'PB Ratio' in df.columns:
        df['Value_Score'] += np.where(df['PB Ratio'] < df['PB Ratio'].quantile(0.3), 25, 0)
    if 'PS Ratio' in df.columns:
        df['Value_Score'] += np.where(df['PS Ratio'] < df['PS Ratio'].quantile(0.3), 25, 0)
    if 'EV/EBITDA' in df.columns:
        df['Value_Score'] += np.where(
            (df['EV/EBITDA'] > 0) & (df['EV/EBITDA'] < df['EV/EBITDA'].quantile(0.3)), 25, 0)
    
    # Growth Score (0-100)
    df['Growth_Score'] = 0
    if 'Rev. Growth' in df.columns:
        df['Growth_Score'] += np.where(df['Rev. Growth'] > 20, 25, 0)
    if 'EPS Growth' in df.columns:
        df['Growth_Score'] += np.where(df['EPS Growth'] > 20, 25, 0)
    if 'Rev Gr. Next Y' in df.columns:
        df['Growth_Score'] += np.where(df['Rev Gr. Next Y'] > 15, 25, 0)
    if 'EPS Gr. Next Y' in df.columns:
        df['Growth_Score'] += np.where(df['EPS Gr. Next Y'] > 15, 25, 0)
    
    # Financial Health Score (0-100)
    df['Financial_Health_Score'] = 0
    if 'Current Ratio' in df.columns:
        df['Financial_Health_Score'] += np.where(df['Current Ratio'] > 1.5, 25, 0)
    if 'Debt / Equity' in df.columns:
        df['Financial_Health_Score'] += np.where(df['Debt / Equity'] < 1, 25, 0)
    if 'Z-Score' in df.columns:
        df['Financial_Health_Score'] += np.where(df['Z-Score'] > 3, 25, 0)
    if 'FCF Yield' in df.columns:
        df['Financial_Health_Score'] += np.where(df['FCF Yield'] > 5, 25, 0)
    
    # Momentum Score (0-100)
    df['Momentum_Score'] = 0
    if 'Return 1Y' in df.columns:
        df['Momentum_Score'] += np.where(df['Return 1Y'] > df['Return 1Y'].quantile(0.7), 30, 0)
    if 'Return 3M' in df.columns:
        df['Momentum_Score'] += np.where(df['Return 3M'] > 0, 20, 0)
    if 'Return 1M' in df.columns:
        df['Momentum_Score'] += np.where(df['Return 1M'] > 0, 20, 0)
    if 'RSI' in df.columns:
        df['Momentum_Score'] += np.where((df['RSI'] > 50) & (df['RSI'] < 70), 30, 0)
    
    # Composite Master Score
    df['Master_Score'] = (
        df['Quality_Score'] * 0.3 +
        df['Value_Score'] * 0.25 +
        df['Growth_Score'] * 0.2 +
        df['Financial_Health_Score'] * 0.15 +
        df['Momentum_Score'] * 0.1
    )
    
    return df

def format_number(num, prefix="", suffix="", decimals=2):
    """Formatea números de forma legible"""
    if pd.isna(num):
        return "N/A"
    
    if abs(num) >= 1e12:
        return f"{prefix}{num/1e12:.{decimals}f}T{suffix}"
    elif abs(num) >= 1e9:
        return f"{prefix}{num/1e9:.{decimals}f}B{suffix}"
    elif abs(num) >= 1e6:
        return f"{prefix}{num/1e6:.{decimals}f}M{suffix}"
    elif abs(num) >= 1e3:
        return f"{prefix}{num/1e3:.{decimals}f}K{suffix}"
    else:
        return f"{prefix}{num:.{decimals}f}{suffix}"

def parse_market_cap(value_str):
    """Convierte string de market cap a número"""
    if not value_str or value_str == "":
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

# =============================================================================
# SCREENERS PROFESIONALES
# =============================================================================

SCREENERS = {
    "🎯 Constructor Personalizado": {
        "description": "Construye tu propio screener con filtros personalizados",
        "filters": {}
    },
    
    # VALUE INVESTING
    "💎 Deep Value Contrarian": {
        "description": "Empresas extremadamente infravaloradas con catalizadores (P/B < 1, P/E < 10, FCF positivo)",
        "filters": {
            "pb_max": 1.0,
            "pe_max": 10.0,
            "pe_min": 0.1,
            "fcf_yield_min": 5.0,
            "current_ratio_min": 1.5,
            "value_score_min": 70
        }
    },
    
    "🏦 Graham Net-Net": {
        "description": "Trading por debajo del valor de liquidación (P/B < 0.66, Current Ratio > 2)",
        "filters": {
            "pb_max": 0.66,
            "current_ratio_min": 2.0,
            "z_score_min": 1.8,
            "debt_equity_max": 0.5,
            "value_score_min": 80
        }
    },
    
    # GROWTH INVESTING
    "🚀 Hypergrowth Tech": {
        "description": "Crecimiento explosivo con márgenes altos (Rev > 30%, Gross Margin > 60%)",
        "filters": {
            "rev_growth_min": 30.0,
            "gross_margin_min": 60.0,
            "sectors": ["Technology", "Communication Services"],
            "growth_score_min": 70
        }
    },
    
    "⚡ GARP Excellence": {
        "description": "Crecimiento a precio razonable con calidad (PEG < 1, ROE > 15%, EPS Growth > 15%)",
        "filters": {
            "peg_max": 1.0,
            "peg_min": 0.1,
            "eps_growth_min": 15.0,
            "roe_min": 15.0,
            "debt_equity_max": 1.0,
            "profit_margin_min": 10.0
        }
    },
    
    # DIVIDEND & INCOME
    "💰 Dividend Aristocrats": {
        "description": "25+ años de dividendos crecientes con sostenibilidad (Yield > 2.5%, Payout < 70%)",
        "filters": {
            "years_min": 25,
            "div_yield_min": 2.5,
            "div_yield_max": 8.0,
            "payout_ratio_max": 70.0,
            "fcf_payout_ratio_max": 60.0,
            "market_cap_min": 10e9
        }
    },
    
    "🏆 High Yield Quality": {
        "description": "Alto rendimiento con seguridad (Yield > 4%, FCF coverage, Z-Score > 3)",
        "filters": {
            "div_yield_min": 4.0,
            "div_yield_max": 10.0,
            "payout_ratio_max": 80.0,
            "z_score_min": 3.0,
            "current_ratio_min": 1.5,
            "financial_health_score_min": 60
        }
    },
    
    # QUALITY COMPANIES
    "👑 Quality Compounders": {
        "description": "Empresas de calidad excepcional (ROE > 20%, FCF Yield > 5%, Debt/Eq < 0.5)",
        "filters": {
            "roe_min": 20.0,
            "roic_min": 15.0,
            "fcf_yield_min": 5.0,
            "debt_equity_max": 0.5,
            "profit_margin_min": 15.0,
            "quality_score_min": 80
        }
    },
    
    "🛡️ Defensive Fortress": {
        "description": "Baja volatilidad con fundamentos sólidos (Beta < 0.8, Margin > 15%, Dividend)",
        "filters": {
            "beta_max": 0.8,
            "profit_margin_min": 15.0,
            "div_yield_min": 2.0,
            "current_ratio_min": 1.5,
            "sectors": ["Consumer Staples", "Healthcare", "Utilities"]
        }
    },
    
    # MOMENTUM & TECHNICAL
    "📈 Momentum Leaders": {
        "description": "Fuerte momentum con volumen (RSI 50-70, Return 1Y > 20%, Vol > avg)",
        "filters": {
            "rsi_min": 50.0,
            "rsi_max": 70.0,
            "return_1y_min": 20.0,
            "return_3m_min": 10.0,
            "rel_volume_min": 1.2,
            "momentum_score_min": 70
        }
    },
    
    "🔥 Breakout Candidates": {
        "description": "Cerca de máximos con momentum (Dist. 52W High < 10%, RSI > 55)",
        "filters": {
            "distance_52w_high_max": 10.0,
            "rsi_min": 55.0,
            "rsi_max": 75.0,
            "return_1m_min": 5.0,
            "volume_ratio_min": 1.5
        }
    },
    
    # SPECIAL SITUATIONS
    "🔄 Turnaround Stories": {
        "description": "Empresas en recuperación con señales positivas (Z-Score > 1.8, FCF positivo)",
        "filters": {
            "z_score_min": 1.8,
            "z_score_max": 3.0,
            "fcf_min": 0.0,
            "return_3m_min": 10.0,
            "rsi_min": 40.0,
            "rsi_max": 60.0
        }
    },
    
    "💎 Small Cap Gems": {
        "description": "Pequeña capitalización con métricas excepcionales ($200M-$2B, ROE > 15%)",
        "filters": {
            "market_cap_min": 200e6,
            "market_cap_max": 2e9,
            "roe_min": 15.0,
            "rev_growth_min": 15.0,
            "insider_ownership_min": 5.0,
            "master_score_min": 60
        }
    },
    
    # FACTOR MODELS
    "🎯 Multi-Factor Quant": {
        "description": "Modelo cuantitativo con 5 factores: Value + Quality + Growth + Momentum + Low Risk",
        "filters": {
            "value_score_min": 60,
            "quality_score_min": 60,
            "growth_score_min": 60,
            "momentum_score_min": 60,
            "beta_max": 1.5,
            "master_score_min": 70
        }
    },
    
    "📊 Magic Formula Plus": {
        "description": "Joel Greenblatt mejorado: Earnings Yield alto + ROIC alto + Momentum",
        "filters": {
            "earnings_yield_min": 10.0,
            "roic_min": 20.0,
            "return_6m_min": 0.0,
            "debt_equity_max": 1.0,
            "market_cap_min": 50e6
        }
    },
    
    "🌟 CANSLIM Screener": {
        "description": "William O'Neil: EPS +25%, Rev +20%, New highs, Inst. ownership",
        "filters": {
            "eps_growth_min": 25.0,
            "rev_growth_min": 20.0,
            "distance_52w_high_max": 15.0,
            "institutional_ownership_min": 30.0,
            "institutional_ownership_max": 80.0,
            "rsi_min": 50.0
        }
    }
}

# =============================================================================
# INICIALIZACIÓN Y CARGA DE DATOS
# =============================================================================

# Inicializar estado de sesión
if 'filters_applied' not in st.session_state:
    st.session_state.filters_applied = False

if 'selected_screener' not in st.session_state:
    st.session_state.selected_screener = "🎯 Constructor Personalizado"

# Cargar datos
with st.spinner("Cargando base de datos de 5,500+ acciones..."):
    df = load_and_preprocess_data()

# =============================================================================
# HEADER PRINCIPAL
# =============================================================================

st.markdown("""
<div style='text-align: center; padding: 20px 0; border-bottom: 1px solid #2e3139;'>
    <h1 style='margin: 0; color: #ffffff;'>📊 BQuant Professional Stock Screener</h1>
    <p style='color: #b8b8b8; margin-top: 10px; font-size: 1.1em;'>
        Análisis avanzado de 5,500+ acciones con 230+ métricas
    </p>
    <p style='color: #4a9eff; margin-top: 5px;'>
        Desarrollado por <strong>@Gsnchez</strong> | <strong>bquantfinance.com</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - SELECTOR DE SCREENER Y FILTROS BÁSICOS
# =============================================================================

st.sidebar.markdown("# 🎯 Screener Selector")
st.sidebar.markdown("---")

# Selector de Screener
selected_screener = st.sidebar.selectbox(
    "📋 **Selecciona un Screener**",
    options=list(SCREENERS.keys()),
    index=list(SCREENERS.keys()).index(st.session_state.selected_screener),
    help="Elige un screener predefinido o construye el tuyo"
)

st.session_state.selected_screener = selected_screener

# Información del screener
screener_config = SCREENERS[selected_screener]
st.sidebar.info(f"📝 {screener_config['description']}")

st.sidebar.markdown("---")

# FILTROS BÁSICOS EN SIDEBAR
st.sidebar.markdown("### 🔍 Filtros Básicos")

# Búsqueda
search_term = st.sidebar.text_input("🔎 Buscar", placeholder="Ticker o nombre...")

# Sectores
sectors_filter = st.sidebar.multiselect(
    "🏢 Sectores",
    options=sorted(df['Sector'].dropna().unique()),
    default=screener_config['filters'].get('sectors', [])
)

# Market Cap
st.sidebar.markdown("**💰 Market Cap**")
col1, col2 = st.sidebar.columns(2)
with col1:
    min_mcap = st.text_input(
        "Min",
        value=f"{int(screener_config['filters'].get('market_cap_min', 0)/1e6)}M" if screener_config['filters'].get('market_cap_min', 0) > 0 else "",
        placeholder="100M"
    )
with col2:
    max_mcap = st.text_input(
        "Max",
        value=f"{int(screener_config['filters'].get('market_cap_max', 0)/1e9)}B" if screener_config['filters'].get('market_cap_max', 0) > 0 else "",
        placeholder="10B"
    )

# Exchanges
exchanges = st.sidebar.multiselect(
    "🏛️ Exchanges",
    options=sorted(df['Exchange'].dropna().unique()) if 'Exchange' in df.columns else [],
    default=[]
)

# Índices
if 'In Index' in df.columns:
    in_index = st.sidebar.multiselect(
        "📈 Índices",
        ["SP500", "NASDAQ100", "DOW30"],
        default=[]
    )
else:
    in_index = []

st.sidebar.markdown("---")

# Botón de aplicar filtros básicos
apply_basic = st.sidebar.button("🔍 **APLICAR FILTROS**", type="primary", use_container_width=True)

if apply_basic:
    st.session_state.filters_applied = True

# =============================================================================
# ÁREA PRINCIPAL - FILTROS AVANZADOS Y RESULTADOS
# =============================================================================

# Crear pestañas para organizar el contenido
tab_filters, tab_results, tab_analysis, tab_rankings, tab_sector, tab_export = st.tabs([
    "⚙️ Filtros Avanzados", 
    "📊 Resultados", 
    "📈 Análisis Visual",
    "🏆 Rankings",
    "🎯 Análisis Sectorial",
    "💾 Exportar"
])

# =============================================================================
# TAB 1: FILTROS AVANZADOS
# =============================================================================

with tab_filters:
    st.markdown("### ⚙️ Constructor de Filtros Avanzados")
    st.info("💡 Ajusta los filtros para refinar tu búsqueda. Los valores predeterminados corresponden al screener seleccionado.")
    
    # Obtener filtros del screener seleccionado
    preset_filters = screener_config.get('filters', {})
    
    # Organizar filtros en columnas
    st.markdown("---")
    st.markdown("#### 📊 Métricas de Valoración")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pe_min = st.number_input("P/E Min", value=float(preset_filters.get('pe_min', 0.0)), min_value=0.0, key="pe_min_filter")
        pb_min = st.number_input("P/B Min", value=float(preset_filters.get('pb_min', 0.0)), min_value=0.0, key="pb_min_filter")
        ps_min = st.number_input("P/S Min", value=float(preset_filters.get('ps_min', 0.0)), min_value=0.0, key="ps_min_filter")
    
    with col2:
        pe_max = st.number_input("P/E Max", value=float(preset_filters.get('pe_max', 100.0)), min_value=0.0, key="pe_max_filter")
        pb_max = st.number_input("P/B Max", value=float(preset_filters.get('pb_max', 10.0)), min_value=0.0, key="pb_max_filter")
        ps_max = st.number_input("P/S Max", value=float(preset_filters.get('ps_max', 20.0)), min_value=0.0, key="ps_max_filter")
    
    with col3:
        peg_min = st.number_input("PEG Min", value=float(preset_filters.get('peg_min', 0.0)), min_value=0.0, key="peg_min_filter")
        ev_ebitda_min = st.number_input("EV/EBITDA Min", value=float(preset_filters.get('ev_ebitda_min', 0.0)), min_value=0.0, key="ev_ebitda_min_filter")
        pcf_min = st.number_input("P/CF Min", value=float(preset_filters.get('pcf_min', 0.0)), min_value=0.0, key="pcf_min_filter")
    
    with col4:
        peg_max = st.number_input("PEG Max", value=float(preset_filters.get('peg_max', 3.0)), min_value=0.0, key="peg_max_filter")
        ev_ebitda_max = st.number_input("EV/EBITDA Max", value=float(preset_filters.get('ev_ebitda_max', 50.0)), min_value=0.0, key="ev_ebitda_max_filter")
        pcf_max = st.number_input("P/CF Max", value=float(preset_filters.get('pcf_max', 50.0)), min_value=0.0, key="pcf_max_filter")
    
    st.markdown("---")
    st.markdown("#### 📈 Métricas de Crecimiento")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rev_growth_min = st.number_input("Revenue Growth Min %", value=float(preset_filters.get('rev_growth_min', -100.0)), key="rev_growth_filter")
        eps_growth_min = st.number_input("EPS Growth Min %", value=float(preset_filters.get('eps_growth_min', -100.0)), key="eps_growth_filter")
        fcf_growth_min = st.number_input("FCF Growth Min %", value=float(preset_filters.get('fcf_growth_min', -100.0)), key="fcf_growth_filter")
    
    with col2:
        rev_growth_max = st.number_input("Revenue Growth Max %", value=float(preset_filters.get('rev_growth_max', 500.0)), key="rev_growth_max_filter")
        eps_growth_max = st.number_input("EPS Growth Max %", value=float(preset_filters.get('eps_growth_max', 500.0)), key="eps_growth_max_filter")
        rev_growth_3y_min = st.number_input("Rev CAGR 3Y Min %", value=float(preset_filters.get('rev_growth_3y_min', -100.0)), key="rev_3y_filter")
    
    with col3:
        rev_growth_5y_min = st.number_input("Rev CAGR 5Y Min %", value=float(preset_filters.get('rev_growth_5y_min', -100.0)), key="rev_5y_filter")
        eps_growth_3y_min = st.number_input("EPS CAGR 3Y Min %", value=float(preset_filters.get('eps_growth_3y_min', -100.0)), key="eps_3y_filter")
        eps_growth_5y_min = st.number_input("EPS CAGR 5Y Min %", value=float(preset_filters.get('eps_growth_5y_min', -100.0)), key="eps_5y_filter")
    
    with col4:
        rev_growth_next_min = st.number_input("Rev Growth Next Y Min %", value=float(preset_filters.get('rev_growth_next_min', -100.0)), key="rev_next_filter")
        eps_growth_next_min = st.number_input("EPS Growth Next Y Min %", value=float(preset_filters.get('eps_growth_next_min', -100.0)), key="eps_next_filter")
        earnings_yield_min = st.number_input("Earnings Yield Min %", value=float(preset_filters.get('earnings_yield_min', 0.0)), key="ey_filter")
    
    st.markdown("---")
    st.markdown("#### 💎 Rentabilidad y Márgenes")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        roe_min = st.number_input("ROE Min %", value=float(preset_filters.get('roe_min', -50.0)), key="roe_filter")
        roa_min = st.number_input("ROA Min %", value=float(preset_filters.get('roa_min', -50.0)), key="roa_filter")
        roic_min = st.number_input("ROIC Min %", value=float(preset_filters.get('roic_min', -50.0)), key="roic_filter")
    
    with col2:
        roe_max = st.number_input("ROE Max %", value=float(preset_filters.get('roe_max', 100.0)), key="roe_max_filter")
        roa_max = st.number_input("ROA Max %", value=float(preset_filters.get('roa_max', 100.0)), key="roa_max_filter")
        roce_min = st.number_input("ROCE Min %", value=float(preset_filters.get('roce_min', -50.0)), key="roce_filter")
    
    with col3:
        profit_margin_min = st.number_input("Profit Margin Min %", value=float(preset_filters.get('profit_margin_min', -100.0)), key="pm_filter")
        gross_margin_min = st.number_input("Gross Margin Min %", value=float(preset_filters.get('gross_margin_min', 0.0)), key="gm_filter")
        operating_margin_min = st.number_input("Operating Margin Min %", value=float(preset_filters.get('operating_margin_min', -100.0)), key="om_filter")
    
    with col4:
        fcf_margin_min = st.number_input("FCF Margin Min %", value=float(preset_filters.get('fcf_margin_min', -100.0)), key="fcfm_filter")
        ebitda_margin_min = st.number_input("EBITDA Margin Min %", value=float(preset_filters.get('ebitda_margin_min', -100.0)), key="ebitdam_filter")
        ebit_margin_min = st.number_input("EBIT Margin Min %", value=float(preset_filters.get('ebit_margin_min', -100.0)), key="ebitm_filter")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💵 Dividendos")
        col1a, col1b = st.columns(2)
        with col1a:
            div_yield_min = st.number_input("Dividend Yield Min %", value=float(preset_filters.get('div_yield_min', 0.0)), key="div_min_filter")
            payout_ratio_min = st.number_input("Payout Ratio Min %", value=float(preset_filters.get('payout_ratio_min', 0.0)), key="payout_min_filter")
            years_min = st.number_input("Years of Dividends Min", value=preset_filters.get('years_min', 0), min_value=0, key="years_filter")
        with col1b:
            div_yield_max = st.number_input("Dividend Yield Max %", value=float(preset_filters.get('div_yield_max', 20.0)), key="div_max_filter")
            payout_ratio_max = st.number_input("Payout Ratio Max %", value=float(preset_filters.get('payout_ratio_max', 100.0)), key="payout_max_filter")
            fcf_payout_ratio_max = st.number_input("FCF Payout Max %", value=float(preset_filters.get('fcf_payout_ratio_max', 100.0)), key="fcf_payout_filter")
    
    with col2:
        st.markdown("#### 🏥 Salud Financiera")
        col2a, col2b = st.columns(2)
        with col2a:
            current_ratio_min = st.number_input("Current Ratio Min", value=float(preset_filters.get('current_ratio_min', 0.0)), key="cr_filter")
            debt_equity_max = st.number_input("Debt/Equity Max", value=float(preset_filters.get('debt_equity_max', 10.0)), key="de_filter")
            z_score_min = st.number_input("Altman Z-Score Min", value=float(preset_filters.get('z_score_min', -5.0)), key="z_filter")
        with col2b:
            quick_ratio_min = st.number_input("Quick Ratio Min", value=float(preset_filters.get('quick_ratio_min', 0.0)), key="qr_filter")
            interest_coverage_min = st.number_input("Interest Coverage Min", value=float(preset_filters.get('interest_coverage_min', 0.0)), key="ic_filter")
            f_score_min = st.number_input("Piotroski F-Score Min", value=preset_filters.get('f_score_min', 0), min_value=0, max_value=9, key="f_filter")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📉 Indicadores Técnicos")
        col1a, col1b = st.columns(2)
        with col1a:
            rsi_min = st.number_input("RSI Min", value=float(preset_filters.get('rsi_min', 0.0)), min_value=0.0, max_value=100.0, key="rsi_min_filter")
            beta_min = st.number_input("Beta Min", value=float(preset_filters.get('beta_min', 0.0)), min_value=0.0, key="beta_min_filter")
            rel_volume_min = st.number_input("Relative Volume Min", value=float(preset_filters.get('rel_volume_min', 0.0)), key="rv_filter")
        with col1b:
            rsi_max = st.number_input("RSI Max", value=float(preset_filters.get('rsi_max', 100.0)), min_value=0.0, max_value=100.0, key="rsi_max_filter")
            beta_max = st.number_input("Beta Max", value=float(preset_filters.get('beta_max', 5.0)), min_value=0.0, key="beta_max_filter")
            volume_ratio_min = st.number_input("Volume/Avg Min", value=float(preset_filters.get('volume_ratio_min', 0.0)), key="vr_filter")
    
    with col2:
        st.markdown("#### 📊 Retornos")
        col2a, col2b = st.columns(2)
        with col2a:
            return_1y_min = st.number_input("Return 1Y Min %", value=float(preset_filters.get('return_1y_min', -100.0)), key="r1y_filter")
            return_6m_min = st.number_input("Return 6M Min %", value=float(preset_filters.get('return_6m_min', -100.0)), key="r6m_filter")
            return_3m_min = st.number_input("Return 3M Min %", value=float(preset_filters.get('return_3m_min', -100.0)), key="r3m_filter")
        with col2b:
            return_1m_min = st.number_input("Return 1M Min %", value=float(preset_filters.get('return_1m_min', -100.0)), key="r1m_filter")
            return_ytd_min = st.number_input("Return YTD Min %", value=float(preset_filters.get('return_ytd_min', -100.0)), key="rytd_filter")
            distance_52w_high_max = st.number_input("Distance from 52W High Max %", value=float(preset_filters.get('distance_52w_high_max', 100.0)), key="d52w_filter")
    
    st.markdown("---")
    st.markdown("#### 🎯 Scores Algorítmicos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        quality_score_min = st.slider("**Quality Score Min**", 0, 100, 
                                     value=int(preset_filters.get('quality_score_min', 0)), key="qs_filter")
        value_score_min = st.slider("**Value Score Min**", 0, 100,
                                   value=int(preset_filters.get('value_score_min', 0)), key="vs_filter")
    
    with col2:
        growth_score_min = st.slider("**Growth Score Min**", 0, 100,
                                    value=int(preset_filters.get('growth_score_min', 0)), key="gs_filter")
        financial_health_score_min = st.slider("**Financial Health Min**", 0, 100,
                                              value=int(preset_filters.get('financial_health_score_min', 0)), key="fhs_filter")
    
    with col3:
        momentum_score_min = st.slider("**Momentum Score Min**", 0, 100,
                                      value=int(preset_filters.get('momentum_score_min', 0)), key="ms_filter")
        master_score_min = st.slider("**Master Score Min**", 0, 100,
                                    value=int(preset_filters.get('master_score_min', 0)), key="master_filter")
    
    st.markdown("---")
    st.markdown("#### 👥 Propiedad")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        insider_ownership_min = st.number_input("Insider Ownership Min %", value=float(preset_filters.get('insider_ownership_min', 0.0)), key="io_min_filter")
        insider_ownership_max = st.number_input("Insider Ownership Max %", value=float(preset_filters.get('insider_ownership_max', 100.0)), key="io_max_filter")
    
    with col2:
        institutional_ownership_min = st.number_input("Inst. Ownership Min %", value=float(preset_filters.get('institutional_ownership_min', 0.0)), key="inst_min_filter")
        institutional_ownership_max = st.number_input("Inst. Ownership Max %", value=float(preset_filters.get('institutional_ownership_max', 100.0)), key="inst_max_filter")
    
    with col3:
        short_float_min = st.number_input("Short % Float Min", value=float(preset_filters.get('short_float_min', 0.0)), key="sf_min_filter")
        short_float_max = st.number_input("Short % Float Max", value=float(preset_filters.get('short_float_max', 100.0)), key="sf_max_filter")
    
    # Botón de aplicar filtros avanzados
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        apply_advanced = st.button("⚡ **APLICAR TODOS LOS FILTROS**", type="primary", use_container_width=True, key="apply_advanced")
    
    if apply_advanced:
        st.session_state.filters_applied = True
        st.success("✅ Filtros aplicados correctamente")

# =============================================================================
# APLICACIÓN DE FILTROS
# =============================================================================

if st.session_state.filters_applied:
    
    filtered_df = df.copy()
    
    # Filtros básicos
    if search_term:
        filtered_df = filtered_df[
            (filtered_df['Symbol'].str.contains(search_term.upper(), na=False)) |
            (filtered_df['Company Name'].str.contains(search_term, case=False, na=False))
        ]
    
    if sectors_filter:
        filtered_df = filtered_df[filtered_df['Sector'].isin(sectors_filter)]
    
    if exchanges and 'Exchange' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Exchange'].isin(exchanges)]
    
    if in_index and 'In Index' in filtered_df.columns:
        for index in in_index:
            filtered_df = filtered_df[filtered_df['In Index'].str.contains(index, na=False)]
    
    # Market Cap
    min_mc = parse_market_cap(min_mcap)
    max_mc = parse_market_cap(max_mcap)
    if min_mc is not None and 'Market Cap' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Market Cap'] >= min_mc]
    if max_mc is not None and 'Market Cap' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Market Cap'] <= max_mc]
    
    # Aplicar TODOS los filtros numéricos de manera eficiente
    # Crear lista de todos los filtros para aplicar
    filters_to_apply = {
        'PE Ratio': (pe_min, pe_max),
        'PB Ratio': (pb_min, pb_max),
        'PS Ratio': (ps_min, ps_max),
        'PEG Ratio': (peg_min, peg_max),
        'EV/EBITDA': (ev_ebitda_min, ev_ebitda_max),
        'P/CF': (pcf_min, pcf_max),
        'Rev. Growth': (rev_growth_min, rev_growth_max),
        'EPS Growth': (eps_growth_min, eps_growth_max),
        'FCF Growth': (fcf_growth_min, None),
        'ROE': (roe_min, roe_max),
        'ROA': (roa_min, roa_max),
        'ROIC': (roic_min, None),
        'ROCE': (roce_min, None),
        'Profit Margin': (profit_margin_min, None),
        'Gross Margin': (gross_margin_min, None),
        'Operating Margin': (operating_margin_min, None),
        'FCF Margin': (fcf_margin_min, None),
        'EBITDA Margin': (ebitda_margin_min, None),
        'EBIT Margin': (ebit_margin_min, None),
        'Div. Yield': (div_yield_min, div_yield_max),
        'Payout Ratio': (payout_ratio_min, payout_ratio_max),
        'Years': (years_min, None),
        'Current Ratio': (current_ratio_min, None),
        'Quick Ratio': (quick_ratio_min, None),
        'Debt / Equity': (None, debt_equity_max),
        'Int. Cov.': (interest_coverage_min, None),
        'Z-Score': (z_score_min, None),
        'F-Score': (f_score_min, None),
        'RSI': (rsi_min, rsi_max),
        'Beta (5Y)': (beta_min, beta_max),
        'Rel. Volume': (rel_volume_min, None),
        'Return 1Y': (return_1y_min, None),
        'Return 6M': (return_6m_min, None),
        'Return 3M': (return_3m_min, None),
        'Return 1M': (return_1m_min, None),
        'Return YTD': (return_ytd_min, None),
        'Quality_Score': (quality_score_min, None),
        'Value_Score': (value_score_min, None),
        'Growth_Score': (growth_score_min, None),
        'Financial_Health_Score': (financial_health_score_min, None),
        'Momentum_Score': (momentum_score_min, None),
        'Master_Score': (master_score_min, None),
    }
    
    # Aplicar cada filtro
    for col_name, (min_val, max_val) in filters_to_apply.items():
        if col_name in filtered_df.columns:
            if min_val is not None and min_val != -100.0 and min_val != 0.0:
                filtered_df = filtered_df[filtered_df[col_name] >= min_val]
            if max_val is not None and max_val != 100.0 and max_val != 500.0:
                filtered_df = filtered_df[filtered_df[col_name] <= max_val]
    
    # =============================================================================
    # MÉTRICAS RESUMEN
    # =============================================================================
    
    st.markdown("---")
    
    # Métricas principales
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("📊 Acciones", f"{len(filtered_df):,}", f"{len(filtered_df)/len(df)*100:.1f}% del total")
    with col2:
        total_mcap = filtered_df['Market Cap'].sum() if 'Market Cap' in filtered_df.columns else 0
        st.metric("💰 Cap Total", format_number(total_mcap, prefix="$", decimals=1))
    with col3:
        median_pe = filtered_df['PE Ratio'].median() if 'PE Ratio' in filtered_df.columns else 0
        st.metric("P/E Med", f"{median_pe:.1f}")
    with col4:
        avg_yield = filtered_df['Div. Yield'].mean() if 'Div. Yield' in filtered_df.columns else 0
        st.metric("Yield", f"{avg_yield:.2f}%")
    with col5:
        median_roe = filtered_df['ROE'].median() if 'ROE' in filtered_df.columns else 0
        st.metric("ROE Med", f"{median_roe:.1f}%")
    with col6:
        avg_master = filtered_df['Master_Score'].mean() if 'Master_Score' in filtered_df.columns else 0
        st.metric("Score", f"{avg_master:.0f}/100")
    
    # =============================================================================
    # TAB 2: RESULTADOS
    # =============================================================================
    
    with tab_results:
        st.markdown(f"### 📊 Resultados del Screener: {selected_screener}")
        
        # Configuración de vista
        with st.expander("⚙️ Configurar Vista", expanded=False):
            
            # Columnas predeterminadas según el screener
            if "Value" in selected_screener or "Graham" in selected_screener:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'PE Ratio', 'PB Ratio', 
                              'Value_Score', 'FCF Yield', 'Current Ratio', 'Sector']
            elif "Growth" in selected_screener or "GARP" in selected_screener:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'Rev. Growth', 
                              'EPS Growth', 'Growth_Score', 'PEG Ratio', 'Sector']
            elif "Dividend" in selected_screener:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'Div. Yield', 
                              'Payout Ratio', 'Years', 'Financial_Health_Score', 'Sector']
            elif "Quality" in selected_screener or "Defensive" in selected_screener:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'ROE', 'ROIC', 
                              'Quality_Score', 'Profit Margin', 'Sector']
            elif "Momentum" in selected_screener or "Breakout" in selected_screener:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'Return 1Y', 'RSI',
                              'Momentum_Score', 'Rel. Volume', 'Sector']
            elif "Quant" in selected_screener or "Factor" in selected_screener:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'Master_Score', 
                              'Quality_Score', 'Value_Score', 'Growth_Score', 'Momentum_Score']
            else:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'PE Ratio', 
                              'ROE', 'Master_Score', 'Sector']
            
            available_cols = [col for col in default_cols if col in filtered_df.columns]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_columns = st.multiselect("Columnas:", options=filtered_df.columns.tolist(), 
                                                 default=available_cols)
            with col2:
                sort_column = st.selectbox("Ordenar por:", 
                                          options=selected_columns if selected_columns else ['Symbol'])
                sort_order = st.radio("Orden:", ["Descendente", "Ascendente"], horizontal=True)
            with col3:
                n_rows = st.select_slider("Filas a mostrar:", options=[25, 50, 100, 200, 500], value=100)
        
        # Mostrar tabla de resultados
        if selected_columns:
            display_df = filtered_df[selected_columns].sort_values(
                by=sort_column,
                ascending=(sort_order == "Ascendente")
            ).head(n_rows)
            
            # Formateo
            format_dict = {}
            for col in selected_columns:
                if 'Market Cap' in col or 'Revenue' in col:
                    format_dict[col] = lambda x: format_number(x, prefix="$", decimals=1)
                elif any(term in col for term in ['Yield', 'Growth', 'ROE', 'ROA', 'Margin', '%']):
                    format_dict[col] = '{:.2f}%'
                elif 'Score' in col:
                    format_dict[col] = '{:.0f}'
                elif any(term in col for term in ['Ratio', 'PE', 'PB', 'PS', 'PEG']):
                    format_dict[col] = '{:.2f}'
            
            # Aplicar color gradient a scores
            score_cols = [col for col in selected_columns if 'Score' in col]
            
            styled_df = display_df.style.format(format_dict, na_rep='N/A')
            if score_cols:
                styled_df = styled_df.background_gradient(cmap='RdYlGn', subset=score_cols, vmin=0, vmax=100)
            
            st.dataframe(styled_df, use_container_width=True, height=600)
            
            # Información de resultados
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success(f"✅ {len(display_df)} de {len(filtered_df)} resultados mostrados")
            with col2:
                st.info(f"📊 Total en universo: {len(df):,} acciones")
            with col3:
                active_filters = sum(1 for x in [search_term, sectors_filter, min_mc, max_mc] if x)
                st.warning(f"🔍 Filtros activos: {active_filters}")
    
    # =============================================================================
    # TAB 3: ANÁLISIS VISUAL
    # =============================================================================
    
    with tab_analysis:
        st.markdown("### 📈 Dashboard de Análisis Visual")
        
        # Primera fila de gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Scatter: Value vs Quality
            if all(col in filtered_df.columns for col in ['Value_Score', 'Quality_Score']):
                fig = px.scatter(
                    filtered_df.head(300),
                    x='Value_Score',
                    y='Quality_Score',
                    size='Market Cap' if 'Market Cap' in filtered_df.columns else None,
                    color='Master_Score',
                    hover_data=['Symbol', 'Company Name'],
                    title="📊 Matriz Value vs Quality",
                    color_continuous_scale='Viridis',
                    labels={'Value_Score': 'Value Score', 'Quality_Score': 'Quality Score'}
                )
                fig.add_hline(y=50, line_dash="dash", opacity=0.3)
                fig.add_vline(x=50, line_dash="dash", opacity=0.3)
                fig.update_layout(template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Scatter: Growth vs Momentum
            if all(col in filtered_df.columns for col in ['Growth_Score', 'Momentum_Score']):
                fig = px.scatter(
                    filtered_df.head(300),
                    x='Growth_Score',
                    y='Momentum_Score',
                    size='Market Cap' if 'Market Cap' in filtered_df.columns else None,
                    color='Financial_Health_Score' if 'Financial_Health_Score' in filtered_df.columns else None,
                    hover_data=['Symbol', 'Company Name'],
                    title="🚀 Matriz Growth vs Momentum",
                    color_continuous_scale='RdYlGn',
                    labels={'Growth_Score': 'Growth Score', 'Momentum_Score': 'Momentum Score'}
                )
                fig.add_hline(y=50, line_dash="dash", opacity=0.3)
                fig.add_vline(x=50, line_dash="dash", opacity=0.3)
                fig.update_layout(template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Segunda fila - Distribuciones
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución por sector
            if 'Sector' in filtered_df.columns:
                sector_data = filtered_df['Sector'].value_counts().head(10)
                fig = px.bar(
                    sector_data, # Pass the Series directly
                    orientation='h',
                    title="🏢 Top 10 Sectores",
                    labels={'value': 'Número de Acciones', 'index': 'Sector'}, 
                    color_discrete_sequence=['#4a9eff']
                )
                fig.update_layout(yaxis={'categoryorder':'total ascending'}) 
                
                fig.update_layout(template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Histograma de Master Score
            if 'Master_Score' in filtered_df.columns:
                fig = px.histogram(
                    filtered_df,
                    x='Master_Score',
                    nbins=20,
                    title="📊 Distribución del Master Score",
                    labels={'Master_Score': 'Master Score', 'count': 'Frecuencia'},
                    color_discrete_sequence=['#4a9eff']
                )
                fig.add_vline(x=filtered_df['Master_Score'].median(), line_dash="dash", 
                            annotation_text=f"Mediana: {filtered_df['Master_Score'].median():.0f}")
                fig.update_layout(template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Tercera fila - Heatmap de correlaciones
        st.markdown("---")
        st.markdown("### 🔥 Matriz de Correlación de Scores")
        
        score_cols = ['Master_Score', 'Quality_Score', 'Value_Score', 'Growth_Score', 
                     'Financial_Health_Score', 'Momentum_Score']
        available_scores = [col for col in score_cols if col in filtered_df.columns]
        
        if len(available_scores) > 1:
            corr_matrix = filtered_df[available_scores].corr()
            fig = px.imshow(
                corr_matrix,
                title="Correlaciones entre Scores",
                color_continuous_scale='RdBu',
                aspect='auto',
                zmin=-1, zmax=1,
                text_auto='.2f'
            )
            fig.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    # =============================================================================
    # TAB 4: RANKINGS
    # =============================================================================
    
    with tab_rankings:
        st.markdown("### 🏆 Rankings por Categorías")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 💎 **Top Value**")
            if 'Value_Score' in filtered_df.columns:
                top_value = filtered_df.nlargest(10, 'Value_Score')[['Symbol', 'Company Name', 'Value_Score', 'PE Ratio']]
                for idx, row in top_value.iterrows():
                    color = "#4caf50" if row['Value_Score'] > 80 else "#ff9800" if row['Value_Score'] > 60 else "#f44336"
                    st.markdown(f"<span style='color: {color}'>**{row['Symbol']}** - Score: {row['Value_Score']:.0f}</span>", unsafe_allow_html=True)
                    st.caption(f"{row['Company Name'][:30]} | P/E: {row['PE Ratio']:.1f}")
        
        with col2:
            st.markdown("#### 🚀 **Top Growth**")
            if 'Growth_Score' in filtered_df.columns:
                top_growth = filtered_df.nlargest(10, 'Growth_Score')[['Symbol', 'Company Name', 'Growth_Score', 'Rev. Growth']]
                for idx, row in top_growth.iterrows():
                    color = "#4caf50" if row['Growth_Score'] > 80 else "#ff9800" if row['Growth_Score'] > 60 else "#f44336"
                    st.markdown(f"<span style='color: {color}'>**{row['Symbol']}** - Score: {row['Growth_Score']:.0f}</span>", unsafe_allow_html=True)
                    st.caption(f"{row['Company Name'][:30]} | Rev: {row['Rev. Growth']:.1f}%")
        
        with col3:
            st.markdown("#### 🏅 **Top Quality**")
            if 'Quality_Score' in filtered_df.columns:
                top_quality = filtered_df.nlargest(10, 'Quality_Score')[['Symbol', 'Company Name', 'Quality_Score', 'ROE']]
                for idx, row in top_quality.iterrows():
                    color = "#4caf50" if row['Quality_Score'] > 80 else "#ff9800" if row['Quality_Score'] > 60 else "#f44336"
                    st.markdown(f"<span style='color: {color}'>**{row['Symbol']}** - Score: {row['Quality_Score']:.0f}</span>", unsafe_allow_html=True)
                    st.caption(f"{row['Company Name'][:30]} | ROE: {row['ROE']:.1f}%")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📈 **Top Momentum**")
            if 'Momentum_Score' in filtered_df.columns:
                top_momentum = filtered_df.nlargest(10, 'Momentum_Score')[['Symbol', 'Company Name', 'Momentum_Score', 'Return 1Y']]
                for idx, row in top_momentum.iterrows():
                    color = "#4caf50" if row['Momentum_Score'] > 80 else "#ff9800" if row['Momentum_Score'] > 60 else "#f44336"
                    st.markdown(f"<span style='color: {color}'>**{row['Symbol']}** - Score: {row['Momentum_Score']:.0f}</span>", unsafe_allow_html=True)
                    st.caption(f"{row['Company Name'][:30]} | 1Y: {row['Return 1Y']:.1f}%")
        
        with col2:
            st.markdown("#### 💰 **Top Dividend**")
            if 'Div. Yield' in filtered_df.columns:
                top_dividend = filtered_df[filtered_df['Div. Yield'] > 0].nlargest(10, 'Div. Yield')[['Symbol', 'Company Name', 'Div. Yield', 'Payout Ratio']]
                for idx, row in top_dividend.iterrows():
                    color = "#4caf50" if row['Payout Ratio'] < 60 else "#ff9800" if row['Payout Ratio'] < 80 else "#f44336"
                    st.markdown(f"<span style='color: {color}'>**{row['Symbol']}** - Yield: {row['Div. Yield']:.2f}%</span>", unsafe_allow_html=True)
                    st.caption(f"{row['Company Name'][:30]} | Payout: {row['Payout Ratio']:.1f}%")
        
        with col3:
            st.markdown("#### 🏥 **Top Financial Health**")
            if 'Financial_Health_Score' in filtered_df.columns:
                top_health = filtered_df.nlargest(10, 'Financial_Health_Score')[['Symbol', 'Company Name', 'Financial_Health_Score', 'Current Ratio']]
                for idx, row in top_health.iterrows():
                    color = "#4caf50" if row['Financial_Health_Score'] > 80 else "#ff9800" if row['Financial_Health_Score'] > 60 else "#f44336"
                    st.markdown(f"<span style='color: {color}'>**{row['Symbol']}** - Score: {row['Financial_Health_Score']:.0f}</span>", unsafe_allow_html=True)
                    st.caption(f"{row['Company Name'][:30]} | CR: {row['Current Ratio']:.2f}")
    
    # =============================================================================
    # TAB 5: ANÁLISIS SECTORIAL
    # =============================================================================
    
    with tab_sector:
        st.markdown("### 🎯 Análisis Sectorial Profundo")
        
        if 'Sector' in filtered_df.columns:
            # Métricas por sector
            sector_metrics = filtered_df.groupby('Sector').agg({
                'Symbol': 'count',
                'Market Cap': 'sum',
                'PE Ratio': 'median',
                'ROE': 'median',
                'Rev. Growth': 'median',
                'Div. Yield': 'mean',
                'Master_Score': 'mean'
            }).round(2)
            
            sector_metrics.columns = ['Acciones', 'Cap Total', 'P/E Med', 'ROE Med', 
                                     'Crec Med', 'Yield Prom', 'Master Score']
            sector_metrics = sector_metrics.sort_values('Master Score', ascending=False)
            
            # Mostrar tabla
            st.dataframe(
                sector_metrics.style.format({
                    'Cap Total': lambda x: format_number(x, prefix="$", decimals=1),
                    'P/E Med': '{:.1f}',
                    'ROE Med': '{:.1f}%',
                    'Crec Med': '{:.1f}%',
                    'Yield Prom': '{:.2f}%',
                    'Master Score': '{:.0f}'
                }).background_gradient(cmap='RdYlGn', subset=['Master Score', 'ROE Med']),
                use_container_width=True
            )
            
            # Gráfico de burbujas
            st.markdown("---")
            st.markdown("### 📊 Mapa de Oportunidades Sectoriales")
            
            sector_data = sector_metrics.reset_index()
            sector_data = sector_data[sector_data['Acciones'] >= 3]  # Solo sectores con 3+ acciones
            
            if len(sector_data) > 0:
                fig = px.scatter(
                    sector_data,
                    x='P/E Med',
                    y='ROE Med',
                    size='Cap Total',
                    color='Master Score',
                    hover_data=['Acciones', 'Yield Prom', 'Crec Med'],
                    text='Sector',
                    title="Sectores: Valoración vs Rentabilidad",
                    color_continuous_scale='RdYlGn',
                    labels={'P/E Med': 'P/E Mediano', 'ROE Med': 'ROE Mediano (%)'}
                )
                
                # Añadir líneas de referencia
                fig.add_hline(y=15, line_dash="dash", line_color="gray", opacity=0.5)
                fig.add_vline(x=20, line_dash="dash", line_color="gray", opacity=0.5)
                
                fig.update_traces(textposition='top center')
                fig.update_layout(template="plotly_dark", height=600)
                st.plotly_chart(fig, use_container_width=True)
    
    # =============================================================================
    # TAB 6: EXPORTAR
    # =============================================================================
    
    with tab_export:
        st.markdown("### 💾 Exportar Resultados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"📊 **{len(filtered_df):,}** acciones filtradas listas para exportar")
            
            export_preset = st.selectbox(
                "Preset de exportación:",
                ["Columnas Actuales", "Datos Básicos", "Análisis Completo", "Solo Scores", "Personalizado"]
            )
            
            if export_preset == "Columnas Actuales":
                export_cols = selected_columns if 'selected_columns' in locals() else ['Symbol', 'Company Name']
            elif export_preset == "Datos Básicos":
                export_cols = ['Symbol', 'Company Name', 'Market Cap', 'PE Ratio', 'ROE', 'Div. Yield', 'Master_Score']
            elif export_preset == "Solo Scores":
                export_cols = ['Symbol', 'Company Name', 'Master_Score', 'Quality_Score', 
                              'Value_Score', 'Growth_Score', 'Financial_Health_Score', 'Momentum_Score']
            elif export_preset == "Análisis Completo":
                export_cols = filtered_df.columns.tolist()
            else:
                export_cols = st.multiselect(
                    "Selecciona columnas:",
                    options=filtered_df.columns.tolist(),
                    default=['Symbol', 'Company Name', 'Market Cap', 'Master_Score']
                )
            
            # Filtrar columnas disponibles
            export_cols = [col for col in export_cols if col in filtered_df.columns]
        
        with col2:
            st.markdown("#### 📥 Descargar Datos")
            
            # CSV
            csv = filtered_df[export_cols].to_csv(index=False)
            st.download_button(
                label="📄 Descargar CSV",
                data=csv,
                file_name=f"bquant_screener_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Excel
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    # Hoja de resultados
                    filtered_df[export_cols].to_excel(writer, sheet_name='Screener Results', index=False)
                    
                    # Hoja de información
                    info_data = {
                        'Información': ['Fecha', 'Screener', 'Total Resultados', 'Filtros Aplicados'],
                        'Valor': [
                            pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                            selected_screener,
                            len(filtered_df),
                            f"{search_term or 'N/A'}, {', '.join(sectors_filter) if sectors_filter else 'Todos'}"
                        ]
                    }
                    pd.DataFrame(info_data).to_excel(writer, sheet_name='Info', index=False)
                
                st.download_button(
                    label="📗 Descargar Excel",
                    data=buffer.getvalue(),
                    file_name=f"bquant_screener_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except:
                st.info("Instala `openpyxl` para exportar a Excel: `pip install openpyxl`")
        
        # Vista previa
        st.markdown("---")
        st.markdown("#### 👁️ Vista Previa de Exportación")
        st.dataframe(filtered_df[export_cols].head(10), use_container_width=True)

else:
    # Si no se han aplicado filtros, mostrar mensaje
    st.info("👈 Selecciona un screener y aplica filtros para ver resultados")
    
    # Mostrar algunos stats generales
    st.markdown("### 📊 Estadísticas Generales del Universo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Acciones", f"{len(df):,}")
    with col2:
        st.metric("Sectores", f"{df['Sector'].nunique()}")
    with col3:
        median_pe = df['PE Ratio'].median() if 'PE Ratio' in df.columns else 0
        st.metric("P/E Mediano", f"{median_pe:.1f}")
    with col4:
        total_mcap = df['Market Cap'].sum() if 'Market Cap' in df.columns else 0
        st.metric("Cap. Total", format_number(total_mcap, prefix="$", decimals=0))

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #b8b8b8;'>
    <strong>BQuant Professional Stock Screener</strong><br>
    Desarrollado por <strong>@Gsnchez</strong> | <strong>bquantfinance.com</strong><br>
    <small>Base de datos: 5,500+ acciones | 230+ métricas | Actualizado: Sept 2025</small>
</div>
""", unsafe_allow_html=True)

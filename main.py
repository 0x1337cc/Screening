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
# ÁREA PRINCIPAL - PESTAÑAS
# =============================================================================
tab_filters, tab_results, tab_analysis, tab_rankings, tab_sector, tab_export = st.tabs(["⚙️ Filtros Avanzados", "📊 Resultados", "📈 Análisis Visual", "🏆 Rankings", "🎯 Análisis Sectorial", "💾 Exportar"])

with tab_filters:
    st.markdown("### ⚙️ Constructor de Filtros Avanzados")
    st.info("💡 Introduce valores en los campos para filtrar. Solo se aplicarán los filtros que rellenes.")
    
    st.markdown("---")
    st.markdown("#### 📊 Métricas de Valoración")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pe_min = st.number_input("P/E Min", value=None, placeholder="Ej: 0", format="%.2f")
        pb_min = st.number_input("P/B Min", value=None, placeholder="Ej: 0", format="%.2f")
    with col2:
        pe_max = st.number_input("P/E Max", value=None, placeholder="Ej: 20", format="%.2f")
        pb_max = st.number_input("P/B Max", value=None, placeholder="Ej: 2.5", format="%.2f")
    with col3:
        ps_min = st.number_input("P/S Min", value=None, placeholder="Ej: 0", format="%.2f")
        peg_min = st.number_input("PEG Min", value=None, placeholder="Ej: 0", format="%.2f")
    with col4:
        ps_max = st.number_input("P/S Max", value=None, placeholder="Ej: 3", format="%.2f")
        peg_max = st.number_input("PEG Max", value=None, placeholder="Ej: 1.2", format="%.2f")

    with st.expander("➕ Más filtros de Valoración"):
        st.markdown("##### Ratios sobre Valor de Empresa (EV)")
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            ev_ebitda_min = st.number_input("EV/EBITDA Min", value=None, format="%.2f")
            ev_sales_min = st.number_input("EV/Sales Min", value=None, format="%.2f")
        with ec2:
            ev_ebitda_max = st.number_input("EV/EBITDA Max", value=None, format="%.2f")
            ev_sales_max = st.number_input("EV/Sales Max", value=None, format="%.2f")
        with ec3:
            ev_fcf_min = st.number_input("EV/FCF Min", value=None, format="%.2f")
            ev_fcf_max = st.number_input("EV/FCF Max", value=None, format="%.2f")

        st.markdown("##### Ratios sobre Flujo de Caja (Cash Flow)")
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            pcf_min = st.number_input("P/CF Min", value=None, format="%.2f")
            pfcf_min = st.number_input("P/FCF Min", value=None, format="%.2f")
        with ec2:
            pcf_max = st.number_input("P/CF Max", value=None, format="%.2f")
            pfcf_max = st.number_input("P/FCF Max", value=None, format="%.2f")
        with ec3:
            fcf_yield_min = st.number_input("FCF Yield Min %", value=None, format="%.2f")
            earnings_yield_min = st.number_input("Earnings Yield Min %", value=None, format="%.2f")

        st.markdown("##### Ratios sobre Valor Contable (Book Value)")
        ec1, ec2 = st.columns(2)
        with ec1:
            ptbv_min = st.number_input("P/TBV Min", value=None, format="%.2f")
        with ec2:
            ptbv_max = st.number_input("P/TBV Max", value=None, format="%.2f")
        
        st.markdown("##### Fórmulas de Valor Intrínseco")
        ec1, ec2 = st.columns(2)
        with ec1:
            graham_upside_min = st.number_input("Graham Upside Min %", value=None, format="%.2f")
        with ec2:
            lynch_upside_min = st.number_input("Lynch FV Upside Min %", value=None, format="%.2f")
    
    st.markdown("---")
    st.markdown("#### 📈 Métricas de Crecimiento")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        rev_growth_min = st.number_input("Rev Growth TTM Min %", value=None, format="%.2f")
        eps_growth_min = st.number_input("EPS Growth TTM Min %", value=None, format="%.2f")
    with col2:
        rev_growth_max = st.number_input("Rev Growth TTM Max %", value=None, format="%.2f")
        eps_growth_max = st.number_input("EPS Growth TTM Max %", value=None, format="%.2f")
    with col3:
        rev_growth_3y_min = st.number_input("Rev CAGR 3Y Min %", value=None, format="%.2f")
        eps_growth_3y_min = st.number_input("EPS CAGR 3Y Min %", value=None, format="%.2f")
    with col4:
        rev_growth_5y_min = st.number_input("Rev CAGR 5Y Min %", value=None, format="%.2f")
        eps_growth_5y_min = st.number_input("EPS CAGR 5Y Min %", value=None, format="%.2f")

    with st.expander("➕ Más filtros de Crecimiento"):
        st.markdown("##### Crecimiento Estimado (Forward)")
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            rev_growth_next_y_min = st.number_input("Rev Growth Next Y Min %", value=None, format="%.2f")
            eps_growth_next_y_min = st.number_input("EPS Growth Next Y Min %", value=None, format="%.2f")
        with ec2:
            rev_growth_next_5y_min = st.number_input("Rev Growth Next 5Y Min %", value=None, format="%.2f")
            eps_growth_next_5y_min = st.number_input("EPS Growth Next 5Y Min %", value=None, format="%.2f")
        with ec3:
            rev_growth_next_q_min = st.number_input("Rev Growth Next Q Min %", value=None, format="%.2f")
            eps_growth_next_q_min = st.number_input("EPS Growth Next Q Min %", value=None, format="%.2f")

        st.markdown("##### Crecimiento del Flujo de Caja (FCF)")
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            fcf_growth_min = st.number_input("FCF Growth TTM Min %", value=None, format="%.2f")
        with ec2:
            fcf_growth_3y_min = st.number_input("FCF CAGR 3Y Min %", value=None, format="%.2f")
        with ec3:
            fcf_growth_5y_min = st.number_input("FCF CAGR 5Y Min %", value=None, format="%.2f")
            
    st.markdown("---")
    st.markdown("#### 💎 Rentabilidad y Márgenes")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        roe_min = st.number_input("ROE Min %", value=None, format="%.2f")
        roa_min = st.number_input("ROA Min %", value=None, format="%.2f")
    with col2:
        roic_min = st.number_input("ROIC Min %", value=None, format="%.2f")
        roce_min = st.number_input("ROCE Min %", value=None, format="%.2f")
    with col3:
        profit_margin_min = st.number_input("Profit Margin Min %", value=None, format="%.2f")
        gross_margin_min = st.number_input("Gross Margin Min %", value=None, format="%.2f")
    with col4:
        operating_margin_min = st.number_input("Operating Margin Min %", value=None, format="%.2f")
        fcf_margin_min = st.number_input("FCF Margin Min %", value=None, format="%.2f")

    with st.expander("➕ Más filtros de Rentabilidad"):
        st.markdown("##### Márgenes Adicionales")
        ec1, ec2 = st.columns(2)
        with ec1:
            ebitda_margin_min = st.number_input("EBITDA Margin Min %", value=None, format="%.2f")
        with ec2:
            ebit_margin_min = st.number_input("EBIT Margin Min %", value=None, format="%.2f")
        
        st.markdown("##### Rentabilidad Media (Consistencia)")
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            roe_5y_min = st.number_input("ROE (5Y Avg) Min %", value=None, format="%.2f")
        with ec2:
            roa_5y_min = st.number_input("ROA (5Y Avg) Min %", value=None, format="%.2f")
        with ec3:
            roic_5y_min = st.number_input("ROIC (5Y Avg) Min %", value=None, format="%.2f")
        
        st.markdown("##### Eficiencia")
        ec1, ec2 = st.columns(2)
        with ec1:
            asset_turnover_min = st.number_input("Asset Turnover Min", value=None, format="%.2f")
        with ec2:
            rd_rev_min = st.number_input("R&D / Revenue Min %", value=None, format="%.2f")
    
    st.markdown("---")
    st.markdown("#### 🏥 Salud Financiera")
    col1, col2, col3 = st.columns(3)
    with col1:
        current_ratio_min = st.number_input("Current Ratio Min", value=None, format="%.2f")
        quick_ratio_min = st.number_input("Quick Ratio Min", value=None, format="%.2f")
    with col2:
        debt_equity_max = st.number_input("Debt/Equity Max", value=None, format="%.2f")
        debt_ebitda_max = st.number_input("Debt/EBITDA Max", value=None, format="%.2f")
    with col3:
        z_score_min = st.number_input("Altman Z-Score Min", value=None, format="%.2f")
        f_score_min = st.number_input("Piotroski F-Score Min", value=None, min_value=0, max_value=9, step=1)

    with st.expander("➕ Más filtros de Salud Financiera"):
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            debt_fcf_max = st.number_input("Debt/FCF Max", value=None, format="%.2f")
            interest_coverage_min = st.number_input("Interest Coverage Min", value=None, format="%.2f")
        with ec2:
            cash_mcap_min = st.number_input("Total Cash / M.Cap Min %", value=None, format="%.2f")
            debt_growth_yoy_max = st.number_input("Debt Growth (YoY) Max %", value=None, format="%.2f")
        with ec3:
            total_debt_min = st.number_input("Total Debt Min ($)", value=None)
            total_cash_min = st.number_input("Total Cash Min ($)", value=None)

    st.markdown("---")
    st.markdown("#### 💵 Dividendos y Retorno al Accionista")
    col1, col2, col3 = st.columns(3)
    with col1:
        div_yield_min = st.number_input("Dividend Yield Min %", value=None, format="%.2f")
        div_yield_max = st.number_input("Dividend Yield Max %", value=None, format="%.2f")
    with col2:
        payout_ratio_max = st.number_input("Payout Ratio Max %", value=None, format="%.2f")
        years_min = st.number_input("Years of Div Growth Min", value=None, min_value=0, step=1)
    with col3:
        shareholder_yield_min = st.number_input("Shareholder Yield Min %", value=None, format="%.2f")
        buyback_yield_min = st.number_input("Buyback Yield Min %", value=None, format="%.2f")

    with st.expander("➕ Más filtros de Dividendos"):
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            div_growth_1y_min = st.number_input("Div Growth (1Y) Min %", value=None, format="%.2f")
        with ec2:
            div_growth_3y_min = st.number_input("Div Growth (3Y) Min %", value=None, format="%.2f")
        with ec3:
            div_growth_5y_min = st.number_input("Div Growth (5Y) Min %", value=None, format="%.2f")
    
    st.markdown("---")
    st.markdown("#### 📉 Técnicos y Retornos")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("##### Indicadores")
        rsi_min = st.number_input("RSI Min", value=None, min_value=0.0, max_value=100.0, format="%.2f")
        rsi_max = st.number_input("RSI Max", value=None, min_value=0.0, max_value=100.0, format="%.2f")
        beta_max = st.number_input("Beta Max", value=None, format="%.2f")
    with col2:
        st.markdown("##### Retornos a Corto Plazo")
        return_1w_min = st.number_input("Return 1W Min %", value=None, format="%.2f")
        return_1m_min = st.number_input("Return 1M Min %", value=None, format="%.2f")
        return_3m_min = st.number_input("Return 3M Min %", value=None, format="%.2f")
    with col3:
        st.markdown("##### Retornos a Largo Plazo")
        return_ytd_min = st.number_input("Return YTD Min %", value=None, format="%.2f")
        return_1y_min = st.number_input("Return 1Y Min %", value=None, format="%.2f")
        return_3y_min = st.number_input("Return 3Y Min %", value=None, format="%.2f")

    with st.expander("➕ Más filtros Técnicos y de Retornos"):
        ec1, ec2, ec3 = st.columns(3)
        with ec1:
            distance_52w_high_max = st.number_input("Dist from 52W High Max %", value=None, help="Ej: 10 para acciones a un 10% o menos de su máximo.", format="%.2f")
            ath_chg_max = st.number_input("Dist from All-Time High Max %", value=None, format="%.2f")
        with ec2:
            distance_52w_low_min = st.number_input("Dist from 52W Low Min %", value=None, help="Ej: 10 para acciones a un 10% o más de su mínimo.", format="%.2f")
            atl_chg_min = st.number_input("Dist from All-Time Low Min %", value=None, format="%.2f")
        with ec3:
            rel_volume_min = st.number_input("Relative Volume Min", value=None, help="Ej: 1.5 para volumen 50% superior a la media.", format="%.2f")
            atr_min = st.number_input("ATR Min", value=None, format="%.2f")
    
    st.markdown("---")
    st.markdown("#### 🏢 Perfil y Propiedad")
    col1, col2, col3 = st.columns(3)
    with col1:
        employees_min = st.number_input("Nº Empleados Min", value=None, min_value=0, step=100)
        analysts_min = st.number_input("Nº Analistas Min", value=None, min_value=0, step=1)
    with col2:
        insider_ownership_min = st.number_input("Insider Ownership Min %", value=None, format="%.2f")
        institutional_ownership_min = st.number_input("Inst. Ownership Min %", value=None, format="%.2f")
    with col3:
        short_float_max = st.number_input("Short % Float Max", value=None, format="%.2f")
        
    st.markdown("---")
    st.markdown("#### 🎯 Scores Algorítmicos")
    col1, col2, col3, col4, col5 = st.columns(5)
    quality_score_min = col1.slider("Quality", 0, 100, 0)
    value_score_min = col2.slider("Value", 0, 100, 0)
    growth_score_min = col3.slider("Growth", 0, 100, 0)
    financial_health_score_min = col4.slider("Health", 0, 100, 0)
    momentum_score_min = col5.slider("Momentum", 0, 100, 0)
    master_score_min = st.slider("**Master Score Min**", 0, 100, 0)

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    if col2.button("⚡ **APLICAR TODOS LOS FILTROS**", type="primary", use_container_width=True):
        st.session_state.filters_applied = True
            
# =============================================================================
# APLICACIÓN DE FILTROS
# =============================================================================
if st.session_state.filters_applied:
    filtered_df = df.copy()
    
    # Filtros básicos
    if search_term: filtered_df = filtered_df[filtered_df['Symbol'].str.contains(search_term.upper(), na=False) | filtered_df['Company Name'].str.contains(search_term, case=False, na=False)]
    if sectors_filter: filtered_df = filtered_df[filtered_df['Sector'].isin(sectors_filter)]
    if exchanges: filtered_df = filtered_df[filtered_df['Exchange'].isin(exchanges)]
    if in_index:
        for index in in_index: filtered_df = filtered_df[filtered_df['In Index'].str.contains(index, na=False)]
    
    min_mc = parse_market_cap(min_mcap)
    max_mc = parse_market_cap(max_mcap)
    if min_mc is not None: filtered_df = filtered_df[filtered_df['Market Cap'] >= min_mc]
    if max_mc is not None: filtered_df = filtered_df[filtered_df['Market Cap'] <= max_mc]
    
    # Filtros avanzados numéricos (solo se aplican si no son None)
    filters_to_apply_adv = {
        'PE Ratio': (pe_min, pe_max), 'PB Ratio': (pb_min, pb_max), 'PS Ratio': (ps_min, ps_max),
        'PEG Ratio': (peg_min, peg_max), 'EV/EBITDA': (ev_ebitda_min, ev_ebitda_max),
        'EV/Sales': (ev_sales_min, ev_sales_max), 'EV/FCF': (ev_fcf_min, ev_fcf_max),
        'P/CF': (pcf_min, pcf_max), 'P/FCF': (pfcf_min, pfcf_max),
        'FCF Yield': (fcf_yield_min, None), 'Earnings Yield': (earnings_yield_min, None),
        'Graham (%)': (graham_upside_min, None), 'Lynch (%)': (lynch_upside_min, None),
        'P/TBV': (ptbv_min, ptbv_max),

        'Rev. Growth': (rev_growth_min, rev_growth_max), 'EPS Growth': (eps_growth_min, eps_growth_max),
        'Rev. Growth 3Y': (rev_growth_3y_min, None), 'EPS Growth 3Y': (eps_growth_3y_min, None),
        'Rev. Growth 5Y': (rev_growth_5y_min, None), 'EPS Growth 5Y': (eps_growth_5y_min, None),
        'Rev Gr. Next Y': (rev_growth_next_y_min, None), 'EPS Gr. Next Y': (eps_growth_next_y_min, None),
        'Rev Gr. Next 5Y': (rev_growth_next_5y_min, None), 'EPS Gr. Next 5Y': (eps_growth_next_5y_min, None),
        'Rev Gr. Next Q': (rev_growth_next_q_min, None), 'EPS Gr. Next Q': (eps_growth_next_q_min, None),
        'FCF Growth': (fcf_growth_min, None), 'FCF Growth 3Y': (fcf_growth_3y_min, None),
        'FCF Growth 5Y': (fcf_growth_5y_min, None),

        'ROE': (roe_min, None), 'ROA': (roa_min, None), 'ROIC': (roic_min, None), 'ROCE': (roce_min, None),
        'Profit Margin': (profit_margin_min, None), 'Gross Margin': (gross_margin_min, None),
        'Oper. Margin': (operating_margin_min, None), 'FCF Margin': (fcf_margin_min, None),
        'EBITDA Margin': (ebitda_margin_min, None), 'EBIT Margin': (ebit_margin_min, None),
        'ROE (5Y)': (roe_5y_min, None), 'ROA (5Y)': (roa_5y_min, None), 'ROIC (5Y)': (roic_5y_min, None),
        'Asset Turnover': (asset_turnover_min, None), 'R&D / Rev': (rd_rev_min, None),

        'Current Ratio': (current_ratio_min, None), 'Quick Ratio': (quick_ratio_min, None),
        'Debt / Equity': (None, debt_equity_max), 'Debt / EBITDA': (None, debt_ebitda_max),
        'Z-Score': (z_score_min, None), 'F-Score': (f_score_min, None),
        'Debt / FCF': (None, debt_fcf_max), 'Int. Cov.': (interest_coverage_min, None),
        'Cash / M.Cap': (cash_mcap_min, None), 'Debt Growth (YoY)': (None, debt_growth_yoy_max),
        'Total Debt': (total_debt_min, None), 'Total Cash': (total_cash_min, None),

        'Div. Yield': (div_yield_min, div_yield_max), 'Payout Ratio': (None, payout_ratio_max),
        'Years': (years_min, None), 'Shareh. Yield': (shareholder_yield_min, None),
        'Buyback Yield': (buyback_yield_min, None), 'Div. Growth': (div_growth_1y_min, None),
        'Div. Growth 3Y': (div_growth_3y_min, None), 'Div. Growth 5Y': (div_growth_5y_min, None),
        
        'RSI': (rsi_min, rsi_max), 'Beta (5Y)': (None, beta_max),
        'Return 1W': (return_1w_min, None), 'Return 1M': (return_1m_min, None),
        'Return 3M': (return_3m_min, None), 'Return YTD': (return_ytd_min, None),
        'Return 1Y': (return_1y_min, None), 'Return 3Y': (return_3y_min, None),
        '52W High': (None, distance_52w_high_max), 'ATH Chg (%)': (None, ath_chg_max),
        '52W Low': (distance_52w_low_min, None), 'ATL Chg (%)': (atl_chg_min, None),
        'Rel. Volume': (rel_volume_min, None), 'ATR': (atr_min, None),
        
        'Employees': (employees_min, None), 'Analysts': (analysts_min, None),
        'Shares Insiders': (insider_ownership_min, None), 'Shares Institut.': (institutional_ownership_min, None),
        'Short % Float': (None, short_float_max),

        'Quality_Score': (quality_score_min if quality_score_min > 0 else None, None),
        'Value_Score': (value_score_min if value_score_min > 0 else None, None),
        'Growth_Score': (growth_score_min if growth_score_min > 0 else None, None),
        'Financial_Health_Score': (financial_health_score_min if financial_health_score_min > 0 else None, None),
        'Momentum_Score': (momentum_score_min if momentum_score_min > 0 else None, None),
        'Master_Score': (master_score_min if master_score_min > 0 else None, None),
    }

    for col, (min_val, max_val) in filters_to_apply_adv.items():
        if col in filtered_df.columns:
            if min_val is not None:
                filtered_df = filtered_df.dropna(subset=[col])[filtered_df[col] >= min_val]
            if max_val is not None:
                filtered_df = filtered_df.dropna(subset=[col])[filtered_df[col] <= max_val]

    if not filtered_df.empty:
        st.success(f"✅ Filtros aplicados correctamente. Se encontraron {len(filtered_df)} resultados.")
    else:
        st.warning("⚠️ No se encontraron resultados que coincidan con los filtros aplicados. Intenta ser menos restrictivo.")

    # =============================================================================
    # MÉTRICAS RESUMEN, RESULTADOS Y RESTO DE TABS
    # =============================================================================
    st.markdown("---")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("📊 Acciones", f"{len(filtered_df):,}", f"{(len(filtered_df)/len(df)*100) if len(df) > 0 else 0:.1f}% del total")
    with col2:
        total_mcap = filtered_df['Market Cap'].sum() if 'Market Cap' in filtered_df.columns and not filtered_df.empty else 0
        st.metric("💰 Cap Total", format_number(total_mcap, prefix="$", decimals=1))
    with col3:
        median_pe = filtered_df['PE Ratio'].median() if 'PE Ratio' in filtered_df.columns and not filtered_df.empty else 0
        st.metric("P/E Med", f"{median_pe:.1f}")
    with col4:
        avg_yield = filtered_df['Div. Yield'].mean() if 'Div. Yield' in filtered_df.columns and not filtered_df.empty else 0
        st.metric("Yield", f"{avg_yield:.2f}%")
    with col5:
        median_roe = filtered_df['ROE'].median() if 'ROE' in filtered_df.columns and not filtered_df.empty else 0
        st.metric("ROE Med", f"{median_roe:.1f}%")
    with col6:
        avg_master = filtered_df['Master_Score'].mean() if 'Master_Score' in filtered_df.columns and not filtered_df.empty else 0
        st.metric("Score", f"{avg_master:.0f}/100")

        with tab_results:
        st.markdown(f"### 📊 Resultados del Screener: {selected_screener}")
        
        with st.expander("⚙️ Configurar Vista de Resultados", expanded=False):
            if not filtered_df.empty:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'Master_Score', 'PE Ratio', 'ROE', 'Rev. Growth', 'Sector']
                available_cols = [col for col in default_cols if col in filtered_df.columns]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    selected_columns = st.multiselect("Selecciona Columnas:", options=list(filtered_df.columns), default=available_cols)
                with col2:
                    sort_column = st.selectbox("Ordenar por:", options=selected_columns if selected_columns else ['Symbol'])
                    sort_order = st.radio("Orden:", ["Descendente", "Ascendente"], horizontal=True)
                with col3:
                    n_rows = st.select_slider("Filas a mostrar:", options=[25, 50, 100, 200, 500, 1000], value=100)
            else:
                st.info("No hay filtros activos para configurar.")

        if not filtered_df.empty:
            if 'selected_columns' in locals() and selected_columns:
                display_df = filtered_df[selected_columns].sort_values(
                    by=sort_column, ascending=(sort_order == "Ascendente")
                ).head(n_rows)
                
                st.dataframe(display_df.style.format(na_rep='-'), use_container_width=True, height=600)
            else:
                st.dataframe(filtered_df, use_container_width=True, height=600)
        else:
            st.info("No hay resultados para mostrar.")

    with tab_analysis:
        st.markdown("### 📈 Dashboard de Análisis Visual")
        if not filtered_df.empty and len(filtered_df) > 1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### Matriz de Valor vs Calidad")
                fig = px.scatter(
                    filtered_df.head(250), x='Value_Score', y='Quality_Score',
                    size='Market Cap', color='Master_Score', hover_data=['Symbol'],
                    color_continuous_scale='Viridis', template='plotly_dark'
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown("##### Matriz de Crecimiento vs Momentum")
                fig = px.scatter(
                    filtered_df.head(250), x='Growth_Score', y='Momentum_Score',
                    size='Market Cap', color='Financial_Health_Score', hover_data=['Symbol'],
                    color_continuous_scale='RdYlGn', template='plotly_dark'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No hay suficientes datos para mostrar los gráficos (se necesita más de 1 resultado).")
            
    with tab_rankings:
        st.markdown("### 🏆 Rankings por Categorías")
        if not filtered_df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("#### 💎 Top Value")
                if 'Value_Score' in filtered_df.columns:
                    for _, row in filtered_df.nlargest(10, 'Value_Score').iterrows():
                        st.markdown(f"**{row['Symbol']}** | Score: {row['Value_Score']:.0f} | P/E: {row.get('PE Ratio', 'N/A'):.1f}")
                        st.caption(row['Company Name'])
            with col2:
                st.markdown("#### 🚀 Top Growth")
                if 'Growth_Score' in filtered_df.columns:
                     for _, row in filtered_df.nlargest(10, 'Growth_Score').iterrows():
                        st.markdown(f"**{row['Symbol']}** | Score: {row['Growth_Score']:.0f} | Rev Gr: {row.get('Rev. Growth', 'N/A'):.1f}%")
                        st.caption(row['Company Name'])
            with col3:
                st.markdown("#### 🏅 Top Quality")
                if 'Quality_Score' in filtered_df.columns:
                    for _, row in filtered_df.nlargest(10, 'Quality_Score').iterrows():
                        st.markdown(f"**{row['Symbol']}** | Score: {row['Quality_Score']:.0f} | ROE: {row.get('ROE', 'N/A'):.1f}%")
                        st.caption(row['Company Name'])
        else:
            st.warning("⚠️ No hay datos para mostrar rankings.")

    with tab_sector:
        st.markdown("### 🎯 Análisis Sectorial Profundo")
        if not filtered_df.empty and 'Sector' in filtered_df.columns:
            sector_metrics = filtered_df.groupby('Sector').agg({
                'Symbol': 'count', 'Market Cap': 'sum', 'PE Ratio': 'median',
                'ROE': 'median', 'Rev. Growth': 'median', 'Div. Yield': 'mean', 'Master_Score': 'mean'
            }).round(2)
            sector_metrics.columns = ['Acciones', 'Cap Total', 'P/E Med', 'ROE Med', 
                                     'Crec Med', 'Yield Prom', 'Master Score']
            st.dataframe(sector_metrics.style.format({
                'Cap Total': lambda x: format_number(x, prefix="$", decimals=1),
                'P/E Med': '{:.1f}', 'ROE Med': '{:.1f}%', 'Crec Med': '{:.1f}%',
                'Yield Prom': '{:.2f}%', 'Master Score': '{:.0f}'
            }).background_gradient(cmap='RdYlGn', subset=['Master Score', 'ROE Med']), use_container_width=True)
            
            sector_data = sector_metrics.reset_index()
            if len(sector_data) > 2:
                 fig = px.scatter(
                    sector_data, x='P/E Med', y='ROE Med', size='Cap Total', color='Master Score',
                    text='Sector', title="Mapa de Oportunidades Sectoriales",
                    color_continuous_scale='RdYlGn', template='plotly_dark',
                    labels={'P/E Med': 'P/E Mediano (Valoración)', 'ROE Med': 'ROE Mediano (Calidad)'})
                 fig.update_traces(textposition='top center')
                 st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos para el análisis sectorial.")
    
    with tab_export:
        st.markdown("### 💾 Exportar Resultados")
        if not filtered_df.empty:
            st.info(f"📊 **{len(filtered_df):,}** acciones filtradas listas para exportar")
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Descargar CSV",
                data=csv,
                file_name=f"bquant_screener_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("⚠️ No hay datos para exportar.")


else:
    st.info("👈 Selecciona un screener o construye el tuyo y aplica filtros para ver resultados.")
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
st.markdown("""<div style='text-align: center; padding: 20px; color: #b8b8b8;'><strong>BQuant Professional Stock Screener</strong><br>Desarrollado por <strong>@Gsnchez</strong> | <strong>bquantfinance.com</strong><br><small>Base de datos: 5,500+ acciones | 230+ métricas | Actualizado: Sept 2025</small></div>""", unsafe_allow_html=True)

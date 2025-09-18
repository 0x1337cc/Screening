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
        width: 380px;
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
    
    .stButton > button {
        background-color: #4a9eff;
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 6px;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #3a8eef;
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
    
    .stAlert {
        background-color: #1c1f26;
        border: 1px solid #2e3139;
        color: #ffffff;
    }
    
    /* Custom classes */
    .screener-title {
        color: #4a9eff;
        font-size: 1.1em;
        font-weight: 600;
        margin: 10px 0;
    }
    
    .screener-description {
        color: #b8b8b8;
        font-size: 0.9em;
        line-height: 1.4;
        margin-bottom: 15px;
    }
    
    .metric-highlight {
        background: linear-gradient(90deg, #4a9eff20, transparent);
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 500;
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
        df = pd.read_csv("screener-stocks-2025-09-18.csv")
        
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
        st.error("❌ **No se encontró el archivo 'screenerstocks20250918.csv'**")
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
    
    # Composite Master Score (promedio ponderado)
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
# SCREENERS AVANZADOS PREDEFINIDOS
# =============================================================================

ADVANCED_SCREENERS = {
    "🎯 Constructor Personalizado": {
        "description": "Construye tu propio screener combinando cualquier métrica",
        "strategy": "Define tus propios criterios de inversión",
        "filters": {},
        "composite_filters": {}
    },
    
    "🏆 The Magic Formula (Greenblatt)": {
        "description": "Combina empresas baratas (Earnings Yield alto) con alto retorno de capital (ROIC)",
        "strategy": "Ranking combinado de Earnings Yield y ROIC. Busca empresas en el top 20% de ambas métricas.",
        "filters": {
            "pe_max": 25,
            "market_cap_min": 50e6,
        },
        "composite_filters": {
            "earnings_yield_percentile": 80,  # Top 20%
            "roic_percentile": 80,  # Top 20%
            "combined_rank": "top_10_percent"
        }
    },
    
    "💎 Super GARP (Growth at Reasonable Price)": {
        "description": "Crecimiento sostenible a precio razonable con calidad financiera",
        "strategy": "PEG < 1, pero también ROE > 15%, márgenes crecientes y deuda controlada",
        "filters": {
            "peg_max": 1.0,
            "peg_min": 0.1,
            "eps_growth_min": 15,
            "eps_growth_max": 50,
            "roe_min": 15,
            "debt_equity_max": 1,
            "current_ratio_min": 1.5,
            "profit_margin_min": 10
        },
        "composite_filters": {
            "quality_score_min": 50,
            "growth_consistency": True  # 3 años de crecimiento consecutivo
        }
    },
    
    "🚀 Hypergrowth Quality": {
        "description": "Empresas de hipercrecimiento pero con fundamentos sólidos",
        "strategy": "Rev Growth > 30%, pero con FCF positivo, márgenes brutos > 50% y mejora de eficiencia",
        "filters": {
            "rev_growth_min": 30,
            "gross_margin_min": 50,
            "fcf_min": 0,
            "rev_growth_3y_min": 25,  # Crecimiento sostenido
            "insider_ownership_min": 5,  # Skin in the game
        },
        "composite_filters": {
            "growth_score_min": 75,
            "margin_expansion": True,  # Márgenes mejorando YoY
            "rule_of_40": True  # Growth Rate + Profit Margin > 40
        }
    },
    
    "🛡️ Dividend Aristocrats Plus": {
        "description": "Dividendos crecientes + valoración atractiva + salud financiera",
        "strategy": "No solo dividendos consistentes, sino también capacidad de mantenerlos y hacerlos crecer",
        "filters": {
            "div_yield_min": 2.5,
            "div_yield_max": 8,  # Evitar dividend traps
            "years_min": 10,
            "payout_ratio_max": 70,
            "fcf_payout_ratio_max": 60,  # FCF debe cubrir dividendos
            "debt_equity_max": 1,
            "roe_min": 12,
            "market_cap_min": 5e9
        },
        "composite_filters": {
            "div_growth_5y_min": 5,  # Crecimiento de dividendo 5Y
            "earnings_stability": True,  # Earnings consistentes
            "fcf_consistency": True
        }
    },
    
    "⚡ Momentum Quality": {
        "description": "Momentum técnico + fundamentos sólidos + catalizadores",
        "strategy": "Acciones en tendencia alcista con mejora de fundamentos y volumen institucional",
        "filters": {
            "return_1y_min": 20,
            "return_3m_min": 10,
            "rsi_min": 50,
            "rsi_max": 75,
            "roe_min": 15,
            "eps_growth_min": 10,
            "institutional_ownership_min": 40,
            "volume_ratio_min": 1.2  # Volumen sobre promedio
        },
        "composite_filters": {
            "momentum_score_min": 70,
            "earnings_surprise": True,  # Beat últimas 2 earnings
            "estimate_revisions_up": True
        }
    },
    
    "🏦 Buffett-Lynch Hybrid": {
        "description": "Combina moat de Buffett con crecimiento de Lynch",
        "strategy": "Empresas con ventajas competitivas durables y crecimiento predecible 10-25%",
        "filters": {
            "roe_min": 15,
            "roe_5y_min": 15,  # ROE consistente
            "eps_growth_min": 10,
            "eps_growth_max": 25,
            "debt_equity_max": 0.5,
            "fcf_margin_min": 10,
            "pe_max": 25,
            "market_cap_min": 10e9
        },
        "composite_filters": {
            "quality_score_min": 70,
            "competitive_advantage": True,  # ROE > Industry Avg
            "predictable_earnings": True  # Low earnings volatility
        }
    },
    
    "🔥 Turnaround Momentum": {
        "description": "Empresas en recuperación con señales tempranas de mejora",
        "strategy": "RSI oversold recuperándose + mejora de márgenes + insider buying",
        "filters": {
            "rsi_min": 35,
            "rsi_max": 55,
            "return_1m_min": 5,
            "z_score_min": 1.8,
            "current_ratio_min": 1,
            "market_cap_min": 100e6
        },
        "composite_filters": {
            "margin_improvement": True,  # QoQ improvement
            "debt_reduction": True,  # YoY debt reduction
            "insider_buying": True,
            "short_squeeze_potential": True  # Short % > 15%
        }
    },
    
    "💰 Deep Value Special Situations": {
        "description": "Valor extremo con catalizadores de revalorización",
        "strategy": "Trading bajo valor contable/liquidación con mejora operativa",
        "filters": {
            "pb_max": 1,
            "pe_max": 10,
            "pe_min": 0,  # Rentable
            "current_ratio_min": 2,
            "debt_equity_max": 0.5,
            "fcf_yield_min": 8
        },
        "composite_filters": {
            "ncav_discount": True,  # Trading below NCAV
            "value_score_min": 80,
            "buyback_program": True,
            "activist_involvement": False  # Opcional
        }
    },
    
    "🌟 CANSLIM Enhanced": {
        "description": "Sistema CANSLIM de O'Neil con filtros adicionales de calidad",
        "strategy": "C-A-N-S-L-I-M: Current earnings, Annual earnings, New products, Supply/demand, Leader, Institutional, Market",
        "filters": {
            "eps_growth_q_min": 25,  # Current quarter
            "eps_growth_min": 25,  # Annual
            "rev_growth_min": 20,
            "roe_min": 17,
            "shares_outstanding_decrease": True,  # Supply
            "institutional_ownership_min": 30,
            "institutional_ownership_max": 80,
            "relative_strength_min": 80  # RS Rating
        },
        "composite_filters": {
            "industry_leader": True,  # Top 3 in industry
            "new_high_proximity": True,  # Within 15% of 52w high
            "volume_surge": True,
            "earnings_acceleration": True
        }
    },
    
    "🎲 Quant Factor Model": {
        "description": "Modelo multifactor cuantitativo: Value + Quality + Momentum + Low Vol",
        "strategy": "Scoring ponderado de múltiples factores probados académicamente",
        "filters": {
            "market_cap_min": 500e6,
            "volume_avg_min": 100000,
            "price_min": 5
        },
        "composite_filters": {
            "value_score_min": 60,
            "quality_score_min": 60,
            "momentum_score_min": 60,
            "low_volatility": True,  # Beta < 1.2
            "master_score_min": 70
        }
    },
    
    "🏭 Sector Rotation Leader": {
        "description": "Líderes en sectores con momentum positivo",
        "strategy": "Mejores empresas en los sectores con mejor performance",
        "filters": {
            "market_cap_min": 1e9,
            "roe_min": 12,
            "relative_strength_sector_min": 70
        },
        "composite_filters": {
            "sector_momentum": "top_3_sectors",
            "industry_leader": True,
            "quality_score_min": 60,
            "institutional_accumulation": True
        }
    },
    
    "🔬 Innovation Growth": {
        "description": "Empresas con alto R&D y crecimiento de patentes",
        "strategy": "Innovación medida por R&D/Sales > 10% + crecimiento + márgenes en expansión",
        "filters": {
            "rd_to_revenue_min": 10,
            "rev_growth_min": 15,
            "gross_margin_min": 40,
            "market_cap_min": 1e9
        },
        "composite_filters": {
            "patent_growth": True,
            "margin_expansion": True,
            "tam_growth": True,  # Total Addressable Market growing
            "competitive_position": "improving"
        }
    }
}

# =============================================================================
# INTERFAZ PRINCIPAL
# =============================================================================

# Cargar datos
with st.spinner("Cargando base de datos de 5,500+ acciones..."):
    df = load_and_preprocess_data()

# Header
st.markdown("""
<div style='text-align: center; padding: 20px 0; border-bottom: 1px solid #2e3139;'>
    <h1 style='margin: 0; color: #ffffff;'>📊 BQuant Professional Stock Screener</h1>
    <p style='color: #b8b8b8; margin-top: 10px; font-size: 1.1em;'>
        Sistema avanzado de screening con 230+ métricas y algoritmos institucionales
    </p>
    <p style='color: #4a9eff; margin-top: 5px;'>
        Desarrollado por <strong>@Gsnchez</strong> | <strong>bquantfinance.com</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - CONSTRUCTOR DE SCREENERS
# =============================================================================

st.sidebar.markdown("# 🎯 Constructor de Screeners")
st.sidebar.markdown("---")

# Selector de Screener Avanzado
selected_screener = st.sidebar.selectbox(
    "📋 **Screener Predefinido**",
    options=list(ADVANCED_SCREENERS.keys()),
    help="Selecciona un screener algorítmico o construye el tuyo propio"
)

# Información del Screener
screener_config = ADVANCED_SCREENERS[selected_screener]
st.sidebar.markdown(f"<p class='screener-title'>{selected_screener}</p>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p class='screener-description'>{screener_config['description']}</p>", unsafe_allow_html=True)

with st.sidebar.expander("📖 Estrategia Detallada", expanded=False):
    st.write(screener_config['strategy'])

st.sidebar.markdown("---")

# =============================================================================
# CONSTRUCTOR DE FILTROS COMPLETO
# =============================================================================

st.sidebar.markdown("### 🔧 Constructor de Filtros")

# Modo de filtrado
filter_mode = st.sidebar.radio(
    "Modo de construcción:",
    ["🎯 Guiado (Recomendado)", "⚙️ Experto (Todos los filtros)"],
    help="El modo Guiado muestra los filtros más relevantes según el screener"
)

# Obtener filtros del screener
preset_filters = screener_config.get('filters', {})

# FILTROS BÁSICOS
with st.sidebar.expander("📊 **Filtros Fundamentales**", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("🔍 Buscar", placeholder="Ticker o nombre...")
    
    with col2:
        in_index = st.multiselect(
            "📈 Índices",
            ["SP500", "NASDAQ100", "DOW30"],
            default=[]
        )
    
    sectors = st.multiselect(
        "🏢 Sectores",
        options=sorted(df['Sector'].dropna().unique()),
        default=preset_filters.get('sectors', [])
    )
    
    industries = st.multiselect(
        "🏭 Industrias",
        options=sorted(df['Industry'].dropna().unique()) if 'Industry' in df.columns else [],
        default=[]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        min_mcap = st.text_input(
            "Market Cap Min",
            value=f"{preset_filters.get('market_cap_min', 0)/1e6:.0f}M" if 'market_cap_min' in preset_filters else "",
            placeholder="ej: 100M, 1B"
        )
    with col2:
        max_mcap = st.text_input(
            "Market Cap Max",
            value=f"{preset_filters.get('market_cap_max', 0)/1e9:.0f}B" if 'market_cap_max' in preset_filters else "",
            placeholder="ej: 10B, 1T"
        )
    
    exchanges = st.multiselect(
        "🏛️ Exchanges",
        options=sorted(df['Exchange'].dropna().unique()) if 'Exchange' in df.columns else [],
        default=[]
    )

# VALORACIÓN
with st.sidebar.expander("💰 **Métricas de Valoración**", expanded=(filter_mode == "⚙️ Experto")):
    col1, col2 = st.columns(2)
    
    with col1:
        pe_min = st.number_input("P/E Min", value=preset_filters.get('pe_min', 0), min_value=0.0, key="pe_min")
        pb_min = st.number_input("P/B Min", value=preset_filters.get('pb_min', 0), min_value=0.0, key="pb_min")
        ps_min = st.number_input("P/S Min", value=preset_filters.get('ps_min', 0), min_value=0.0, key="ps_min")
        peg_min = st.number_input("PEG Min", value=preset_filters.get('peg_min', 0), min_value=0.0, key="peg_min")
        ev_ebitda_min = st.number_input("EV/EBITDA Min", value=0.0, min_value=0.0)
        
    with col2:
        pe_max = st.number_input("P/E Max", value=preset_filters.get('pe_max', 100), min_value=0.0, key="pe_max")
        pb_max = st.number_input("P/B Max", value=preset_filters.get('pb_max', 10), min_value=0.0, key="pb_max")
        ps_max = st.number_input("P/S Max", value=preset_filters.get('ps_max', 20), min_value=0.0, key="ps_max")
        peg_max = st.number_input("PEG Max", value=preset_filters.get('peg_max', 3), min_value=0.0, key="peg_max")
        ev_ebitda_max = st.number_input("EV/EBITDA Max", value=50.0, min_value=0.0)
    
    # Más métricas de valoración
    pcf_max = st.number_input("P/CF Max", value=50.0, min_value=0.0)
    pfcf_max = st.number_input("P/FCF Max", value=50.0, min_value=0.0)
    earnings_yield_min = st.number_input("Earnings Yield Min (%)", value=0.0)

# CRECIMIENTO
with st.sidebar.expander("📈 **Métricas de Crecimiento**", expanded=(filter_mode == "⚙️ Experto")):
    
    st.markdown("**Crecimiento de Ingresos**")
    col1, col2 = st.columns(2)
    with col1:
        rev_growth_min = st.number_input("Rev Growth Min %", value=preset_filters.get('rev_growth_min', -100))
        rev_growth_3y_min = st.number_input("Rev CAGR 3Y Min %", value=-100.0)
        rev_growth_5y_min = st.number_input("Rev CAGR 5Y Min %", value=-100.0)
    with col2:
        rev_growth_max = st.number_input("Rev Growth Max %", value=500.0)
        rev_growth_next_min = st.number_input("Rev Growth Next Y Min %", value=-100.0)
        rev_growth_qtrs = st.number_input("Qtrs Rev Growth +", value=0, min_value=0, max_value=12)
    
    st.markdown("**Crecimiento de Beneficios**")
    col1, col2 = st.columns(2)
    with col1:
        eps_growth_min = st.number_input("EPS Growth Min %", value=preset_filters.get('eps_growth_min', -100))
        eps_growth_3y_min = st.number_input("EPS CAGR 3Y Min %", value=-100.0)
        eps_growth_5y_min = st.number_input("EPS CAGR 5Y Min %", value=-100.0)
    with col2:
        eps_growth_max = st.number_input("EPS Growth Max %", value=preset_filters.get('eps_growth_max', 500))
        eps_growth_next_min = st.number_input("EPS Growth Next Y Min %", value=-100.0)
        eps_growth_next_5y_min = st.number_input("EPS Growth Next 5Y Min %", value=-100.0)
    
    st.markdown("**Crecimiento FCF y Márgenes**")
    fcf_growth_min = st.number_input("FCF Growth Min %", value=-100.0)
    margin_expansion = st.checkbox("Márgenes en Expansión YoY", value=False)
    accelerating_growth = st.checkbox("Crecimiento Acelerando", value=False)

# RENTABILIDAD
with st.sidebar.expander("💎 **Métricas de Rentabilidad**", expanded=(filter_mode == "⚙️ Experto")):
    
    col1, col2 = st.columns(2)
    with col1:
        roe_min = st.number_input("ROE Min %", value=preset_filters.get('roe_min', -50))
        roa_min = st.number_input("ROA Min %", value=preset_filters.get('roa_min', -50))
        roic_min = st.number_input("ROIC Min %", value=preset_filters.get('roic_min', -50))
        roce_min = st.number_input("ROCE Min %", value=-50.0)
    
    with col2:
        roe_max = st.number_input("ROE Max %", value=100.0)
        roa_max = st.number_input("ROA Max %", value=50.0)
        roic_max = st.number_input("ROIC Max %", value=100.0)
        roce_max = st.number_input("ROCE Max %", value=100.0)
    
    st.markdown("**Márgenes**")
    gross_margin_min = st.number_input("Margen Bruto Min %", value=preset_filters.get('gross_margin_min', 0))
    operating_margin_min = st.number_input("Margen Operativo Min %", value=-100.0)
    profit_margin_min = st.number_input("Margen Neto Min %", value=preset_filters.get('profit_margin_min', -100))
    fcf_margin_min = st.number_input("FCF Margin Min %", value=-100.0)
    ebitda_margin_min = st.number_input("EBITDA Margin Min %", value=-100.0)

# DIVIDENDOS
with st.sidebar.expander("💵 **Análisis de Dividendos**", expanded=(filter_mode == "⚙️ Experto")):
    
    col1, col2 = st.columns(2)
    with col1:
        div_yield_min = st.number_input("Yield Min %", value=preset_filters.get('div_yield_min', 0))
        div_yield_max = st.number_input("Yield Max %", value=preset_filters.get('div_yield_max', 20))
        payout_ratio_max = st.number_input("Payout Ratio Max %", value=preset_filters.get('payout_ratio_max', 100))
    
    with col2:
        years_min = st.number_input("Años Dividendos Min", value=preset_filters.get('years_min', 0), min_value=0)
        div_growth_3y_min = st.number_input("Div Growth 3Y Min %", value=-100.0)
        div_growth_5y_min = st.number_input("Div Growth 5Y Min %", value=preset_filters.get('div_growth_5y_min', -100))
    
    fcf_payout_max = st.number_input("FCF Payout Max %", value=preset_filters.get('fcf_payout_ratio_max', 100))
    dividend_consistency = st.checkbox("Dividendos Consistentes (sin cortes)", value=False)

# SALUD FINANCIERA
with st.sidebar.expander("🏥 **Salud Financiera**", expanded=(filter_mode == "⚙️ Experto")):
    
    st.markdown("**Ratios de Liquidez**")
    col1, col2 = st.columns(2)
    with col1:
        current_ratio_min = st.number_input("Current Ratio Min", value=preset_filters.get('current_ratio_min', 0))
        quick_ratio_min = st.number_input("Quick Ratio Min", value=0.0)
        cash_ratio_min = st.number_input("Cash Ratio Min", value=0.0)
    
    with col2:
        current_ratio_max = st.number_input("Current Ratio Max", value=10.0)
        quick_ratio_max = st.number_input("Quick Ratio Max", value=10.0)
        working_capital_min = st.number_input("Working Cap Min (M)", value=-1000.0)
    
    st.markdown("**Endeudamiento**")
    debt_equity_max = st.number_input("Deuda/Capital Max", value=preset_filters.get('debt_equity_max', 5))
    debt_ebitda_max = st.number_input("Deuda/EBITDA Max", value=10.0)
    debt_fcf_max = st.number_input("Deuda/FCF Max", value=10.0)
    interest_coverage_min = st.number_input("Cobertura Intereses Min", value=0.0)
    
    st.markdown("**Scores Financieros**")
    z_score_min = st.number_input("Altman Z-Score Min", value=preset_filters.get('z_score_min', -5))
    f_score_min = st.number_input("Piotroski F-Score Min", value=0, min_value=0, max_value=9)
    
    st.markdown("**Free Cash Flow**")
    fcf_min = st.number_input("FCF Min (M)", value=preset_filters.get('fcf_min', -1000) if 'fcf_min' in preset_filters else -1000.0)
    fcf_yield_min = st.number_input("FCF Yield Min %", value=preset_filters.get('fcf_yield_min', -20))
    fcf_per_share_min = st.number_input("FCF/Share Min", value=-100.0)

# INDICADORES TÉCNICOS
with st.sidebar.expander("📉 **Indicadores Técnicos**", expanded=(filter_mode == "⚙️ Experto")):
    
    st.markdown("**Momentum y Tendencia**")
    col1, col2 = st.columns(2)
    with col1:
        rsi_min = st.number_input("RSI Min", value=preset_filters.get('rsi_min', 0), min_value=0.0, max_value=100.0)
        rsi_max = st.number_input("RSI Max", value=preset_filters.get('rsi_max', 100), min_value=0.0, max_value=100.0)
        
    with col2:
        relative_strength_min = st.number_input("Rel Strength Min", value=preset_filters.get('relative_strength_min', 0))
        distance_52w_high_max = st.number_input("Dist. 52W High Max %", value=100.0)
    
    st.markdown("**Retornos**")
    col1, col2 = st.columns(2)
    with col1:
        return_1y_min = st.number_input("Return 1Y Min %", value=preset_filters.get('return_1y_min', -100))
        return_6m_min = st.number_input("Return 6M Min %", value=-100.0)
        return_3m_min = st.number_input("Return 3M Min %", value=preset_filters.get('return_3m_min', -100))
    
    with col2:
        return_1m_min = st.number_input("Return 1M Min %", value=preset_filters.get('return_1m_min', -100))
        return_1w_min = st.number_input("Return 1W Min %", value=-100.0)
        return_ytd_min = st.number_input("Return YTD Min %", value=-100.0)
    
    st.markdown("**Volatilidad y Riesgo**")
    beta_min = st.number_input("Beta Min", value=0.0, min_value=0.0)
    beta_max = st.number_input("Beta Max", value=preset_filters.get('beta_max', 3), min_value=0.0)
    atr_max = st.number_input("ATR Max", value=1000.0)
    
    st.markdown("**Volumen**")
    volume_avg_min = st.number_input("Vol Promedio Min", value=preset_filters.get('volume_avg_min', 0))
    volume_ratio_min = st.number_input("Vol/Avg Min", value=preset_filters.get('volume_ratio_min', 0))
    dollar_volume_min = st.number_input("Dollar Volume Min (M)", value=0.0)

# PROPIEDAD Y GESTIÓN
with st.sidebar.expander("👥 **Propiedad y Gestión**", expanded=(filter_mode == "⚙️ Experto")):
    
    insider_ownership_min = st.number_input("Insider Ownership Min %", value=preset_filters.get('insider_ownership_min', 0))
    insider_ownership_max = st.number_input("Insider Ownership Max %", value=100.0)
    
    institutional_ownership_min = st.number_input("Inst. Ownership Min %", value=preset_filters.get('institutional_ownership_min', 0))
    institutional_ownership_max = st.number_input("Inst. Ownership Max %", value=preset_filters.get('institutional_ownership_max', 100))
    
    shares_float_min = st.number_input("Float Min (M)", value=0.0)
    shares_float_max = st.number_input("Float Max (M)", value=100000.0)
    
    short_float_min = st.number_input("Short % Float Min", value=0.0)
    short_float_max = st.number_input("Short % Float Max", value=100.0)
    
    insider_transactions = st.selectbox("Insider Transactions", ["Cualquiera", "Comprando", "Vendiendo", "Neutral"])
    buyback_program = st.checkbox("Programa de Recompra Activo", value=False)

# SCORES COMPUESTOS
with st.sidebar.expander("🎯 **Scores Compuestos**", expanded=True):
    
    st.markdown("**Scores Algorítmicos (0-100)**")
    
    quality_score_min = st.slider("Quality Score Min", 0, 100, 
                                  value=preset_filters.get('quality_score_min', 0))
    value_score_min = st.slider("Value Score Min", 0, 100,
                                value=preset_filters.get('value_score_min', 0))
    growth_score_min = st.slider("Growth Score Min", 0, 100,
                                 value=preset_filters.get('growth_score_min', 0))
    financial_health_score_min = st.slider("Financial Health Score Min", 0, 100, 
                                           value=preset_filters.get('financial_health_score_min', 0))
    momentum_score_min = st.slider("Momentum Score Min", 0, 100,
                                   value=preset_filters.get('momentum_score_min', 0))
    master_score_min = st.slider("Master Score Min", 0, 100,
                                 value=preset_filters.get('master_score_min', 0))

# Botón de aplicar
st.sidebar.markdown("---")
col1, col2 = st.sidebar.columns(2)
with col1:
    apply_button = st.button("🔍 **APLICAR**", type="primary", use_container_width=True)
with col2:
    reset_button = st.button("🔄 **RESET**", type="secondary", use_container_width=True)

if reset_button:
    st.rerun()

# =============================================================================
# APLICACIÓN DE FILTROS
# =============================================================================

filtered_df = df.copy()

# Búsqueda de texto
if search_term:
    filtered_df = filtered_df[
        (filtered_df['Symbol'].str.contains(search_term.upper(), na=False)) |
        (filtered_df['Company Name'].str.contains(search_term, case=False, na=False))
    ]

# Índices
if in_index:
    for index in in_index:
        if 'In Index' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['In Index'].str.contains(index, na=False)]

# Sectores e Industrias
if sectors:
    filtered_df = filtered_df[filtered_df['Sector'].isin(sectors)]

if industries and 'Industry' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Industry'].isin(industries)]

# Exchanges
if exchanges and 'Exchange' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Exchange'].isin(exchanges)]

# Market Cap
min_mc = parse_market_cap(min_mcap)
max_mc = parse_market_cap(max_mcap)
if min_mc is not None and 'Market Cap' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Market Cap'] >= min_mc]
if max_mc is not None and 'Market Cap' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Market Cap'] <= max_mc]

# Aplicar todos los filtros numéricos
numeric_filters = [
    ('PE Ratio', pe_min, pe_max),
    ('PB Ratio', pb_min, pb_max),
    ('PS Ratio', ps_min, ps_max),
    ('PEG Ratio', peg_min, peg_max),
    ('EV/EBITDA', ev_ebitda_min, ev_ebitda_max),
    ('Rev. Growth', rev_growth_min, rev_growth_max),
    ('EPS Growth', eps_growth_min, eps_growth_max),
    ('ROE', roe_min, roe_max),
    ('ROA', roa_min, roa_max),
    ('ROIC', roic_min, roic_max),
    ('Gross Margin', gross_margin_min, None),
    ('Profit Margin', profit_margin_min, None),
    ('Div. Yield', div_yield_min, div_yield_max),
    ('Payout Ratio', None, payout_ratio_max),
    ('Years', years_min, None),
    ('Current Ratio', current_ratio_min, current_ratio_max),
    ('Debt / Equity', None, debt_equity_max),
    ('Z-Score', z_score_min, None),
    ('F-Score', f_score_min, None),
    ('FCF Yield', fcf_yield_min, None),
    ('RSI', rsi_min, rsi_max),
    ('Beta (5Y)', beta_min, beta_max),
    ('Return 1Y', return_1y_min, None),
    ('Return 3M', return_3m_min, None),
    ('Return 1M', return_1m_min, None),
    # Scores compuestos
    ('Quality_Score', quality_score_min, None),
    ('Value_Score', value_score_min, None),
    ('Growth_Score', growth_score_min, None),
    ('Financial_Health_Score', financial_health_score_min, None),
    ('Momentum_Score', momentum_score_min, None),
    ('Master_Score', master_score_min, None),
]

for col_name, min_val, max_val in numeric_filters:
    if col_name in filtered_df.columns:
        if min_val is not None:
            filtered_df = filtered_df[filtered_df[col_name] >= min_val]
        if max_val is not None:
            filtered_df = filtered_df[filtered_df[col_name] <= max_val]

# =============================================================================
# MÉTRICAS Y VISUALIZACIÓN
# =============================================================================

# Métricas resumen
st.markdown("---")
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

with col1:
    st.metric("📊 Acciones", f"{len(filtered_df):,}")
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
    median_growth = filtered_df['Rev. Growth'].median() if 'Rev. Growth' in filtered_df.columns else 0
    st.metric("Crec Med", f"{median_growth:.1f}%")
with col7:
    avg_quality = filtered_df['Quality_Score'].mean() if 'Quality_Score' in filtered_df.columns else 0
    st.metric("Quality", f"{avg_quality:.0f}/100")
with col8:
    avg_master = filtered_df['Master_Score'].mean() if 'Master_Score' in filtered_df.columns else 0
    st.metric("Master", f"{avg_master:.0f}/100")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Tabla de Resultados",
    "📈 Análisis Visual",
    "🎯 Scoring Detallado",
    "🏆 Rankings",
    "📋 Análisis Sectorial",
    "💾 Exportar"
])

with tab1:
    st.markdown(f"### Resultados: {selected_screener}")
    
    # Configuración de columnas según screener
    if "Magic Formula" in selected_screener:
        default_columns = ['Symbol', 'Company Name', 'Market Cap', 'PE Ratio', 'ROIC', 
                          'Earnings Yield', 'Master_Score', 'Sector']
    elif "GARP" in selected_screener:
        default_columns = ['Symbol', 'Company Name', 'PEG Ratio', 'EPS Growth', 'PE Ratio',
                          'ROE', 'Quality_Score', 'Market Cap']
    elif "Dividend" in selected_screener:
        default_columns = ['Symbol', 'Company Name', 'Div. Yield', 'Payout Ratio', 'Years',
                          'FCF Yield', 'Financial_Health_Score', 'Market Cap']
    elif "Momentum" in selected_screener:
        default_columns = ['Symbol', 'Company Name', 'Return 1Y', 'Return 3M', 'RSI',
                          'Momentum_Score', 'Volume Ratio', 'Market Cap']
    else:
        default_columns = ['Symbol', 'Company Name', 'Market Cap', 'PE Ratio', 'ROE',
                          'Rev. Growth', 'Master_Score', 'Sector']
    
    available_columns = [col for col in default_columns if col in filtered_df.columns]
    
    with st.expander("⚙️ Configurar Vista"):
        selected_columns = st.multiselect(
            "Columnas:",
            options=filtered_df.columns.tolist(),
            default=available_columns
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sort_column = st.selectbox("Ordenar por:", 
                                       options=selected_columns if selected_columns else ['Symbol'])
        with col2:
            sort_order = st.radio("Orden:", ["Descendente", "Ascendente"], horizontal=True)
        with col3:
            n_rows = st.select_slider("Filas:", options=[25, 50, 100, 200, 500, 1000], value=100)
    
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
        
        st.dataframe(
            display_df.style.format(format_dict, na_rep='N/A')
                            .background_gradient(cmap='RdYlGn', subset=[col for col in selected_columns 
                                                                         if 'Score' in col]),
            use_container_width=True,
            height=600
        )
        
        st.success(f"✅ Mostrando {len(display_df)} de {len(filtered_df)} resultados | "
                  f"Filtros aplicados: {sum(1 for f in [pe_min, pe_max, roe_min] if f != 0)}")

with tab2:
    st.markdown("### 📈 Dashboard Visual")
    
    # Crear visualizaciones
    col1, col2 = st.columns(2)
    
    with col1:
        # Scatter: Value vs Quality
        if all(col in filtered_df.columns for col in ['Value_Score', 'Quality_Score']):
            fig = px.scatter(
                filtered_df.head(500),
                x='Value_Score',
                y='Quality_Score',
                size='Market Cap' if 'Market Cap' in filtered_df.columns else None,
                color='Master_Score',
                hover_data=['Symbol', 'Company Name', 'PE Ratio', 'ROE'],
                title="Matriz Value vs Quality",
                color_continuous_scale='Viridis'
            )
            fig.add_hline(y=50, line_dash="dash", opacity=0.5)
            fig.add_vline(x=50, line_dash="dash", opacity=0.5)
            fig.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter: Growth vs Valuation
        if all(col in filtered_df.columns for col in ['PE Ratio', 'Rev. Growth']):
            fig = px.scatter(
                filtered_df.head(500),
                x='PE Ratio',
                y='Rev. Growth',
                size='Market Cap' if 'Market Cap' in filtered_df.columns else None,
                color='Growth_Score',
                hover_data=['Symbol', 'Company Name', 'EPS Growth'],
                title="Crecimiento vs Valoración",
                color_continuous_scale='RdYlGn'
            )
            fig.add_hline(y=20, line_dash="dash", opacity=0.5)
            fig.add_vline(x=20, line_dash="dash", opacity=0.5)
            fig.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Distribución de Scores
    if 'Master_Score' in filtered_df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(
                filtered_df,
                x='Master_Score',
                nbins=20,
                title="Distribución del Master Score",
                color_discrete_sequence=['#4a9eff']
            )
            fig.update_layout(template="plotly_dark", height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Box plot de scores por sector
            if 'Sector' in filtered_df.columns:
                top_sectors = filtered_df['Sector'].value_counts().head(8).index
                sector_data = filtered_df[filtered_df['Sector'].isin(top_sectors)]
                
                fig = px.box(
                    sector_data,
                    x='Sector',
                    y='Master_Score',
                    title="Master Score por Sector",
                    color_discrete_sequence=['#4a9eff']
                )
                fig.update_layout(template="plotly_dark", height=300)
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 🎯 Análisis de Scoring Detallado")
    
    # Top 20 por Master Score
    if 'Master_Score' in filtered_df.columns:
        top_scored = filtered_df.nlargest(20, 'Master_Score')[
            ['Symbol', 'Company Name', 'Master_Score', 'Quality_Score', 
             'Value_Score', 'Growth_Score', 'Financial_Health_Score', 'Momentum_Score']
        ]
        
        st.markdown("#### Top 20 Acciones por Master Score")
        
        # Crear heatmap de scores
        scores_cols = ['Quality_Score', 'Value_Score', 'Growth_Score', 
                      'Financial_Health_Score', 'Momentum_Score']
        available_scores = [col for col in scores_cols if col in top_scored.columns]
        
        if available_scores:
            fig = go.Figure(data=go.Heatmap(
                z=top_scored[available_scores].values.T,
                x=top_scored['Symbol'].values,
                y=[col.replace('_Score', '') for col in available_scores],
                colorscale='Viridis',
                text=top_scored[available_scores].values.T,
                texttemplate="%{text:.0f}",
                textfont={"size": 10},
                colorbar=dict(title="Score")
            ))
            
            fig.update_layout(
                title="Heatmap de Scores - Top 20 Acciones",
                height=400,
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.dataframe(
            top_scored.style.background_gradient(cmap='RdYlGn', subset=available_scores),
            use_container_width=True
        )

with tab4:
    st.markdown("### 🏆 Rankings por Categorías")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 💎 **Mejor Valor**")
        if all(col in filtered_df.columns for col in ['PE Ratio', 'Value_Score']):
            value_stocks = filtered_df[filtered_df['PE Ratio'] > 0].nlargest(10, 'Value_Score')[
                ['Symbol', 'Company Name', 'PE Ratio', 'PB Ratio', 'Value_Score']
            ]
            for idx, row in value_stocks.iterrows():
                st.markdown(f"**{row['Symbol']}** - Score: {row['Value_Score']:.0f}")
                st.caption(f"P/E: {row['PE Ratio']:.1f} | P/B: {row['PB Ratio']:.1f}")
    
    with col2:
        st.markdown("#### 🚀 **Mayor Crecimiento**")
        if 'Growth_Score' in filtered_df.columns:
            growth_stocks = filtered_df.nlargest(10, 'Growth_Score')[
                ['Symbol', 'Company Name', 'Rev. Growth', 'EPS Growth', 'Growth_Score']
            ]
            for idx, row in growth_stocks.iterrows():
                st.markdown(f"**{row['Symbol']}** - Score: {row['Growth_Score']:.0f}")
                st.caption(f"Rev: {row['Rev. Growth']:.1f}% | EPS: {row['EPS Growth']:.1f}%")
    
    with col3:
        st.markdown("#### 🏅 **Mejor Calidad**")
        if 'Quality_Score' in filtered_df.columns:
            quality_stocks = filtered_df.nlargest(10, 'Quality_Score')[
                ['Symbol', 'Company Name', 'ROE', 'Profit Margin', 'Quality_Score']
            ]
            for idx, row in quality_stocks.iterrows():
                st.markdown(f"**{row['Symbol']}** - Score: {row['Quality_Score']:.0f}")
                st.caption(f"ROE: {row['ROE']:.1f}% | Margin: {row['Profit Margin']:.1f}%")

with tab5:
    st.markdown("### 📋 Análisis Sectorial Profundo")
    
    if 'Sector' in filtered_df.columns:
        # Métricas por sector
        sector_metrics = filtered_df.groupby('Sector').agg({
            'Symbol': 'count',
            'Market Cap': 'sum',
            'PE Ratio': 'median',
            'ROE': 'median',
            'Rev. Growth': 'median',
            'Master_Score': 'mean',
            'Quality_Score': 'mean',
            'Value_Score': 'mean'
        }).round(2)
        
        sector_metrics.columns = ['Acciones', 'Cap Total', 'P/E Med', 'ROE Med', 
                                  'Crec Med', 'Master Score', 'Quality', 'Value']
        sector_metrics = sector_metrics.sort_values('Master Score', ascending=False)
        
        # Mostrar tabla
        st.dataframe(
            sector_metrics.style.format({
                'Cap Total': lambda x: format_number(x, prefix="$", decimals=1),
                'P/E Med': '{:.1f}',
                'ROE Med': '{:.1f}%',
                'Crec Med': '{:.1f}%',
                'Master Score': '{:.0f}',
                'Quality': '{:.0f}',
                'Value': '{:.0f}'
            }).background_gradient(cmap='RdYlGn', subset=['Master Score', 'Quality', 'Value']),
            use_container_width=True
        )
        
        # Gráfico de radar para top 5 sectores
        top_5_sectors = sector_metrics.head(5)
        
        if len(top_5_sectors) > 0:
            categories = ['Quality', 'Value', 'ROE Med', 'Crec Med']
            
            fig = go.Figure()
            
            for sector in top_5_sectors.index:
                values = [
                    top_5_sectors.loc[sector, 'Quality'],
                    top_5_sectors.loc[sector, 'Value'],
                    top_5_sectors.loc[sector, 'ROE Med'],
                    top_5_sectors.loc[sector, 'Crec Med']
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=sector[:20]
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title="Análisis Multifactor - Top 5 Sectores",
                template="plotly_dark",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.markdown("### 💾 Exportar Resultados")
    
    st.info("Selecciona las columnas y el formato de exportación")
    
    # Presets de exportación
    export_preset = st.selectbox(
        "Preset de exportación:",
        ["Personalizado", "Screener Completo", "Análisis Fundamental", 
         "Scores y Rankings", "Métricas de Crecimiento", "Todo"]
    )
    
    if export_preset == "Screener Completo":
        export_cols = ['Symbol', 'Company Name', 'Sector', 'Market Cap', 
                      'Master_Score', 'PE Ratio', 'ROE', 'Rev. Growth', 
                      'Div. Yield', 'Return 1Y']
    elif export_preset == "Scores y Rankings":
        export_cols = ['Symbol', 'Company Name', 'Master_Score', 'Quality_Score',
                      'Value_Score', 'Growth_Score', 'Financial_Health_Score', 
                      'Momentum_Score']
    elif export_preset == "Todo":
        export_cols = filtered_df.columns.tolist()
    else:
        export_cols = ['Symbol', 'Company Name', 'Market Cap', 'PE Ratio', 'Master_Score']
    
    # Filtrar columnas disponibles
    available_export_cols = [col for col in export_cols if col in filtered_df.columns]
    
    export_columns = st.multiselect(
        "Columnas a exportar:",
        options=filtered_df.columns.tolist(),
        default=available_export_cols
    )
    
    if export_columns:
        export_df = filtered_df[export_columns]
        
        # Vista previa
        st.markdown("#### Vista Previa")
        st.dataframe(export_df.head(5), use_container_width=True)
        
        # Información
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filas", f"{len(export_df):,}")
        with col2:
            st.metric("Columnas", len(export_columns))
        with col3:
            st.metric("Screener", selected_screener[:20])
        
        # Botones de descarga
        col1, col2 = st.columns(2)
        
        with col1:
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"bquant_screener_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary"
            )
        
        with col2:
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    export_df.to_excel(writer, sheet_name='Screener Results', index=False)
                    
                    # Añadir hoja de metadata
                    metadata = pd.DataFrame({
                        'Campo': ['Fecha', 'Screener', 'Total Resultados', 
                                 'Market Cap Total', 'P/E Mediano', 'Master Score Promedio'],
                        'Valor': [
                            pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
                            selected_screener,
                            len(export_df),
                            format_number(export_df['Market Cap'].sum() if 'Market Cap' in export_df.columns else 0, prefix="$"),
                            f"{export_df['PE Ratio'].median():.1f}" if 'PE Ratio' in export_df.columns else "N/A",
                            f"{export_df['Master_Score'].mean():.1f}" if 'Master_Score' in export_df.columns else "N/A"
                        ]
                    })
                    metadata.to_excel(writer, sheet_name='Info', index=False)
                
                st.download_button(
                    label="📗 Descargar Excel",
                    data=buffer.getvalue(),
                    file_name=f"bquant_screener_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="secondary"
                )
            except:
                st.info("Instala openpyxl para exportar a Excel: `pip install openpyxl`")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #b8b8b8;'>
    <strong>BQuant Professional Stock Screener</strong><br>
    Desarrollado por <strong>@Gsnchez</strong> | <strong>bquantfinance.com</strong><br>
    <small>5,500+ acciones | 230+ métricas | Algoritmos institucionales</small>
</div>
""", unsafe_allow_html=True)

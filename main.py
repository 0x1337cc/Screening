import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="BQuant Ultra Screener Pro | @Gsnchez",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Profesional Dark Mode
professional_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #1a1d24 100%);
        font-family: 'Inter', sans-serif;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1c1f26 0%, #262b36 100%);
        border-right: 2px solid #4a9eff20;
    }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1c1f26 0%, #262b36 100%);
        border: 1px solid #4a9eff30;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    div[data-testid="metric-container"]:hover {
        border-color: #4a9eff;
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(74, 158, 255, 0.2);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #4a9eff 0%, #3a8eef 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(74, 158, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(74, 158, 255, 0.5);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-weight: 500;
        color: #b8b8b8;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #4a9eff 0%, #3a8eef 100%);
        color: white;
        border-radius: 8px 8px 0 0;
    }
    
    h1, h2, h3 {
        background: linear-gradient(90deg, #ffffff 0%, #b8b8b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
    }
    
    .screener-card {
        background: linear-gradient(135deg, #1c1f26 0%, #262b36 100%);
        border: 1px solid #4a9eff30;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .screener-card:hover {
        border-color: #4a9eff;
        transform: translateX(5px);
        box-shadow: 0 8px 12px rgba(74, 158, 255, 0.3);
    }
    
    .score-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    
    .score-high { background: linear-gradient(90deg, #4caf50, #45a049); color: white; }
    .score-medium { background: linear-gradient(90deg, #ff9800, #fb8c00); color: white; }
    .score-low { background: linear-gradient(90deg, #f44336, #e53935); color: white; }
</style>
"""

st.markdown(professional_css, unsafe_allow_html=True)

# =============================================================================
# FUNCIONES DE CARGA Y ANÁLISIS AVANZADO
# =============================================================================

@st.cache_data(persist="disk", show_spinner=False, ttl=3600)
def load_and_preprocess_data():
    """Carga y preprocesa los datos con análisis avanzado"""
    try:
        df = pd.read_csv('screener-stocks-2025-09-18.csv')
        
        # Convertir porcentajes a números
        for col in df.columns:
            if df[col].dtype == 'object':
                sample = df[col].dropna().head(100)
                if sample.astype(str).str.contains('%', na=False).any():
                    df[col] = df[col].astype(str).str.replace('%', '').astype(float, errors='ignore')
        
        # Crear TODOS los scores compuestos
        df = create_all_composite_scores(df)
        
        # Detectar anomalías y oportunidades
        df = detect_opportunities(df)
        
        # Calcular rankings relativos
        df = calculate_relative_rankings(df)
        
        return df
        
    except FileNotFoundError:
        st.error("❌ **No se encontró el archivo 'screener-stocks-2025-09-18.csv'**")
        st.stop()

def create_all_composite_scores(df):
    """Crea TODOS los scores compuestos y métricas avanzadas"""
    
    # 1. QUALITY SCORES DETALLADOS
    df['Profitability_Score'] = 0
    for metric in ['ROE', 'ROA', 'ROIC', 'ROCE']:
        if metric in df.columns:
            df['Profitability_Score'] += np.where(df[metric] > df[metric].quantile(0.75), 25, 0)
    
    df['Margin_Score'] = 0
    for metric in ['Gross Margin', 'Operating Margin', 'Profit Margin', 'FCF Margin']:
        if metric in df.columns:
            df['Margin_Score'] += np.where(df[metric] > df[metric].quantile(0.75), 25, 0)
    
    df['Efficiency_Score'] = 0
    if 'Asset Turnover' in df.columns:
        df['Efficiency_Score'] += np.where(df['Asset Turnover'] > df['Asset Turnover'].quantile(0.7), 33, 0)
    if 'Inv. Turnover' in df.columns:
        df['Efficiency_Score'] += np.where(df['Inv. Turnover'] > df['Inv. Turnover'].quantile(0.7), 33, 0)
    if 'WC Turnover' in df.columns:
        df['Efficiency_Score'] += np.where(df['WC Turnover'] > df['WC Turnover'].quantile(0.7), 34, 0)
    
    # 2. VALUE SCORES AVANZADOS
    df['Deep_Value_Score'] = 0
    if 'PE Ratio' in df.columns:
        df['Deep_Value_Score'] += np.where((df['PE Ratio'] > 0) & (df['PE Ratio'] < 10), 25, 0)
    if 'PB Ratio' in df.columns:
        df['Deep_Value_Score'] += np.where(df['PB Ratio'] < 1, 25, 0)
    if 'P/FCF' in df.columns:
        df['Deep_Value_Score'] += np.where((df['P/FCF'] > 0) & (df['P/FCF'] < 15), 25, 0)
    if 'EV/EBITDA' in df.columns:
        df['Deep_Value_Score'] += np.where((df['EV/EBITDA'] > 0) & (df['EV/EBITDA'] < 8), 25, 0)
    
    df['Relative_Value_Score'] = 0
    # Valor relativo al sector
    if 'PE Ratio' in df.columns and 'Sector' in df.columns:
        sector_pe = df.groupby('Sector')['PE Ratio'].transform('median')
        df['PE_vs_Sector'] = df['PE Ratio'] / sector_pe
        df['Relative_Value_Score'] += np.where(df['PE_vs_Sector'] < 0.8, 50, 0)
    
    # 3. GROWTH SCORES DETALLADOS
    df['Revenue_Growth_Score'] = 0
    for metric in ['Rev. Growth', 'Rev. Growth 3Y', 'Rev. Growth 5Y', 'Rev Gr. Next Y']:
        if metric in df.columns:
            df['Revenue_Growth_Score'] += np.where(df[metric] > 15, 25, 0)
    
    df['Earnings_Growth_Score'] = 0
    for metric in ['EPS Growth', 'EPS Growth 3Y', 'EPS Growth 5Y', 'EPS Gr. Next Y']:
        if metric in df.columns:
            df['Earnings_Growth_Score'] += np.where(df[metric] > 15, 25, 0)
    
    df['Growth_Consistency_Score'] = 0
    if 'Rev Growth (Qtrs)' in df.columns:
        df['Growth_Consistency_Score'] += np.where(df['Rev Growth (Qtrs)'] >= 4, 50, 0)
    if 'EPS Growth (Qtrs)' in df.columns:
        df['Growth_Consistency_Score'] += np.where(df['EPS Growth (Qtrs)'] >= 4, 50, 0)
    
    # 4. FINANCIAL HEALTH SCORES AVANZADOS
    df['Liquidity_Score'] = 0
    for metric in ['Current Ratio', 'Quick Ratio', 'Cash Ratio']:
        if metric in df.columns:
            df['Liquidity_Score'] += np.where(df[metric] > 1.5, 33, 0)
    
    df['Solvency_Score'] = 0
    if 'Debt / Equity' in df.columns:
        df['Solvency_Score'] += np.where(df['Debt / Equity'] < 0.5, 25, 0)
    if 'Debt / EBITDA' in df.columns:
        df['Solvency_Score'] += np.where(df['Debt / EBITDA'] < 3, 25, 0)
    if 'Int. Cov.' in df.columns:
        df['Solvency_Score'] += np.where(df['Int. Cov.'] > 5, 25, 0)
    if 'Z-Score' in df.columns:
        df['Solvency_Score'] += np.where(df['Z-Score'] > 3, 25, 0)
    
    # 5. MOMENTUM SCORES DETALLADOS
    df['Price_Momentum_Score'] = 0
    momentum_periods = ['Return 1W', 'Return 1M', 'Return 3M', 'Return 6M', 'Return 1Y']
    for period in momentum_periods:
        if period in df.columns:
            df['Price_Momentum_Score'] += np.where(df[period] > 0, 20, 0)
    
    df['Volume_Momentum_Score'] = 0
    if 'Rel. Volume' in df.columns:
        df['Volume_Momentum_Score'] = np.where(df['Rel. Volume'] > 1.5, 100, 
                                               np.where(df['Rel. Volume'] > 1, 50, 0))
    
    # 6. DIVIDEND SCORES
    df['Dividend_Quality_Score'] = 0
    if 'Div. Yield' in df.columns:
        df['Dividend_Quality_Score'] += np.where((df['Div. Yield'] > 2) & (df['Div. Yield'] < 8), 25, 0)
    if 'Payout Ratio' in df.columns:
        df['Dividend_Quality_Score'] += np.where((df['Payout Ratio'] > 0) & (df['Payout Ratio'] < 60), 25, 0)
    if 'Years' in df.columns:
        df['Dividend_Quality_Score'] += np.where(df['Years'] > 10, 25, 0)
    if 'Div. Growth 5Y' in df.columns:
        df['Dividend_Quality_Score'] += np.where(df['Div. Growth 5Y'] > 5, 25, 0)
    
    # 7. INNOVATION & R&D SCORE
    df['Innovation_Score'] = 0
    if 'R&D / Rev' in df.columns:
        df['Innovation_Score'] = np.where(df['R&D / Rev'] > 15, 100,
                                         np.where(df['R&D / Rev'] > 10, 75,
                                                np.where(df['R&D / Rev'] > 5, 50, 0)))
    
    # 8. INSIDER CONFIDENCE SCORE
    df['Insider_Score'] = 0
    if 'Shares Insiders' in df.columns:
        df['Insider_Score'] += np.where(df['Shares Insiders'] > 10, 50, 0)
    if 'Shares Institut.' in df.columns:
        df['Insider_Score'] += np.where((df['Shares Institut.'] > 40) & (df['Shares Institut.'] < 80), 50, 0)
    
    # 9. VOLATILITY & RISK SCORES
    df['Low_Risk_Score'] = 0
    if 'Beta (5Y)' in df.columns:
        df['Low_Risk_Score'] += np.where(df['Beta (5Y)'] < 1, 50, 0)
    if 'ATR' in df.columns:
        df['Low_Risk_Score'] += np.where(df['ATR'] < df['ATR'].quantile(0.3), 50, 0)
    
    # 10. SHORT INTEREST SCORE (para detectar squeezes)
    df['Short_Squeeze_Score'] = 0
    if 'Short % Float' in df.columns:
        df['Short_Squeeze_Score'] = np.where(df['Short % Float'] > 20, 100,
                                            np.where(df['Short % Float'] > 15, 75,
                                                   np.where(df['Short % Float'] > 10, 50, 0)))
    
    # 11. EARNINGS QUALITY SCORE
    df['Earnings_Quality_Score'] = 0
    if 'FCF' in df.columns and 'Net Income' in df.columns:
        df['FCF_to_NI'] = df['FCF'] / df['Net Income']
        df['Earnings_Quality_Score'] += np.where(df['FCF_to_NI'] > 0.8, 50, 0)
    if 'F-Score' in df.columns:
        df['Earnings_Quality_Score'] += np.where(df['F-Score'] >= 7, 50, 0)
    
    # 12. CANSLIM SCORE
    df['CANSLIM_Score'] = 0
    if 'EPS Growth' in df.columns:
        df['CANSLIM_Score'] += np.where(df['EPS Growth'] > 25, 20, 0)  # Current earnings
    if 'EPS Growth 5Y' in df.columns:
        df['CANSLIM_Score'] += np.where(df['EPS Growth 5Y'] > 25, 20, 0)  # Annual earnings
    if 'Return 3M' in df.columns:
        df['CANSLIM_Score'] += np.where(df['Return 3M'] > 10, 20, 0)  # New highs
    if 'Shares' in df.columns:
        df['CANSLIM_Score'] += np.where(df['Shares'] < df['Shares'].quantile(0.3), 20, 0)  # Supply/demand
    if 'Shares Institut.' in df.columns:
        df['CANSLIM_Score'] += np.where(df['Shares Institut.'] > 30, 20, 0)  # Institutional
    
    # 13. MAGIC FORMULA SCORE (Joel Greenblatt)
    if 'ROIC' in df.columns and 'PE Ratio' in df.columns:
        df['Earnings_Yield'] = 1 / df['PE Ratio'].replace(0, np.nan)
        df['Magic_Rank_ROIC'] = df['ROIC'].rank(ascending=False)
        df['Magic_Rank_EY'] = df['Earnings_Yield'].rank(ascending=False)
        df['Magic_Formula_Score'] = 100 - ((df['Magic_Rank_ROIC'] + df['Magic_Rank_EY']) / (2 * len(df)) * 100)
    
    # 14. RULE OF 40 SCORE (para growth stocks)
    df['Rule_of_40_Score'] = 0
    if 'Rev. Growth' in df.columns and 'FCF Margin' in df.columns:
        df['Rule_of_40'] = df['Rev. Growth'] + df['FCF Margin']
        df['Rule_of_40_Score'] = np.where(df['Rule_of_40'] > 40, 100,
                                         np.where(df['Rule_of_40'] > 30, 75,
                                                np.where(df['Rule_of_40'] > 20, 50, 0)))
    
    # 15. MASTER SCORE SUPREMO (combinación ponderada de TODO)
    score_columns = [col for col in df.columns if col.endswith('_Score')]
    if score_columns:
        df['Ultra_Master_Score'] = df[score_columns].mean(axis=1)
    
    return df

def detect_opportunities(df):
    """Detecta oportunidades especiales y anomalías"""
    
    # Detectar Value Traps
    df['Value_Trap_Risk'] = 0
    if all(col in df.columns for col in ['PE Ratio', 'Debt / Equity', 'Rev. Growth']):
        df['Value_Trap_Risk'] = np.where(
            (df['PE Ratio'] < 10) & (df['Debt / Equity'] > 2) & (df['Rev. Growth'] < -10), 100, 0)
    
    # Detectar Hidden Gems
    df['Hidden_Gem'] = 0
    if all(col in df.columns for col in ['Market Cap', 'ROE', 'Rev. Growth', 'Shares Institut.']):
        df['Hidden_Gem'] = np.where(
            (df['Market Cap'] < 2e9) & (df['ROE'] > 15) & (df['Rev. Growth'] > 20) & 
            (df['Shares Institut.'] < 30), 100, 0)
    
    # Detectar Turnaround Candidates
    df['Turnaround_Potential'] = 0
    if all(col in df.columns for col in ['Return 3M', 'Z-Score', 'FCF']):
        df['Turnaround_Potential'] = np.where(
            (df['Return 3M'] > 10) & (df['Z-Score'] > 1.8) & (df['FCF'] > 0), 100, 0)
    
    # Detectar Dividend Aristocrats
    df['Dividend_Aristocrat'] = 0
    if all(col in df.columns for col in ['Years', 'Div. Growth 5Y', 'Payout Ratio']):
        df['Dividend_Aristocrat'] = np.where(
            (df['Years'] >= 25) & (df['Div. Growth 5Y'] > 0) & (df['Payout Ratio'] < 70), 100, 0)
    
    # Detectar Hypergrowth
    df['Hypergrowth'] = 0
    if 'Rev. Growth' in df.columns:
        df['Hypergrowth'] = np.where(df['Rev. Growth'] > 50, 100, 0)
    
    # Detectar Potential Acquisition Targets
    df['Acquisition_Target'] = 0
    if all(col in df.columns for col in ['Market Cap', 'FCF', 'Debt / Equity']):
        df['Acquisition_Target'] = np.where(
            (df['Market Cap'] < 5e9) & (df['FCF'] > 0) & (df['Debt / Equity'] < 1), 100, 0)
    
    return df

def calculate_relative_rankings(df):
    """Calcula rankings relativos por sector e industria"""
    
    # Rankings por sector
    if 'Sector' in df.columns:
        for metric in ['ROE', 'Rev. Growth', 'PE Ratio', 'Market Cap']:
            if metric in df.columns:
                df[f'{metric}_Sector_Rank'] = df.groupby('Sector')[metric].rank(pct=True) * 100
    
    # Rankings globales
    for metric in ['Ultra_Master_Score', 'Market Cap', 'ROE', 'Rev. Growth']:
        if metric in df.columns:
            df[f'{metric}_Global_Rank'] = df[metric].rank(pct=True) * 100
    
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
# SCREENERS ULTRA AVANZADOS
# =============================================================================

ULTRA_SCREENERS = {
    "🎯 Constructor Universal": {
        "name": "Constructor Universal",
        "description": "Acceso a TODAS las 230+ métricas y scores",
        "category": "custom",
        "filters": {}
    },
    
    # ESTRATEGIAS VALUE AVANZADAS
    "💎 Deep Value Contrarian": {
        "name": "Deep Value Contrarian",
        "description": "Empresas extremadamente infravaloradas con catalizadores - P/B < 0.7, FCF positivo, insider buying",
        "category": "value",
        "filters": {
            "pb_max": 0.7,
            "pe_max": 8,
            "fcf_min": 0,
            "insider_score_min": 50,
            "deep_value_score_min": 75
        }
    },
    
    "🏦 Benjamin Graham Net-Net": {
        "name": "Graham Net-Net",
        "description": "Trading por debajo del valor de liquidación - P/B < 0.66, Current Ratio > 2",
        "category": "value",
        "filters": {
            "pb_max": 0.66,
            "current_ratio_min": 2,
            "z_score_min": 1.8,
            "deep_value_score_min": 80
        }
    },
    
    # ESTRATEGIAS GROWTH AVANZADAS
    "🚀 Hypergrowth SaaS": {
        "name": "Hypergrowth SaaS",
        "description": "Rule of 40 > 40%, Gross Margin > 70%, Rev Growth > 30%",
        "category": "growth",
        "filters": {
            "rule_of_40_score_min": 75,
            "gross_margin_min": 70,
            "rev_growth_min": 30,
            "revenue_growth_score_min": 80
        }
    },
    
    "⚡ Earnings Acceleration": {
        "name": "Earnings Acceleration",
        "description": "EPS acelerando trimestre a trimestre, sorpresas positivas",
        "category": "growth",
        "filters": {
            "eps_growth_min": 20,
            "earnings_growth_score_min": 75,
            "growth_consistency_score_min": 75,
            "canslim_score_min": 60
        }
    },
    
    # ESTRATEGIAS MOMENTUM
    "📈 Institutional Accumulation": {
        "name": "Institutional Accumulation",
        "description": "Fuerte compra institucional + momentum técnico",
        "category": "momentum",
        "filters": {
            "institutional_ownership_min": 40,
            "institutional_ownership_max": 80,
            "price_momentum_score_min": 70,
            "volume_momentum_score_min": 50,
            "rsi_min": 50,
            "rsi_max": 70
        }
    },
    
    "🎢 Short Squeeze Candidates": {
        "name": "Short Squeeze Setup",
        "description": "Alto short interest + momentum positivo = potential squeeze",
        "category": "momentum",
        "filters": {
            "short_squeeze_score_min": 75,
            "return_1m_min": 5,
            "volume_momentum_score_min": 50,
            "rsi_min": 45,
            "rsi_max": 65
        }
    },
    
    # ESTRATEGIAS QUALITY
    "🏆 Competitive Advantage": {
        "name": "Moat Companies",
        "description": "ROE > 20% sostenido, márgenes superiores al sector",
        "category": "quality",
        "filters": {
            "roe_min": 20,
            "profitability_score_min": 80,
            "margin_score_min": 75,
            "earnings_quality_score_min": 70
        }
    },
    
    "💰 Cash Flow Machines": {
        "name": "FCF Generators",
        "description": "FCF Yield > 8%, FCF/NI > 0.9, crecimiento de FCF",
        "category": "quality",
        "filters": {
            "fcf_yield_min": 8,
            "earnings_quality_score_min": 80,
            "fcf_margin_min": 15,
            "solvency_score_min": 75
        }
    },
    
    # ESTRATEGIAS INCOME
    "👑 Dividend Aristocrats Plus": {
        "name": "Dividend Excellence",
        "description": "25+ años dividendos, crecimiento sostenible, FCF coverage",
        "category": "income",
        "filters": {
            "dividend_aristocrat": 100,
            "dividend_quality_score_min": 80,
            "financial_health_score_min": 70
        }
    },
    
    "💵 High Yield Safe": {
        "name": "Safe High Yield",
        "description": "Yield > 5% pero con cobertura de FCF y bajo payout",
        "category": "income",
        "filters": {
            "div_yield_min": 5,
            "div_yield_max": 10,
            "payout_ratio_max": 60,
            "fcf_payout_max": 50,
            "solvency_score_min": 70
        }
    },
    
    # ESTRATEGIAS ESPECIALES
    "🔬 Innovation Leaders": {
        "name": "R&D Champions",
        "description": "Alto R&D/Sales, crecimiento, sector tech/healthcare",
        "category": "thematic",
        "filters": {
            "innovation_score_min": 75,
            "rev_growth_min": 15,
            "sectors": ["Technology", "Healthcare"],
            "gross_margin_min": 50
        }
    },
    
    "🎯 Hidden Gems Finder": {
        "name": "Undiscovered Value",
        "description": "Small caps ignorados con métricas excepcionales",
        "category": "special",
        "filters": {
            "hidden_gem": 100,
            "market_cap_max": 2e9,
            "institutional_ownership_max": 30,
            "ultra_master_score_min": 70
        }
    },
    
    "🔄 Turnaround Plays": {
        "name": "Recovery Stories",
        "description": "Empresas saliendo de problemas con señales positivas",
        "category": "special",
        "filters": {
            "turnaround_potential": 100,
            "z_score_min": 1.8,
            "return_3m_min": 10,
            "fcf_min": 0
        }
    },
    
    "🏦 M&A Targets": {
        "name": "Acquisition Candidates",
        "description": "Potenciales objetivos de adquisición",
        "category": "special",
        "filters": {
            "acquisition_target": 100,
            "market_cap_max": 5e9,
            "fcf_min": 0,
            "debt_equity_max": 1
        }
    },
    
    # FACTOR INVESTING
    "📊 Multi-Factor Quant": {
        "name": "5-Factor Model",
        "description": "Combina Value + Quality + Growth + Momentum + Low Risk",
        "category": "quant",
        "filters": {
            "deep_value_score_min": 60,
            "profitability_score_min": 60,
            "revenue_growth_score_min": 60,
            "price_momentum_score_min": 60,
            "low_risk_score_min": 60
        }
    },
    
    "🎲 Magic Formula Enhanced": {
        "name": "Greenblatt Plus",
        "description": "Magic Formula mejorada con quality y momentum",
        "category": "quant",
        "filters": {
            "magic_formula_score_min": 80,
            "earnings_quality_score_min": 60,
            "price_momentum_score_min": 50
        }
    },
    
    "🌟 CANSLIM Algorithm": {
        "name": "O'Neil CANSLIM",
        "description": "Sistema completo CAN-SLIM de William O'Neil",
        "category": "quant",
        "filters": {
            "canslim_score_min": 80,
            "price_momentum_score_min": 70,
            "volume_momentum_score_min": 50,
            "institutional_ownership_min": 30
        }
    }
}

# =============================================================================
# INICIALIZACIÓN
# =============================================================================

if 'filters_applied' not in st.session_state:
    st.session_state.filters_applied = False
if 'selected_stocks' not in st.session_state:
    st.session_state.selected_stocks = []
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False
if 'advanced_mode' not in st.session_state:
    st.session_state.advanced_mode = False

# Cargar datos
with st.spinner("🚀 Cargando base de datos con 230+ métricas..."):
    df = load_and_preprocess_data()

# =============================================================================
# HEADER
# =============================================================================

st.markdown("""
<div style='text-align: center; padding: 30px 0; background: linear-gradient(135deg, #1c1f26 0%, #262b36 100%); 
            border-radius: 20px; margin-bottom: 30px; border: 2px solid #4a9eff30;'>
    <h1 style='margin: 0; font-size: 2.5em;'>🚀 BQuant Ultra Screener Pro</h1>
    <p style='color: #b8b8b8; margin-top: 10px; font-size: 1.2em;'>
        Sistema profesional con <strong>230+ métricas</strong> | <strong>20+ scores algorítmicos</strong> | <strong>ML insights</strong>
    </p>
    <p style='color: #4a9eff; margin-top: 10px;'>
        <strong>@Gsnchez</strong> | <strong>bquantfinance.com</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# Quick Stats
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("📊 Acciones", f"{len(df):,}")
with col2:
    st.metric("📈 Métricas", "230+")
with col3:
    st.metric("🎯 Scores", "20+")
with col4:
    st.metric("💎 Value Ops", len(df[df['Deep_Value_Score'] > 80]) if 'Deep_Value_Score' in df.columns else 0)
with col5:
    st.metric("🚀 Growth Ops", len(df[df['Revenue_Growth_Score'] > 80]) if 'Revenue_Growth_Score' in df.columns else 0)
with col6:
    st.metric("🔥 Hot Stocks", len(df[df['Price_Momentum_Score'] > 80]) if 'Price_Momentum_Score' in df.columns else 0)

# =============================================================================
# SIDEBAR
# =============================================================================

st.sidebar.markdown("# ⚡ Ultra Screener Control")
st.sidebar.markdown("---")

# Modo de operación
operation_mode = st.sidebar.radio(
    "🎮 Modo de Operación",
    ["🎯 Screeners Predefinidos", "🔬 Constructor Avanzado", "🤖 ML Discovery", "📊 Factor Analysis"],
    help="Elige tu modo de análisis"
)

if operation_mode == "🎯 Screeners Predefinidos":
    # Categorías de screeners
    categories = list(set([s['category'] for s in ULTRA_SCREENERS.values()]))
    selected_category = st.sidebar.selectbox("📁 Categoría", categories)
    
    # Filtrar screeners por categoría
    category_screeners = {k: v for k, v in ULTRA_SCREENERS.items() if v['category'] == selected_category}
    
    selected_screener = st.sidebar.selectbox(
        "🎯 Screener",
        options=list(category_screeners.keys())
    )
    
    screener_config = ULTRA_SCREENERS[selected_screener]
    
    # Mostrar descripción
    st.sidebar.info(f"📝 {screener_config['description']}")
    
    # Aplicar filtros del screener
    preset_filters = screener_config['filters']

elif operation_mode == "🔬 Constructor Avanzado":
    st.sidebar.info("Construye tu screener con acceso total a 230+ métricas")
    preset_filters = {}
    selected_screener = "Constructor Avanzado"

elif operation_mode == "🤖 ML Discovery":
    st.sidebar.info("Descubrimiento automático de oportunidades con Machine Learning")
    preset_filters = {}
    selected_screener = "ML Discovery"

else:  # Factor Analysis
    st.sidebar.info("Análisis factorial y construcción de portfolios")
    preset_filters = {}
    selected_screener = "Factor Analysis"

# Filtros básicos siempre visibles
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros Rápidos")

search_term = st.sidebar.text_input("🔎 Buscar", placeholder="Ticker o nombre...")

col1, col2 = st.sidebar.columns(2)
with col1:
    min_mcap = st.text_input("MCap Min", placeholder="1B")
with col2:
    max_mcap = st.text_input("MCap Max", placeholder="100B")

sectors = st.sidebar.multiselect(
    "🏢 Sectores",
    options=sorted(df['Sector'].dropna().unique()),
    default=preset_filters.get('sectors', [])
)

# Botón aplicar
st.sidebar.markdown("---")
if st.sidebar.button("⚡ **EJECUTAR ANÁLISIS**", type="primary", use_container_width=True):
    st.session_state.filters_applied = True

# =============================================================================
# ÁREA PRINCIPAL
# =============================================================================

# Tabs principales
if operation_mode == "🎯 Screeners Predefinidos":
    tabs = st.tabs([
        "📊 Resultados", 
        "📈 Analytics", 
        "🎯 Scores", 
        "🔥 Heatmaps",
        "📋 Comparador",
        "💾 Export"
    ])
elif operation_mode == "🔬 Constructor Avanzado":
    tabs = st.tabs([
        "⚙️ Constructor",
        "📊 Resultados",
        "📈 Analytics",
        "💾 Export"
    ])
elif operation_mode == "🤖 ML Discovery":
    tabs = st.tabs([
        "🤖 ML Analysis",
        "🎯 Anomalías",
        "📊 Clusters",
        "🔮 Predicciones"
    ])
else:  # Factor Analysis
    tabs = st.tabs([
        "📊 Factores",
        "🎯 Portfolio",
        "📈 Backtest",
        "⚖️ Optimización"
    ])

# =============================================================================
# CONTENIDO DE TABS SEGÚN MODO
# =============================================================================

if operation_mode == "🎯 Screeners Predefinidos":
    
    # Aplicar filtros
    if st.session_state.filters_applied:
        filtered_df = df.copy()
        
        # Aplicar todos los filtros
        if search_term:
            filtered_df = filtered_df[
                (filtered_df['Symbol'].str.contains(search_term.upper(), na=False)) |
                (filtered_df['Company Name'].str.contains(search_term, case=False, na=False))
            ]
        
        if sectors:
            filtered_df = filtered_df[filtered_df['Sector'].isin(sectors)]
        
        # Market Cap
        min_mc = parse_market_cap(min_mcap)
        max_mc = parse_market_cap(max_mcap)
        if min_mc:
            filtered_df = filtered_df[filtered_df['Market Cap'] >= min_mc]
        if max_mc:
            filtered_df = filtered_df[filtered_df['Market Cap'] <= max_mc]
        
        # Aplicar filtros del screener
        for key, value in preset_filters.items():
            if key == 'sectors':
                continue
            elif key.endswith('_min'):
                col = key.replace('_min', '').replace('_', ' ').title()
                # Buscar columna exacta
                for df_col in filtered_df.columns:
                    if df_col.lower().replace(' ', '_') == key.replace('_min', ''):
                        filtered_df = filtered_df[filtered_df[df_col] >= value]
                        break
            elif key.endswith('_max'):
                col = key.replace('_max', '').replace('_', ' ').title()
                for df_col in filtered_df.columns:
                    if df_col.lower().replace(' ', '_') == key.replace('_max', ''):
                        filtered_df = filtered_df[filtered_df[df_col] <= value]
                        break
            elif key in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[key] == value]
        
        # TAB 1: RESULTADOS
        with tabs[0]:
            st.markdown(f"### 📊 Resultados: {selected_screener}")
            
            # Métricas resumen
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total", f"{len(filtered_df):,}")
            with col2:
                avg_score = filtered_df['Ultra_Master_Score'].mean() if 'Ultra_Master_Score' in filtered_df.columns else 0
                st.metric("Score Promedio", f"{avg_score:.0f}")
            with col3:
                median_pe = filtered_df['PE Ratio'].median() if 'PE Ratio' in filtered_df.columns else 0
                st.metric("P/E Mediano", f"{median_pe:.1f}")
            with col4:
                total_mcap = filtered_df['Market Cap'].sum() if 'Market Cap' in filtered_df.columns else 0
                st.metric("MCap Total", format_number(total_mcap, prefix="$"))
            
            # Selector de columnas inteligente según screener
            if "Value" in selected_screener:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'PE Ratio', 'PB Ratio',
                               'Deep_Value_Score', 'Magic_Formula_Score', 'FCF Yield']
            elif "Growth" in selected_screener:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'Rev. Growth',
                               'Revenue_Growth_Score', 'Rule_of_40_Score', 'CANSLIM_Score']
            elif "Dividend" in selected_screener:
                default_cols = ['Symbol', 'Company Name', 'Div. Yield', 'Payout Ratio',
                               'Dividend_Quality_Score', 'Years', 'FCF Yield']
            elif "Momentum" in selected_screener:
                default_cols = ['Symbol', 'Company Name', 'Return 1Y', 'RSI',
                               'Price_Momentum_Score', 'Volume_Momentum_Score', 'Short_Squeeze_Score']
            else:
                default_cols = ['Symbol', 'Company Name', 'Market Cap', 'Ultra_Master_Score',
                               'Deep_Value_Score', 'Revenue_Growth_Score', 'Profitability_Score']
            
            available_cols = [col for col in default_cols if col in filtered_df.columns]
            
            # Tabla interactiva
            st.dataframe(
                filtered_df[available_cols].head(100).style.background_gradient(
                    cmap='RdYlGn',
                    subset=[col for col in available_cols if 'Score' in col],
                    vmin=0, vmax=100
                ),
                use_container_width=True,
                height=600
            )
        
        # TAB 2: ANALYTICS
        with tabs[1]:
            st.markdown("### 📈 Analytics Avanzado")
            
            # Scatter matrix de scores
            score_cols = [col for col in filtered_df.columns if col.endswith('_Score')][:6]
            if len(score_cols) >= 2:
                fig = px.scatter_matrix(
                    filtered_df.head(500),
                    dimensions=score_cols,
                    color='Ultra_Master_Score' if 'Ultra_Master_Score' in filtered_df.columns else None,
                    title="Matrix de Scores Multi-Dimensional",
                    height=800
                )
                fig.update_layout(template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
        
        # TAB 3: SCORES
        with tabs[2]:
            st.markdown("### 🎯 Análisis de Scores")
            
            # Top 10 por cada score
            score_types = ['Deep_Value_Score', 'Revenue_Growth_Score', 'Profitability_Score',
                          'Dividend_Quality_Score', 'Price_Momentum_Score', 'Innovation_Score']
            
            cols = st.columns(3)
            for i, score in enumerate(score_types):
                if score in filtered_df.columns:
                    with cols[i % 3]:
                        st.markdown(f"**Top {score.replace('_', ' ')}**")
                        top = filtered_df.nlargest(5, score)[['Symbol', score]]
                        for _, row in top.iterrows():
                            color = "#4caf50" if row[score] > 80 else "#ff9800" if row[score] > 60 else "#f44336"
                            st.markdown(f"<span style='color: {color}'>**{row['Symbol']}**: {row[score]:.0f}</span>", 
                                      unsafe_allow_html=True)
        
        # TAB 4: HEATMAPS
        with tabs[3]:
            st.markdown("### 🔥 Heatmaps de Correlación")
            
            # Correlación entre scores
            score_cols = [col for col in filtered_df.columns if col.endswith('_Score')][:15]
            if len(score_cols) > 2:
                corr = filtered_df[score_cols].corr()
                fig = px.imshow(
                    corr,
                    title="Correlación entre Scores",
                    color_continuous_scale='RdBu',
                    zmin=-1, zmax=1
                )
                fig.update_layout(template='plotly_dark', height=600)
                st.plotly_chart(fig, use_container_width=True)

elif operation_mode == "🔬 Constructor Avanzado":
    
    with tabs[0]:  # Constructor
        st.markdown("### ⚙️ Constructor de Filtros Avanzado")
        st.info("Acceso completo a las 230+ métricas disponibles")
        
        # Organizar métricas por categorías
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("#### 📊 Scores Algorítmicos")
            with st.expander("20+ Scores Disponibles"):
                ultra_master_min = st.slider("Ultra Master Score", 0, 100, 0)
                deep_value_min = st.slider("Deep Value Score", 0, 100, 0)
                revenue_growth_min = st.slider("Revenue Growth Score", 0, 100, 0)
                profitability_min = st.slider("Profitability Score", 0, 100, 0)
                dividend_quality_min = st.slider("Dividend Quality Score", 0, 100, 0)
                momentum_min = st.slider("Price Momentum Score", 0, 100, 0)
                innovation_min = st.slider("Innovation Score", 0, 100, 0)
                canslim_min = st.slider("CANSLIM Score", 0, 100, 0)
                magic_formula_min = st.slider("Magic Formula Score", 0, 100, 0)
        
        with col2:
            st.markdown("#### 💰 Valoración")
            with st.expander("Métricas de Valor"):
                pe_max = st.number_input("P/E Max", value=100.0)
                pb_max = st.number_input("P/B Max", value=10.0)
                ps_max = st.number_input("P/S Max", value=20.0)
                peg_max = st.number_input("PEG Max", value=3.0)
                ev_ebitda_max = st.number_input("EV/EBITDA Max", value=50.0)
                pfcf_max = st.number_input("P/FCF Max", value=50.0)
        
        with col3:
            st.markdown("#### 📈 Crecimiento")
            with st.expander("Métricas de Growth"):
                rev_growth_min = st.number_input("Revenue Growth Min %", value=-100.0)
                eps_growth_min = st.number_input("EPS Growth Min %", value=-100.0)
                fcf_growth_min = st.number_input("FCF Growth Min %", value=-100.0)
                rev_5y_cagr_min = st.number_input("Revenue 5Y CAGR Min %", value=-100.0)
                rule_of_40_min = st.number_input("Rule of 40 Min", value=0.0)
        
        with col4:
            st.markdown("#### 🏥 Salud Financiera")
            with st.expander("Balance y Liquidez"):
                current_ratio_min = st.number_input("Current Ratio Min", value=0.0)
                debt_equity_max = st.number_input("Debt/Equity Max", value=10.0)
                z_score_min = st.number_input("Z-Score Min", value=-5.0)
                fcf_yield_min = st.number_input("FCF Yield Min %", value=-20.0)
                roe_min = st.number_input("ROE Min %", value=-100.0)

elif operation_mode == "🤖 ML Discovery":
    
    with tabs[0]:  # ML Analysis
        st.markdown("### 🤖 Machine Learning Discovery")
        
        # PCA Analysis
        st.markdown("#### 🎯 Análisis de Componentes Principales")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        score_cols = [col for col in numeric_cols if 'Score' in col]
        
        if len(score_cols) > 2:
            # Preparar datos para PCA
            pca_data = df[score_cols].dropna()
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(pca_data)
            
            # PCA
            pca = PCA(n_components=3)
            pca_result = pca.fit_transform(scaled_data)
            
            # Visualización 3D
            fig = px.scatter_3d(
                x=pca_result[:, 0],
                y=pca_result[:, 1],
                z=pca_result[:, 2],
                color=df.loc[pca_data.index, 'Ultra_Master_Score'] if 'Ultra_Master_Score' in df.columns else None,
                hover_data={'Symbol': df.loc[pca_data.index, 'Symbol'].values},
                title="PCA 3D - Espacio de Scores",
                labels={'x': f'PC1 ({pca.explained_variance_ratio_[0]:.1%})',
                       'y': f'PC2 ({pca.explained_variance_ratio_[1]:.1%})',
                       'z': f'PC3 ({pca.explained_variance_ratio_[2]:.1%})'}
            )
            fig.update_layout(template='plotly_dark', height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # Explicación de componentes
            st.info(f"Los 3 componentes principales explican el {pca.explained_variance_ratio_.sum():.1%} de la varianza")
    
    with tabs[1]:  # Anomalías
        st.markdown("### 🎯 Detección de Anomalías")
        
        # Mostrar stocks con características especiales
        anomaly_cols = ['Value_Trap_Risk', 'Hidden_Gem', 'Turnaround_Potential', 
                       'Dividend_Aristocrat', 'Hypergrowth', 'Acquisition_Target']
        
        for anomaly in anomaly_cols:
            if anomaly in df.columns:
                anomaly_stocks = df[df[anomaly] == 100]
                if len(anomaly_stocks) > 0:
                    st.markdown(f"#### {anomaly.replace('_', ' ')}")
                    st.dataframe(
                        anomaly_stocks[['Symbol', 'Company Name', 'Market Cap', 'Ultra_Master_Score']].head(10),
                        use_container_width=True
                    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #b8b8b8;'>
    <strong>BQuant Ultra Screener Pro</strong> | 230+ métricas | 20+ scores algorítmicos<br>
    Desarrollado por <strong>@Gsnchez</strong> | <strong>bquantfinance.com</strong>
</div>
""", unsafe_allow_html=True)

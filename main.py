import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import warnings
import io

warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="BQuant Global Professional Screener | @Gsnchez",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Profesional Mejorado
professional_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --primary-color: #4a9eff;
        --primary-hover: #3a8eef;
        --secondary-color: #9333ea;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --bg-color: #0e1117;
        --content-bg: #1c1f26;
        --border-color: #2e3139;
        --text-color: #c9d1d9;
        --header-color: #f0f6fc;
        --muted-color: #8b949e;
    }

    /* Ocultar sidebar */
    section[data-testid="stSidebar"] {
        display: none;
    }

    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1f2e 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-color);
    }
    
    /* Headers con gradiente */
    h1, h2, h3, h4, h5 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--header-color);
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Botones con animación */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(74, 158, 255, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(74, 158, 255, 0.5);
    }
    
    /* Secciones de filtros con glassmorphism */
    .filter-section {
        background: rgba(28, 31, 38, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid rgba(74, 158, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Métricas con hover effect */
    .metric-card {
        background: linear-gradient(135deg, rgba(74, 158, 255, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border: 1px solid rgba(74, 158, 255, 0.3);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .metric-card:hover {
        transform: scale(1.02);
        border-color: var(--primary-color);
        box-shadow: 0 0 20px rgba(74, 158, 255, 0.4);
    }
    
    /* Tooltips educativos */
    .tooltip {
        position: relative;
        display: inline-block;
        color: var(--warning-color);
        cursor: help;
        font-size: 12px;
        margin-left: 4px;
    }
    
    /* Tabs mejorados */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(145deg, rgba(28, 31, 38, 0.9), rgba(21, 25, 34, 0.9));
        border-radius: 12px;
        padding: 8px;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.4);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
        box-shadow: 0 4px 12px rgba(74, 158, 255, 0.4);
        font-weight: 600;
    }
    
    /* Inputs con estilo */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        background: rgba(30, 35, 45, 0.6);
        border: 1px solid rgba(74, 158, 255, 0.3);
        color: var(--text-color);
        padding: 10px 14px;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.2);
        background: rgba(30, 35, 45, 0.8);
    }
    
    /* Headers de sección */
    .section-header {
        font-size: 1.2em;
        font-weight: 600;
        color: var(--header-color);
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--primary-color);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Badges de screener */
    .screener-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 24px;
        font-size: 12px;
        font-weight: 600;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        box-shadow: 0 4px 12px rgba(147, 51, 234, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(74, 158, 255, 0.1));
        border-left: 4px solid var(--success-color);
        padding: 12px 16px;
        border-radius: 8px;
        margin: 12px 0;
        font-size: 13px;
        color: var(--text-color);
    }
    
    /* Sliders personalizados */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, var(--danger-color), var(--warning-color), var(--success-color));
    }
</style>
"""
st.markdown(professional_css, unsafe_allow_html=True)


# =============================================================================
# FUNCIONES PRINCIPALES
# =============================================================================

@st.cache_data(persist="disk", show_spinner=False, ttl=3600)
def load_and_preprocess_data():
    try:
        df = pd.read_csv('all_countries_stocks_20250919_122611.csv', low_memory=False)
        
        # Fill missing country values
        if 'Country' in df.columns:
            df['Country'] = df['Country'].fillna('Unknown')
            if 'Country_Original' in df.columns:
                df.loc[df['Country'] == 'Unknown', 'Country'] = df.loc[df['Country'] == 'Unknown', 'Country_Original']
        if 'Market Cap' in df.columns:
            df['Market Cap'] = df['Market Cap'].fillna(0)
            
        # List of columns that should be numeric
        numeric_columns = [
            'PE Ratio', 'Forward PE', 'PB Ratio', 'PS Ratio', 'Forward PS', 'PEG Ratio',
            'P/FCF', 'P/OCF', 'P/EBITDA', 'P/TBV', 'P/FFO',
            'EV/Sales', 'EV/EBITDA', 'EV/EBIT', 'EV/FCF', 'EV/Earnings',
            'FCF Yield', 'Earnings Yield', 'Graham (%)', 'Lynch (%)',
            'ROE', 'ROA', 'ROIC', 'ROCE', 'ROE (5Y)', 'ROA (5Y)', 'ROIC (5Y)',
            'Gross Margin', 'Oper. Margin', 'Pretax Margin', 'Profit Margin',
            'FCF Margin', 'EBITDA Margin', 'EBIT Margin',
            'Rev. Growth', 'Rev. Growth (Q)', 'Rev. Growth 3Y', 'Rev. Growth 5Y',
            'EPS Growth', 'EPS Growth (Q)', 'EPS Growth 3Y', 'EPS Growth 5Y',
            'Current Ratio', 'Quick Ratio', 'Debt / Equity', 'Debt / EBITDA',
            'Z-Score', 'F-Score', 'FCF', 'Market Cap',
            'Years', 'Div. Yield', 'Payout Ratio', 'Div. Growth',
            'RSI', 'RSI (W)', 'RSI (M)', 'Beta (5Y)', 'ATR', 'Rel. Volume',
            'Return 1W', 'Return 1M', 'Return 3M', 'Return 6M', 'Return YTD',
            'Return 1Y', 'Return 3Y', 'Return 5Y', 'Return 10Y',
            'Shares Insiders', 'Shares Institut.', 'Short % Float', 'Short Ratio',
            '52W High Chg', '52W Low Chg', 'Employees', 'Founded', 'Analysts',
            'Rev Gr. This Y', 'Rev Gr. Next Y', 'EPS Gr. This Y', 'EPS Gr. Next Y',
            'Rev Gr. This Q', 'Rev Gr. Next Q', 'EPS Gr. This Q', 'EPS Gr. Next Q'
        ]
        
        # Process columns that might contain percentage signs
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains percentage values
                sample = df[col].dropna().head(100).astype(str)
                if sample.str.contains('%', na=False).any():
                    # Remove % and convert to float
                    df[col] = df[col].astype(str).str.replace('%', '', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert all numeric columns to proper numeric type
        for col in numeric_columns:
            if col in df.columns:
                # Handle special cases
                if df[col].dtype == 'object':
                    # Remove any non-numeric characters (except . and -)
                    df[col] = df[col].astype(str).str.replace('[^0-9.-]', '', regex=True)
                    # Replace empty strings with NaN
                    df[col] = df[col].replace('', np.nan)
                    df[col] = df[col].replace('-', np.nan)
                    df[col] = df[col].replace('N/A', np.nan)
                    df[col] = df[col].replace('n/a', np.nan)
                
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Handle Market Cap specifically (might have K, M, B suffixes)
        if 'Market Cap' in df.columns and df['Market Cap'].dtype == 'object':
            def parse_market_cap_value(val):
                if pd.isna(val) or val == '':
                    return np.nan
                val = str(val).upper().replace(',', '').strip()
                multipliers = {'K': 1e3, 'M': 1e6, 'B': 1e9, 'T': 1e12}
                for suffix, mult in multipliers.items():
                    if val.endswith(suffix):
                        try:
                            return float(val[:-1]) * mult
                        except:
                            return np.nan
                try:
                    return float(val)
                except:
                    return np.nan
            
            df['Market Cap'] = df['Market Cap'].apply(parse_market_cap_value)
        
        # Process date columns
        date_cols = ['IPO Date', 'Ex-Div Date', 'Payment Date', 'Earnings Date', 
                     'Last Report Date', 'Next Earnings', 'Last Earnings', 'ATH Date', 'ATL Date',
                     'Last Stock Split', 'Last Split Date', '10K Date']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Create composite metrics
        df = create_composite_metrics(df)
        
        # Final validation: ensure critical numeric columns are numeric
        critical_numeric = ['PE Ratio', 'PB Ratio', 'ROE', 'Market Cap', 'Rev. Growth', 'Return 1Y']
        for col in critical_numeric:
            if col in df.columns and df[col].dtype == 'object':
                print(f"Warning: {col} still contains non-numeric values after processing")
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
        
    except FileNotFoundError:
        st.error(f"❌ **Archivo no encontrado: all_countries_stocks_20250919_122611.csv**")
        st.info("Por favor asegúrese de que el archivo CSV esté en el mismo directorio que esta aplicación.")
        st.stop()

def create_composite_metrics(df):
    # Score de Calidad
    df['Quality_Score'] = 0
    if 'ROE' in df.columns and df['ROE'].notna().any(): 
        df['Quality_Score'] += np.where(df['ROE'] > df['ROE'].quantile(0.7), 25, 0)
    if 'ROA' in df.columns and df['ROA'].notna().any(): 
        df['Quality_Score'] += np.where(df['ROA'] > df['ROA'].quantile(0.7), 25, 0)
    if 'ROIC' in df.columns and df['ROIC'].notna().any(): 
        df['Quality_Score'] += np.where(df['ROIC'] > df['ROIC'].quantile(0.7), 25, 0)
    if 'Profit Margin' in df.columns and df['Profit Margin'].notna().any(): 
        df['Quality_Score'] += np.where(df['Profit Margin'] > df['Profit Margin'].quantile(0.7), 25, 0)
    
    # Score de Valor
    df['Value_Score'] = 0
    if 'PE Ratio' in df.columns and df['PE Ratio'].notna().any(): 
        df['Value_Score'] += np.where((df['PE Ratio'] > 0) & (df['PE Ratio'] < df['PE Ratio'].quantile(0.3)), 25, 0)
    if 'PB Ratio' in df.columns and df['PB Ratio'].notna().any(): 
        df['Value_Score'] += np.where(df['PB Ratio'] < df['PB Ratio'].quantile(0.3), 25, 0)
    if 'PS Ratio' in df.columns and df['PS Ratio'].notna().any(): 
        df['Value_Score'] += np.where(df['PS Ratio'] < df['PS Ratio'].quantile(0.3), 25, 0)
    if 'EV/EBITDA' in df.columns and df['EV/EBITDA'].notna().any(): 
        df['Value_Score'] += np.where((df['EV/EBITDA'] > 0) & (df['EV/EBITDA'] < df['EV/EBITDA'].quantile(0.3)), 25, 0)
    
    # Score de Crecimiento  
    df['Growth_Score'] = 0
    if 'Rev. Growth' in df.columns and df['Rev. Growth'].notna().any():
        df['Growth_Score'] += np.where(df['Rev. Growth'] > 20, 25, 0)
    if 'EPS Growth' in df.columns and df['EPS Growth'].notna().any():
        df['Growth_Score'] += np.where(df['EPS Growth'] > 20, 25, 0)
    if 'Rev Gr. Next Y' in df.columns and df['Rev Gr. Next Y'].notna().any(): 
        df['Growth_Score'] += np.where(df['Rev Gr. Next Y'] > 15, 25, 0)
    if 'EPS Gr. Next Y' in df.columns and df['EPS Gr. Next Y'].notna().any(): 
        df['Growth_Score'] += np.where(df['EPS Gr. Next Y'] > 15, 25, 0)
    
    # Score de Salud Financiera
    df['Financial_Health_Score'] = 0
    if 'Current Ratio' in df.columns and df['Current Ratio'].notna().any(): 
        df['Financial_Health_Score'] += np.where(df['Current Ratio'] > 1.5, 25, 0)
    if 'Debt / Equity' in df.columns and df['Debt / Equity'].notna().any(): 
        df['Financial_Health_Score'] += np.where(df['Debt / Equity'] < 1, 25, 0)
    if 'Z-Score' in df.columns and df['Z-Score'].notna().any(): 
        df['Financial_Health_Score'] += np.where(df['Z-Score'] > 3, 25, 0)
    if 'FCF Yield' in df.columns and df['FCF Yield'].notna().any(): 
        df['Financial_Health_Score'] += np.where(df['FCF Yield'] > 5, 25, 0)
    
    # Score de Momentum
    df['Momentum_Score'] = 0
    if 'Return 1Y' in df.columns and df['Return 1Y'].notna().any(): 
        df['Momentum_Score'] += np.where(df['Return 1Y'] > df['Return 1Y'].quantile(0.7), 30, 0)
    if 'Return 3M' in df.columns and df['Return 3M'].notna().any(): 
        df['Momentum_Score'] += np.where(df['Return 3M'] > 0, 20, 0)
    if 'Return 1M' in df.columns and df['Return 1M'].notna().any(): 
        df['Momentum_Score'] += np.where(df['Return 1M'] > 0, 20, 0)
    if 'RSI' in df.columns and df['RSI'].notna().any(): 
        df['Momentum_Score'] += np.where((df['RSI'] > 50) & (df['RSI'] < 70), 30, 0)
    
    # Score Maestro
    df['Master_Score'] = (df['Quality_Score']*0.3 + df['Value_Score']*0.25 + 
                          df['Growth_Score']*0.2 + df['Financial_Health_Score']*0.15 + 
                          df['Momentum_Score']*0.1)
    return df

def format_number(num, prefix="", suffix="", decimals=2):
    if pd.isna(num): return "N/D"
    if abs(num) >= 1e12: return f"{prefix}{num/1e12:.{decimals}f}T{suffix}"
    elif abs(num) >= 1e9: return f"{prefix}{num/1e9:.{decimals}f}B{suffix}"
    elif abs(num) >= 1e6: return f"{prefix}{num/1e6:.{decimals}f}M{suffix}"
    elif abs(num) >= 1e3: return f"{prefix}{num/1e3:.{decimals}f}K{suffix}"
    else: return f"{prefix}{num:.{decimals}f}{suffix}"

def parse_market_cap(value_str):
    if not value_str or value_str == "": return None
    value_str = value_str.upper().replace(',', '').strip()
    multipliers = {'K': 1e3, 'M': 1e6, 'B': 1e9, 'T': 1e12}
    for suffix, multiplier in multipliers.items():
        if value_str.endswith(suffix):
            try: return float(value_str[:-1]) * multiplier
            except: return None
    try: return float(value_str)
    except: return None

def render_ranking_card(title, emoji, df, score_col, metric_col, metric_label, metric_format, num_results=10):
    st.markdown(f"#### {emoji} {title}")
    
    if score_col not in df.columns or df[score_col].empty:
        st.caption(f"Sin datos para '{score_col}'.")
        return
        
    sorted_df = df.nlargest(num_results, score_col)
    
    if sorted_df.empty:
        st.caption("Sin resultados en esta categoría.")
        return

    for _, row in sorted_df.iterrows():
        score = row[score_col]
        color = "#10b981" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
        
        metric_value = row.get(metric_col, 'N/D')
        if pd.notna(metric_value) and isinstance(metric_value, (int, float)):
             metric_display = metric_format.format(metric_value)
        else:
             metric_display = "-"
        
        symbol = row['Symbol']
        country = row.get('Country', '')
        country_display = f" | {country}" if country else ""
        
        st.markdown(
            f"<span style='color: {color}; font-weight: bold;'>{symbol}</span> - Puntuación: {score:.0f}{country_display}",
            unsafe_allow_html=True
        )
        st.caption(f"{row['Company Name'][:35]} | {metric_label}: {metric_display}")


# Función mejorada para la página de bienvenida
def show_welcome_page():
    """
    Muestra una página de bienvenida mejorada con:
    - Pie chart de distribución global
    - Explicación paso a paso clara
    - Explorador de cobertura de datos interactivo
    - Ejemplos de uso concretos
    """
    
    # Header principal con gradiente
    st.markdown("""
    <div style='text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 20px; margin-bottom: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.3);'>
        <h1 style='margin: 0; color: #ffffff; font-size: 2.8em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin-bottom: 15px;'>
            🌍 Bienvenido al BQuant Global Stock Screener
        </h1>
        <p style='color: #f0f0f0; margin-top: 15px; font-size: 1.3em; font-weight: 300; line-height: 1.5;'>
            Tu herramienta profesional para analizar <strong style='color: #ffd700;'>68,000+ acciones</strong> 
            en <strong style='color: #ffd700;'>89 países</strong> con <strong style='color: #ffd700;'>270+ métricas</strong>
        </p>
        <p style='color: #e0e0e0; margin-top: 10px; font-size: 1.1em;'>
            Encuentra las mejores oportunidades de inversión global con análisis institucional
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos para estadísticas
    with st.spinner("🔄 Cargando base de datos global..."):
        df_welcome = load_and_preprocess_data()
    
    # ============= SECCIÓN 1: ¿QUÉ PUEDES HACER? =============
    st.markdown("## 🎯 ¿Qué Puedes Hacer con Este Screener?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="text-align: center; padding: 20px;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">🔍</div>
            <h4 style="color: #4a9eff; margin-bottom: 10px;">Buscar Valor</h4>
            <p style="font-size: 0.9em; color: #c9d1d9;">
                Encuentra acciones infravaloradas con P/E bajo, P/B < 1, 
                alto FCF Yield
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="text-align: center; padding: 20px;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">🚀</div>
            <h4 style="color: #4a9eff; margin-bottom: 10px;">Identificar Crecimiento</h4>
            <p style="font-size: 0.9em; color: #c9d1d9;">
                Descubre empresas con crecimiento explosivo de ingresos 
                y beneficios
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card" style="text-align: center; padding: 20px;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">💎</div>
            <h4 style="color: #4a9eff; margin-bottom: 10px;">Analizar Calidad</h4>
            <p style="font-size: 0.9em; color: #c9d1d9;">
                Evalúa empresas con ROE alto, márgenes sólidos 
                y balance fuerte
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card" style="text-align: center; padding: 20px;">
            <div style="font-size: 2.5em; margin-bottom: 10px;">🌐</div>
            <h4 style="color: #4a9eff; margin-bottom: 10px;">Explorar Mercados</h4>
            <p style="font-size: 0.9em; color: #c9d1d9;">
                Compara oportunidades en 89 países y mercados 
                emergentes
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============= SECCIÓN 2: DISTRIBUCIÓN GLOBAL (PIE CHART) =============
    st.markdown("## 🌐 Distribución Global de Acciones")
    
    # Preparar datos para el pie chart
    country_counts = df_welcome['Country'].value_counts()
    
    # Agrupar países por regiones para mejor visualización
    regions = {
        'Estados Unidos': ['United States', 'US OTC'],
        'Europa': ['Germany', 'United Kingdom', 'France', 'Netherlands', 'Spain', 'Italy', 
                   'Belgium', 'Switzerland', 'Sweden', 'Norway', 'Denmark', 'Finland', 
                   'Ireland', 'Austria', 'Poland', 'Greece', 'Portugal'],
        'Asia Desarrollada': ['Japan', 'Hong Kong', 'Singapore', 'South Korea', 'Taiwan'],
        'China': ['China'],
        'Asia Emergente': ['India', 'Indonesia', 'Thailand', 'Malaysia', 'Philippines', 
                          'Vietnam', 'Pakistan', 'Bangladesh'],
        'América Latina': ['Brazil', 'Mexico', 'Argentina', 'Chile', 'Colombia', 'Peru'],
        'Medio Oriente y África': ['Saudi Arabia', 'United Arab Emirates', 'Israel', 
                                   'Turkey', 'Egypt', 'South Africa', 'Nigeria', 'Morocco'],
        'Oceanía': ['Australia', 'New Zealand'],
        'Otros': []  # Para países no clasificados
    }
    
    # Calcular totales por región
    region_totals = {}
    countries_used = set()
    
    for region, countries in regions.items():
        total = 0
        for country in countries:
            if country in country_counts.index:
                total += country_counts[country]
                countries_used.add(country)
        if total > 0:
            region_totals[region] = total
    
    # Agregar países no clasificados a "Otros"
    otros_total = 0
    for country, count in country_counts.items():
        if country not in countries_used:
            otros_total += count
    if otros_total > 0:
        region_totals['Otros'] = otros_total
    
    # Crear dos columnas para el pie chart y la tabla
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # Crear pie chart interactivo
        fig = go.Figure(data=[go.Pie(
            labels=list(region_totals.keys()),
            values=list(region_totals.values()),
            hole=0.3,  # Donut chart
            marker=dict(
                colors=['#4a9eff', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', 
                       '#ec4899', '#14b8a6', '#fbbf24', '#6b7280'],
                line=dict(color='#1a1f2e', width=2)
            ),
            textposition='inside',
            texttemplate='%{label}<br>%{value:,}<br>(%{percent})',
            hovertemplate='<b>%{label}</b><br>' +
                         'Acciones: %{value:,}<br>' +
                         'Porcentaje: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(
                text='Distribución de Acciones por Región',
                font=dict(size=20, color='#f0f6fc')
            ),
            template='plotly_dark',
            height=450,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            ),
            margin=dict(l=20, r=150, t=60, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Resumen por Región")
        
        # Crear tabla resumen
        summary_data = []
        for region, total in sorted(region_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (total / len(df_welcome)) * 100
            summary_data.append({
                'Región': region,
                'Acciones': f'{total:,}',
                'Porcentaje': f'{percentage:.1f}%'
            })
        
        summary_df = pd.DataFrame(summary_data)
        
        # Mostrar como dataframe estilizado
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Región": st.column_config.TextColumn(
                    "Región",
                    width="medium",
                ),
                "Acciones": st.column_config.TextColumn(
                    "Acciones",
                    width="small",
                ),
                "Porcentaje": st.column_config.TextColumn(
                    "%",
                    width="small",
                ),
            }
        )
    
    st.markdown("---")
    
    # ============= SECCIÓN 3: CÓMO FUNCIONA =============
    st.markdown("## 🚀 Cómo Funciona: 3 Pasos Simples")
    
    # Crear tabs para cada paso
    tab1, tab2, tab3 = st.tabs(["1️⃣ Selecciona Estrategia", "2️⃣ Aplica Filtros", "3️⃣ Analiza Resultados"])
    
    with tab1:
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.markdown("""
            ### Paso 1: Elige tu Estrategia
            
            **Opciones disponibles:**
            - 🎯 **Constructor Personalizado**: Crea tu propia estrategia
            - 💎 **Valor Profundo**: P/E < 10, P/B < 1
            - 🚀 **Hipercrecimiento**: Crecimiento > 30%
            - 💰 **Aristócratas del Dividendo**: 25+ años de aumentos
            - 🏆 **Calidad Premium**: ROE > 20%, ROIC > 15%
            - Y 15+ estrategias más...
            
            **Tip:** Comienza con una plantilla y ajústala a tus necesidades
            """)
        
        with col2:
            st.info("💡 Cada estrategia incluye filtros pre-configurados basados en metodologías probadas de inversión")
    
    with tab2:
        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.markdown("""
            ### Paso 2: Personaliza tus Filtros
            
            **Categorías de filtros disponibles:**
            
            📊 **Valoración**: P/E, P/B, P/S, EV/EBITDA, PEG  
            📈 **Crecimiento**: Ingresos, BPA, estimaciones futuras  
            💎 **Rentabilidad**: ROE, ROA, ROIC, márgenes  
            🏥 **Salud Financiera**: Liquidez, deuda, Z-Score  
            💵 **Dividendos**: Yield, payout, historial  
            📉 **Técnico**: RSI, retornos, momentum  
            🌍 **Geografía**: 89 países, regiones, mercados  
            
            **Ejemplo de filtro combinado:**
            - P/E < 15 AND ROE > 15% AND Deuda/Equity < 1
            """)
        
        with col2:
            st.metric("Total de Filtros", "270+", "Métricas profesionales")
            st.metric("Países", "89", "Mercados globales")
            st.metric("Combinaciones", "∞", "Posibilidades infinitas")
            
            st.success("✅ Los filtros se aplican en tiempo real sobre toda la base de datos")
    
    with tab3:
        st.markdown("""
        ### Paso 3: Explora y Exporta Resultados
        
        Una vez aplicados los filtros, obtendrás:
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📊 Tabla Interactiva**
            - Ordena por cualquier columna
            - Selecciona métricas a mostrar
            - Vista personalizable
            """)
        
        with col2:
            st.markdown("""
            **📈 Visualizaciones**
            - Gráficos de dispersión
            - Análisis por sector/país
            - Correlaciones y heatmaps
            """)
        
        with col3:
            st.markdown("""
            **💾 Exportación**
            - CSV para Excel
            - JSON para APIs
            - Reportes ejecutivos
            """)
    
    st.markdown("---")
    
    # ============= SECCIÓN 4: EXPLORADOR DE COBERTURA (CORREGIDO) =============
    st.markdown("## 🔍 Explorador de Cobertura de Datos por País")
    
    st.info("""
    ⚠️ **Importante**: La profundidad de datos varía significativamente entre países. 
    USA y mercados desarrollados tienen cobertura completa, mientras que mercados emergentes pueden tener datos limitados.
    Usa este explorador para entender qué filtros funcionarán mejor en cada mercado.
    """)
    
    # Selector de país con preview
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Top 20 países por número de acciones
        top_countries = country_counts.head(20)
        selected_country = st.selectbox(
            "🌍 Selecciona un país para analizar:",
            options=top_countries.index.tolist(),
            format_func=lambda x: f"{x} ({country_counts[x]:,} acciones)"
        )
        
        if selected_country:
            country_df = df_welcome[df_welcome['Country'] == selected_country]
            
            # Métricas del país seleccionado
            st.metric("Total Acciones", f"{len(country_df):,}")
            st.metric("Sectores", f"{country_df['Sector'].nunique() if 'Sector' in country_df.columns else 0}")
            
            # Cap. de mercado total
            total_mcap = country_df['Market Cap'].sum() if 'Market Cap' in country_df.columns else 0
            st.metric("Cap. Total", format_number(total_mcap, prefix="$"))
    
    with col2:
        if selected_country:
            # Análisis de cobertura de datos
            st.markdown(f"### 📊 Cobertura de Datos: **{selected_country}**")
            
            # Categorías de métricas a evaluar
            metric_categories = {
                "Valoración Fundamental": ['PE Ratio', 'PB Ratio', 'PS Ratio', 'PEG Ratio', 'EV/EBITDA'],
                "Rentabilidad": ['ROE', 'ROA', 'ROIC', 'Profit Margin', 'Gross Margin'],
                "Crecimiento": ['Rev. Growth', 'EPS Growth', 'Rev Gr. Next Y', 'EPS Gr. Next Y'],
                "Salud Financiera": ['Current Ratio', 'Debt / Equity', 'Z-Score', 'FCF'],
                "Dividendos": ['Div. Yield', 'Payout Ratio', 'Years', 'Div. Growth'],
                "Técnico": ['RSI', 'Beta (5Y)', 'Return 1Y', 'Rel. Volume'],
                "Estimaciones": ['Forward PE', 'Analysts', 'PT Upside', 'Rating']
            }
            
            # Calcular cobertura para cada categoría
            coverage_results = []
            for category, metrics in metric_categories.items():
                available_metrics = [m for m in metrics if m in country_df.columns]
                if available_metrics:
                    # Calcular porcentaje de empresas con datos en esta categoría
                    has_data = country_df[available_metrics].notna().any(axis=1)
                    coverage_pct = (has_data.sum() / len(country_df) * 100) if len(country_df) > 0 else 0
                else:
                    coverage_pct = 0
                
                coverage_results.append({
                    'Categoría': category,
                    'Cobertura': coverage_pct,
                    'Calidad': '🟢 Excelente' if coverage_pct >= 80 else 
                              '🟡 Buena' if coverage_pct >= 50 else 
                              '🟠 Limitada' if coverage_pct >= 20 else 
                              '🔴 Muy Limitada'
                })
            
            # Crear DataFrame de resultados
            coverage_df = pd.DataFrame(coverage_results)
            
            # Mostrar como barras de progreso CORREGIDAS
            for _, row in coverage_df.iterrows():
                col_a, col_b = st.columns([1, 3])
                with col_a:
                    st.markdown(f"**{row['Categoría']}**")
                with col_b:
                    # Determinar colores y estilos según cobertura
                    progress_color = '#10b981' if row['Cobertura'] >= 80 else '#f59e0b' if row['Cobertura'] >= 50 else '#ef4444'
                    
                    # CORRECCIÓN: Para cobertura 0%, mostrar el texto fuera de la barra
                    if row['Cobertura'] < 5:
                        # Cuando la barra es muy pequeña, mostrar texto fuera
                        st.markdown(f"""
                        <div style="position: relative; background: rgba(255,255,255,0.1); border-radius: 10px; height: 25px;">
                            <div style="background: {progress_color}; width: {max(row['Cobertura'], 2):.0f}%; height: 100%; 
                                       border-radius: 10px;">
                            </div>
                            <span style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%);
                                        color: #c9d1d9; font-weight: bold; font-size: 12px; z-index: 10;">
                                {row['Cobertura']:.0f}% {row['Calidad']}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Cuando la barra es suficientemente grande, mostrar texto dentro
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 25px; position: relative;">
                            <div style="background: {progress_color}; width: {row['Cobertura']:.0f}%; height: 100%; 
                                       border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                                <span style="color: white; font-weight: bold; font-size: 12px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
                                    {row['Cobertura']:.0f}% {row['Calidad']}
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Recomendación basada en cobertura
            avg_coverage = coverage_df['Cobertura'].mean()
            
            if avg_coverage >= 70:
                st.success(f"""
                ✅ **{selected_country}** tiene EXCELENTE cobertura de datos. 
                Puedes usar cualquier combinación de filtros con confianza.
                """)
            elif avg_coverage >= 40:
                st.warning(f"""
                ⚠️ **{selected_country}** tiene cobertura MODERADA. 
                Enfócate en métricas básicas (P/E, P/B, ROE, Crecimiento).
                """)
            else:
                st.error(f"""
                🔴 **{selected_country}** tiene cobertura LIMITADA. 
                Usa principalmente filtros de precio y capitalización.
                """)
    
    st.markdown("---")
    
    # ============= SECCIÓN 5: CASOS DE USO =============
    st.markdown("## 💡 Casos de Uso y Ejemplos")
    
    example_tabs = st.tabs(["Para Inversores Valor", "Para Growth", "Para Dividendos", "Para Trading"])
    
    with example_tabs[0]:
        st.markdown("""
        ### 🎯 Inversor de Valor Buscando Gangas
        
        **Objetivo:** Encontrar empresas sólidas cotizando por debajo de su valor intrínseco
        
        **Filtros sugeridos:**
        - P/E < 15
        - P/B < 1.5
        - FCF Yield > 5%
        - Debt/Equity < 1
        - ROE > 10%
        - Current Ratio > 1.5
        
        **Resultado esperado:** 200-500 empresas globales infravaloradas con fundamentos sólidos
        """)
    
    with example_tabs[1]:
        st.markdown("""
        ### 🚀 Inversor Growth Buscando el Próximo 10-Bagger
        
        **Objetivo:** Identificar empresas con crecimiento explosivo y potencial disruptivo
        
        **Filtros sugeridos:**
        - Crecimiento Ingresos > 30%
        - Crecimiento BPA > 25%
        - Margen Bruto > 60%
        - Insider Ownership > 10%
        - Momentum (Return 3M) > 15%
        
        **Resultado esperado:** 100-300 empresas de hipercrecimiento con momentum positivo
        """)
    
    with example_tabs[2]:
        st.markdown("""
        ### 💰 Inversor de Dividendos Buscando Ingresos Pasivos
        
        **Objetivo:** Construir cartera de dividendos crecientes y sostenibles
        
        **Filtros sugeridos:**
        - Dividend Yield: 3% - 7%
        - Años consecutivos aumentando: > 10
        - Payout Ratio < 70%
        - Z-Score > 3
        - Free Cash Flow > 0
        
        **Resultado esperado:** 150-400 empresas con dividendos seguros y crecientes
        """)
    
    with example_tabs[3]:
        st.markdown("""
        ### 📈 Trader Buscando Oportunidades de Momentum
        
        **Objetivo:** Encontrar acciones con fuerte momentum y volumen para trading
        
        **Filtros sugeridos:**
        - RSI: 50-70
        - Distancia desde máximo 52S: < 10%
        - Volumen Relativo > 1.5
        - Return 1M > 10%
        - Beta < 2
        
        **Resultado esperado:** 50-200 acciones con setup técnico favorable
        """)
    
    st.markdown("---")
    
    # ============= LLAMADA A LA ACCIÓN =============
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(74, 158, 255, 0.1)); 
                border-radius: 20px; border: 2px solid rgba(74, 158, 255, 0.3);'>
        <h2 style='color: #4a9eff; margin-bottom: 20px;'>¿Listo para Encontrar tu Próxima Gran Inversión?</h2>
        <p style='color: #c9d1d9; font-size: 1.2em; margin-bottom: 30px;'>
            Únete a miles de inversores que ya usan BQuant para tomar mejores decisiones
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón centrado para comenzar
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2:
        if st.button("🚀 **¡COMENZAR ANÁLISIS AHORA!**", 
                    type="primary", 
                    use_container_width=True,
                    help="Haz clic para acceder al screener completo"):
            st.session_state.app_started = True
            st.rerun()
    
    # Footer con información adicional
    st.markdown("""
    <div style='text-align: center; margin-top: 40px; padding: 20px; background: rgba(74, 158, 255, 0.05); 
                border-radius: 10px;'>
        <p style='color: #8b949e; font-size: 0.9em;'>
            Desarrollado por <strong>@Gsnchez</strong> | <strong>bquantfinance.com</strong><br>
            Datos actualizados: Septiembre 2025 | Sin registro requerido | 100% Gratis
        </p>
    </div>
    """, unsafe_allow_html=True)

# Inicializar estado de la aplicación
if 'app_started' not in st.session_state:
    st.session_state.app_started = False

# Si no ha comenzado, mostrar página de bienvenida y DETENER la ejecución
if not st.session_state.app_started:
    show_welcome_page()
    st.stop()  # <-- Esto detiene la ejecución aquí, no se ejecuta nada más abajo

# =============================================================================
# DICCIONARIO COMPLETO DE DESCRIPCIONES DE MÉTRICAS (270 métricas)
# =============================================================================

METRIC_DESCRIPTIONS = {
    # Valoración Fundamental
    "pe_ratio": "Precio/Beneficios - Precio de la acción dividido por beneficios por acción. Menor = potencialmente infravalorado",
    "forward_pe": "P/E futuro basado en beneficios estimados. Expectativas del mercado",
    "pb_ratio": "Precio/Valor Libro - Capitalización dividida por valor contable. <1 = cotiza bajo valor en libros",
    "ps_ratio": "Precio/Ventas - Capitalización dividida por ingresos. Útil para empresas sin beneficios",
    "forward_ps": "P/S futuro basado en ventas estimadas",
    "peg_ratio": "P/E/Crecimiento - P/E dividido por tasa de crecimiento. <1 = crecimiento a precio razonable",
    "p_fcf": "Precio/Flujo Caja Libre - Valoración basada en generación real de caja",
    "p_ocf": "Precio/Flujo Caja Operativo - Valoración sobre caja de operaciones",
    "p_ebitda": "Precio/EBITDA - Múltiplo sobre beneficios operativos",
    "p_tbv": "Precio/Valor Tangible - Excluye intangibles del valor libro",
    "p_ffo": "Precio/FFO - Métrica clave para REITs",
    
    # Enterprise Value
    "ev_sales": "EV/Ventas - Valor empresa sobre ingresos. Incluye deuda",
    "fwd_ev_s": "EV/Ventas futuro - Basado en ventas estimadas",
    "ev_earnings": "EV/Beneficios - Valor empresa sobre beneficios netos",
    "ev_ebitda": "EV/EBITDA - Múltiplo clave comparable entre industrias",
    "ev_ebit": "EV/EBIT - Valor empresa sobre beneficios operativos",
    "ev_fcf": "EV/FCF - Valor empresa sobre flujo caja libre",
    
    # Yields
    "earnings_yield": "Beneficios/Precio - Inverso del P/E. Comparar con bonos",
    "fcf_yield": "FCF/Capitalización - Generación de caja vs precio. Mayor = mejor valor",
    "fcf_ev": "FCF/EV - Rendimiento del flujo caja sobre valor empresa",
    "div_yield": "Rentabilidad por dividendo - Retorno anual por dividendos",
    "buyback_yield": "Recompras/Capitalización - Retorno por recompra de acciones",
    "shareh_yield": "Rentabilidad total accionista - Dividendos + Recompras",
    
    # Crecimiento - Histórico
    "rev_growth": "Crecimiento ingresos últimos 12 meses",
    "rev_growth_q": "Crecimiento ingresos trimestral",
    "rev_growth_3y": "CAGR ingresos 3 años - Crecimiento anualizado",
    "rev_growth_5y": "CAGR ingresos 5 años - Tendencia largo plazo",
    "eps_growth": "Crecimiento BPA últimos 12 meses",
    "eps_growth_q": "Crecimiento BPA trimestral",
    "eps_growth_3y": "CAGR BPA 3 años",
    "eps_growth_5y": "CAGR BPA 5 años",
    
    # Crecimiento - Estimaciones
    "rev_gr_this_q": "Crecimiento ingresos esperado este trimestre",
    "rev_gr_next_q": "Crecimiento ingresos próximo trimestre",
    "rev_gr_this_y": "Crecimiento ingresos esperado este año",
    "rev_gr_next_y": "Crecimiento ingresos próximo año",
    "rev_gr_next_5y": "CAGR ingresos esperado próximos 5 años",
    "eps_gr_this_q": "Crecimiento BPA esperado este trimestre",
    "eps_gr_next_q": "Crecimiento BPA próximo trimestre",
    "eps_gr_this_y": "Crecimiento BPA esperado este año",
    "eps_gr_next_y": "Crecimiento BPA próximo año",
    "eps_gr_next_5y": "CAGR BPA esperado próximos 5 años",
    
    # Crecimiento - Otros
    "gp_growth": "Crecimiento beneficio bruto anual",
    "gp_growth_q": "Crecimiento beneficio bruto trimestral",
    "opinc_growth": "Crecimiento beneficio operativo anual",
    "netinc_growth": "Crecimiento beneficio neto anual",
    "fcf_growth": "Crecimiento flujo caja libre anual",
    "debt_growth_yoy": "Crecimiento deuda año a año",
    "empl_growth": "Crecimiento empleados - Expansión empresa",
    
    # Rentabilidad
    "roe": "ROE - Beneficio neto/Patrimonio. Eficiencia uso capital accionistas",
    "roa": "ROA - Beneficio neto/Activos. Eficiencia uso activos totales",
    "roic": "ROIC - Beneficio operativo/Capital invertido. Retorno real negocio",
    "roce": "ROCE - EBIT/Capital empleado. Eficiencia capital empleado",
    "roe_5y": "ROE promedio 5 años - Consistencia rentabilidad",
    "roa_5y": "ROA promedio 5 años",
    "roic_5y": "ROIC promedio 5 años",
    
    # Márgenes
    "gross_margin": "Margen bruto - Poder de precios y ventaja competitiva",
    "oper_margin": "Margen operativo - Eficiencia operacional",
    "pretax_margin": "Margen antes impuestos",
    "profit_margin": "Margen neto - % ventas que se convierte en beneficio",
    "fcf_margin": "Margen FCF - Conversión ventas a caja libre",
    "ebitda_margin": "Margen EBITDA - Rentabilidad operativa",
    "ebit_margin": "Margen EBIT - Beneficio operativo sobre ventas",
    
    # Salud Financiera
    "current_ratio": "Ratio corriente - Activos/Pasivos corrientes. >1.5 = buena liquidez",
    "quick_ratio": "Ratio ácida - Liquidez sin inventarios. >1 = sólido",
    "debt_equity": "Deuda/Patrimonio - <1 conservador, >2 arriesgado",
    "debt_ebitda": "Deuda/EBITDA - Años para pagar deuda. <3 = saludable",
    "debt_fcf": "Deuda/FCF - Años para pagar con caja libre",
    "interest_coverage": "Cobertura intereses - EBIT/Intereses. >3 = cómodo",
    "z_score": "Altman Z-Score - Predice quiebra. >3 seguro, <1.8 riesgo",
    "f_score": "Piotroski F-Score - Salud financiera 0-9. >7 = muy sano",
    
    # Eficiencia
    "asset_turnover": "Rotación activos - Ventas/Activos. Eficiencia uso activos",
    "inv_turnover": "Rotación inventario - Velocidad venta inventario",
    "wc_turnover": "Rotación capital trabajo - Eficiencia capital circulante",
    "rev_employee": "Ingresos/Empleado - Productividad laboral",
    "prof_employee": "Beneficio/Empleado - Rentabilidad por empleado",
    
    # Dividendos
    "div_growth": "Crecimiento dividendo último año",
    "div_growth_3y": "CAGR dividendo 3 años",
    "div_growth_5y": "CAGR dividendo 5 años",
    "div_growth_10y": "CAGR dividendo 10 años",
    "years": "Años consecutivos aumentando dividendo",
    "payout_ratio": "Dividendos/Beneficios - <60% = sostenible",
    "div_dollar": "Dividendo por acción en dólares",
    "payout_freq": "Frecuencia pago dividendo (anual, trimestral)",
    
    # Técnico - Retornos
    "return_1w": "Retorno 1 semana - Momentum muy corto plazo",
    "return_1m": "Retorno 1 mes - Momentum corto plazo",
    "return_3m": "Retorno 3 meses - Tendencia trimestral",
    "return_6m": "Retorno 6 meses - Tendencia semestral",
    "return_ytd": "Retorno año hasta fecha",
    "return_1y": "Retorno 1 año - Performance anual",
    "return_3y": "Retorno 3 años total",
    "return_5y": "Retorno 5 años total",
    "return_10y": "Retorno 10 años - Creación valor largo plazo",
    "return_15y": "Retorno 15 años total",
    "return_20y": "Retorno 20 años total",
    "return_ipo": "Retorno desde IPO - Performance histórica total",
    
    # Técnico - CAGR
    "cagr_1y": "Retorno anualizado 1 año",
    "cagr_3y": "Retorno anualizado 3 años",
    "cagr_5y": "Retorno anualizado 5 años",
    "cagr_10y": "Retorno anualizado 10 años",
    "cagr_15y": "Retorno anualizado 15 años",
    "cagr_20y": "Retorno anualizado 20 años",
    
    # Técnico - Indicadores
    "rsi": "RSI - Índice fuerza relativa. 30=sobreventa, 70=sobrecompra",
    "rsi_w": "RSI semanal - Tendencia medio plazo",
    "rsi_m": "RSI mensual - Tendencia largo plazo",
    "beta": "Beta 5 años - Volatilidad vs mercado. 1=mercado, <1=defensivo",
    "atr": "ATR - Rango verdadero promedio. Mide volatilidad",
    "rel_volume": "Volumen relativo - Vs promedio. >1.5 = actividad inusual",
    "avg_volume": "Volumen promedio diario - Liquidez",
    "dollar_vol": "Volumen en dólares - Liquidez monetaria",
    
    # Técnico - Medias Móviles
    "ma_20": "Media móvil 20 días - Tendencia corto plazo",
    "ma_50": "Media móvil 50 días - Tendencia medio plazo",
    "ma_150": "Media móvil 150 días",
    "ma_200": "Media móvil 200 días - Tendencia largo plazo",
    "ma20_chg": "Distancia a MA20 - Desviación corto plazo",
    "ma50_chg": "Distancia a MA50",
    "ma200_chg": "Distancia a MA200 - Desviación largo plazo",
    "ma50vs200": "MA50 vs MA200 - Golden/Death cross",
    
    # Técnico - Rangos
    "52w_high_chg": "% desde máximo 52 semanas - Cerca máximo = momentum",
    "52w_low_chg": "% desde mínimo 52 semanas - Potencial rebote",
    "ath_chg": "% desde máximo histórico",
    "atl_chg": "% desde mínimo histórico",
    "gap": "Gap apertura - Salto de precio en apertura",
    "chg_open": "Cambio desde apertura - Performance intradía",
    
    # Propiedad
    "insider_own": "% propiedad insiders - Alto = intereses alineados",
    "institutional_own": "% propiedad institucional - 30-80% = punto óptimo",
    "shares": "Acciones en circulación totales",
    "float": "Float - Acciones disponibles para trading",
    "shares_ch_yoy": "Cambio acciones año - Dilución/Recompra",
    "shares_ch_qoq": "Cambio acciones trimestral",
    
    # Cortos
    "short_float": "% float en corto - Sentimiento bajista o squeeze",
    "short_shares": "% acciones en corto",
    "short_ratio": "Days to cover - Días para cubrir cortos",
    
    # Cash Flow
    "operating_cf": "Flujo caja operativo - Caja de operaciones",
    "investing_cf": "Flujo caja inversión - CapEx y adquisiciones",
    "financing_cf": "Flujo caja financiación - Deuda y dividendos",
    "net_cf": "Flujo caja neto total",
    "capex": "CapEx - Inversión en activos fijos",
    "fcf": "Flujo caja libre - Caja disponible tras CapEx",
    "fcf_sbc": "FCF ajustado por compensación en acciones",
    "fcf_share": "FCF por acción",
    
    # Balance
    "total_cash": "Caja total y equivalentes",
    "total_debt": "Deuda total",
    "net_cash": "Caja neta - Caja menos deuda",
    "net_cash_growth": "Crecimiento caja neta",
    "cash_mcap": "Caja/Capitalización - % empresa en efectivo",
    "assets": "Activos totales",
    "liabilities": "Pasivos totales",
    "equity": "Patrimonio neto",
    "bv_share": "Valor libro por acción",
    "tbv_share": "Valor tangible por acción",
    "working_capital": "Capital trabajo - Activos menos pasivos corrientes",
    "net_wc": "Capital trabajo neto",
    
    # Analistas
    "rating": "Rating consenso analistas",
    "price_target": "Precio objetivo consenso",
    "analysts": "Número de analistas cubriendo",
    "pt_upside": "Potencial alcista a precio objetivo",
    "top_rating": "Rating mejores analistas",
    "top_pt_upside": "Potencial según mejores analistas",
    
    # Estimaciones
    "est_revenue": "Ingresos estimados próximo reporte",
    "est_rev_growth": "Crecimiento ingresos estimado",
    "est_eps": "BPA estimado próximo reporte",
    "est_eps_growth": "Crecimiento BPA estimado",
    
    # Fechas y Eventos
    "earnings_date": "Fecha próximos resultados",
    "ex_div_date": "Fecha ex-dividendo",
    "payment_date": "Fecha pago dividendo",
    "ipo_date": "Fecha salida a bolsa",
    "last_split_date": "Fecha último split",
    
    # Información Empresa
    "employees": "Número total empleados",
    "founded": "Año fundación empresa",
    "industry": "Industria específica",
    "sector": "Sector económico amplio",
    "exchange": "Bolsa donde cotiza",
    "country": "País sede central",
    "state": "Estado/Provincia sede",
    "website": "Sitio web corporativo",
    
    # Fair Value
    "lynch_fv": "Fair Value Peter Lynch - Basado en crecimiento",
    "graham_no": "Número Graham - Valor intrínseco Benjamin Graham",
    "lynch_upside": "% potencial método Lynch",
    "graham_upside": "% potencial método Graham",
    
    # Otros
    "sbc": "Compensación basada en acciones",
    "sbc_rev": "SBC/Ingresos - Dilución por compensación",
    "rd": "Gasto en I+D",
    "rd_rev": "I+D/Ingresos - Inversión en innovación",
    "tax_rate": "Tasa impositiva efectiva",
    "tax_revenue": "Impuestos/Ingresos",
    "is_spac": "Es un SPAC (Special Purpose Acquisition Company)",
    "options": "Tiene opciones disponibles",
    "mc_group": "Grupo por capitalización (Large/Mid/Small/Micro)",
    "in_index": "Índices donde está incluida (SP500, NASDAQ100, DOW30)",
    "tags": "Etiquetas temáticas",
    "views": "Vistas/Popularidad"
}

# =============================================================================
# SCREENERS PROFESIONALES EN ESPAÑOL (20 estrategias)
# =============================================================================

SCREENERS = {
    "🎯 Constructor Personalizado": {
        "description": "Construye tu propio screener con filtros personalizados",
        "filters": {}
    },

    "🇮🇳 India - Filtros Optimizados": {
        "description": "India - Filtros mínimos para máximos resultados",
        "filters": {
            "countries": ["India"],
            "market_cap_min": 10e6,  # Reduced from 100M to 10M
 
        }
    },
    
    "🇨🇳 China Tech Focus": {
        "description": "Empresas tecnológicas chinas",
        "filters": {
            "countries": ["China"],
            "sectors": ["Technology", "Communication Services"],
            "market_cap_min": 50e6,  # Reduced from 500M to 50M
      
        }
    },
    
    "🌏 Asia Emergente Básico": {
        "description": "Indonesia, Tailandia, Malasia, Filipinas, Vietnam",
        "filters": {
            "countries": ["Indonesia", "Thailand", "Malaysia", "Philippines", "Vietnam"],
            "market_cap_min": 10e6,  # Reduced from 200M to 10M

        }
    },
    
    "🌎 LATAM Oportunidades": {
        "description": "Brasil, México, Argentina, Chile, Colombia, Perú",
        "filters": {
            "countries": ["Brazil", "Mexico", "Argentina", "Chile", "Colombia", "Peru"],
            "market_cap_min": 10e6,  # Reduced from 100M to 10M

        }
    },
    
    "🌍 MENA Básico": {
        "description": "Medio Oriente y África",
        "filters": {
            "countries": ["Saudi Arabia", "United Arab Emirates", "Turkey", "Egypt", "South Africa", "Israel"],
            "market_cap_min": 50e6,  
        }
    },
    
    "🔴 Mercados Frontera": {
        "description": "Países con datos muy limitados",
        "filters": {
            "countries": ["Pakistan", "Bangladesh", "Nigeria", "Kenya", "Morocco", "Sri Lanka"],
        }
    },
    
    "🏛️ Europa del Este": {
        "description": "Polonia, Grecia, Rumania, República Checa, Hungría",
        "filters": {
            "countries": ["Poland", "Greece", "Romania", "Czech Republic", "Hungary"],
            "market_cap_min": 10e6,  # Reduced from 100M to 10M
            # Removed PE, PB, ROE, and debt filters
        }
    },
    
    "🌐 Global Ex-USA Simplificado": {
        "description": "Todo excepto USA",
        "filters": {
            "exclude_countries": ["United States", "US OTC"],
            "market_cap_min": 100e6,  # Reduced from 500M to 100M
            # Removed PE and PB filters
        }
    },
    
    "💎 Emergentes Value Simple": {
        "description": "Valor en mercados emergentes",
        "filters": {
            "countries": ["India", "China", "Brazil", "Mexico", "Indonesia", "Turkey", "Thailand"],
            "market_cap_min": 100e6,  # Reduced from 1B to 100M
            "pe_max": 20.0,  # Increased from 12 to 20
            # Removed PB and return filters
        }
    },
    
    "🚀 Emergentes Growth Simple": {
        "description": "Crecimiento en emergentes",
        "filters": {
            "countries": ["India", "China", "Brazil", "Indonesia", "Vietnam", "Philippines"],
            "market_cap_min": 50e6,  # Reduced from 500M to 50M
            # Removed growth and return filters (often missing data)
        }
    },
    
    "🏦 Bancos Globales Ex-USA": {
        "description": "Bancos fuera de USA",
        "filters": {
            "exclude_countries": ["United States", "US OTC"],
            "sectors": ["Financials"],
            "market_cap_min": 100e6,  # Reduced from 1B to 100M
            # Removed PE, PB, and ROE filters
        }
    },
    
    "⚡ Asia Pacífico Large Cap": {
        "description": "Grandes empresas de Asia-Pacífico",
        "filters": {
            "countries": ["Japan", "China", "Hong Kong", "Singapore", "South Korea", "Taiwan", "Australia"],
            "market_cap_min": 1e9,  # Reduced from 10B to 1B
            # Removed PE, debt, and return filters
        }
    },
    
    "🌟 BRICS Oportunidades": {
        "description": "Brasil, Rusia, India, China, Sudáfrica",
        "filters": {
            "countries": ["Brazil", "Russia", "India", "China", "South Africa"],
            "market_cap_min": 50e6,  # Reduced from 500M to 50M
            # Removed PE and return filters
        }
    },
    
    "📉 Emergentes Oversold": {
        "description": "Acciones castigadas en emergentes",
        "filters": {
            "exclude_countries": ["United States", "US OTC", "United Kingdom", "Germany", "France", "Japan"],
            "market_cap_min": 10e6,  # Reduced from 200M to 10M
            "return_1y_max": 0.0,  # Changed from -30% to 0% (less restrictive)
            # Removed return_3m and PE filters
        }
    },
    
    "🎯 Mínimos Datos Requeridos": {
        "description": "Para cualquier país - Solo usa Market Cap, Sector y Retornos (siempre disponibles)",
        "filters": {
            "market_cap_min": 100e6,
            "market_cap_max": 100e9,
            "return_1y_min": -50.0,
            "return_1y_max": 500.0,
            "return_1m_min": -20.0
        }
    }, 
    "🌍 Campeones de Valor Global": {
        "description": "Mejores oportunidades de valor mundial (P/E < 12, P/B < 1.5, FCF Yield > 5%)",
        "filters": {
            "pe_max": 12.0,
            "pb_max": 1.5,
            "fcf_yield_min": 5.0,
            "current_ratio_min": 1.5,
            "value_score_min": 70
        }
    },
    
    "🇺🇸 Líderes de Calidad USA": {
        "description": "Empresas americanas de alta calidad (ROE > 15%, ROIC > 12%, D/E < 1)",
        "filters": {
            "countries": ["United States", "US OTC"],
            "roe_min": 15.0,
            "roic_min": 12.0,
            "debt_equity_max": 1.0,
            "quality_score_min": 70
        }
    },
    
    "🌐 Crecimiento Internacional": {
        "description": "Líderes de crecimiento fuera de USA (Crecimiento Ingresos > 25%, BPA > 20%)",
        "filters": {
            "rev_growth_min": 25.0,
            "eps_growth_min": 20.0,
            "exclude_countries": ["United States", "US OTC"],
            "growth_score_min": 70
        }
    },
    
    "💎 Valor Profundo Contrarian": {
        "description": "Extremadamente infravaloradas con catalizadores (P/B < 1, P/E < 10)",
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
        "description": "Cotizando bajo valor de liquidación (P/B < 0.66, Current Ratio > 2)",
        "filters": {
            "pb_max": 0.66,
            "current_ratio_min": 2.0,
            "z_score_min": 1.8,
            "debt_equity_max": 0.5,
            "value_score_min": 80
        }
    },
    
    "🚀 Hipercrecimiento Tecnológico": {
        "description": "Crecimiento explosivo tech (Ingresos > 30%, Margen Bruto > 60%)",
        "filters": {
            "rev_growth_min": 30.0,
            "gross_margin_min": 60.0,
            "sectors": ["Technology", "Communication Services"],
            "growth_score_min": 70
        }
    },
    
    "⚡ GARP Excelencia": {
        "description": "Crecimiento a precio razonable (PEG < 1, ROE > 15%, Crecimiento BPA > 15%)",
        "filters": {
            "peg_max": 1.0,
            "peg_min": 0.1,
            "eps_growth_min": 15.0,
            "roe_min": 15.0,
            "debt_equity_max": 1.0,
            "profit_margin_min": 10.0
        }
    },
    
    "💰 Aristócratas del Dividendo": {
        "description": "25+ años crecimiento dividendos (Yield 2.5-8%, Payout < 70%)",
        "filters": {
            "years_min": 25,
            "div_yield_min": 2.5,
            "div_yield_max": 8.0,
            "payout_ratio_max": 70.0,
            "market_cap_min": 10e9
        }
    },
    
    "🏆 Alta Rentabilidad de Calidad": {
        "description": "Yields seguros (Yield > 4%, Z-Score > 3, Payout < 80%)",
        "filters": {
            "div_yield_min": 4.0,
            "div_yield_max": 10.0,
            "payout_ratio_max": 80.0,
            "z_score_min": 3.0,
            "current_ratio_min": 1.5,
            "financial_health_score_min": 60
        }
    },
    
    "👑 Compounders de Calidad": {
        "description": "Negocios excepcionales (ROE > 20%, ROIC > 15%, FCF Yield > 5%)",
        "filters": {
            "roe_min": 20.0,
            "roic_min": 15.0,
            "fcf_yield_min": 5.0,
            "debt_equity_max": 0.5,
            "profit_margin_min": 15.0,
            "quality_score_min": 80
        }
    },
    
    "🛡️ Fortaleza Defensiva": {
        "description": "Baja volatilidad defensivas (Beta < 0.8, Margen > 15%, Yield > 2%)",
        "filters": {
            "beta_max": 0.8,
            "profit_margin_min": 15.0,
            "div_yield_min": 2.0,
            "current_ratio_min": 1.5,
            "sectors": ["Consumer Staples", "Healthcare", "Utilities"]
        }
    },
    
    "📈 Líderes de Momentum": {
        "description": "Fuerte momentum técnico (RSI 50-70, Retorno 1A > 20%, Volumen alto)",
        "filters": {
            "rsi_min": 50.0,
            "rsi_max": 70.0,
            "return_1y_min": 20.0,
            "return_3m_min": 10.0,
            "rel_volume_min": 1.2,
            "momentum_score_min": 70
        }
    },
    
    "🔥 Candidatos a Ruptura": {
        "description": "Cerca máximos 52 semanas (<10% del máximo, RSI 55-75)",
        "filters": {
            "distance_52w_high_max": 10.0,
            "rsi_min": 55.0,
            "rsi_max": 75.0,
            "return_1m_min": 5.0,
            "rel_volume_min": 1.5
        }
    },
    
    "🔄 Historias de Turnaround": {
        "description": "Recuperación con señales positivas (Z-Score 1.8-3, FCF > 0)",
        "filters": {
            "z_score_min": 1.8,
            "z_score_max": 3.0,
            "fcf_min": 0.0,
            "return_3m_min": 10.0,
            "rsi_min": 40.0,
            "rsi_max": 60.0
        }
    },
    
    "💎 Gemas Small Cap": {
        "description": "Small caps de calidad ($200M-$2B, ROE > 15%, Crecimiento > 15%)",
        "filters": {
            "market_cap_min": 200e6,
            "market_cap_max": 2e9,
            "roe_min": 15.0,
            "rev_growth_min": 15.0,
            "insider_ownership_min": 5.0,
            "master_score_min": 60
        }
    },
    
    "🎯 Quant Multi-Factor": {
        "description": "Modelo 5 factores: Valor + Calidad + Crecimiento + Momentum + Bajo Riesgo",
        "filters": {
            "value_score_min": 60,
            "quality_score_min": 60,
            "growth_score_min": 60,
            "momentum_score_min": 60,
            "beta_max": 1.5,
            "master_score_min": 70
        }
    },
    
    "📊 Fórmula Mágica Plus": {
        "description": "Greenblatt mejorado (Earnings Yield > 10%, ROIC > 20%, Momentum)",
        "filters": {
            "earnings_yield_min": 10.0,
            "roic_min": 20.0,
            "return_6m_min": 0.0,
            "debt_equity_max": 1.0,
            "market_cap_min": 50e6
        }
    },
    
    "🌟 Screener CANSLIM": {
        "description": "Método O'Neil (BPA +25%, Ingresos +20%, Cerca máximos, Inst. 30-80%)",
        "filters": {
            "eps_growth_min": 25.0,
            "rev_growth_min": 20.0,
            "distance_52w_high_max": 15.0,
            "institutional_ownership_min": 30.0,
            "institutional_ownership_max": 80.0,
            "rsi_min": 50.0
        }
    },
    
    "🌏 Estrellas Mercados Emergentes": {
        "description": "Mejores oportunidades en emergentes (Crecimiento > 15%, ROE > 12%)",
        "filters": {
            "countries": ["China", "India", "Brazil", "Mexico", "Indonesia", 
                        "Thailand", "Malaysia", "Philippines", "Vietnam", "Turkey"],
            "rev_growth_min": 15.0,
            "roe_min": 12.0,
            "master_score_min": 60
        }
    }
}

# =============================================================================
# INICIALIZACIÓN MEJORADA
# =============================================================================

# Inicializar estados principales
if 'filters_applied' not in st.session_state:
    st.session_state.filters_applied = False
if 'selected_screener' not in st.session_state:
    st.session_state.selected_screener = "🎯 Constructor Personalizado"
if 'countries_filter' not in st.session_state:
    st.session_state.countries_filter = []
if 'exclude_countries' not in st.session_state:
    st.session_state.exclude_countries = []
if 'active_filters' not in st.session_state:
    st.session_state.active_filters = {}
if 'last_applied_screener' not in st.session_state:
    st.session_state.last_applied_screener = None
if 'manual_filters_modified' not in st.session_state:
    st.session_state.manual_filters_modified = False

# =============================================================================
# FUNCIONES AUXILIARES -
# =============================================================================

def mark_filters_as_modified():
    """Marca que los filtros han sido modificados manualmente"""
    st.session_state.manual_filters_modified = True

def parse_market_cap(value_str):
    """Convierte strings de capitalización de mercado a números"""
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

def get_filter_initial_value(key, default_value, screener_config=None):
    """
    Obtiene el valor inicial para un filtro considerando:
    1. Si se acaba de cambiar el screener -> usar valor del screener
    2. Si hay un valor en session_state -> usar ese
    3. Si no -> usar el valor por defecto
    """
    if screener_config is None:
        screener_config = {}
    
    if st.session_state.get('screener_changed') and key in screener_config.get('filters', {}):
        return screener_config['filters'][key]
    elif key in st.session_state.get('active_filters', {}):
        return st.session_state.active_filters[key]
    else:
        return default_value

def capture_current_filter_values():
    """
    Captura todos los valores actuales de los inputs de filtros
    y los devuelve como un diccionario
    """
    current_filters = {}
    
    # Filtros básicos
    if 'search_term' in st.session_state and st.session_state.search_term:
        current_filters['search_term'] = st.session_state.search_term
    
    # Países
    if 'countries_filter' in st.session_state and st.session_state.countries_filter:
        current_filters['countries'] = st.session_state.countries_filter
    if 'exclude_countries' in st.session_state and st.session_state.exclude_countries:
        current_filters['exclude_countries'] = st.session_state.exclude_countries
    
    # Sectores
    if 'sectors_filter' in st.session_state and st.session_state.sectors_filter:
        current_filters['sectors'] = st.session_state.sectors_filter
    
    # Market Cap
    if 'min_mcap' in st.session_state and st.session_state.min_mcap:
        mcap_val = parse_market_cap(st.session_state.min_mcap)
        if mcap_val:
            current_filters['market_cap_min'] = mcap_val
    
    if 'max_mcap' in st.session_state and st.session_state.max_mcap:
        mcap_val = parse_market_cap(st.session_state.max_mcap)
        if mcap_val:
            current_filters['market_cap_max'] = mcap_val
    
    # Empleados y fundación
    if 'employees_min' in st.session_state and st.session_state.employees_min > 0:
        current_filters['employees_min'] = st.session_state.employees_min
    if 'founded_after' in st.session_state and st.session_state.founded_after > 1900:
        current_filters['founded_after'] = st.session_state.founded_after
    
    # Mapeo completo de filtros
    filter_mappings = {
        # Valoración
        'pe_min': ('pe_min', 0.0), 'pe_max': ('pe_max', 100.0),
        'fpe_min': ('forward_pe_min', 0.0), 'fpe_max': ('forward_pe_max', 100.0),
        'pb_min': ('pb_min', 0.0), 'pb_max': ('pb_max', 10.0),
        'ps_min': ('ps_min', 0.0), 'ps_max': ('ps_max', 20.0),
        'fps_min': ('forward_ps_min', 0.0), 'fps_max': ('forward_ps_max', 20.0),
        'peg_min': ('peg_min', 0.0), 'peg_max': ('peg_max', 5.0),
        'p_fcf_min': ('p_fcf_min', 0.0), 'p_fcf_max': ('p_fcf_max', 100.0),
        'p_ocf_min': ('p_ocf_min', 0.0), 'p_ocf_max': ('p_ocf_max', 100.0),
        'p_ebitda_min': ('p_ebitda_min', 0.0), 'p_ebitda_max': ('p_ebitda_max', 50.0),
        'p_tbv_min': ('p_tbv_min', 0.0), 'p_tbv_max': ('p_tbv_max', 10.0),
        'p_ffo_min': ('p_ffo_min', 0.0), 'p_ffo_max': ('p_ffo_max', 50.0),
        
        # Enterprise Value
        'ev_s_min': ('ev_sales_min', 0.0), 'ev_s_max': ('ev_sales_max', 20.0),
        'fwd_ev_s_min': ('fwd_ev_s_min', 0.0), 'fwd_ev_s_max': ('fwd_ev_s_max', 20.0),
        'ev_earn_min': ('ev_earnings_min', 0.0), 'ev_earn_max': ('ev_earnings_max', 100.0),
        'ev_eb_min': ('ev_ebitda_min', 0.0), 'ev_eb_max': ('ev_ebitda_max', 50.0),
        'ev_ebit_min': ('ev_ebit_min', 0.0), 'ev_ebit_max': ('ev_ebit_max', 50.0),
        'ev_fcf_min': ('ev_fcf_min', 0.0), 'ev_fcf_max': ('ev_fcf_max', 100.0),
        
        # Yields
        'fcf_y_min': ('fcf_yield_min', 0.0),
        'earn_y_min': ('earnings_yield_min', 0.0),
        'fcf_ev_min': ('fcf_ev_min', 0.0),
        'graham_up': ('graham_upside_min', -100.0),
        'lynch_up': ('lynch_upside_min', -100.0),
        
        # Crecimiento
        'rev_g_min': ('rev_growth_min', -100.0), 'rev_g_max': ('rev_growth_max', 500.0),
        'rev_gq_min': ('rev_growth_q_min', -100.0), 'rev_gq_max': ('rev_growth_q_max', 500.0),
        'rev_3y': ('rev_growth_3y_min', -100.0),
        'rev_5y': ('rev_growth_5y_min', -100.0),
        'rev_tq': ('rev_gr_this_q_min', -100.0),
        'rev_nq': ('rev_gr_next_q_min', -100.0),
        'eps_g_min': ('eps_growth_min', -100.0), 'eps_g_max': ('eps_growth_max', 500.0),
        'eps_gq_min': ('eps_growth_q_min', -100.0), 'eps_gq_max': ('eps_growth_q_max', 500.0),
        'eps_3y': ('eps_growth_3y_min', -100.0),
        'eps_5y': ('eps_growth_5y_min', -100.0),
        'eps_tq': ('eps_gr_this_q_min', -100.0),
        'eps_nq': ('eps_gr_next_q_min', -100.0),
        'rev_ty': ('rev_gr_this_y_min', -100.0),
        'rev_ny': ('rev_gr_next_y_min', -100.0),
        'rev_n5y': ('rev_gr_next_5y_min', -100.0),
        'eps_ty': ('eps_gr_this_y_min', -100.0),
        'eps_ny': ('eps_gr_next_y_min', -100.0),
        'eps_n5y': ('eps_gr_next_5y_min', -100.0),
        'fcf_g': ('fcf_growth_min', -100.0),
        'fcf_3y': ('fcf_growth_3y_min', -100.0),
        
        # Rentabilidad
        'roe_min': ('roe_min', -100.0), 'roe_max': ('roe_max', 200.0),
        'roa_min': ('roa_min', -100.0), 'roa_max': ('roa_max', 100.0),
        'roic_min': ('roic_min', -100.0), 'roic_max': ('roic_max', 200.0),
        'roce_min': ('roce_min', -100.0), 'roce_max': ('roce_max', 200.0),
        'roe_5y': ('roe_5y_min', -100.0),
        'roa_5y': ('roa_5y_min', -100.0),
        'roic_5y': ('roic_5y_min', -100.0),
        
        # Márgenes
        'gross_m': ('gross_margin_min', 0.0), 'gross_m_max': ('gross_margin_max', 100.0),
        'op_m': ('operating_margin_min', -100.0), 'op_m_max': ('operating_margin_max', 100.0),
        'pretax_m': ('pretax_margin_min', -100.0), 'pretax_m_max': ('pretax_margin_max', 100.0),
        'prof_m': ('profit_margin_min', -100.0), 'prof_m_max': ('profit_margin_max', 100.0),
        'fcf_m': ('fcf_margin_min', -100.0), 'fcf_m_max': ('fcf_margin_max', 100.0),
        'ebitda_m': ('ebitda_margin_min', -100.0), 'ebitda_m_max': ('ebitda_margin_max', 100.0),
        'ebit_m': ('ebit_margin_min', -100.0), 'ebit_m_max': ('ebit_margin_max', 100.0),
        
        # Salud Financiera
        'curr_r': ('current_ratio_min', 0.0), 'curr_r_max': ('current_ratio_max', 10.0),
        'quick_r': ('quick_ratio_min', 0.0), 'quick_r_max': ('quick_ratio_max', 10.0),
        'cash_r': ('cash_ratio_min', 0.0),
        'wc_min': ('working_capital_min', -1000.0),
        'de_min': ('debt_equity_min', 0.0), 'de_max': ('debt_equity_max', 5.0),
        'deb_min': ('debt_ebitda_min', 0.0), 'deb_max': ('debt_ebitda_max', 10.0),
        'dfcf_min': ('debt_fcf_min', 0.0), 'dfcf_max': ('debt_fcf_max', 20.0),
        'int_c': ('interest_coverage_min', 0.0), 'int_c_max': ('interest_coverage_max', 100.0),
        'z_min': ('z_score_min', -10.0), 'z_max': ('z_score_max', 10.0),
        'f_min': ('f_score_min', 0), 'f_max': ('f_score_max', 9),
        'fcf_min': ('fcf_min', -1000.0), 'fcf_max': ('fcf_max', 100000.0),
        'cash_min': ('total_cash_min', 0.0),
        'debt_max': ('total_debt_max', 100000.0),
        
        # Dividendos
        'div_y_min': ('div_yield_min', 0.0), 'div_y_max': ('div_yield_max', 20.0),
        'pay_min': ('payout_ratio_min', 0.0), 'pay_max': ('payout_ratio_max', 100.0),
        'years_min': ('years_min', 0), 'years_max': ('years_max', 100),
        'div_d_min': ('div_dollar_min', 0.0), 'div_d_max': ('div_dollar_max', 100.0),
        'div_1y': ('div_growth_1y_min', -100.0), 'div_1y_max': ('div_growth_1y_max', 500.0),
        'div_3y': ('div_growth_3y_min', -100.0), 'div_3y_max': ('div_growth_3y_max', 500.0),
        'div_5y': ('div_growth_5y_min', -100.0), 'div_5y_max': ('div_growth_5y_max', 500.0),
        'div_10y': ('div_growth_10y_min', -100.0), 'div_10y_max': ('div_growth_10y_max', 500.0),
        'sh_y': ('shareholder_yield_min', 0.0), 'sh_y_max': ('shareholder_yield_max', 50.0),
        'buy_y': ('buyback_yield_min', 0.0), 'buy_y_max': ('buyback_yield_max', 20.0),
        
        # Técnico
        'rsi_min': ('rsi_min', 0.0), 'rsi_max': ('rsi_max', 100.0),
        'rsi_w_min': ('rsi_w_min', 0.0), 'rsi_w_max': ('rsi_w_max', 100.0),
        'rsi_m_min': ('rsi_m_min', 0.0), 'rsi_m_max': ('rsi_m_max', 100.0),
        'ret_1w': ('return_1w_min', -100.0), 'ret_1w_max': ('return_1w_max', 100.0),
        'ret_1m': ('return_1m_min', -100.0), 'ret_1m_max': ('return_1m_max', 100.0),
        'ret_3m': ('return_3m_min', -100.0), 'ret_3m_max': ('return_3m_max', 200.0),
        'ret_6m': ('return_6m_min', -100.0), 'ret_6m_max': ('return_6m_max', 300.0),
        'ret_ytd': ('return_ytd_min', -100.0), 'ret_ytd_max': ('return_ytd_max', 500.0),
        'ret_1y': ('return_1y_min', -100.0), 'ret_1y_max': ('return_1y_max', 500.0),
        'ret_3y': ('return_3y_min', -100.0), 'ret_3y_max': ('return_3y_max', 1000.0),
        'ret_5y': ('return_5y_min', -100.0), 'ret_5y_max': ('return_5y_max', 2000.0),
        'ret_10y': ('return_10y_min', -100.0), 'ret_10y_max': ('return_10y_max', 5000.0),
        'ret_15y': ('return_15y_min', -100.0),
        'ret_20y': ('return_20y_min', -100.0),
        'ret_ipo': ('return_ipo_min', -100.0),
        '52h_max': ('distance_52w_high_max', 100.0),
        '52l_min': ('distance_52w_low_min', 0.0),
        'ath_max': ('ath_chg_max', 100.0),
        'atl_min': ('atl_chg_min', 0.0),
        'beta_min': ('beta_min', -2.0), 'beta_max': ('beta_max', 3.0),
        'atr_min': ('atr_min', 0.0), 'atr_max': ('atr_max', 100.0),
        'rel_v': ('rel_volume_min', 0.0), 'rel_v_max': ('rel_volume_max', 10.0),
        'avg_v_min': ('avg_volume_min', 0.0), 'avg_v_max': ('avg_volume_max', 1000.0),
        'dol_v_min': ('dollar_vol_min', 0.0),
        
        # Propiedad
        'ins_own': ('insider_ownership_min', 0.0), 'ins_own_max': ('insider_ownership_max', 100.0),
        'inst_min': ('institutional_ownership_min', 0.0), 'inst_max': ('institutional_ownership_max', 100.0),
        'ana_min': ('analysts_min', 0), 'ana_max': ('analysts_max', 100),
        'short_f_min': ('short_float_min', 0.0), 'short_f': ('short_float_max', 100.0),
        'short_s_min': ('short_shares_min', 0.0), 'short_s_max': ('short_shares_max', 100.0),
        'short_r_min': ('short_ratio_min', 0.0), 'short_r': ('short_ratio_max', 50.0),
        'sh_yoy_min': ('shares_ch_yoy_min', -50.0), 'sh_yoy_max': ('shares_ch_yoy_max', 50.0),
        'sh_qoq_min': ('shares_ch_qoq_min', -20.0), 'sh_qoq_max': ('shares_ch_qoq_max', 20.0),
        
        # Scores
        'quality_score_min': ('quality_score_min', 0),
        'value_score_min': ('value_score_min', 0),
        'growth_score_min': ('growth_score_min', 0),
        'financial_health_score_min': ('financial_health_score_min', 0),
        'momentum_score_min': ('momentum_score_min', 0),
        'master_score_min': ('master_score_min', 0),
        
        # Otros
        'pt_up_min': ('pt_upside_min', -100.0), 'pt_up_max': ('pt_upside_max', 500.0),
        'rat_min': ('rating_min', 1.0), 'rat_max': ('rating_max', 5.0),
        'sbc_min': ('sbc_rev_min', 0.0), 'sbc_max': ('sbc_rev_max', 50.0),
        'rd_min': ('rd_rev_min', 0.0), 'rd_max': ('rd_rev_max', 100.0),
    }
    
    # Capturar valores de todos los filtros numéricos
    for session_key, (filter_key, default_value) in filter_mappings.items():
        if session_key in st.session_state:
            value = st.session_state.get(session_key)
            # Solo agregar si el valor es diferente del default
            if value is not None and value != default_value:
                current_filters[filter_key] = value
    
    # Filtros adicionales de listas/multiselect
    additional_filters = [
        'exchanges_filter', 'in_index_filter', 'industries_filter',
        'mc_groups_filter', 'is_spac_filter', 'has_options_filter'
    ]
    
    for filter_key in additional_filters:
        if filter_key in st.session_state and st.session_state.get(filter_key):
            current_filters[filter_key] = st.session_state.get(filter_key)
    
    # Fechas
    date_filters = {
        'ipo_after': 'ipo_date_after',
        'ipo_before': 'ipo_date_before',
        'earn_after': 'earnings_date_after',
        'earn_before': 'earnings_date_before',
        'exdiv_after': 'ex_div_date_after',
        'exdiv_before': 'ex_div_date_before'
    }
    
    for session_key, filter_key in date_filters.items():
        if session_key in st.session_state:
            date_value = st.session_state.get(session_key)
            if date_value:
                current_filters[filter_key] = date_value
    
    return current_filters

def create_beautiful_html_table(df):
    """Crea una tabla HTML hermosa con estilos personalizados"""
    
    html_rows = []
    for idx, row in df.iterrows():
        row_html = "<tr>"
        for col in df.columns:
            value = row[col]
            
            # Estilos específicos por columna
            if col == 'Symbol':
                cell_html = f'<td style="font-weight: bold; color: #4a9eff; font-size: 14px;">{value}</td>'
            elif col == 'Company Name':
                display_name = str(value)[:40] + '...' if len(str(value)) > 40 else str(value)
                cell_html = f'<td style="color: #e8e8e8; font-size: 13px;">{display_name}</td>'
            elif col == 'Country':
                bg_color = '#4e7ce2' if value == 'United States' else 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                cell_html = f'''
                <td>
                    <span style="background: {bg_color}; color: white; padding: 4px 10px; 
                                border-radius: 12px; font-size: 11px; font-weight: 600;">
                        {value}
                    </span>
                </td>'''
            elif col == 'Sector':
                sector_colors = {
                    'Technology': '#6366f1',
                    'Healthcare': '#14b8a6', 
                    'Financials': '#f59e0b',
                    'Consumer Discretionary': '#ec4899',
                    'Communication Services': '#8b5cf6',
                    'Industrials': '#6b7280',
                    'Materials': '#84cc16',
                    'Energy': '#ef4444',
                    'Consumer Staples': '#06b6d4',
                    'Utilities': '#fbbf24',
                    'Real Estate': '#10b981'
                }
                bg_color = sector_colors.get(value, '#6b7280')
                cell_html = f'''
                <td>
                    <span style="background: {bg_color}; color: white; padding: 4px 10px; 
                                border-radius: 12px; font-size: 11px; font-weight: 500;">
                        {value}
                    </span>
                </td>'''
            elif col == 'Market Cap':
                formatted_val = format_number(value, prefix='$') if pd.notna(value) else '-'
                cell_html = f'<td style="color: #ffd700; font-weight: 500;">{formatted_val}</td>'
            elif 'Score' in col:
                if pd.notna(value):
                    color = '#10b981' if value >= 75 else '#f59e0b' if value >= 50 else '#ef4444'
                    bar_width = int(value) if value > 0 else 0
                    cell_html = f'''
                    <td>
                        <div style="display: flex; align-items: center; justify-content: center;">
                            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; 
                                       height: 20px; width: 100px; position: relative; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, {color}, {color}CC); 
                                           height: 100%; width: {bar_width}%; border-radius: 10px;"></div>
                                <span style="position: absolute; left: 50%; transform: translateX(-50%); 
                                            color: white; font-weight: bold; font-size: 12px; 
                                            line-height: 20px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
                                    {value:.0f}
                                </span>
                            </div>
                        </div>
                    </td>'''
                else:
                    cell_html = '<td>-</td>'
            else:
                # Formato general para otras columnas
                display_val = str(value) if pd.notna(value) else '-'
                if isinstance(value, (int, float)) and pd.notna(value):
                    if any(keyword in col for keyword in ['Growth', 'Return', 'Yield', 'Margin', 'ROE', 'ROA', 'ROIC']):
                        display_val = f"{value:.1f}%"
                        color = '#10b981' if value > 0 else '#ef4444' if value < 0 else '#e8e8e8'
                        cell_html = f'<td style="color: {color};">{display_val}</td>'
                    elif any(keyword in col for keyword in ['Ratio', 'PE', 'PB', 'PS']):
                        display_val = f"{value:.2f}"
                        cell_html = f'<td style="color: #e8e8e8;">{display_val}</td>'
                    else:
                        cell_html = f'<td style="color: #e8e8e8;">{display_val}</td>'
                else:
                    cell_html = f'<td style="color: #e8e8e8;">{display_val}</td>'
            
            row_html += cell_html
        row_html += "</tr>"
        html_rows.append(row_html)
    
    # Crear headers
    headers = ''.join([f'<th>{col}</th>' for col in df.columns])
    
    # Tabla completa con estilos
    html_table = f'''
    <div style="border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.5); 
                background: linear-gradient(145deg, #1a1f2e, #151922); margin-top: 20px;">
        <style>
            .bquant-table {{
                width: 100%;
                border-collapse: collapse;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            .bquant-table th {{
                background: linear-gradient(135deg, #4a9eff 0%, #3a7dd8 100%);
                color: white;
                padding: 14px 10px;
                text-align: left;
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                border: none;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            .bquant-table tr {{
                border-bottom: 1px solid rgba(74, 158, 255, 0.1);
                transition: all 0.3s ease;
            }}
            .bquant-table tr:hover {{
                background: rgba(74, 158, 255, 0.08) !important;
                transform: scale(1.005);
                box-shadow: 0 2px 10px rgba(74, 158, 255, 0.2);
            }}
            .bquant-table td {{
                padding: 12px 10px;
                font-size: 13px;
            }}
            .bquant-table tbody tr:nth-child(even) {{
                background: rgba(74, 158, 255, 0.03);
            }}
        </style>
        <table class="bquant-table">
            <thead>
                <tr>{headers}</tr>
            </thead>
            <tbody>
                {''.join(html_rows)}
            </tbody>
        </table>
    </div>
    '''
    
    return html_table

def get_available_filters_for_countries(df, countries):
    """Returns which filters have sufficient data for selected countries"""
    if countries:
        country_df = df[df['Country'].isin(countries)]
    else:
        country_df = df
    
    # Define minimum data threshold (10% of companies must have data)
    min_coverage = 0.1
    available_filters = {}
    
    filter_groups = {
        'valoracion': ['PE Ratio', 'PB Ratio', 'PS Ratio', 'PEG Ratio'],
        'crecimiento': ['Rev. Growth', 'EPS Growth', 'Rev Gr. Next Y'],
        'rentabilidad': ['ROE', 'ROA', 'ROIC', 'Profit Margin'],
        'dividendos': ['Div. Yield', 'Payout Ratio', 'Years'],
        'salud': ['Current Ratio', 'Debt / Equity', 'Z-Score'],
        'tecnico': ['RSI', 'Return 1Y', 'Beta (5Y)']
    }
    
    for group, metrics in filter_groups.items():
        available_filters[group] = []
        for metric in metrics:
            if metric in country_df.columns:
                coverage = country_df[metric].notna().sum() / len(country_df)
                if coverage >= min_coverage:
                    available_filters[group].append(metric)
    
    return available_filters

def disable_filter_if_no_data(df, countries, metric_name):
    """Check if a metric has sufficient data for selected countries"""
    if countries:
        country_df = df[df['Country'].isin(countries)]
    else:
        country_df = df
    
    if metric_name not in country_df.columns:
        return True  # Disable if column doesn't exist
    
    coverage = country_df[metric_name].notna().sum() / len(country_df)
    return coverage < 0.1  # Disable if less than 10% coverage

# =============================================================================
# HEADER PRINCIPAL
# =============================================================================

st.markdown("""
<div style='text-align: center; padding: 30px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin-bottom: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.3);'>
    <h1 style='margin: 0; color: #ffffff; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
        🌍 BQuant Global Stock Screener (By @Gsnchez)
    </h1>
    <p style='color: #f0f0f0; margin-top: 15px; font-size: 1.2em; font-weight: 300;'>
        Análisis avanzado de <strong>68,000+ acciones globales</strong> | <strong>89 países</strong> | <strong>270+ métricas</strong>
    </p>
    <p style='color: #ffffff; margin-top: 10px;'>
        Desarrollado por <strong>@Gsnchez</strong> | <strong>bquantfinance.com</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# Cargar datos
with st.spinner("Cargando base de datos global..."):
    df = load_and_preprocess_data()

# =============================================================================
# PANEL DE CONTROL SIMPLIFICADO - VERSIÓN CORREGIDA
# =============================================================================

st.markdown("## 🚀 Panel de Control Rápido")

# Selector de plantilla y botón en una línea
col1, col2, col3 = st.columns([3, 4, 2])

with col1:
    st.markdown("#### 📋 Seleccionar Plantilla")
    
    # Callback para cuando cambia el screener seleccionado
    def on_screener_change():
        """
        Callback cuando cambia el selector de screener
        """
        new_screener = st.session_state.screener_selector
        if new_screener != st.session_state.get('selected_screener'):
            st.session_state.selected_screener = new_screener
            # NO aplicar automáticamente, solo marcar el cambio
            st.session_state.screener_changed = True
            
            # Si hay modificaciones pendientes, preguntar al usuario
            if st.session_state.get('manual_filters_modified', False):
                # Resetear las modificaciones ya que cambió de screener
                st.session_state.manual_filters_modified = False
    
    selected_screener = st.selectbox(
        "Seleccionar Screener",  
        options=list(SCREENERS.keys()),
        index=list(SCREENERS.keys()).index(st.session_state.selected_screener),
        key="screener_selector",
        on_change=on_screener_change,
        label_visibility="collapsed" 
)

with col2:
    screener_config = SCREENERS.get(selected_screener, {"description": "", "filters": {}})
    st.markdown("#### 📝 Descripción")
    st.info(screener_config['description'])
    
    # Mostrar si hay filtros manuales modificados
    if st.session_state.get('manual_filters_modified', False):
        st.warning("⚠️ Has modificado los filtros manualmente. Haz clic en EJECUTAR para aplicar los cambios.")

with col3:
    st.markdown("#### ⚡ Acción")
    
    def execute_screener():
        """
        Ejecuta el screener con la lógica correcta:
        1. Si es Constructor Personalizado -> captura valores actuales
        2. Si hay modificaciones manuales -> captura valores actuales
        3. Si se cambió de screener sin modificaciones -> usa predefinidos
        4. Si no hay cambios -> mantiene los filtros actuales activos
        """
        
        # Determinar qué filtros usar
        if selected_screener == "🎯 Constructor Personalizado":
            # Constructor personalizado siempre captura valores actuales
            filters_to_apply = capture_current_filter_values()
        elif st.session_state.get('manual_filters_modified', False):
            # Si hay modificaciones manuales, capturar valores actuales
            filters_to_apply = capture_current_filter_values()
        elif selected_screener != st.session_state.get('last_applied_screener'):
            # Si cambió el screener, usar los valores predefinidos
            filters_to_apply = screener_config.get('filters', {})
            # Actualizar también los filtros de países si están definidos
            if 'countries' in filters_to_apply:
                st.session_state.countries_filter = filters_to_apply['countries']
            else:
                st.session_state.countries_filter = []
            if 'exclude_countries' in filters_to_apply:
                st.session_state.exclude_countries = filters_to_apply['exclude_countries']
            else:
                st.session_state.exclude_countries = []
        else:
            # No hay cambios, mantener filtros activos actuales
            filters_to_apply = st.session_state.get('active_filters', {})
        
        # Aplicar los filtros
        st.session_state.active_filters = filters_to_apply
        st.session_state.filters_applied = True
        st.session_state.last_applied_screener = selected_screener
        st.session_state.show_success = True
        st.session_state.manual_filters_modified = False
        st.session_state.screener_changed = False
    
    # Botón EJECUTAR principal
    if st.button("🚀 **EJECUTAR**", 
                 type="primary", 
                 use_container_width=True, 
                 key="run_screener",
                 help="Ejecuta el screener seleccionado con los filtros configurados"):
        execute_screener()
        st.rerun()

# Línea divisoria
st.markdown("---")

# =============================================================================
# ESTADÍSTICAS DE LA BASE DE DATOS
# =============================================================================

st.markdown("### 📊 Estadísticas de la Base de Datos")

# Métricas en una sola fila
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        label="Total Acciones",
        value=f"{len(df):,}",
        delta=None,
        help="Total de acciones en la base de datos"
    )

with col2:
    st.metric(
        label="Países",
        value=f"{df['Country'].nunique() if 'Country' in df.columns else 0}",
        delta=None,
        help="Número de países cubiertos"
    )

with col3:
    st.metric(
        label="Sectores",
        value=f"{df['Sector'].nunique() if 'Sector' in df.columns else 0}",
        delta=None,
        help="Número de sectores disponibles"
    )

with col4:
    pe_median = df['PE Ratio'].median() if 'PE Ratio' in df.columns and not df['PE Ratio'].isna().all() else 0
    st.metric(
        label="P/E Mediano",
        value=f"{pe_median:.1f}",
        delta=None,
        help="P/E mediano del mercado global"
    )

with col5:
    total_cap = df['Market Cap'].sum() if 'Market Cap' in df.columns else 0
    st.metric(
        label="Cap. Mercado",
        value=format_number(total_cap, prefix="$"),
        delta=None,
        help="Capitalización total del mercado"
    )

with col6:
    st.metric(
        label="Actualizado",
        value="Sept 2025",
        delta=None,
        help="Última actualización de datos"
    )

if st.session_state.filters_applied:
    active_count = len(st.session_state.get('active_filters', {}))
    screener_name = st.session_state.get('last_applied_screener', 'No definido')
    
    # Determinar el tipo de mensaje según el estado
    if st.session_state.get('manual_filters_modified', False):
        st.warning(f"""
        ⚠️ **Filtros Modificados Manualmente**
        - Basado en: {screener_name}
        - {active_count} filtros configurados
        - **Cambios pendientes de aplicar**
        - Usa EJECUTAR o APLICAR FILTROS para aplicar los cambios
        """)
    else:
        # Verificar si los filtros actuales coinciden con algún screener predefinido
        is_modified = "(Modificado)" in str(screener_name)
        
        if is_modified:
            st.success(f"""
            ✅ **Filtros Personalizados Activos**
            - Basado en: {screener_name}
            - {active_count} filtros aplicados
            - Configuración personalizada en uso
            """)
        else:
            st.success(f"""
            ✅ **Filtros Activos**
            - Screener: {screener_name}
            - {active_count} filtros aplicados
            - Usando configuración predefinida
            """)
    
    # Mostrar resumen de filtros principales activos
    with st.expander("📋 Ver Filtros Activos", expanded=False):
        active_filters = st.session_state.get('active_filters', {})
        if active_filters:
            # Agrupar por categoría para mejor visualización
            filter_categories = {
                "🌍 Geografía": ['countries', 'exclude_countries'],
                "📊 Valoración": ['pe_min', 'pe_max', 'pb_min', 'pb_max', 'ps_min', 'ps_max', 
                                'peg_min', 'peg_max', 'fcf_yield_min', 'earnings_yield_min'],
                "📈 Crecimiento": ['rev_growth_min', 'rev_growth_max', 'eps_growth_min', 'eps_growth_max',
                                 'rev_gr_next_y_min', 'eps_gr_next_y_min'],
                "💎 Rentabilidad": ['roe_min', 'roe_max', 'roa_min', 'roa_max', 'roic_min', 'roic_max',
                                   'profit_margin_min', 'gross_margin_min'],
                "🏥 Salud Financiera": ['current_ratio_min', 'debt_equity_max', 'z_score_min', 
                                      'f_score_min', 'fcf_min'],
                "💵 Dividendos": ['div_yield_min', 'div_yield_max', 'payout_ratio_max', 'years_min'],
                "📉 Técnico": ['rsi_min', 'rsi_max', 'return_1y_min', 'return_3m_min', 
                             'distance_52w_high_max', 'rel_volume_min'],
                "🏢 Propiedad": ['insider_ownership_min', 'institutional_ownership_min', 
                               'institutional_ownership_max'],
                "🎯 Scores": ['quality_score_min', 'value_score_min', 'growth_score_min', 
                            'master_score_min', 'financial_health_score_min', 'momentum_score_min']
            }
            
            filters_shown = False
            for category, keys in filter_categories.items():
                category_filters = {k: v for k, v in active_filters.items() if k in keys}
                if category_filters:
                    filters_shown = True
                    st.markdown(f"**{category}**")
                    for key, value in category_filters.items():
                        # Formatear el nombre del filtro de manera más legible
                        display_name = key.replace('_', ' ').title()
                        display_name = display_name.replace('Min', '≥').replace('Max', '≤')
                        
                        # Formatear el valor según el tipo
                        if isinstance(value, list):
                            value_str = ', '.join(map(str, value[:5])) + ('...' if len(value) > 5 else '')
                        elif isinstance(value, float):
                            value_str = f"{value:.2f}"
                        else:
                            value_str = str(value)
                        
                        st.text(f"  • {display_name}: {value_str}")
            
            # Mostrar otros filtros no categorizados
            other_filters = {k: v for k, v in active_filters.items() 
                           if not any(k in cat for cat in filter_categories.values())}
            if other_filters:
                filters_shown = True
                st.markdown("**📋 Otros Filtros**")
                for key, value in other_filters.items():
                    display_name = key.replace('_', ' ').title()
                    if isinstance(value, list):
                        value_str = ', '.join(map(str, value[:3])) + ('...' if len(value) > 3 else '')
                    else:
                        value_str = str(value)
                    st.text(f"  • {display_name}: {value_str}")
            
            if not filters_shown:
                st.info("No hay filtros específicos configurados")
        else:
            st.info("No hay filtros específicos configurados")
    
    # Botón para limpiar todos los filtros
    col_clear1, col_clear2, col_clear3 = st.columns([1, 1, 1])
    with col_clear2:
        if st.button("🗑️ **Limpiar Todos los Filtros**", 
                     use_container_width=True,
                     key="clear_all_filters",
                     help="Elimina todos los filtros aplicados y reinicia el screener"):
            st.session_state.active_filters = {}
            st.session_state.filters_applied = False
            st.session_state.countries_filter = []
            st.session_state.exclude_countries = []
            st.session_state.selected_screener = "🎯 Constructor Personalizado"
            st.session_state.last_applied_screener = None
            st.session_state.manual_filters_modified = False
            st.session_state.screener_changed = False
            # Limpiar también los valores de los inputs
            for key in list(st.session_state.keys()):
                if any(x in key for x in ['_min', '_max', 'filter', 'score']):
                    del st.session_state[key]
            st.rerun()

else:
    st.info("""
    ℹ️ **Sin Filtros Activos**
    
    Para comenzar:
    1. Selecciona un screener predefinido y haz clic en **EJECUTAR**
    2. O configura filtros personalizados y haz clic en **APLICAR TODOS LOS FILTROS**
    
    💡 **Tip:** Los screeners predefinidos son un buen punto de partida que puedes personalizar después.
    """)

st.markdown("---")

# =============================================================================
# INSTANT RESULTS PREVIEW - COMPLETE CODE TO PASTE
# =============================================================================

if st.session_state.filters_applied:
    # Apply ALL filters to get accurate count
    filtered_df = df.copy()
    active_filters = st.session_state.get('active_filters', {})
    
    # Apply search term
    if 'search_term' in active_filters and active_filters['search_term']:
        filtered_df = filtered_df[
            filtered_df['Symbol'].str.contains(active_filters['search_term'].upper(), na=False) |
            filtered_df['Company Name'].str.contains(active_filters['search_term'], case=False, na=False)
        ]
    
    # Apply country filters
    if 'countries' in active_filters:
        filtered_df = filtered_df[filtered_df['Country'].isin(active_filters['countries'])]
    if 'exclude_countries' in active_filters:
        filtered_df = filtered_df[~filtered_df['Country'].isin(active_filters['exclude_countries'])]
    
    # Apply sector filters
    if 'sectors' in active_filters and 'Sector' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Sector'].isin(active_filters['sectors'])]
    
    # Apply market cap
    if 'market_cap_min' in active_filters and 'Market Cap' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Market Cap'] >= active_filters['market_cap_min']]
    if 'market_cap_max' in active_filters and 'Market Cap' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Market Cap'] <= active_filters['market_cap_max']]
    
    # Apply ALL numeric filters
    column_filter_mapping = {
        'PE Ratio': {
            'min': active_filters.get('pe_min'),
            'max': active_filters.get('pe_max')
        },
        'PB Ratio': {
            'min': active_filters.get('pb_min'),
            'max': active_filters.get('pb_max')
        },
        'PS Ratio': {
            'min': active_filters.get('ps_min'),
            'max': active_filters.get('ps_max')
        },
        'PEG Ratio': {
            'min': active_filters.get('peg_min'),
            'max': active_filters.get('peg_max')
        },
        'FCF Yield': {
            'min': active_filters.get('fcf_yield_min')
        },
        'Current Ratio': {
            'min': active_filters.get('current_ratio_min')
        },
        'Debt / Equity': {
            'max': active_filters.get('debt_equity_max')
        },
        'Z-Score': {
            'min': active_filters.get('z_score_min')
        },
        'ROE': {
            'min': active_filters.get('roe_min'),
            'max': active_filters.get('roe_max')
        },
        'ROA': {
            'min': active_filters.get('roa_min'),
            'max': active_filters.get('roa_max')
        },
        'ROIC': {
            'min': active_filters.get('roic_min'),
            'max': active_filters.get('roic_max')
        },
        'Rev. Growth': {
            'min': active_filters.get('rev_growth_min'),
            'max': active_filters.get('rev_growth_max')
        },
        'EPS Growth': {
            'min': active_filters.get('eps_growth_min'),
            'max': active_filters.get('eps_growth_max')
        },
        'Profit Margin': {
            'min': active_filters.get('profit_margin_min'),
            'max': active_filters.get('profit_margin_max')
        },
        'Gross Margin': {
            'min': active_filters.get('gross_margin_min'),
            'max': active_filters.get('gross_margin_max')
        },
        'Years': {
            'min': active_filters.get('years_min'),
            'max': active_filters.get('years_max')
        },
        'Div. Yield': {
            'min': active_filters.get('div_yield_min'),
            'max': active_filters.get('div_yield_max')
        },
        'Payout Ratio': {
            'min': active_filters.get('payout_ratio_min'),
            'max': active_filters.get('payout_ratio_max')
        },
        'RSI': {
            'min': active_filters.get('rsi_min'),
            'max': active_filters.get('rsi_max')
        },
        'Beta (5Y)': {
            'min': active_filters.get('beta_min'),
            'max': active_filters.get('beta_max')
        },
        'Return 1Y': {
            'min': active_filters.get('return_1y_min'),
            'max': active_filters.get('return_1y_max')
        },
        'Return 3M': {
            'min': active_filters.get('return_3m_min'),
            'max': active_filters.get('return_3m_max')
        },
        'Return 6M': {
            'min': active_filters.get('return_6m_min'),
            'max': active_filters.get('return_6m_max')
        },
        'Rel. Volume': {
            'min': active_filters.get('rel_volume_min'),
            'max': active_filters.get('rel_volume_max')
        },
        'Shares Insiders': {
            'min': active_filters.get('insider_ownership_min'),
            'max': active_filters.get('insider_ownership_max')
        },
        'Shares Institut.': {
            'min': active_filters.get('institutional_ownership_min'),
            'max': active_filters.get('institutional_ownership_max')
        },
        'Quality_Score': {
            'min': active_filters.get('quality_score_min')
        },
        'Value_Score': {
            'min': active_filters.get('value_score_min')
        },
        'Growth_Score': {
            'min': active_filters.get('growth_score_min')
        },
        'Financial_Health_Score': {
            'min': active_filters.get('financial_health_score_min')
        },
        'Momentum_Score': {
            'min': active_filters.get('momentum_score_min')
        },
        'Master_Score': {
            'min': active_filters.get('master_score_min')
        }
    }
    
    # Apply all numeric filters
    for col, limits in column_filter_mapping.items():
        if col in filtered_df.columns:
            if 'min' in limits and limits['min'] is not None:
                filtered_df = filtered_df[filtered_df[col] >= limits['min']]
            if 'max' in limits and limits['max'] is not None:
                filtered_df = filtered_df[filtered_df[col] <= limits['max']]
    
    # Special handling for 52W High distance
    if 'distance_52w_high_max' in active_filters and '52W High Chg' in filtered_df.columns:
        max_distance = -active_filters['distance_52w_high_max']
        filtered_df = filtered_df[filtered_df['52W High Chg'] >= max_distance]
    
    # Calculate metrics from the fully filtered dataframe
    results_count = len(filtered_df)
    countries_count = filtered_df['Country'].nunique() if 'Country' in filtered_df.columns else 0
    total_mcap = filtered_df['Market Cap'].sum() if 'Market Cap' in filtered_df.columns else 0
    median_pe = filtered_df['PE Ratio'].median() if 'PE Ratio' in filtered_df.columns and not filtered_df['PE Ratio'].isna().all() else 0
    avg_roe = filtered_df['ROE'].mean() if 'ROE' in filtered_df.columns and not filtered_df['ROE'].isna().all() else 0
    avg_score = filtered_df['Master_Score'].mean() if 'Master_Score' in filtered_df.columns and not filtered_df['Master_Score'].isna().all() else 0
    
    # Show balloons only once after executing
    if st.session_state.get('show_success', False):
        st.balloons()
        st.session_state.show_success = False
    
    # Display results summary bar (only if there are results)
    if results_count > 0:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981, #059669); 
                    padding: 20px; border-radius: 12px; margin: 20px 0;
                    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);'>
            <div style='display: flex; align-items: center; margin-bottom: 15px;'>
                <span style='font-size: 24px; margin-right: 10px;'>✅</span>
                <h3 style='color: white; margin: 0; font-size: 20px;'>
                    Encontradas {results_count:,} acciones que cumplen los criterios
                </h3>
            </div>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                        gap: 15px; margin-top: 15px;'>
                <div style='text-align: center;'>
                    <div style='color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 5px;'>
                        📊 Resultados
                    </div>
                    <div style='color: white; font-size: 24px; font-weight: bold;'>
                        {results_count}
                    </div>
                    <div style='color: rgba(255,255,255,0.7); font-size: 11px;'>
                        {(results_count/len(df)*100):.1f}% del total
                    </div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 5px;'>
                        🌍 Países
                    </div>
                    <div style='color: white; font-size: 24px; font-weight: bold;'>
                        {countries_count}
                    </div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 5px;'>
                        💰 Cap. Total
                    </div>
                    <div style='color: white; font-size: 24px; font-weight: bold;'>
                        {format_number(total_mcap, prefix='$')}
                    </div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 5px;'>
                        P/E Mediano
                    </div>
                    <div style='color: white; font-size: 24px; font-weight: bold;'>
                        {median_pe:.1f}
                    </div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 5px;'>
                        ROE Promedio
                    </div>
                    <div style='color: white; font-size: 24px; font-weight: bold;'>
                        {avg_roe:.1f}%
                    </div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 5px;'>
                        Score Promedio
                    </div>
                    <div style='color: white; font-size: 24px; font-weight: bold;'>
                        {avg_score:.0f}/100
                    </div>
                </div>
            </div>
            <div style='text-align: center; margin-top: 20px; padding-top: 15px; 
                        border-top: 1px solid rgba(255,255,255,0.2);'>
                <p style='color: rgba(255,255,255,0.9); margin: 0;'>
                    📊 Ve a la pestaña <strong>Resultados y Análisis</strong> para ver todos los detalles
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # No results found
        st.warning("⚠️ No se encontraron acciones que cumplan todos los criterios. Intenta ajustar los filtros.")

st.markdown("---")


# =============================================================================
# INDICADOR DE ESTADO DE FILTROS
# =============================================================================

if st.session_state.filters_applied:
    st.success(f"✅ **Filtros Activos** - Screener: {selected_screener}")
else:
    st.info("ℹ️ **Sin Filtros Activos** - Selecciona un screener y haz clic en EJECUTAR")

st.markdown("---")


# =============================================================================
# TABS PRINCIPALES - SECCIÓN COMPLETA DE FILTROS CON CALLBACKS
# =============================================================================

main_tab1, main_tab2 = st.tabs(["⚙️ Filtros Avanzados", "📊 Resultados y Análisis"])

with main_tab1:
    preset_filters = screener_config.get('filters', {})
    
    # Inicializar filtros de países
    if 'countries' in preset_filters:
        st.session_state.countries_filter = preset_filters['countries']
    if 'exclude_countries' in preset_filters:
        st.session_state.exclude_countries = preset_filters['exclude_countries']
    
    countries_filter = st.session_state.countries_filter
    exclude_countries = st.session_state.exclude_countries
    
    # Crear mensaje informativo
    st.markdown("""
    <div class="info-box">
        💡 <strong>Consejo:</strong> Todos los filtros incluyen descripciones educativas. 
        Pasa el cursor sobre los campos para aprender qué significa cada métrica y cómo interpretarla.
    </div>
    """, unsafe_allow_html=True)
    
    # Categorías de filtros en tabs
    filter_tabs = st.tabs([
        "🔍 Básicos", "🌍 Países", "📊 Valoración", "📈 Crecimiento", 
        "💎 Rentabilidad", "🏥 Salud", "💵 Dividendos", 
        "📉 Técnico", "🏢 Propiedad", "🎯 Puntuaciones", "📅 Fechas", "📋 Otros"
    ])
    
    # =========================================================================
    # TAB 1: FILTROS BÁSICOS
    # =========================================================================
    with filter_tabs[0]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🔍 Filtros de Screening Básicos</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_term = st.text_input(
                "🔎 Buscar", 
                placeholder="Ticker o nombre",
                key="search_term",
                on_change=mark_filters_as_modified,
                help="Buscar por símbolo o nombre de empresa"
            )
        with col2:
            if 'Sector' in df.columns:
                sectors_filter = st.multiselect(
                    "🏢 Sectores",
                    options=sorted(df['Sector'].dropna().unique()),
                    default=preset_filters.get('sectors', []),
                    key="sectors_filter",
                    on_change=mark_filters_as_modified,
                    help="Filtrar por sectores de negocio"
                )
        with col3:
            min_mcap = st.text_input(
                "💰 Cap. Mercado Mín",
                value=f"{int(preset_filters.get('market_cap_min', 0)/1e6)}M" if preset_filters.get('market_cap_min', 0) > 0 else "",
                placeholder="100M",
                key="min_mcap",
                on_change=mark_filters_as_modified,
                help="Capitalización mínima (ej: 100M, 1B)"
            )
        with col4:
            max_mcap = st.text_input(
                "💰 Cap. Mercado Máx",
                value=f"{int(preset_filters.get('market_cap_max', 0)/1e9)}B" if preset_filters.get('market_cap_max', 0) > 0 else "",
                placeholder="10B",
                key="max_mcap",
                on_change=mark_filters_as_modified,
                help="Capitalización máxima"
            )
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            employees_min = st.number_input(
                "👥 Empleados Mín",
                value=preset_filters.get('employees_min', 0),
                key="employees_min",
                on_change=mark_filters_as_modified,
                help=METRIC_DESCRIPTIONS["employees"]
            )
        with col2:
            founded_after = st.number_input(
                "📅 Fundada después de",
                value=preset_filters.get('founded_after', 1900),
                min_value=1800,
                max_value=2025,
                key="founded_after",
                on_change=mark_filters_as_modified,
                help=METRIC_DESCRIPTIONS["founded"]
            )
        with col3:
            if 'Exchange' in df.columns:
                exchanges_filter = st.multiselect(
                    "🏛️ Bolsas",
                    options=sorted(df['Exchange'].dropna().unique()),
                    key="exchanges_filter",
                    on_change=mark_filters_as_modified,
                    help=METRIC_DESCRIPTIONS["exchange"]
                )
        with col4:
            if 'In Index' in df.columns:
                in_index_filter = st.multiselect(
                    "📈 Índices",
                    ["SP500", "NASDAQ100", "DOW30"],
                    key="in_index_filter",
                    on_change=mark_filters_as_modified,
                    help=METRIC_DESCRIPTIONS["in_index"]
                )
        
        st.markdown("##### 🏭 Filtros de Industria y Clasificación")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if 'Industry' in df.columns:
                industries_filter = st.multiselect(
                    "🏭 Industrias",
                    options=sorted(df['Industry'].dropna().unique()),
                    key="industries_filter",
                    on_change=mark_filters_as_modified,
                    help=METRIC_DESCRIPTIONS["industry"]
                )
        with col2:
            if 'MC Group' in df.columns:
                mc_groups_filter = st.multiselect(
                    "📊 Grupo Cap.",
                    options=sorted(df['MC Group'].dropna().unique()),
                    key="mc_groups_filter",
                    on_change=mark_filters_as_modified,
                    help=METRIC_DESCRIPTIONS["mc_group"]
                )
        with col3:
            if 'Is SPAC' in df.columns:
                is_spac_filter = st.selectbox(
                    "🎯 SPAC",
                    ["Todos", "Sí", "No"],
                    key="is_spac_filter",
                    on_change=mark_filters_as_modified,
                    help=METRIC_DESCRIPTIONS["is_spac"]
                )
        with col4:
            if 'Options' in df.columns:
                has_options_filter = st.selectbox(
                    "📊 Opciones",
                    ["Todos", "Sí", "No"],
                    key="has_options_filter",
                    on_change=mark_filters_as_modified,
                    help=METRIC_DESCRIPTIONS["options"]
                )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # TAB 2: PAÍSES
    # =========================================================================
    with filter_tabs[1]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        if 'Country' in df.columns:
            country_counts = df['Country'].value_counts()
            
            st.markdown('<div class="section-header">🌍 Filtros Geográficos</div>', unsafe_allow_html=True)
            
            # Country data quality tiers
            COUNTRY_DATA_TIERS = {
                'Tier 1 - Cobertura Completa': [
                    'United States', 'US OTC', 'United Kingdom', 'Germany', 
                    'Japan', 'Canada', 'France', 'Switzerland', 'Australia', 'Netherlands'
                ],
                'Tier 2 - Buena Cobertura': [
                    'Spain', 'Italy', 'Sweden', 'Norway', 'Denmark', 'Belgium', 
                    'Hong Kong', 'Singapore', 'Finland', 'Austria', 'Ireland', 'New Zealand'
                ],
                'Tier 3 - Cobertura Moderada': [
                    'China', 'India', 'Brazil', 'South Korea', 'Taiwan', 
                    'Mexico', 'Poland', 'Israel', 'Russia', 'Greece', 'Portugal'
                ],
                'Tier 4 - Cobertura Básica': [
                    'Indonesia', 'Thailand', 'Malaysia', 'Philippines', 'Vietnam',
                    'Turkey', 'Saudi Arabia', 'United Arab Emirates', 'Egypt', 
                    'Argentina', 'Chile', 'Colombia', 'Peru', 'Pakistan', 'Bangladesh'
                ]
            }
            
            def get_country_tier(country):
                for tier, countries in COUNTRY_DATA_TIERS.items():
                    if country in countries:
                        return tier
                return 'Tier 5 - Cobertura Muy Limitada'
            
            # Presets rápidos
            st.markdown("###### Presets Rápidos")
            cols = st.columns(10)
            preset_buttons = [
                ("🇺🇸 USA", ["United States", "US OTC"]),
                ("🌍 Ex-USA", "exclude_usa"),
                ("G7", ["United States", "Japan", "Germany", "United Kingdom", "France", "Italy", "Canada"]),
                ("BRICS", ["China", "India", "Brazil", "Russia", "South Africa"]),
                ("EU", ["Germany", "France", "Netherlands", "Spain", "Italy", "Belgium", "Ireland"]),
                ("Asia", ["Japan", "China", "Hong Kong", "Singapore", "South Korea", "India", "Taiwan"]),
                ("LatAm", ["Brazil", "Mexico", "Argentina", "Chile", "Colombia", "Peru"]),
                ("MENA", ["Saudi Arabia", "United Arab Emirates", "Israel", "Turkey", "Egypt"]),
                ("Emergentes", ["China", "India", "Brazil", "Mexico", "Indonesia", "Turkey", "Thailand"]),
                ("Limpiar", "clear")
            ]
            
            for i, (label, countries) in enumerate(preset_buttons):
                with cols[i]:
                    if st.button(label, use_container_width=True, key=f"preset_{i}"):
                        if countries == "exclude_usa":
                            st.session_state.exclude_countries = ["United States", "US OTC"]
                            st.session_state.countries_filter = []
                        elif countries == "clear":
                            st.session_state.countries_filter = []
                            st.session_state.exclude_countries = []
                        else:
                            st.session_state.countries_filter = countries
                            st.session_state.exclude_countries = []
                        mark_filters_as_modified()
                        countries_filter = st.session_state.countries_filter
                        exclude_countries = st.session_state.exclude_countries
            
            # Modo de filtro
            filter_mode = st.radio(
                "Modo de Filtro",
                ["Incluir Países", "Excluir Países"],
                horizontal=True,
                key="country_filter_mode",
                on_change=mark_filters_as_modified,
                help="Elige incluir o excluir países específicos"
            )
            
            # Multiselect de países con indicador de calidad de datos
            if filter_mode == "Incluir Países":
                # Create formatted options with data quality indicators
                country_options = []
                for country in country_counts.index:
                    tier = get_country_tier(country)
                    if 'Tier 1' in tier:
                        emoji = "🟢"
                    elif 'Tier 2' in tier:
                        emoji = "🟡"
                    elif 'Tier 3' in tier:
                        emoji = "🟠"
                    elif 'Tier 4' in tier:
                        emoji = "🔴"
                    else:
                        emoji = "⚫"
                    country_options.append(country)
                
                countries_filter = st.multiselect(
                    "Seleccionar países a incluir:",
                    options=country_options,
                    default=countries_filter,
                    format_func=lambda x: f"{x} ({country_counts[x]:,} acciones) {['🟢' if 'Tier 1' in get_country_tier(x) else '🟡' if 'Tier 2' in get_country_tier(x) else '🟠' if 'Tier 3' in get_country_tier(x) else '🔴' if 'Tier 4' in get_country_tier(x) else '⚫'][0]}",
                    key="countries_include",
                    on_change=mark_filters_as_modified,
                    help="🟢 Excelente | 🟡 Buena | 🟠 Moderada | 🔴 Básica | ⚫ Muy Limitada"
                )
                st.session_state.countries_filter = countries_filter
            else:
                exclude_countries = st.multiselect(
                    "Seleccionar países a excluir:",
                    options=country_counts.index.tolist(),
                    default=exclude_countries,
                    format_func=lambda x: f"{x} ({country_counts[x]:,} acciones) {['🟢' if 'Tier 1' in get_country_tier(x) else '🟡' if 'Tier 2' in get_country_tier(x) else '🟠' if 'Tier 3' in get_country_tier(x) else '🔴' if 'Tier 4' in get_country_tier(x) else '⚫'][0]}",
                    key="countries_exclude",
                    on_change=mark_filters_as_modified,
                    help="🟢 Excelente | 🟡 Buena | 🟠 Moderada | 🔴 Básica | ⚫ Muy Limitada"
                )
                st.session_state.exclude_countries = exclude_countries
            
            # DATA COVERAGE ANALYSIS SECTION
            if countries_filter or exclude_countries:
                st.markdown("---")
                st.markdown("##### 📊 Análisis de Cobertura de Datos")
                
                # Get the dataframe for selected countries
                if filter_mode == "Incluir Países" and countries_filter:
                    selected_countries_df = df[df['Country'].isin(countries_filter)]
                    selected_countries_list = countries_filter
                elif filter_mode == "Excluir Países" and exclude_countries:
                    selected_countries_df = df[~df['Country'].isin(exclude_countries)]
                    selected_countries_list = [c for c in df['Country'].unique() if c not in exclude_countries]
                else:
                    selected_countries_df = df
                    selected_countries_list = list(df['Country'].unique())
                
                # Calculate detailed coverage metrics
                coverage_categories = {
                    '📊 Valoración Fundamental': ['PE Ratio', 'PB Ratio', 'PS Ratio', 'PEG Ratio', 'EV/EBITDA'],
                    '📈 Crecimiento': ['Rev. Growth', 'EPS Growth', 'Rev Gr. Next Y', 'EPS Gr. Next Y'],
                    '💎 Rentabilidad': ['ROE', 'ROA', 'ROIC', 'Profit Margin', 'Gross Margin'],
                    '🏥 Salud Financiera': ['Current Ratio', 'Debt / Equity', 'Z-Score', 'FCF'],
                    '💵 Dividendos': ['Div. Yield', 'Payout Ratio', 'Years', 'Div. Growth'],
                    '📉 Técnico': ['RSI', 'Beta (5Y)', 'Return 1Y', 'Rel. Volume'],
                    '🎯 Estimaciones Analistas': ['Forward PE', 'Analysts', 'PT Upside', 'Rating']
                }
                
                coverage_scores = {}
                missing_categories = []
                
                for category, metrics in coverage_categories.items():
                    available_count = 0
                    total_data_points = 0
                    
                    for metric in metrics:
                        if metric in selected_countries_df.columns:
                            non_null = selected_countries_df[metric].notna().sum()
                            total_data_points += non_null
                            if non_null > len(selected_countries_df) * 0.1:  # At least 10% coverage
                                available_count += 1
                    
                    if len(metrics) > 0:
                        coverage_pct = (available_count / len(metrics)) * 100
                        coverage_scores[category] = coverage_pct
                        if coverage_pct < 20:
                            missing_categories.append(category)
                
                # Calculate overall coverage
                avg_coverage = sum(coverage_scores.values()) / len(coverage_scores) if coverage_scores else 0
                
                # Determine tier distribution of selected countries
                tier_distribution = {}
                for country in selected_countries_list[:20]:  # Limit to first 20 for performance
                    tier = get_country_tier(country)
                    tier_name = tier.split(' - ')[0]
                    tier_distribution[tier_name] = tier_distribution.get(tier_name, 0) + 1
                
                # Display coverage alert based on average coverage
                if avg_coverage < 30:
                    st.error("""
                    ⚠️ **COBERTURA DE DATOS MUY LIMITADA**
                    
                    Los países seleccionados tienen datos muy escasos. **Recomendaciones críticas:**
                    - ✅ **USA SOLO ESTOS FILTROS:** Capitalización de mercado, Sector, País, Retornos básicos
                    - ❌ **EVITA:** Estimaciones de analistas, ratios complejos, métricas de crecimiento futuro
                    - 💡 **ALTERNATIVA:** Considera agregar países con mejor cobertura (USA, UK, Alemania, Japón)
                    """)
                elif avg_coverage < 60:
                    st.warning("""
                    ⚠️ **COBERTURA DE DATOS PARCIAL**
                    
                    Los países seleccionados tienen cobertura moderada. **Sugerencias:**
                    - ✅ **FILTROS RECOMENDADOS:** P/E, P/B, ROE, Capitalización, Crecimiento histórico
                    - ⚠️ **USO LIMITADO:** Estimaciones futuras, datos de analistas, métricas avanzadas
                    - 💡 **TIP:** Los filtros de dividendos y técnicos pueden tener datos incompletos
                    """)
                else:
                    st.success("""
                    ✅ **BUENA COBERTURA DE DATOS**
                    
                    Los países seleccionados tienen datos suficientes para la mayoría de análisis.
                    Puedes usar la mayoría de filtros con confianza.
                    """)
                
                # Show detailed coverage breakdown
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Coverage by category bars
                    st.markdown("**Cobertura por Categoría de Métricas:**")
                    
                    for category, score in coverage_scores.items():
                        # Determine color based on coverage
                        if score >= 80:
                            color = '#10b981'
                            status = 'Excelente'
                        elif score >= 60:
                            color = '#3b82f6'
                            status = 'Buena'
                        elif score >= 40:
                            color = '#f59e0b'
                            status = 'Limitada'
                        elif score >= 20:
                            color = '#ef4444'
                            status = 'Muy Limitada'
                        else:
                            color = '#991b1b'
                            status = 'Sin Datos'
                        
                        st.markdown(f"""
                        <div style="margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="color: #c9d1d9; font-size: 13px;">{category}</span>
                                <span style="color: {color}; font-size: 13px; font-weight: 600;">{score:.0f}% - {status}</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 20px; position: relative; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, {color}, {color}CC); 
                                        height: 100%; width: {score}%; border-radius: 10px; 
                                        transition: width 0.3s ease;">
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    # Summary metrics
                    st.markdown("**Resumen:**")
                    st.metric("Cobertura Global", f"{avg_coverage:.0f}%", 
                            delta=f"{avg_coverage-50:.0f}%" if avg_coverage != 50 else None)
                    
                    # Tier distribution
                    if tier_distribution:
                        st.markdown("**Calidad de Países:**")
                        for tier, count in sorted(tier_distribution.items()):
                            tier_emoji = {'Tier 1': '🟢', 'Tier 2': '🟡', 'Tier 3': '🟠', 
                                        'Tier 4': '🔴', 'Tier 5': '⚫'}.get(tier, '⚫')
                            st.markdown(f"{tier_emoji} {tier}: {count}")
                
                # Specific recommendations based on selection
                if missing_categories:
                    with st.expander("⚠️ Ver Filtros No Recomendados", expanded=False):
                        st.markdown("**Estas categorías tienen datos insuficientes para los países seleccionados:**")
                        for cat in missing_categories:
                            st.markdown(f"- {cat}")
                        st.markdown("\n**Recomendación:** Evita usar filtros de estas categorías o pueden no dar resultados.")
                
                # Smart filter suggestions
                if avg_coverage < 60:
                    with st.expander("💡 Filtros Optimizados para tus Países", expanded=True):
                        st.markdown("**Basado en la cobertura de datos, te sugerimos usar estos filtros:**")
                        
                        if avg_coverage >= 40:
                            st.markdown("""
                            ✅ **Filtros Recomendados:**
                            - Capitalización de Mercado (min/max)
                            - P/E Ratio (si aparece en cobertura > 40%)
                            - P/B Ratio
                            - ROE básico
                            - Retorno 1 Año
                            - Sector e Industria
                            """)
                        else:
                            st.markdown("""
                            ✅ **Filtros Básicos Solamente:**
                            - Capitalización de Mercado
                            - Sector
                            - Retornos (1M, 3M, 1Y)
                            - Volumen
                            
                            ❌ **Evitar completamente:**
                            - Estimaciones de analistas
                            - Métricas de crecimiento futuro
                            - Scores complejos
                            - Ratios avanzados
                            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # TAB 3: VALORACIÓN
    # =========================================================================
    with filter_tabs[2]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Métricas de Valoración</div>', unsafe_allow_html=True)
        
        # DATA COVERAGE CHECK FOR VALUATION METRICS
        disable_filters = {}
        show_limited_warning = False
        available_valuation_metrics = []
        
        if 'countries_filter' in st.session_state and st.session_state.countries_filter:
            # Get data for selected countries
            selected_df = df[df['Country'].isin(st.session_state.countries_filter)]
            
            # Check each valuation metric
            valuation_metrics = {
                'PE Ratio': 'P/E',
                'Forward PE': 'P/E Futuro',
                'PB Ratio': 'P/B',
                'PS Ratio': 'P/S',
                'Forward PS': 'P/S Futuro',
                'PEG Ratio': 'PEG',
                'P/FCF': 'P/FCF',
                'P/OCF': 'P/OCF',
                'P/EBITDA': 'P/EBITDA',
                'P/TBV': 'P/TBV',
                'P/FFO': 'P/FFO',
                'EV/Sales': 'EV/Sales',
                'EV/EBITDA': 'EV/EBITDA',
                'EV/EBIT': 'EV/EBIT',
                'EV/FCF': 'EV/FCF',
                'FCF Yield': 'FCF Yield',
                'Earnings Yield': 'Earnings Yield',
                'Graham (%)': 'Graham',
                'Lynch (%)': 'Lynch'
            }
            
            for metric, display_name in valuation_metrics.items():
                if metric in selected_df.columns:
                    coverage = (selected_df[metric].notna().sum() / len(selected_df)) * 100
                    if coverage >= 10:
                        available_valuation_metrics.append((metric, display_name, coverage))
                    else:
                        disable_filters[metric] = True
                else:
                    disable_filters[metric] = True
            
            # Determine warning level
            if len(available_valuation_metrics) < 4:
                show_limited_warning = True
        
        # SHOW WARNING IF DATA IS LIMITED
        if show_limited_warning:
            st.error(f"""
            ⚠️ **Datos de valoración muy limitados para los países seleccionados**
            
            Solo {len(available_valuation_metrics)} métricas de valoración tienen datos suficientes.
            **Métricas disponibles:** {', '.join([m[1] for m in available_valuation_metrics[:5]])}
            
            **Recomendación:** Usa filtros más básicos o cambia la selección de países.
            """)
        elif len(available_valuation_metrics) < 10 and len(available_valuation_metrics) > 0:
            st.warning(f"""
            ⚠️ **Cobertura parcial de datos de valoración**
            
            {len(available_valuation_metrics)} de 19 métricas disponibles.
            Algunos filtros pueden no tener datos completos.
            """)
        
        # SHOW AVAILABLE METRICS IF LIMITED
        if available_valuation_metrics and len(available_valuation_metrics) < 15:
            with st.expander("📊 Ver métricas disponibles y cobertura", expanded=False):
                for metric, display_name, coverage in sorted(available_valuation_metrics, key=lambda x: x[2], reverse=True):
                    color = '#10b981' if coverage >= 70 else '#f59e0b' if coverage >= 40 else '#ef4444'
                    st.markdown(f"""
                    <div style="margin-bottom: 8px;">
                        <span style="color: {color};">●</span> 
                        <span style="color: #c9d1d9;">{display_name}:</span> 
                        <span style="color: {color}; font-weight: 600;">{coverage:.0f}% cobertura</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("###### Ratios Precio")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pe_disabled = disable_filters.get('PE Ratio', False)
            if pe_disabled:
                st.markdown("🔴 **P/E - Sin datos**")
                pe_min = st.number_input("P/E Mín", value=0.0, key="pe_min", disabled=True, 
                                        help="Sin datos disponibles para los países seleccionados")
                pe_max = st.number_input("P/E Máx", value=100.0, key="pe_max", disabled=True,
                                        help="Sin datos disponibles para los países seleccionados")
            else:
                pe_min = st.number_input("P/E Mín", value=preset_filters.get('pe_min', 0.0), 
                                        key="pe_min", on_change=mark_filters_as_modified,
                                        help=METRIC_DESCRIPTIONS.get("pe_ratio", "Precio/Beneficios"))
                pe_max = st.number_input("P/E Máx", value=preset_filters.get('pe_max', 100.0), 
                                        key="pe_max", on_change=mark_filters_as_modified,
                                        help=METRIC_DESCRIPTIONS.get("pe_ratio", "Precio/Beneficios"))
        
        with col2:
            fpe_disabled = disable_filters.get('Forward PE', False)
            if fpe_disabled:
                st.markdown("🔴 **P/E Futuro - Sin datos**")
                forward_pe_min = st.number_input("P/E Futuro Mín", value=0.0, key="fpe_min", disabled=True)
                forward_pe_max = st.number_input("P/E Futuro Máx", value=100.0, key="fpe_max", disabled=True)
            else:
                forward_pe_min = st.number_input("P/E Futuro Mín", value=preset_filters.get('forward_pe_min', 0.0), 
                                                key="fpe_min", on_change=mark_filters_as_modified,
                                                help=METRIC_DESCRIPTIONS.get("forward_pe", "P/E basado en estimaciones"))
                forward_pe_max = st.number_input("P/E Futuro Máx", value=preset_filters.get('forward_pe_max', 100.0), 
                                                key="fpe_max", on_change=mark_filters_as_modified)
        
        with col3:
            pb_disabled = disable_filters.get('PB Ratio', False)
            if pb_disabled:
                st.markdown("🔴 **P/B - Sin datos**")
                pb_min = st.number_input("P/B Mín", value=0.0, key="pb_min", disabled=True)
                pb_max = st.number_input("P/B Máx", value=10.0, key="pb_max", disabled=True)
            else:
                pb_min = st.number_input("P/B Mín", value=preset_filters.get('pb_min', 0.0), 
                                        key="pb_min", on_change=mark_filters_as_modified,
                                        help=METRIC_DESCRIPTIONS.get("pb_ratio", "Precio/Valor Libro"))
                pb_max = st.number_input("P/B Máx", value=preset_filters.get('pb_max', 10.0), 
                                        key="pb_max", on_change=mark_filters_as_modified)
        
        with col4:
            ps_disabled = disable_filters.get('PS Ratio', False)
            if ps_disabled:
                st.markdown("🔴 **P/S - Sin datos**")
                ps_min = st.number_input("P/S Mín", value=0.0, key="ps_min", disabled=True)
                ps_max = st.number_input("P/S Máx", value=20.0, key="ps_max", disabled=True)
            else:
                ps_min = st.number_input("P/S Mín", value=preset_filters.get('ps_min', 0.0), 
                                        key="ps_min", on_change=mark_filters_as_modified,
                                        help=METRIC_DESCRIPTIONS.get("ps_ratio", "Precio/Ventas"))
                ps_max = st.number_input("P/S Máx", value=preset_filters.get('ps_max', 20.0), 
                                        key="ps_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Más Ratios Precio")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fps_disabled = disable_filters.get('Forward PS', False)
            if fps_disabled:
                st.markdown("🟠 **P/S Futuro - Limitado**")
            forward_ps_min = st.number_input("P/S Futuro Mín", value=preset_filters.get('forward_ps_min', 0.0), 
                                            key="fps_min", on_change=mark_filters_as_modified,
                                            disabled=fps_disabled)
            forward_ps_max = st.number_input("P/S Futuro Máx", value=preset_filters.get('forward_ps_max', 20.0), 
                                            key="fps_max", on_change=mark_filters_as_modified,
                                            disabled=fps_disabled)
        
        with col2:
            peg_disabled = disable_filters.get('PEG Ratio', False)
            if peg_disabled:
                st.markdown("🟠 **PEG - Limitado**")
            peg_min = st.number_input("PEG Mín", value=preset_filters.get('peg_min', 0.0), 
                                    key="peg_min", on_change=mark_filters_as_modified,
                                    disabled=peg_disabled,
                                    help="PEG = P/E / Crecimiento" if not peg_disabled else "Sin datos")
            peg_max = st.number_input("PEG Máx", value=preset_filters.get('peg_max', 5.0), 
                                    key="peg_max", on_change=mark_filters_as_modified,
                                    disabled=peg_disabled)
        
        with col3:
            pfcf_disabled = disable_filters.get('P/FCF', False)
            p_fcf_min = st.number_input("P/FCF Mín", value=preset_filters.get('p_fcf_min', 0.0), 
                                    key="p_fcf_min", on_change=mark_filters_as_modified,
                                    disabled=pfcf_disabled)
            p_fcf_max = st.number_input("P/FCF Máx", value=preset_filters.get('p_fcf_max', 100.0), 
                                    key="p_fcf_max", on_change=mark_filters_as_modified,
                                    disabled=pfcf_disabled)
        
        with col4:
            pocf_disabled = disable_filters.get('P/OCF', False)
            p_ocf_min = st.number_input("P/OCF Mín", value=preset_filters.get('p_ocf_min', 0.0), 
                                    key="p_ocf_min", on_change=mark_filters_as_modified,
                                    disabled=pocf_disabled)
            p_ocf_max = st.number_input("P/OCF Máx", value=preset_filters.get('p_ocf_max', 100.0), 
                                    key="p_ocf_max", on_change=mark_filters_as_modified,
                                    disabled=pocf_disabled)
        
        st.markdown("###### Ratios Adicionales")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            p_ebitda_min = st.number_input("P/EBITDA Mín", value=preset_filters.get('p_ebitda_min', 0.0), 
                                        key="p_ebitda_min", on_change=mark_filters_as_modified,
                                        disabled=disable_filters.get('P/EBITDA', False))
            p_ebitda_max = st.number_input("P/EBITDA Máx", value=preset_filters.get('p_ebitda_max', 50.0), 
                                        key="p_ebitda_max", on_change=mark_filters_as_modified,
                                        disabled=disable_filters.get('P/EBITDA', False))
        
        with col2:
            p_tbv_min = st.number_input("P/TBV Mín", value=preset_filters.get('p_tbv_min', 0.0), 
                                    key="p_tbv_min", on_change=mark_filters_as_modified,
                                    disabled=disable_filters.get('P/TBV', False))
            p_tbv_max = st.number_input("P/TBV Máx", value=preset_filters.get('p_tbv_max', 10.0), 
                                    key="p_tbv_max", on_change=mark_filters_as_modified,
                                    disabled=disable_filters.get('P/TBV', False))
        
        with col3:
            p_ffo_min = st.number_input("P/FFO Mín", value=preset_filters.get('p_ffo_min', 0.0), 
                                    key="p_ffo_min", on_change=mark_filters_as_modified,
                                    disabled=disable_filters.get('P/FFO', False))
            p_ffo_max = st.number_input("P/FFO Máx", value=preset_filters.get('p_ffo_max', 50.0), 
                                    key="p_ffo_max", on_change=mark_filters_as_modified,
                                    disabled=disable_filters.get('P/FFO', False))
        with col4:
            st.markdown("")
        
        # ENTERPRISE VALUE SECTION WITH WARNINGS
        st.markdown("###### Ratios Enterprise Value")
        
        ev_metrics = ['EV/Sales', 'EV/EBITDA', 'EV/EBIT', 'EV/FCF']
        ev_coverage = sum(1 for m in ev_metrics if not disable_filters.get(m, False))
        
        if ev_coverage < 2:
            st.info("ℹ️ Métricas EV tienen cobertura muy limitada para los países seleccionados")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ev_sales_disabled = disable_filters.get('EV/Sales', False)
            ev_sales_min = st.number_input("EV/Sales Mín", value=preset_filters.get('ev_sales_min', 0.0), 
                                        key="ev_s_min", on_change=mark_filters_as_modified,
                                        disabled=ev_sales_disabled)
            ev_sales_max = st.number_input("EV/Sales Máx", value=preset_filters.get('ev_sales_max', 20.0), 
                                        key="ev_s_max", on_change=mark_filters_as_modified,
                                        disabled=ev_sales_disabled)
        
        with col2:
            fwd_ev_s_min = st.number_input("EV/Sales Fut Mín", value=preset_filters.get('fwd_ev_s_min', 0.0), 
                                        key="fwd_ev_s_min", on_change=mark_filters_as_modified,
                                        disabled=disable_filters.get('Fwd EV/Sales', False))
            fwd_ev_s_max = st.number_input("EV/Sales Fut Máx", value=preset_filters.get('fwd_ev_s_max', 20.0), 
                                        key="fwd_ev_s_max", on_change=mark_filters_as_modified,
                                        disabled=disable_filters.get('Fwd EV/Sales', False))
        
        with col3:
            ev_earnings_min = st.number_input("EV/Earnings Mín", value=preset_filters.get('ev_earnings_min', 0.0), 
                                            key="ev_earn_min", on_change=mark_filters_as_modified,
                                            disabled=disable_filters.get('EV/Earnings', False))
            ev_earnings_max = st.number_input("EV/Earnings Máx", value=preset_filters.get('ev_earnings_max', 100.0), 
                                            key="ev_earn_max", on_change=mark_filters_as_modified,
                                            disabled=disable_filters.get('EV/Earnings', False))
        
        with col4:
            ev_ebitda_disabled = disable_filters.get('EV/EBITDA', False)
            ev_ebitda_min = st.number_input("EV/EBITDA Mín", value=preset_filters.get('ev_ebitda_min', 0.0), 
                                        key="ev_eb_min", on_change=mark_filters_as_modified,
                                        disabled=ev_ebitda_disabled)
            ev_ebitda_max = st.number_input("EV/EBITDA Máx", value=preset_filters.get('ev_ebitda_max', 50.0), 
                                        key="ev_eb_max", on_change=mark_filters_as_modified,
                                        disabled=ev_ebitda_disabled)
        
        st.markdown("###### Más EV Ratios")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ev_ebit_min = st.number_input("EV/EBIT Mín", value=preset_filters.get('ev_ebit_min', 0.0), 
                                        key="ev_ebit_min", on_change=mark_filters_as_modified,
                                        disabled=disable_filters.get('EV/EBIT', False))
            ev_ebit_max = st.number_input("EV/EBIT Máx", value=preset_filters.get('ev_ebit_max', 50.0), 
                                        key="ev_ebit_max", on_change=mark_filters_as_modified,
                                        disabled=disable_filters.get('EV/EBIT', False))
        
        with col2:
            ev_fcf_min = st.number_input("EV/FCF Mín", value=preset_filters.get('ev_fcf_min', 0.0), 
                                        key="ev_fcf_min", on_change=mark_filters_as_modified,
                                        disabled=disable_filters.get('EV/FCF', False))
            ev_fcf_max = st.number_input("EV/FCF Máx", value=preset_filters.get('ev_fcf_max', 100.0), 
                                        key="ev_fcf_max", on_change=mark_filters_as_modified,
                                        disabled=disable_filters.get('EV/FCF', False))
        with col3:
            st.markdown("")
        with col4:
            st.markdown("")
        
        # YIELDS AND FAIR VALUE SECTION
        st.markdown("###### Yields y Fair Value")
        
        yields_available = not all(disable_filters.get(m, False) for m in ['FCF Yield', 'Earnings Yield'])
        if not yields_available:
            st.warning("⚠️ Yields no disponibles para los países seleccionados. Considera usar ratios P/E y P/B en su lugar.")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fcf_yield_disabled = disable_filters.get('FCF Yield', False)
            if fcf_yield_disabled:
                st.markdown("🔴 **FCF Yield - Sin datos**")
            fcf_yield_min = st.number_input("FCF Yield Mín %", value=preset_filters.get('fcf_yield_min', 0.0), 
                                        key="fcf_y_min", on_change=mark_filters_as_modified,
                                        disabled=fcf_yield_disabled,
                                        help="Flujo de caja libre / Capitalización" if not fcf_yield_disabled else "No disponible")
            
            earnings_yield_disabled = disable_filters.get('Earnings Yield', False)
            earnings_yield_min = st.number_input("Earnings Yield Mín %", value=preset_filters.get('earnings_yield_min', 0.0), 
                                                key="earn_y_min", on_change=mark_filters_as_modified,
                                                disabled=earnings_yield_disabled)
        
        with col2:
            fcf_ev_min = st.number_input("FCF/EV Mín %", value=preset_filters.get('fcf_ev_min', 0.0), 
                                        key="fcf_ev_min", on_change=mark_filters_as_modified,
                                        disabled=disable_filters.get('FCF/EV', False))
        
        with col3:
            graham_disabled = disable_filters.get('Graham (%)', False)
            if graham_disabled:
                st.markdown("🟠 **Graham - Limitado**")
            graham_upside_min = st.number_input("Graham Upside Mín %", value=preset_filters.get('graham_upside_min', -100.0), 
                                            key="graham_up", on_change=mark_filters_as_modified,
                                            disabled=graham_disabled)
        
        with col4:
            lynch_disabled = disable_filters.get('Lynch (%)', False)
            if lynch_disabled:
                st.markdown("🟠 **Lynch - Limitado**")
            lynch_upside_min = st.number_input("Lynch Upside Mín %", value=preset_filters.get('lynch_upside_min', -100.0), 
                                            key="lynch_up", on_change=mark_filters_as_modified,
                                            disabled=lynch_disabled)
        
        # SUMMARY OF DATA AVAILABILITY
        if show_limited_warning or (available_valuation_metrics and len(available_valuation_metrics) < 10):
            st.markdown("---")
            st.markdown("##### 💡 Alternativas Recomendadas")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **Si los datos son limitados, prueba:**
                - 📊 Capitalización de Mercado (siempre disponible)
                - 📈 Retornos históricos (1M, 3M, 1Y)
                - 🏢 Filtros por Sector
                - 📉 Volumen de trading
                """)
            
            with col2:
                st.markdown("""
                **Países con mejor cobertura:**
                - 🇺🇸 Estados Unidos
                - 🇬🇧 Reino Unido
                - 🇩🇪 Alemania
                - 🇯🇵 Japón
                """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # =========================================================================
    # TAB 4: CRECIMIENTO
    # =========================================================================
    with filter_tabs[3]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📈 Métricas de Crecimiento</div>', unsafe_allow_html=True)
        
        st.markdown("###### Crecimiento de Ingresos")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            rev_growth_min = st.number_input("Crec. Ingresos TTM Mín %", value=preset_filters.get('rev_growth_min', -100.0), key="rev_g_min", on_change=mark_filters_as_modified)
            rev_growth_max = st.number_input("Crec. Ingresos TTM Máx %", value=preset_filters.get('rev_growth_max', 500.0), key="rev_g_max", on_change=mark_filters_as_modified)
        with col2:
            rev_growth_q_min = st.number_input("Crec. Ingresos Q Mín %", value=preset_filters.get('rev_growth_q_min', -100.0), key="rev_gq_min", on_change=mark_filters_as_modified)
            rev_growth_q_max = st.number_input("Crec. Ingresos Q Máx %", value=preset_filters.get('rev_growth_q_max', 500.0), key="rev_gq_max", on_change=mark_filters_as_modified)
        with col3:
            rev_growth_3y_min = st.number_input("CAGR Ingresos 3A Mín %", value=preset_filters.get('rev_growth_3y_min', -100.0), key="rev_3y", on_change=mark_filters_as_modified)
            rev_growth_5y_min = st.number_input("CAGR Ingresos 5A Mín %", value=preset_filters.get('rev_growth_5y_min', -100.0), key="rev_5y", on_change=mark_filters_as_modified)
        with col4:
            rev_gr_this_q_min = st.number_input("Crec. Este Q Mín %", value=preset_filters.get('rev_gr_this_q_min', -100.0), key="rev_tq", on_change=mark_filters_as_modified)
            rev_gr_next_q_min = st.number_input("Crec. Próx Q Mín %", value=preset_filters.get('rev_gr_next_q_min', -100.0), key="rev_nq", on_change=mark_filters_as_modified)
        
        st.markdown("###### Crecimiento de Beneficios")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            eps_growth_min = st.number_input("Crec. BPA TTM Mín %", value=preset_filters.get('eps_growth_min', -100.0), key="eps_g_min", on_change=mark_filters_as_modified)
            eps_growth_max = st.number_input("Crec. BPA TTM Máx %", value=preset_filters.get('eps_growth_max', 500.0), key="eps_g_max", on_change=mark_filters_as_modified)
        with col2:
            eps_growth_q_min = st.number_input("Crec. BPA Q Mín %", value=preset_filters.get('eps_growth_q_min', -100.0), key="eps_gq_min", on_change=mark_filters_as_modified)
            eps_growth_q_max = st.number_input("Crec. BPA Q Máx %", value=preset_filters.get('eps_growth_q_max', 500.0), key="eps_gq_max", on_change=mark_filters_as_modified)
        with col3:
            eps_growth_3y_min = st.number_input("CAGR BPA 3A Mín %", value=preset_filters.get('eps_growth_3y_min', -100.0), key="eps_3y", on_change=mark_filters_as_modified)
            eps_growth_5y_min = st.number_input("CAGR BPA 5A Mín %", value=preset_filters.get('eps_growth_5y_min', -100.0), key="eps_5y", on_change=mark_filters_as_modified)
        with col4:
            eps_gr_this_q_min = st.number_input("BPA Este Q Mín %", value=preset_filters.get('eps_gr_this_q_min', -100.0), key="eps_tq", on_change=mark_filters_as_modified)
            eps_gr_next_q_min = st.number_input("BPA Próx Q Mín %", value=preset_filters.get('eps_gr_next_q_min', -100.0), key="eps_nq", on_change=mark_filters_as_modified)
        
        st.markdown("###### Estimaciones Futuras")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            rev_gr_this_y_min = st.number_input("Crec. Ing Este Año Mín %", value=preset_filters.get('rev_gr_this_y_min', -100.0), key="rev_ty", on_change=mark_filters_as_modified)
            rev_gr_next_y_min = st.number_input("Crec. Ing Próx Año Mín %", value=preset_filters.get('rev_gr_next_y_min', -100.0), key="rev_ny", on_change=mark_filters_as_modified)
        with col2:
            rev_gr_next_5y_min = st.number_input("CAGR Ing Próx 5A Mín %", value=preset_filters.get('rev_gr_next_5y_min', -100.0), key="rev_n5y", on_change=mark_filters_as_modified)
            eps_gr_this_y_min = st.number_input("BPA Este Año Mín %", value=preset_filters.get('eps_gr_this_y_min', -100.0), key="eps_ty", on_change=mark_filters_as_modified)
        with col3:
            eps_gr_next_y_min = st.number_input("BPA Próx Año Mín %", value=preset_filters.get('eps_gr_next_y_min', -100.0), key="eps_ny", on_change=mark_filters_as_modified)
            eps_gr_next_5y_min = st.number_input("CAGR BPA Próx 5A Mín %", value=preset_filters.get('eps_gr_next_5y_min', -100.0), key="eps_n5y", on_change=mark_filters_as_modified)
        with col4:
            fcf_growth_min = st.number_input("Crec. FCF Mín %", value=preset_filters.get('fcf_growth_min', -100.0), key="fcf_g", on_change=mark_filters_as_modified)
            fcf_growth_3y_min = st.number_input("CAGR FCF 3A Mín %", value=preset_filters.get('fcf_growth_3y_min', -100.0), key="fcf_3y", on_change=mark_filters_as_modified)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # TAB 5: RENTABILIDAD
    # =========================================================================
    with filter_tabs[4]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">💎 Rentabilidad y Calidad</div>', unsafe_allow_html=True)
        
        st.markdown("###### Retornos sobre Capital")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            roe_min = st.number_input("ROE Mín %", value=preset_filters.get('roe_min', -100.0), key="roe_min", on_change=mark_filters_as_modified)
            roe_max = st.number_input("ROE Máx %", value=preset_filters.get('roe_max', 200.0), key="roe_max", on_change=mark_filters_as_modified)
        with col2:
            roa_min = st.number_input("ROA Mín %", value=preset_filters.get('roa_min', -100.0), key="roa_min", on_change=mark_filters_as_modified)
            roa_max = st.number_input("ROA Máx %", value=preset_filters.get('roa_max', 100.0), key="roa_max", on_change=mark_filters_as_modified)
        with col3:
            roic_min = st.number_input("ROIC Mín %", value=preset_filters.get('roic_min', -100.0), key="roic_min", on_change=mark_filters_as_modified)
            roic_max = st.number_input("ROIC Máx %", value=preset_filters.get('roic_max', 200.0), key="roic_max", on_change=mark_filters_as_modified)
        with col4:
            roce_min = st.number_input("ROCE Mín %", value=preset_filters.get('roce_min', -100.0), key="roce_min", on_change=mark_filters_as_modified)
            roce_max = st.number_input("ROCE Máx %", value=preset_filters.get('roce_max', 200.0), key="roce_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Márgenes Principales")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            gross_margin_min = st.number_input("Margen Bruto Mín %", value=preset_filters.get('gross_margin_min', 0.0), key="gross_m", on_change=mark_filters_as_modified)
            gross_margin_max = st.number_input("Margen Bruto Máx %", value=preset_filters.get('gross_margin_max', 100.0), key="gross_m_max", on_change=mark_filters_as_modified)
        with col2:
            operating_margin_min = st.number_input("Margen Op. Mín %", value=preset_filters.get('operating_margin_min', -100.0), key="op_m", on_change=mark_filters_as_modified)
            operating_margin_max = st.number_input("Margen Op. Máx %", value=preset_filters.get('operating_margin_max', 100.0), key="op_m_max", on_change=mark_filters_as_modified)
        with col3:
            pretax_margin_min = st.number_input("Margen PreTax Mín %", value=preset_filters.get('pretax_margin_min', -100.0), key="pretax_m", on_change=mark_filters_as_modified)
            pretax_margin_max = st.number_input("Margen PreTax Máx %", value=preset_filters.get('pretax_margin_max', 100.0), key="pretax_m_max", on_change=mark_filters_as_modified)
        with col4:
            profit_margin_min = st.number_input("Margen Neto Mín %", value=preset_filters.get('profit_margin_min', -100.0), key="prof_m", on_change=mark_filters_as_modified)
            profit_margin_max = st.number_input("Margen Neto Máx %", value=preset_filters.get('profit_margin_max', 100.0), key="prof_m_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Márgenes Adicionales")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fcf_margin_min = st.number_input("Margen FCF Mín %", value=preset_filters.get('fcf_margin_min', -100.0), key="fcf_m", on_change=mark_filters_as_modified)
            fcf_margin_max = st.number_input("Margen FCF Máx %", value=preset_filters.get('fcf_margin_max', 100.0), key="fcf_m_max", on_change=mark_filters_as_modified)
        with col2:
            ebitda_margin_min = st.number_input("Margen EBITDA Mín %", value=preset_filters.get('ebitda_margin_min', -100.0), key="ebitda_m", on_change=mark_filters_as_modified)
            ebitda_margin_max = st.number_input("Margen EBITDA Máx %", value=preset_filters.get('ebitda_margin_max', 100.0), key="ebitda_m_max", on_change=mark_filters_as_modified)
        with col3:
            ebit_margin_min = st.number_input("Margen EBIT Mín %", value=preset_filters.get('ebit_margin_min', -100.0), key="ebit_m", on_change=mark_filters_as_modified)
            ebit_margin_max = st.number_input("Margen EBIT Máx %", value=preset_filters.get('ebit_margin_max', 100.0), key="ebit_m_max", on_change=mark_filters_as_modified)
        with col4:
            st.markdown("")
        
        st.markdown("###### Promedios Históricos")
        col1, col2, col3 = st.columns(3)
        with col1:
            roe_5y_min = st.number_input("ROE (5A) Mín %", value=preset_filters.get('roe_5y_min', -100.0), key="roe_5y", on_change=mark_filters_as_modified)
        with col2:
            roa_5y_min = st.number_input("ROA (5A) Mín %", value=preset_filters.get('roa_5y_min', -100.0), key="roa_5y", on_change=mark_filters_as_modified)
        with col3:
            roic_5y_min = st.number_input("ROIC (5A) Mín %", value=preset_filters.get('roic_5y_min', -100.0), key="roic_5y", on_change=mark_filters_as_modified)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # TAB 6: SALUD FINANCIERA
    # =========================================================================
    with filter_tabs[5]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🏥 Salud Financiera y Seguridad</div>', unsafe_allow_html=True)
        
        st.markdown("###### Liquidez")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            current_ratio_min = st.number_input("Ratio Corriente Mín", value=preset_filters.get('current_ratio_min', 0.0), key="curr_r", on_change=mark_filters_as_modified)
            current_ratio_max = st.number_input("Ratio Corriente Máx", value=preset_filters.get('current_ratio_max', 10.0), key="curr_r_max", on_change=mark_filters_as_modified)
        with col2:
            quick_ratio_min = st.number_input("Ratio Ácida Mín", value=preset_filters.get('quick_ratio_min', 0.0), key="quick_r", on_change=mark_filters_as_modified)
            quick_ratio_max = st.number_input("Ratio Ácida Máx", value=preset_filters.get('quick_ratio_max', 10.0), key="quick_r_max", on_change=mark_filters_as_modified)
        with col3:
            cash_ratio_min = st.number_input("Ratio Caja Mín", value=preset_filters.get('cash_ratio_min', 0.0), key="cash_r", on_change=mark_filters_as_modified)
        with col4:
            working_capital_min = st.number_input("Capital Trabajo Mín ($M)", value=preset_filters.get('working_capital_min', -1000.0), key="wc_min", on_change=mark_filters_as_modified)
        
        st.markdown("###### Apalancamiento")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            debt_equity_min = st.number_input("Deuda/Patrim. Mín", value=preset_filters.get('debt_equity_min', 0.0), key="de_min", on_change=mark_filters_as_modified)
            debt_equity_max = st.number_input("Deuda/Patrim. Máx", value=preset_filters.get('debt_equity_max', 5.0), key="de_max", on_change=mark_filters_as_modified)
        with col2:
            debt_ebitda_min = st.number_input("Deuda/EBITDA Mín", value=preset_filters.get('debt_ebitda_min', 0.0), key="deb_min", on_change=mark_filters_as_modified)
            debt_ebitda_max = st.number_input("Deuda/EBITDA Máx", value=preset_filters.get('debt_ebitda_max', 10.0), key="deb_max", on_change=mark_filters_as_modified)
        with col3:
            debt_fcf_min = st.number_input("Deuda/FCF Mín", value=preset_filters.get('debt_fcf_min', 0.0), key="dfcf_min", on_change=mark_filters_as_modified)
            debt_fcf_max = st.number_input("Deuda/FCF Máx", value=preset_filters.get('debt_fcf_max', 20.0), key="dfcf_max", on_change=mark_filters_as_modified)
        with col4:
            interest_coverage_min = st.number_input("Cobertura Int. Mín", value=preset_filters.get('interest_coverage_min', 0.0), key="int_c", on_change=mark_filters_as_modified)
            interest_coverage_max = st.number_input("Cobertura Int. Máx", value=preset_filters.get('interest_coverage_max', 100.0), key="int_c_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Scores de Riesgo")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            z_score_min = st.number_input("Z-Score Mín", value=preset_filters.get('z_score_min', -10.0), key="z_min", on_change=mark_filters_as_modified)
            z_score_max = st.number_input("Z-Score Máx", value=preset_filters.get('z_score_max', 10.0), key="z_max", on_change=mark_filters_as_modified)
        with col2:
            f_score_min = st.number_input("F-Score Mín", value=preset_filters.get('f_score_min', 0), min_value=0, max_value=9, key="f_min", on_change=mark_filters_as_modified)
            f_score_max = st.number_input("F-Score Máx", value=preset_filters.get('f_score_max', 9), min_value=0, max_value=9, key="f_max", on_change=mark_filters_as_modified)
        with col3:
            fcf_min = st.number_input("FCF Mín ($M)", value=preset_filters.get('fcf_min', -1000.0), key="fcf_min", on_change=mark_filters_as_modified)
            fcf_max = st.number_input("FCF Máx ($M)", value=preset_filters.get('fcf_max', 100000.0), key="fcf_max", on_change=mark_filters_as_modified)
        with col4:
            total_cash_min = st.number_input("Caja Total Mín ($M)", value=preset_filters.get('total_cash_min', 0.0), key="cash_min", on_change=mark_filters_as_modified)
            total_debt_max = st.number_input("Deuda Total Máx ($M)", value=preset_filters.get('total_debt_max', 100000.0), key="debt_max", on_change=mark_filters_as_modified)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # TAB 7: DIVIDENDOS
    # =========================================================================
    with filter_tabs[6]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">💵 Dividendos e Ingresos</div>', unsafe_allow_html=True)
        
        st.markdown("###### Yield y Payout")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            div_yield_min = st.number_input("Div Yield Mín %", value=preset_filters.get('div_yield_min', 0.0), key="div_y_min", on_change=mark_filters_as_modified)
            div_yield_max = st.number_input("Div Yield Máx %", value=preset_filters.get('div_yield_max', 20.0), key="div_y_max", on_change=mark_filters_as_modified)
        with col2:
            payout_ratio_min = st.number_input("Payout Mín %", value=preset_filters.get('payout_ratio_min', 0.0), key="pay_min", on_change=mark_filters_as_modified)
            payout_ratio_max = st.number_input("Payout Máx %", value=preset_filters.get('payout_ratio_max', 100.0), key="pay_max", on_change=mark_filters_as_modified)
        with col3:
            years_min = st.number_input("Años Crec. Mín", value=preset_filters.get('years_min', 0), min_value=0, key="years_min", on_change=mark_filters_as_modified)
            years_max = st.number_input("Años Crec. Máx", value=preset_filters.get('years_max', 100), min_value=0, key="years_max", on_change=mark_filters_as_modified)
        with col4:
            div_dollar_min = st.number_input("Div ($) Mín", value=preset_filters.get('div_dollar_min', 0.0), key="div_d_min", on_change=mark_filters_as_modified)
            div_dollar_max = st.number_input("Div ($) Máx", value=preset_filters.get('div_dollar_max', 100.0), key="div_d_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Crecimiento de Dividendos")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            div_growth_1y_min = st.number_input("Crec. Div 1A Mín %", value=preset_filters.get('div_growth_1y_min', -100.0), key="div_1y", on_change=mark_filters_as_modified)
            div_growth_1y_max = st.number_input("Crec. Div 1A Máx %", value=preset_filters.get('div_growth_1y_max', 500.0), key="div_1y_max", on_change=mark_filters_as_modified)
        with col2:
            div_growth_3y_min = st.number_input("Crec. Div 3A Mín %", value=preset_filters.get('div_growth_3y_min', -100.0), key="div_3y", on_change=mark_filters_as_modified)
            div_growth_3y_max = st.number_input("Crec. Div 3A Máx %", value=preset_filters.get('div_growth_3y_max', 500.0), key="div_3y_max", on_change=mark_filters_as_modified)
        with col3:
            div_growth_5y_min = st.number_input("Crec. Div 5A Mín %", value=preset_filters.get('div_growth_5y_min', -100.0), key="div_5y", on_change=mark_filters_as_modified)
            div_growth_5y_max = st.number_input("Crec. Div 5A Máx %", value=preset_filters.get('div_growth_5y_max', 500.0), key="div_5y_max", on_change=mark_filters_as_modified)
        with col4:
            div_growth_10y_min = st.number_input("Crec. Div 10A Mín %", value=preset_filters.get('div_growth_10y_min', -100.0), key="div_10y", on_change=mark_filters_as_modified)
            div_growth_10y_max = st.number_input("Crec. Div 10A Máx %", value=preset_filters.get('div_growth_10y_max', 500.0), key="div_10y_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Rentabilidad Total Accionista")
        col1, col2 = st.columns(2)
        with col1:
            shareholder_yield_min = st.number_input("Shareholder Yield Mín %", value=preset_filters.get('shareholder_yield_min', 0.0), key="sh_y", on_change=mark_filters_as_modified)
            shareholder_yield_max = st.number_input("Shareholder Yield Máx %", value=preset_filters.get('shareholder_yield_max', 50.0), key="sh_y_max", on_change=mark_filters_as_modified)
        with col2:
            buyback_yield_min = st.number_input("Buyback Yield Mín %", value=preset_filters.get('buyback_yield_min', 0.0), key="buy_y", on_change=mark_filters_as_modified)
            buyback_yield_max = st.number_input("Buyback Yield Máx %", value=preset_filters.get('buyback_yield_max', 20.0), key="buy_y_max", on_change=mark_filters_as_modified)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # TAB 8: TÉCNICO
    # =========================================================================
    with filter_tabs[7]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📉 Análisis Técnico y Momentum</div>', unsafe_allow_html=True)
        
        st.markdown("###### Indicadores RSI")
        col1, col2, col3 = st.columns(3)
        with col1:
            rsi_min = st.number_input("RSI Mín", value=preset_filters.get('rsi_min', 0.0), min_value=0.0, max_value=100.0, key="rsi_min", on_change=mark_filters_as_modified)
            rsi_max = st.number_input("RSI Máx", value=preset_filters.get('rsi_max', 100.0), min_value=0.0, max_value=100.0, key="rsi_max", on_change=mark_filters_as_modified)
        with col2:
            rsi_w_min = st.number_input("RSI(W) Mín", value=preset_filters.get('rsi_w_min', 0.0), min_value=0.0, max_value=100.0, key="rsi_w_min", on_change=mark_filters_as_modified)
            rsi_w_max = st.number_input("RSI(W) Máx", value=preset_filters.get('rsi_w_max', 100.0), min_value=0.0, max_value=100.0, key="rsi_w_max", on_change=mark_filters_as_modified)
        with col3:
            rsi_m_min = st.number_input("RSI(M) Mín", value=preset_filters.get('rsi_m_min', 0.0), min_value=0.0, max_value=100.0, key="rsi_m_min", on_change=mark_filters_as_modified)
            rsi_m_max = st.number_input("RSI(M) Máx", value=preset_filters.get('rsi_m_max', 100.0), min_value=0.0, max_value=100.0, key="rsi_m_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Retornos Corto Plazo")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            return_1w_min = st.number_input("Ret. 1S Mín %", value=preset_filters.get('return_1w_min', -100.0), key="ret_1w", on_change=mark_filters_as_modified)
            return_1w_max = st.number_input("Ret. 1S Máx %", value=preset_filters.get('return_1w_max', 100.0), key="ret_1w_max", on_change=mark_filters_as_modified)
        with col2:
            return_1m_min = st.number_input("Ret. 1M Mín %", value=preset_filters.get('return_1m_min', -100.0), key="ret_1m", on_change=mark_filters_as_modified)
            return_1m_max = st.number_input("Ret. 1M Máx %", value=preset_filters.get('return_1m_max', 100.0), key="ret_1m_max", on_change=mark_filters_as_modified)
        with col3:
            return_3m_min = st.number_input("Ret. 3M Mín %", value=preset_filters.get('return_3m_min', -100.0), key="ret_3m", on_change=mark_filters_as_modified)
            return_3m_max = st.number_input("Ret. 3M Máx %", value=preset_filters.get('return_3m_max', 200.0), key="ret_3m_max", on_change=mark_filters_as_modified)
        with col4:
            return_6m_min = st.number_input("Ret. 6M Mín %", value=preset_filters.get('return_6m_min', -100.0), key="ret_6m", on_change=mark_filters_as_modified)
            return_6m_max = st.number_input("Ret. 6M Máx %", value=preset_filters.get('return_6m_max', 300.0), key="ret_6m_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Retornos Largo Plazo")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            return_ytd_min = st.number_input("Ret. YTD Mín %", value=preset_filters.get('return_ytd_min', -100.0), key="ret_ytd", on_change=mark_filters_as_modified)
            return_ytd_max = st.number_input("Ret. YTD Máx %", value=preset_filters.get('return_ytd_max', 500.0), key="ret_ytd_max", on_change=mark_filters_as_modified)
        with col2:
            return_1y_min = st.number_input("Ret. 1A Mín %", value=preset_filters.get('return_1y_min', -100.0), key="ret_1y", on_change=mark_filters_as_modified)
            return_1y_max = st.number_input("Ret. 1A Máx %", value=preset_filters.get('return_1y_max', 500.0), key="ret_1y_max", on_change=mark_filters_as_modified)
        with col3:
            return_3y_min = st.number_input("Ret. 3A Mín %", value=preset_filters.get('return_3y_min', -100.0), key="ret_3y", on_change=mark_filters_as_modified)
            return_3y_max = st.number_input("Ret. 3A Máx %", value=preset_filters.get('return_3y_max', 1000.0), key="ret_3y_max", on_change=mark_filters_as_modified)
        with col4:
            return_5y_min = st.number_input("Ret. 5A Mín %", value=preset_filters.get('return_5y_min', -100.0), key="ret_5y", on_change=mark_filters_as_modified)
            return_5y_max = st.number_input("Ret. 5A Máx %", value=preset_filters.get('return_5y_max', 2000.0), key="ret_5y_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Retornos Muy Largo Plazo")
        col1, col2, col3 = st.columns(3)
        with col1:
            return_10y_min = st.number_input("Ret. 10A Mín %", value=preset_filters.get('return_10y_min', -100.0), key="ret_10y", on_change=mark_filters_as_modified)
            return_10y_max = st.number_input("Ret. 10A Máx %", value=preset_filters.get('return_10y_max', 5000.0), key="ret_10y_max", on_change=mark_filters_as_modified)
        with col2:
            return_15y_min = st.number_input("Ret. 15A Mín %", value=preset_filters.get('return_15y_min', -100.0), key="ret_15y", on_change=mark_filters_as_modified)
            return_20y_min = st.number_input("Ret. 20A Mín %", value=preset_filters.get('return_20y_min', -100.0), key="ret_20y", on_change=mark_filters_as_modified)
        with col3:
            return_ipo_min = st.number_input("Ret. desde IPO Mín %", value=preset_filters.get('return_ipo_min', -100.0), key="ret_ipo", on_change=mark_filters_as_modified)
        
        st.markdown("###### Posición y Volatilidad")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            distance_52w_high_max = st.number_input("Desde Máx 52S %", value=preset_filters.get('distance_52w_high_max', 100.0), key="52h_max", on_change=mark_filters_as_modified)
            distance_52w_low_min = st.number_input("Desde Mín 52S %", value=preset_filters.get('distance_52w_low_min', 0.0), key="52l_min", on_change=mark_filters_as_modified)
        with col2:
            ath_chg_max = st.number_input("Desde ATH Máx %", value=preset_filters.get('ath_chg_max', 100.0), key="ath_max", on_change=mark_filters_as_modified)
            atl_chg_min = st.number_input("Desde ATL Mín %", value=preset_filters.get('atl_chg_min', 0.0), key="atl_min", on_change=mark_filters_as_modified)
        with col3:
            beta_min = st.number_input("Beta Mín", value=preset_filters.get('beta_min', -2.0), key="beta_min", on_change=mark_filters_as_modified)
            beta_max = st.number_input("Beta Máx", value=preset_filters.get('beta_max', 3.0), key="beta_max", on_change=mark_filters_as_modified)
        with col4:
            atr_min = st.number_input("ATR Mín", value=preset_filters.get('atr_min', 0.0), key="atr_min", on_change=mark_filters_as_modified)
            atr_max = st.number_input("ATR Máx", value=preset_filters.get('atr_max', 100.0), key="atr_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Volumen")
        col1, col2, col3 = st.columns(3)
        with col1:
            rel_volume_min = st.number_input("Vol. Relativo Mín", value=preset_filters.get('rel_volume_min', 0.0), key="rel_v", on_change=mark_filters_as_modified)
            rel_volume_max = st.number_input("Vol. Relativo Máx", value=preset_filters.get('rel_volume_max', 10.0), key="rel_v_max", on_change=mark_filters_as_modified)
        with col2:
            avg_volume_min = st.number_input("Vol. Promedio Mín (M)", value=preset_filters.get('avg_volume_min', 0.0), key="avg_v_min", on_change=mark_filters_as_modified)
            avg_volume_max = st.number_input("Vol. Promedio Máx (M)", value=preset_filters.get('avg_volume_max', 1000.0), key="avg_v_max", on_change=mark_filters_as_modified)
        with col3:
            dollar_vol_min = st.number_input("Vol. Dólares Mín ($M)", value=preset_filters.get('dollar_vol_min', 0.0), key="dol_v_min", on_change=mark_filters_as_modified)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # TAB 9: PROPIEDAD
    # =========================================================================
    with filter_tabs[8]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🏢 Propiedad y Sentimiento</div>', unsafe_allow_html=True)
        
        st.markdown("###### Propiedad Interna")
        col1, col2, col3 = st.columns(3)
        with col1:
            insider_ownership_min = st.number_input("Prop. Insiders Mín %", value=preset_filters.get('insider_ownership_min', 0.0), key="ins_own", on_change=mark_filters_as_modified)
            insider_ownership_max = st.number_input("Prop. Insiders Máx %", value=preset_filters.get('insider_ownership_max', 100.0), key="ins_own_max", on_change=mark_filters_as_modified)
        with col2:
            institutional_ownership_min = st.number_input("Prop. Inst. Mín %", value=preset_filters.get('institutional_ownership_min', 0.0), key="inst_min", on_change=mark_filters_as_modified)
            institutional_ownership_max = st.number_input("Prop. Inst. Máx %", value=preset_filters.get('institutional_ownership_max', 100.0), key="inst_max", on_change=mark_filters_as_modified)
        with col3:
            analysts_min = st.number_input("Analistas Mín", value=preset_filters.get('analysts_min', 0), min_value=0, key="ana_min", on_change=mark_filters_as_modified)
            analysts_max = st.number_input("Analistas Máx", value=preset_filters.get('analysts_max', 100), min_value=0, key="ana_max", on_change=mark_filters_as_modified)
        
        st.markdown("###### Interés en Corto")
        col1, col2, col3 = st.columns(3)
        with col1:
            short_float_min = st.number_input("Short % Float Mín", value=preset_filters.get('short_float_min', 0.0), key="short_f_min", on_change=mark_filters_as_modified)
            short_float_max = st.number_input("Short % Float Máx", value=preset_filters.get('short_float_max', 100.0), key="short_f", on_change=mark_filters_as_modified)
        with col2:
            short_shares_min = st.number_input("Short % Shares Mín", value=preset_filters.get('short_shares_min', 0.0), key="short_s_min", on_change=mark_filters_as_modified)
            short_shares_max = st.number_input("Short % Shares Máx", value=preset_filters.get('short_shares_max', 100.0), key="short_s_max", on_change=mark_filters_as_modified)
        with col3:
            short_ratio_min = st.number_input("Short Ratio Mín", value=preset_filters.get('short_ratio_min', 0.0), key="short_r_min", on_change=mark_filters_as_modified)
            short_ratio_max = st.number_input("Short Ratio Máx", value=preset_filters.get('short_ratio_max', 50.0), key="short_r", on_change=mark_filters_as_modified)
        
        st.markdown("###### Cambios en Acciones")
        col1, col2 = st.columns(2)
        with col1:
            shares_ch_yoy_min = st.number_input("Cambio Acciones YoY Mín %", value=preset_filters.get('shares_ch_yoy_min', -50.0), key="sh_yoy_min", on_change=mark_filters_as_modified)
            shares_ch_yoy_max = st.number_input("Cambio Acciones YoY Máx %", value=preset_filters.get('shares_ch_yoy_max', 50.0), key="sh_yoy_max", on_change=mark_filters_as_modified)
        with col2:
            shares_ch_qoq_min = st.number_input("Cambio Acciones QoQ Mín %", value=preset_filters.get('shares_ch_qoq_min', -20.0), key="sh_qoq_min", on_change=mark_filters_as_modified)
            shares_ch_qoq_max = st.number_input("Cambio Acciones QoQ Máx %", value=preset_filters.get('shares_ch_qoq_max', 20.0), key="sh_qoq_max", on_change=mark_filters_as_modified)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # TAB 10: PUNTUACIONES
    # =========================================================================
    with filter_tabs[9]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🎯 Puntuaciones BQuant (0-100)</div>', unsafe_allow_html=True)
        st.markdown("###### Sistema de puntuación algorítmica que combina múltiples factores")
        
        col1, col2 = st.columns(2)
        with col1:
            quality_score_min = st.slider("⭐ Puntuación Calidad Mín", 0, 100, preset_filters.get('quality_score_min', 0), 
                                         key="quality_score_min", on_change=mark_filters_as_modified,
                                         help="Combina ROE, ROA, ROIC y márgenes")
            value_score_min = st.slider("💎 Puntuación Valor Mín", 0, 100, preset_filters.get('value_score_min', 0),
                                       key="value_score_min", on_change=mark_filters_as_modified,
                                       help="Combina P/E, P/B, P/S y EV/EBITDA")
            growth_score_min = st.slider("📈 Puntuación Crecimiento Mín", 0, 100, preset_filters.get('growth_score_min', 0),
                                        key="growth_score_min", on_change=mark_filters_as_modified,
                                        help="Combina crecimiento de ingresos, BPA y estimaciones futuras")
        with col2:
            financial_health_score_min = st.slider("🏥 Salud Financiera Mín", 0, 100, preset_filters.get('financial_health_score_min', 0),
                                                  key="financial_health_score_min", on_change=mark_filters_as_modified,
                                                  help="Combina liquidez, apalancamiento y flujo de caja")
            momentum_score_min = st.slider("🚀 Puntuación Momentum Mín", 0, 100, preset_filters.get('momentum_score_min', 0),
                                          key="momentum_score_min", on_change=mark_filters_as_modified,
                                          help="Combina retornos, RSI y volumen")
            master_score_min = st.slider("🏆 **PUNTUACIÓN MAESTRA MÍN**", 0, 100, preset_filters.get('master_score_min', 0),
                                        key="master_score_min", on_change=mark_filters_as_modified,
                                        help="Combinación ponderada de todas las puntuaciones")
        
        st.markdown("##### Fórmula de Puntuación Maestra:")
        st.markdown("""
Master Score = (Calidad × 30%) + (Valor × 25%) + (Crecimiento × 20%) + 
               (Salud Financiera × 15%) + (Momentum × 10%)
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # TAB 11: FECHAS Y EVENTOS
    # =========================================================================
    with filter_tabs[10]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📅 Fechas y Eventos</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            ipo_date_after = st.date_input("IPO después de", value=preset_filters.get('ipo_date_after', date(2000, 1, 1)), key="ipo_after", on_change=mark_filters_as_modified)
            ipo_date_before = st.date_input("IPO antes de", value=preset_filters.get('ipo_date_before', date.today()), key="ipo_before", on_change=mark_filters_as_modified)
        with col2:
            earnings_date_after = st.date_input("Resultados después de", value=preset_filters.get('earnings_date_after', date.today()), key="earn_after", on_change=mark_filters_as_modified)
            earnings_date_before = st.date_input("Resultados antes de", value=preset_filters.get('earnings_date_before', date.today()), key="earn_before", on_change=mark_filters_as_modified)
        with col3:
            ex_div_date_after = st.date_input("Ex-div después de", value=preset_filters.get('ex_div_date_after', date.today()), key="exdiv_after", on_change=mark_filters_as_modified)
            ex_div_date_before = st.date_input("Ex-div antes de", value=preset_filters.get('ex_div_date_before', date.today()), key="exdiv_before", on_change=mark_filters_as_modified)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # TAB 12: OTROS FILTROS
    # =========================================================================
    with filter_tabs[11]:
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📋 Otros Filtros</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            pt_upside_min = st.number_input("Potencial PT Mín %", value=preset_filters.get('pt_upside_min', -100.0), key="pt_up_min", on_change=mark_filters_as_modified)
            pt_upside_max = st.number_input("Potencial PT Máx %", value=preset_filters.get('pt_upside_max', 500.0), key="pt_up_max", on_change=mark_filters_as_modified)
        with col2:
            rating_min = st.number_input("Rating Mín", value=preset_filters.get('rating_min', 1.0), min_value=1.0, max_value=5.0, key="rat_min", on_change=mark_filters_as_modified)
            rating_max = st.number_input("Rating Máx", value=preset_filters.get('rating_max', 5.0), min_value=1.0, max_value=5.0, key="rat_max", on_change=mark_filters_as_modified)
        with col3:
            sbc_rev_min = st.number_input("SBC/Rev Mín %", value=preset_filters.get('sbc_rev_min', 0.0), key="sbc_min", on_change=mark_filters_as_modified)
            sbc_rev_max = st.number_input("SBC/Rev Máx %", value=preset_filters.get('sbc_rev_max', 50.0), key="sbc_max", on_change=mark_filters_as_modified)
        with col4:
            rd_rev_min = st.number_input("I+D/Rev Mín %", value=preset_filters.get('rd_rev_min', 0.0), key="rd_min", on_change=mark_filters_as_modified)
            rd_rev_max = st.number_input("I+D/Rev Máx %", value=preset_filters.get('rd_rev_max', 100.0), key="rd_max", on_change=mark_filters_as_modified)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # BOTÓN DE APLICAR FILTROS
    # =========================================================================
    # Al final de todos los tabs de filtros
    st.markdown("---")

    # Mostrar información sobre el estado actual
    if st.session_state.get('manual_filters_modified', False):
        st.info("""
        ℹ️ **Has modificado filtros manualmente**
        
        Opciones:
        - Haz clic en **"APLICAR TODOS LOS FILTROS"** abajo para aplicar tus cambios personalizados
        - Haz clic en **"EJECUTAR"** arriba para aplicar los cambios al screener actual
        - Selecciona otro screener para descartar los cambios
        """)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Este botón SIEMPRE captura y aplica los valores actuales
        if st.button("⚡ **APLICAR TODOS LOS FILTROS Y EJECUTAR ANÁLISIS**", 
                    type="primary", 
                    use_container_width=True, 
                    key="apply_all_filters",
                    help="Aplica TODOS los valores actuales de los filtros y ejecuta el análisis"):
            
            # SIEMPRE captura los valores actuales
            current_filters = capture_current_filter_values()
            
            # Aplicar los filtros capturados
            st.session_state.active_filters = current_filters
            st.session_state.filters_applied = True
            st.session_state.manual_filters_modified = False
            st.session_state.show_success = True
            
            # Si estamos en Constructor Personalizado, mantenerlo
            # Si no, marcar como "Personalizado" porque el usuario modificó los filtros
            if selected_screener != "🎯 Constructor Personalizado":
                st.session_state.last_applied_screener = f"{selected_screener} (Modificado)"
            else:
                st.session_state.last_applied_screener = selected_screener
            
            st.rerun()

# =============================================================================
# APLICACIÓN DE FILTROS Y RESULTADOS
# =============================================================================

if st.session_state.filters_applied:
    filtered_df = df.copy()
    
    # Obtener los filtros activos del session_state
    active_filters = st.session_state.get('active_filters', {})
    
    # Aplicar búsqueda de texto
    if 'search_term' in active_filters and active_filters['search_term']:
        filtered_df = filtered_df[
            filtered_df['Symbol'].str.contains(active_filters['search_term'].upper(), na=False) |
            filtered_df['Company Name'].str.contains(active_filters['search_term'], case=False, na=False)
        ]
    
    # Aplicar filtros de países
    if 'countries' in active_filters:
        filtered_df = filtered_df[filtered_df['Country'].isin(active_filters['countries'])]
    if 'exclude_countries' in active_filters:
        filtered_df = filtered_df[~filtered_df['Country'].isin(active_filters['exclude_countries'])]
    
    # Aplicar filtros de sectores
    if 'sectors' in active_filters and 'Sector' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Sector'].isin(active_filters['sectors'])]
    
    # Aplicar market cap
    if 'market_cap_min' in active_filters and 'Market Cap' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Market Cap'] >= active_filters['market_cap_min']]
    if 'market_cap_max' in active_filters and 'Market Cap' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Market Cap'] <= active_filters['market_cap_max']]
    
    # Mapeo completo de filtros a columnas
    column_filter_mapping = {
        # Valoración
        'PE Ratio': {
            'min': active_filters.get('pe_min'),
            'max': active_filters.get('pe_max')
        },
        'Forward PE': {
            'min': active_filters.get('forward_pe_min'),
            'max': active_filters.get('forward_pe_max')
        },
        'PB Ratio': {
            'min': active_filters.get('pb_min'),
            'max': active_filters.get('pb_max')
        },
        'PS Ratio': {
            'min': active_filters.get('ps_min'),
            'max': active_filters.get('ps_max')
        },
        'Forward PS': {
            'min': active_filters.get('forward_ps_min'),
            'max': active_filters.get('forward_ps_max')
        },
        'PEG Ratio': {
            'min': active_filters.get('peg_min'),
            'max': active_filters.get('peg_max')
        },
        'P/FCF': {
            'min': active_filters.get('p_fcf_min'),
            'max': active_filters.get('p_fcf_max')
        },
        'P/OCF': {
            'min': active_filters.get('p_ocf_min'),
            'max': active_filters.get('p_ocf_max')
        },
        'P/EBITDA': {
            'min': active_filters.get('p_ebitda_min'),
            'max': active_filters.get('p_ebitda_max')
        },
        
        # Enterprise Value
        'EV/Sales': {
            'min': active_filters.get('ev_sales_min'),
            'max': active_filters.get('ev_sales_max')
        },
        'EV/EBITDA': {
            'min': active_filters.get('ev_ebitda_min'),
            'max': active_filters.get('ev_ebitda_max')
        },
        'EV/EBIT': {
            'min': active_filters.get('ev_ebit_min'),
            'max': active_filters.get('ev_ebit_max')
        },
        'EV/FCF': {
            'min': active_filters.get('ev_fcf_min'),
            'max': active_filters.get('ev_fcf_max')
        },
        
        # Yields
        'FCF Yield': {
            'min': active_filters.get('fcf_yield_min')
        },
        'Earnings Yield': {
            'min': active_filters.get('earnings_yield_min')
        },
        'Graham (%)': {
            'min': active_filters.get('graham_upside_min')
        },
        'Lynch (%)': {
            'min': active_filters.get('lynch_upside_min')
        },
        
        # Crecimiento
        'Rev. Growth': {
            'min': active_filters.get('rev_growth_min'),
            'max': active_filters.get('rev_growth_max')
        },
        'Rev. Growth (Q)': {
            'min': active_filters.get('rev_growth_q_min'),
            'max': active_filters.get('rev_growth_q_max')
        },
        'Rev. Growth 3Y': {
            'min': active_filters.get('rev_growth_3y_min')
        },
        'Rev. Growth 5Y': {
            'min': active_filters.get('rev_growth_5y_min')
        },
        'EPS Growth': {
            'min': active_filters.get('eps_growth_min'),
            'max': active_filters.get('eps_growth_max')
        },
        'EPS Growth (Q)': {
            'min': active_filters.get('eps_growth_q_min'),
            'max': active_filters.get('eps_growth_q_max')
        },
        'EPS Growth 3Y': {
            'min': active_filters.get('eps_growth_3y_min')
        },
        'EPS Growth 5Y': {
            'min': active_filters.get('eps_growth_5y_min')
        },
        'Rev Gr. This Y': {
            'min': active_filters.get('rev_gr_this_y_min')
        },
        'Rev Gr. Next Y': {
            'min': active_filters.get('rev_gr_next_y_min')
        },
        'EPS Gr. This Y': {
            'min': active_filters.get('eps_gr_this_y_min')
        },
        'EPS Gr. Next Y': {
            'min': active_filters.get('eps_gr_next_y_min')
        },
        'FCF Growth': {
            'min': active_filters.get('fcf_growth_min')
        },
        
        # Rentabilidad
        'ROE': {
            'min': active_filters.get('roe_min'),
            'max': active_filters.get('roe_max')
        },
        'ROA': {
            'min': active_filters.get('roa_min'),
            'max': active_filters.get('roa_max')
        },
        'ROIC': {
            'min': active_filters.get('roic_min'),
            'max': active_filters.get('roic_max')
        },
        'ROCE': {
            'min': active_filters.get('roce_min'),
            'max': active_filters.get('roce_max')
        },
        'ROE (5Y)': {
            'min': active_filters.get('roe_5y_min')
        },
        'ROA (5Y)': {
            'min': active_filters.get('roa_5y_min')
        },
        'ROIC (5Y)': {
            'min': active_filters.get('roic_5y_min')
        },
        
        # Márgenes
        'Gross Margin': {
            'min': active_filters.get('gross_margin_min'),
            'max': active_filters.get('gross_margin_max')
        },
        'Oper. Margin': {
            'min': active_filters.get('operating_margin_min'),
            'max': active_filters.get('operating_margin_max')
        },
        'Pretax Margin': {
            'min': active_filters.get('pretax_margin_min'),
            'max': active_filters.get('pretax_margin_max')
        },
        'Profit Margin': {
            'min': active_filters.get('profit_margin_min'),
            'max': active_filters.get('profit_margin_max')
        },
        'FCF Margin': {
            'min': active_filters.get('fcf_margin_min'),
            'max': active_filters.get('fcf_margin_max')
        },
        'EBITDA Margin': {
            'min': active_filters.get('ebitda_margin_min'),
            'max': active_filters.get('ebitda_margin_max')
        },
        'EBIT Margin': {
            'min': active_filters.get('ebit_margin_min'),
            'max': active_filters.get('ebit_margin_max')
        },
        
        # Salud Financiera
        'Current Ratio': {
            'min': active_filters.get('current_ratio_min'),
            'max': active_filters.get('current_ratio_max')
        },
        'Quick Ratio': {
            'min': active_filters.get('quick_ratio_min'),
            'max': active_filters.get('quick_ratio_max')
        },
        'Debt / Equity': {
            'min': active_filters.get('debt_equity_min'),
            'max': active_filters.get('debt_equity_max')
        },
        'Debt / EBITDA': {
            'min': active_filters.get('debt_ebitda_min'),
            'max': active_filters.get('debt_ebitda_max')
        },
        'Debt / FCF': {
            'min': active_filters.get('debt_fcf_min'),
            'max': active_filters.get('debt_fcf_max')
        },
        'Z-Score': {
            'min': active_filters.get('z_score_min'),
            'max': active_filters.get('z_score_max')
        },
        'F-Score': {
            'min': active_filters.get('f_score_min'),
            'max': active_filters.get('f_score_max')
        },
        'Int. Cov.': {
            'min': active_filters.get('interest_coverage_min'),
            'max': active_filters.get('interest_coverage_max')
        },
        'FCF': {
            'min': active_filters.get('fcf_min'),
            'max': active_filters.get('fcf_max')
        },
        
        # Dividendos
        'Years': {
            'min': active_filters.get('years_min'),
            'max': active_filters.get('years_max')
        },
        'Div. Yield': {
            'min': active_filters.get('div_yield_min'),
            'max': active_filters.get('div_yield_max')
        },
        'Payout Ratio': {
            'min': active_filters.get('payout_ratio_min'),
            'max': active_filters.get('payout_ratio_max')
        },
        'Div. Growth': {
            'min': active_filters.get('div_growth_1y_min'),
            'max': active_filters.get('div_growth_1y_max')
        },
        'Div. Growth 3Y': {
            'min': active_filters.get('div_growth_3y_min'),
            'max': active_filters.get('div_growth_3y_max')
        },
        'Div. Growth 5Y': {
            'min': active_filters.get('div_growth_5y_min'),
            'max': active_filters.get('div_growth_5y_max')
        },
        'Div. Growth 10Y': {
            'min': active_filters.get('div_growth_10y_min'),
            'max': active_filters.get('div_growth_10y_max')
        },
        'Shareh. Yield': {
            'min': active_filters.get('shareholder_yield_min'),
            'max': active_filters.get('shareholder_yield_max')
        },
        'Buyback Yield': {
            'min': active_filters.get('buyback_yield_min'),
            'max': active_filters.get('buyback_yield_max')
        },
        
        # Técnico - Retornos
        'Return 1W': {
            'min': active_filters.get('return_1w_min'),
            'max': active_filters.get('return_1w_max')
        },
        'Return 1M': {
            'min': active_filters.get('return_1m_min'),
            'max': active_filters.get('return_1m_max')
        },
        'Return 3M': {
            'min': active_filters.get('return_3m_min'),
            'max': active_filters.get('return_3m_max')
        },
        'Return 6M': {
            'min': active_filters.get('return_6m_min'),
            'max': active_filters.get('return_6m_max')
        },
        'Return YTD': {
            'min': active_filters.get('return_ytd_min'),
            'max': active_filters.get('return_ytd_max')
        },
        'Return 1Y': {
            'min': active_filters.get('return_1y_min'),
            'max': active_filters.get('return_1y_max')
        },
        'Return 3Y': {
            'min': active_filters.get('return_3y_min'),
            'max': active_filters.get('return_3y_max')
        },
        'Return 5Y': {
            'min': active_filters.get('return_5y_min'),
            'max': active_filters.get('return_5y_max')
        },
        'Return 10Y': {
            'min': active_filters.get('return_10y_min'),
            'max': active_filters.get('return_10y_max')
        },
        
        # Técnico - Indicadores
        'RSI': {
            'min': active_filters.get('rsi_min'),
            'max': active_filters.get('rsi_max')
        },
        'RSI (W)': {
            'min': active_filters.get('rsi_w_min'),
            'max': active_filters.get('rsi_w_max')
        },
        'RSI (M)': {
            'min': active_filters.get('rsi_m_min'),
            'max': active_filters.get('rsi_m_max')
        },
        'Beta (5Y)': {
            'min': active_filters.get('beta_min'),
            'max': active_filters.get('beta_max')
        },
        'ATR': {
            'min': active_filters.get('atr_min'),
            'max': active_filters.get('atr_max')
        },
        'Rel. Volume': {
            'min': active_filters.get('rel_volume_min'),
            'max': active_filters.get('rel_volume_max')
        },
        
        # Propiedad
        'Employees': {
            'min': active_filters.get('employees_min')
        },
        'Founded': {
            'min': active_filters.get('founded_after')
        },
        'Shares Insiders': {
            'min': active_filters.get('insider_ownership_min'),
            'max': active_filters.get('insider_ownership_max')
        },
        'Shares Institut.': {
            'min': active_filters.get('institutional_ownership_min'),
            'max': active_filters.get('institutional_ownership_max')
        },
        'Analysts': {
            'min': active_filters.get('analysts_min'),
            'max': active_filters.get('analysts_max')
        },
        'Short % Float': {
            'min': active_filters.get('short_float_min'),
            'max': active_filters.get('short_float_max')
        },
        'Short % Shares': {
            'min': active_filters.get('short_shares_min'),
            'max': active_filters.get('short_shares_max')
        },
        'Short Ratio': {
            'min': active_filters.get('short_ratio_min'),
            'max': active_filters.get('short_ratio_max')
        },
        
        # Scores
        'Quality_Score': {
            'min': active_filters.get('quality_score_min')
        },
        'Value_Score': {
            'min': active_filters.get('value_score_min')
        },
        'Growth_Score': {
            'min': active_filters.get('growth_score_min')
        },
        'Financial_Health_Score': {
            'min': active_filters.get('financial_health_score_min')
        },
        'Momentum_Score': {
            'min': active_filters.get('momentum_score_min')
        },
        'Master_Score': {
            'min': active_filters.get('master_score_min')
        }
    }
    
    # Aplicar todos los filtros numéricos
    for col, limits in column_filter_mapping.items():
        if col in filtered_df.columns:
            if 'min' in limits and limits['min'] is not None:
                filtered_df = filtered_df[filtered_df[col] >= limits['min']]
            if 'max' in limits and limits['max'] is not None:
                filtered_df = filtered_df[filtered_df[col] <= limits['max']]
    
    # Manejo especial para distancia desde máximo 52 semanas
    if 'distance_52w_high_max' in active_filters and '52W High Chg' in filtered_df.columns:
        max_distance = -active_filters['distance_52w_high_max']
        filtered_df = filtered_df[filtered_df['52W High Chg'] >= max_distance]
    
    # Manejo especial para distancia desde mínimo 52 semanas
    if 'distance_52w_low_min' in active_filters and '52W Low Chg' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['52W Low Chg'] >= active_filters['distance_52w_low_min']]
    
    # Mostrar resultados
    with main_tab2:
        if st.session_state.filters_applied and not filtered_df.empty:
            
            # ===== DATA COVERAGE INDICATOR SECTION =====
            # Calculate data completeness for filtered results
            key_metrics = ['PE Ratio', 'ROE', 'Rev. Growth', 'Div. Yield', 'Beta (5Y)', 
                        'Forward PE', 'Analysts', 'EPS Growth', 'Profit Margin']
            completeness_scores = {}
            
            for metric in key_metrics:
                if metric in filtered_df.columns:
                    completeness = (filtered_df[metric].notna().sum() / len(filtered_df)) * 100
                    completeness_scores[metric] = completeness
            
            avg_completeness = sum(completeness_scores.values()) / len(completeness_scores) if completeness_scores else 0
            
            # Display coverage indicator
            coverage_color = "#10b981" if avg_completeness >= 70 else "#f59e0b" if avg_completeness >= 40 else "#ef4444"
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {coverage_color}22, {coverage_color}11); 
                        padding: 15px; border-radius: 10px; margin-bottom: 20px; 
                        border-left: 4px solid {coverage_color};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <h4 style='margin: 0; color: {coverage_color};'>
                            📊 Calidad de Datos en Resultados: {avg_completeness:.0f}%
                        </h4>
                        <p style='margin: 5px 0; color: #c9d1d9; font-size: 0.9em;'>
                            {"✅ Excelente - Datos completos para análisis detallado" if avg_completeness >= 70 else 
                            "⚠️ Parcial - Algunos datos pueden faltar, especialmente estimaciones" if avg_completeness >= 40 else
                            "🔴 Limitada - Muchos campos vacíos, use con precaución"}
                        </p>
                    </div>
                    <div style='text-align: right;'>
                        <span style='font-size: 2em;'>{
                            "✅" if avg_completeness >= 70 else 
                            "⚠️" if avg_completeness >= 40 else "🔴"
                        }</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show detailed coverage breakdown if data is limited
            if avg_completeness < 70:
                with st.expander("📋 Ver detalles de campos con datos", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    sorted_metrics = sorted(completeness_scores.items(), key=lambda x: x[1], reverse=True)
                    for idx, (metric, score) in enumerate(sorted_metrics):
                        col = [col1, col2, col3][idx % 3]
                        with col:
                            color = '#10b981' if score >= 70 else '#f59e0b' if score >= 40 else '#ef4444'
                            st.markdown(f"""
                            <div style="margin-bottom: 8px;">
                                <span style="color: {color};">●</span> 
                                <strong>{metric}:</strong> 
                                <span style="color: {color};">{score:.0f}%</span>
                            </div>
                            """, unsafe_allow_html=True)
            
            # ===== SUCCESS MESSAGE WITH RESULTS SUMMARY =====
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #10b981, #059669); 
                        padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <h3 style='color: white; margin: 0;'>✅ Encontradas {len(filtered_df):,} acciones que cumplen los criterios</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # ===== METRICS SUMMARY =====
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric("📊 Resultados", f"{len(filtered_df):,}", 
                        f"{(len(filtered_df)/len(df)*100):.1f}% del total")
            with col2:
                st.metric("🌍 Países", 
                        f"{filtered_df['Country'].nunique()}" if 'Country' in filtered_df.columns else "N/D")
            with col3:
                total_mcap = filtered_df['Market Cap'].sum() if 'Market Cap' in filtered_df.columns else 0
                st.metric("💰 Cap. Total", format_number(total_mcap, prefix="$"))
            with col4:
                median_pe = filtered_df['PE Ratio'].median() if 'PE Ratio' in filtered_df.columns and not filtered_df['PE Ratio'].isna().all() else 0
                st.metric("P/E Mediano", f"{median_pe:.1f}")
            with col5:
                avg_roe = filtered_df['ROE'].mean() if 'ROE' in filtered_df.columns and not filtered_df['ROE'].isna().all() else 0
                st.metric("ROE Promedio", f"{avg_roe:.1f}%")
            with col6:
                avg_score = filtered_df['Master_Score'].mean() if 'Master_Score' in filtered_df.columns and not filtered_df['Master_Score'].isna().all() else 0
                st.metric("Score Promedio", f"{avg_score:.0f}/100")
            
            # ===== RESULTS TABS =====
            result_tabs = st.tabs([
                "📊 Tabla", "📈 Gráficos", "🏆 Rankings", 
                "🎯 Análisis Sectorial", "🌍 Análisis por País", 
                "📐 Correlaciones", "💾 Exportar"
            ])
            
            # TAB 1: TABLA
            with result_tabs[0]:
                st.markdown("### 📊 Resultados del Screening")
                
                # Configuración de vista
                with st.expander("⚙️ Configurar Vista", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        default_cols = ['Symbol', 'Company Name', 'Country', 'Sector', 
                                    'Market Cap', 'Master_Score', 'PE Ratio', 'ROE', 
                                    'Rev. Growth', 'Return 1Y', 'Div. Yield']
                        available_cols = [col for col in default_cols if col in filtered_df.columns]
                        
                        selected_columns = st.multiselect(
                            "Seleccionar columnas:",
                            options=list(filtered_df.columns),
                            default=available_cols[:10],
                            help="Elige las columnas a mostrar en la tabla"
                        )
                    
                    with col2:
                        if selected_columns:
                            sort_column = st.selectbox(
                                "Ordenar por:",
                                options=selected_columns,
                                index=selected_columns.index('Master_Score') if 'Master_Score' in selected_columns else 0
                            )
                            sort_order = st.radio("Orden:", ["Descendente", "Ascendente"], horizontal=True)
                        else:
                            sort_column = 'Symbol'
                            sort_order = "Descendente"
                    
                    with col3:
                        n_rows = st.select_slider(
                            "Filas a mostrar:",
                            options=[25, 50, 100, 200, 500, 1000],
                            value=100
                        )
                
                # Crear tabla HTML hermosa
                if selected_columns:
                    df_display = filtered_df[selected_columns].copy()
                    df_display = df_display.sort_values(
                        by=sort_column, 
                        ascending=(sort_order == "Ascendente")
                    ).head(n_rows)
                    
                    # Crear tabla HTML con estilos
                    html_table = create_beautiful_html_table(df_display)
                    st.markdown(html_table, unsafe_allow_html=True)
            
            # TAB 2: GRÁFICOS
            with result_tabs[1]:
                st.markdown("### 📈 Análisis Visual")
                
                if len(filtered_df) > 1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("##### Matriz Valor vs Calidad")
                        fig = px.scatter(
                            filtered_df.head(500),
                            x='Value_Score',
                            y='Quality_Score',
                            size='Market Cap',
                            color='Master_Score',
                            hover_data=['Symbol', 'Company Name', 'PE Ratio', 'ROE'],
                            color_continuous_scale='Viridis',
                            template='plotly_dark',
                            title="Matriz Valor vs Calidad"
                        )
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("##### Matriz Crecimiento vs Momentum")
                        fig = px.scatter(
                            filtered_df.head(500),
                            x='Growth_Score',
                            y='Momentum_Score',
                            size='Market Cap',
                            color='Financial_Health_Score',
                            hover_data=['Symbol', 'Company Name', 'Rev. Growth', 'Return 1Y'],
                            color_continuous_scale='RdYlGn',
                            template='plotly_dark',
                            title="Matriz Crecimiento vs Momentum"
                        )
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Gráfico adicional de distribución
                    st.markdown("##### Distribución de Scores")
                    fig = go.Figure()
                    
                    scores = ['Quality_Score', 'Value_Score', 'Growth_Score', 
                            'Financial_Health_Score', 'Momentum_Score']
                    colors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444']
                    
                    for score, color in zip(scores, colors):
                        if score in filtered_df.columns:
                            fig.add_trace(go.Box(
                                y=filtered_df[score],
                                name=score.replace('_', ' '),
                                marker_color=color,
                                boxmean=True
                            ))
                    
                    fig.update_layout(
                        template='plotly_dark',
                        title="Distribución de Puntuaciones",
                        height=400,
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Se necesitan al menos 2 resultados para visualización")
            
            # TAB 3: RANKINGS
            with result_tabs[2]:
                st.markdown("### 🏆 Rankings por Categoría")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    render_ranking_card(
                        "Top Valor", "💎", filtered_df,
                        'Value_Score', 'PE Ratio', 'P/E', "{:.1f}"
                    )
                    
                    st.markdown("---")
                    
                    render_ranking_card(
                        "Top Dividendos", "💰", 
                        filtered_df[filtered_df['Div. Yield'] > 0] if 'Div. Yield' in filtered_df.columns else filtered_df,
                        'Div. Yield', 'Payout Ratio', 'Payout', "{:.1f}%"
                    )
                
                with col2:
                    render_ranking_card(
                        "Top Crecimiento", "🚀", filtered_df,
                        'Growth_Score', 'Rev. Growth', 'Crecimiento Ingresos', "{:.1f}%"
                    )
                    
                    st.markdown("---")
                    
                    render_ranking_card(
                        "Top Momentum", "📈", filtered_df,
                        'Momentum_Score', 'Return 1Y', 'Retorno 1A', "{:.1f}%"
                    )
                
                with col3:
                    render_ranking_card(
                        "Top Calidad", "⭐", filtered_df,
                        'Quality_Score', 'ROE', 'ROE', "{:.1f}%"
                    )
                    
                    st.markdown("---")
                    
                    render_ranking_card(
                        "Top Salud Financiera", "🏥", filtered_df,
                        'Financial_Health_Score', 'Current Ratio', 'Ratio Corriente', "{:.2f}"
                    )
            
            # TAB 4: ANÁLISIS SECTORIAL
            with result_tabs[3]:
                st.markdown("### 🎯 Análisis Sectorial Detallado")
                
                if 'Sector' in filtered_df.columns:
                    # Métricas por sector
                    sector_metrics = filtered_df.groupby('Sector').agg({
                        'Symbol': 'count',
                        'Market Cap': ['sum', 'mean', 'median'],
                        'PE Ratio': 'median',
                        'ROE': 'median',
                        'Rev. Growth': 'median',
                        'Profit Margin': 'median',
                        'Debt / Equity': 'median',
                        'Return 1Y': 'median',
                        'Master_Score': 'mean'
                    }).round(2)
                    
                    sector_metrics.columns = ['Acciones', 'Cap. Total', 'Cap. Media', 'Cap. Mediana',
                                            'P/E Med', 'ROE Med', 'Crec. Ingresos Med', 
                                            'Margen Neto Med', 'D/E Med', 'Retorno 1A Med', 'Score Promedio']
                    sector_metrics = sector_metrics.sort_values('Acciones', ascending=False)
                    
                    # Formatear valores
                    for col in ['Cap. Total', 'Cap. Media', 'Cap. Mediana']:
                        sector_metrics[col] = sector_metrics[col].apply(lambda x: format_number(x, prefix='$'))
                    
                    # Mostrar tabla con estilo
                    st.dataframe(
                        sector_metrics,
                        use_container_width=True,
                        column_config={
                            "Score Promedio": st.column_config.ProgressColumn(
                                "Score Promedio",
                                min_value=0,
                                max_value=100,
                            ),
                            "ROE Med": st.column_config.NumberColumn(
                                "ROE Med",
                                format="%.1f%%"
                            ),
                            "Retorno 1A Med": st.column_config.NumberColumn(
                                "Retorno 1A Med",
                                format="%.1f%%"
                            )
                        }
                    )
                    
                    # Gráficos de sector
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Pie chart de distribución
                        fig = px.pie(
                            values=filtered_df.groupby('Sector')['Symbol'].count().values,
                            names=filtered_df.groupby('Sector')['Symbol'].count().index,
                            title="Distribución por Sector",
                            template='plotly_dark'
                        )
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Bar chart de performance
                        sector_perf = filtered_df.groupby('Sector')['Master_Score'].mean().sort_values()
                        fig = px.bar(
                            x=sector_perf.values,
                            y=sector_perf.index,
                            orientation='h',
                            title="Score Promedio por Sector",
                            template='plotly_dark',
                            color=sector_perf.values,
                            color_continuous_scale='RdYlGn'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Heatmap de métricas por sector
                    st.markdown("##### Mapa de Calor - Métricas por Sector")
                    metrics_for_heatmap = ['ROE', 'ROA', 'Profit Margin', 'Rev. Growth', 'Return 1Y']
                    heatmap_data = []
                    
                    for sector in filtered_df['Sector'].unique():
                        sector_data = []
                        for metric in metrics_for_heatmap:
                            if metric in filtered_df.columns:
                                value = filtered_df[filtered_df['Sector'] == sector][metric].median()
                                sector_data.append(value)
                            else:
                                sector_data.append(0)
                        heatmap_data.append(sector_data)
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=heatmap_data,
                        x=metrics_for_heatmap,
                        y=filtered_df['Sector'].unique(),
                        colorscale='RdYlGn',
                        text=np.round(heatmap_data, 1),
                        texttemplate='%{text}',
                        textfont={"size": 10},
                        colorbar=dict(title="Valor")
                    ))
                    
                    fig.update_layout(
                        title="Mapa de Calor de Métricas por Sector",
                        template='plotly_dark',
                        height=600
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay datos de sector disponibles")
            
            # TAB 5: ANÁLISIS POR PAÍS
            with result_tabs[4]:
                st.markdown("### 🌍 Análisis Geográfico")
                
                if 'Country' in filtered_df.columns:
                    # Métricas por país
                    country_metrics = filtered_df.groupby('Country').agg({
                        'Symbol': 'count',
                        'Market Cap': 'sum',
                        'Master_Score': 'mean',
                        'PE Ratio': 'median',
                        'ROE': 'median',
                        'Return 1Y': 'median'
                    }).round(2)
                    
                    country_metrics.columns = ['Acciones', 'Cap. Total', 'Score Prom', 
                                            'P/E Med', 'ROE Med', 'Ret. 1A Med']
                    country_metrics = country_metrics.sort_values('Acciones', ascending=False)
                    
                    # Top 20 países
                    st.markdown("##### Top 20 Países por Número de Acciones")
                    top_countries = country_metrics.head(20)
                    
                    # Formatear
                    top_countries_display = top_countries.copy()
                    top_countries_display['Cap. Total'] = top_countries_display['Cap. Total'].apply(
                        lambda x: format_number(x, prefix='$')
                    )
                    
                    st.dataframe(
                        top_countries_display,
                        use_container_width=True,
                        column_config={
                            "Score Prom": st.column_config.ProgressColumn(
                                min_value=0,
                                max_value=100,
                            )
                        }
                    )
                    
                    # Mapa treemap
                    if len(country_metrics) > 1:
                        fig = px.treemap(
                            country_metrics.reset_index(),
                            path=['Country'],
                            values='Acciones',
                            color='Score Prom',
                            color_continuous_scale='RdYlGn',
                            title="Distribución Global de Acciones",
                            hover_data={'Cap. Total': True, 'ROE Med': True}
                        )
                        fig.update_layout(height=500, template='plotly_dark')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay datos de país disponibles")
            
            # TAB 6: CORRELACIONES
            with result_tabs[5]:
                st.markdown("### 📐 Análisis de Correlaciones")
                
                # Seleccionar métricas numéricas clave
                numeric_cols = ['PE Ratio', 'PB Ratio', 'PS Ratio', 'ROE', 'ROA', 'ROIC',
                            'Profit Margin', 'Rev. Growth', 'EPS Growth', 'Debt / Equity',
                            'Current Ratio', 'Return 1Y', 'Div. Yield', 'Beta (5Y)',
                            'Quality_Score', 'Value_Score', 'Growth_Score', 
                            'Financial_Health_Score', 'Momentum_Score', 'Master_Score']
                
                available_numeric = [col for col in numeric_cols if col in filtered_df.columns]
                
                if len(available_numeric) > 2:
                    # Calcular correlaciones
                    corr_matrix = filtered_df[available_numeric].corr()
                    
                    # Heatmap de correlaciones
                    fig = px.imshow(
                        corr_matrix,
                        labels=dict(color="Correlación"),
                        x=available_numeric,
                        y=available_numeric,
                        color_continuous_scale='RdBu',
                        aspect="auto",
                        title="Matriz de Correlación de Métricas Clave"
                    )
                    fig.update_layout(height=700, template='plotly_dark')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Correlaciones más fuertes
                    st.markdown("##### Correlaciones Más Fuertes")
                    
                    # Obtener pares de correlaciones
                    corr_pairs = []
                    for i in range(len(corr_matrix.columns)):
                        for j in range(i+1, len(corr_matrix.columns)):
                            corr_pairs.append({
                                'Métrica 1': corr_matrix.columns[i],
                                'Métrica 2': corr_matrix.columns[j],
                                'Correlación': corr_matrix.iloc[i, j]
                            })
                    
                    corr_df = pd.DataFrame(corr_pairs)
                    corr_df['Correlación Abs'] = corr_df['Correlación'].abs()
                    corr_df = corr_df.sort_values('Correlación Abs', ascending=False).head(20)
                    
                    # Mostrar tabla de correlaciones
                    st.dataframe(
                        corr_df[['Métrica 1', 'Métrica 2', 'Correlación']],
                        use_container_width=True,
                        column_config={
                            "Correlación": st.column_config.NumberColumn(
                                format="%.3f",
                                min_value=-1,
                                max_value=1
                            )
                        }
                    )
                else:
                    st.info("No hay suficientes métricas numéricas para análisis de correlación")
            
            # TAB 7: EXPORTAR
            with result_tabs[6]:
                st.markdown("### 💾 Opciones de Exportación")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📊 Resumen de Exportación</h4>
                        <p><strong>{len(filtered_df):,}</strong> acciones filtradas</p>
                        <p><strong>{len(filtered_df.columns)}</strong> columnas de datos</p>
                        <p><strong>{filtered_df['Country'].nunique() if 'Country' in filtered_df.columns else 0}</strong> países</p>
                        <p><strong>{filtered_df['Sector'].nunique() if 'Sector' in filtered_df.columns else 0}</strong> sectores</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    export_columns = st.multiselect(
                        "Seleccionar columnas para exportar (dejar vacío para todas):",
                        options=list(filtered_df.columns),
                        help="Si no seleccionas ninguna, se exportarán todas las columnas"
                    )
                
                # Preparar dataframe para exportar
                if export_columns:
                    export_df = filtered_df[export_columns]
                else:
                    export_df = filtered_df
                
                # Botones de exportación - REGENERATE FILES EACH TIME
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # CSV - Generate fresh each time
                    @st.cache_data
                    def convert_df_to_csv(df):
                        return df.to_csv(index=False).encode('utf-8')
                    
                    csv_data = convert_df_to_csv(export_df)
                    st.download_button(
                        label="📄 Descargar CSV",
                        data=csv_data,
                        file_name=f"bquant_screener_{date.today().isoformat()}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        help="Formato compatible con Excel y análisis de datos"
                    )
                
                with col2:
                    # Excel - Generate fresh each time
                    @st.cache_data
                    def convert_df_to_excel(df, summary_df):
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, sheet_name='Resultados', index=False)
                            summary_df.to_excel(writer, sheet_name='Resumen', index=False)
                        return output.getvalue()
                    
                    # Create summary data
                    summary_data = pd.DataFrame({
                        'Métrica': ['Total Acciones', 'Países', 'Sectores', 'Cap. Mercado Total',
                                   'P/E Mediano', 'ROE Promedio', 'Score Promedio'],
                        'Valor': [
                            len(filtered_df),
                            filtered_df['Country'].nunique() if 'Country' in filtered_df.columns else 0,
                            filtered_df['Sector'].nunique() if 'Sector' in filtered_df.columns else 0,
                            format_number(filtered_df['Market Cap'].sum() if 'Market Cap' in filtered_df.columns else 0, prefix='$'),
                            f"{filtered_df['PE Ratio'].median():.1f}" if 'PE Ratio' in filtered_df.columns and not filtered_df['PE Ratio'].isna().all() else 'N/D',
                            f"{filtered_df['ROE'].mean():.1f}%" if 'ROE' in filtered_df.columns and not filtered_df['ROE'].isna().all() else 'N/D',
                            f"{filtered_df['Master_Score'].mean():.0f}" if 'Master_Score' in filtered_df.columns and not filtered_df['Master_Score'].isna().all() else 'N/D'
                        ]
                    })
                    
                    excel_data = convert_df_to_excel(export_df, summary_data)
                    st.download_button(
                        label="📊 Descargar Excel",
                        data=excel_data,
                        file_name=f"bquant_screener_{date.today().isoformat()}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        help="Excel con múltiples hojas y formato"
                    )
                
                with col3:
                    # JSON - Generate fresh each time
                    @st.cache_data
                    def convert_df_to_json(df):
                        return df.to_json(orient='records', indent=2)
                    
                    json_data = convert_df_to_json(export_df)
                    st.download_button(
                        label="📋 Descargar JSON",
                        data=json_data,
                        file_name=f"bquant_screener_{date.today().isoformat()}.json",
                        mime="application/json",
                        use_container_width=True,
                        help="Formato para APIs y desarrollo web"
                    )
                
                with col4:
                    # Text Report - Generate fresh each time
                    @st.cache_data
                    def generate_report(df, screener_name):
                        report = "BQUANT GLOBAL SCREENER - REPORTE DE RESULTADOS\n"
                        report += "=" * 50 + "\n"
                        report += f"Fecha: {date.today().isoformat()}\n"
                        report += f"Screener: {screener_name}\n\n"
                        report += "RESUMEN EJECUTIVO\n"
                        report += "-" * 20 + "\n"
                        report += f"Total acciones: {len(df):,}\n"
                        
                        if 'Country' in df.columns:
                            report += f"Países: {df['Country'].nunique()}\n"
                        if 'Sector' in df.columns:
                            report += f"Sectores: {df['Sector'].nunique()}\n"
                        if 'Market Cap' in df.columns:
                            report += f"Cap. Total: {format_number(df['Market Cap'].sum(), prefix='$')}\n"
                        
                        report += "\nTOP 10 ACCIONES\n"
                        report += "-" * 20 + "\n"
                        
                        if 'Master_Score' in df.columns and not df['Master_Score'].isna().all():
                            top10 = df.nlargest(10, 'Master_Score')[['Symbol', 'Company Name', 'Master_Score']]
                            for _, row in top10.iterrows():
                                report += f"{row['Symbol']}: {str(row['Company Name'])[:40]} - Score: {row['Master_Score']:.0f}\n"
                        
                        return report
                    
                    report_data = generate_report(export_df, st.session_state.get('selected_screener', 'Custom'))
                    st.download_button(
                        label="📝 Descargar Reporte",
                        data=report_data,
                        file_name=f"bquant_reporte_{date.today().isoformat()}.txt",
                        mime="text/plain",
                        use_container_width=True,
                        help="Reporte ejecutivo en texto plano"
                    )
        
        elif st.session_state.filters_applied and filtered_df.empty:
            # No results found
            st.warning("⚠️ No se encontraron acciones que cumplan todos los criterios.")
            
            # Provide helpful suggestions based on country selection
            if 'countries_filter' in st.session_state and st.session_state.countries_filter:
                selected_countries = st.session_state.countries_filter
                
                # Check if selected countries have poor data coverage
                country_df = df[df['Country'].isin(selected_countries)]
                sample_metrics = ['PE Ratio', 'ROE', 'Rev. Growth']
                coverage_check = {}
                
                for metric in sample_metrics:
                    if metric in country_df.columns:
                        coverage_check[metric] = (country_df[metric].notna().sum() / len(country_df)) * 100
                
                avg_country_coverage = sum(coverage_check.values()) / len(coverage_check) if coverage_check else 0
                
                if avg_country_coverage < 30:
                    st.error("""
                    🔴 **Problema Detectado: Baja cobertura de datos**
                    
                    Los países seleccionados tienen muy pocos datos disponibles.
                    
                    **Soluciones recomendadas:**
                    1. Reduce significativamente el número de filtros
                    2. Usa solo filtros básicos: Market Cap, Retornos
                    3. Considera cambiar a países con mejor cobertura (USA, UK, Alemania)
                    4. Prueba el screener "Emergentes Básico" diseñado para datos limitados
                    """)
                else:
                    st.info("""
                    💡 **Sugerencias para obtener resultados:**
                    
                    • Reduce el número de filtros aplicados
                    • Amplía los rangos de valores (ej: P/E 0-50 en vez de 10-15)
                    • Verifica que no tengas filtros contradictorios
                    • Prueba con un screener predefinido
                    """)
            else:
                st.info("""
                💡 **Sugerencias para obtener resultados:**
                
                • Reduce el número de filtros aplicados
                • Amplía los rangos de valores
                • Verifica que los países seleccionados tengan datos
                • Prueba con un screener predefinido
                """)
        
        else:
            # Initial state - no filters applied
            st.markdown("""
            <div style='text-align: center; padding: 50px; background: linear-gradient(135deg, rgba(74, 158, 255, 0.1), rgba(147, 51, 234, 0.1)); 
                        border-radius: 20px; border: 2px dashed rgba(74, 158, 255, 0.3);'>
                <h2 style='color: #4a9eff; margin-bottom: 20px;'>👈 Configura los filtros para comenzar</h2>
                <p style='color: #c9d1d9; font-size: 1.1em;'>
                    Selecciona un screener predefinido o crea tu propia estrategia con filtros personalizados.
                    <br><br>
                    Haz clic en <strong>'EJECUTAR'</strong> o <strong>'APLICAR TODOS LOS FILTROS'</strong> para ver los resultados.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show database statistics
            st.markdown("### 📊 Resumen de la Base de Datos")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Acciones", f"{len(df):,}")
            with col2:
                if 'Country' in df.columns:
                    st.metric("Países", f"{df['Country'].nunique()}")
            with col3:
                median_pe = df['PE Ratio'].median() if 'PE Ratio' in df.columns else 0
                st.metric("P/E Mediano Global", f"{median_pe:.1f}")
            with col4:
                total_mcap = df['Market Cap'].sum() if 'Market Cap' in df.columns else 0
                st.metric("Cap. Total", format_number(total_mcap, prefix="$"))
            
            # Top countries chart
            if 'Country' in df.columns:
                st.markdown("### 🌍 Top 10 Países por Número de Acciones")
                top_countries = df['Country'].value_counts().head(10)
                
                fig = px.bar(
                    x=top_countries.values,
                    y=top_countries.index,
                    orientation='h',
                    title="Distribución Global de Acciones",
                    template='plotly_dark',
                    color=top_countries.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

else:
    # Estado inicial cuando no se han aplicado filtros
    with main_tab2:
        st.markdown("""
        <div style='text-align: center; padding: 50px; background: linear-gradient(135deg, rgba(74, 158, 255, 0.1), rgba(147, 51, 234, 0.1)); 
                    border-radius: 20px; border: 2px dashed rgba(74, 158, 255, 0.3);'>
            <h2 style='color: #4a9eff; margin-bottom: 20px;'>👈 Configura los filtros para comenzar</h2>
            <p style='color: #c9d1d9; font-size: 1.1em;'>
                Selecciona un screener predefinido o crea tu propia estrategia con filtros personalizados.
                <br><br>
                Haz clic en <strong>'EJECUTAR'</strong> o <strong>'APLICAR TODOS LOS FILTROS'</strong> para ver los resultados.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar estadísticas de la base de datos
        st.markdown("### 📊 Resumen de la Base de Datos")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Acciones", f"{len(df):,}")
        with col2:
            if 'Country' in df.columns:
                st.metric("Países", f"{df['Country'].nunique()}")
        with col3:
            median_pe = df['PE Ratio'].median() if 'PE Ratio' in df.columns else 0
            st.metric("P/E Mediano Global", f"{median_pe:.1f}")
        with col4:
            total_mcap = df['Market Cap'].sum() if 'Market Cap' in df.columns else 0
            st.metric("Cap. Total", format_number(total_mcap, prefix="$"))
        
        # Top países por número de acciones
        if 'Country' in df.columns:
            st.markdown("### 🌍 Top 10 Países por Número de Acciones")
            top_countries = df['Country'].value_counts().head(10)
            
            fig = px.bar(
                x=top_countries.values,
                y=top_countries.index,
                orientation='h',
                title="Distribución Global de Acciones",
                template='plotly_dark',
                color=top_countries.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(74, 158, 255, 0.05), rgba(147, 51, 234, 0.05)); 
            border-radius: 20px; margin-top: 30px;'>
    <h3 style='color: #4a9eff; margin-bottom: 15px;'>BQuant Global Professional Stock Screener</h3>
    <p style='color: #8b949e;'>
        Desarrollado por <strong style='color: #f0f6fc;'>@Gsnchez</strong> | 
        <strong style='color: #f0f6fc;'>bquantfinance.com</strong><br>
        <small>68,000+ acciones | 89 países | 270+ métricas | Actualizado Septiembre 2025</small>
    </p>
    <div style='margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(74, 158, 255, 0.2);'>
        <small style='color: #6b7280;'>
            💡 Nota: Este screener es una herramienta de análisis. 
            Siempre realiza tu propia investigación antes de invertir.
        </small>
    </div>
</div>
""", unsafe_allow_html=True)

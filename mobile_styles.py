"""
Mobile-friendly responsive CSS utilities for SalesPulse Dashboard
"""
import streamlit as st

def get_responsive_styles():
    """Returns comprehensive responsive CSS for mobile, tablet, and desktop views"""
    return """
    <style>
    /* ═══════════════════════════════════════════════════════════ */
    /* BASE RESPONSIVE TYPOGRAPHY */
    /* ═══════════════════════════════════════════════════════════ */
    
    /* Desktop (> 1024px) */
    h1 { font-size: 32px !important; }
    h2 { font-size: 24px !important; }
    h3 { font-size: 20px !important; }
    p { font-size: 15px !important; }
    
    /* Tablet (768px - 1023px) */
    @media screen and (max-width: 1024px) {
        h1 { font-size: 28px !important; }
        h2 { font-size: 22px !important; }
        h3 { font-size: 18px !important; }
        p { font-size: 14px !important; }
    }
    
    /* Mobile (< 768px) */
    @media screen and (max-width: 768px) {
        h1 { font-size: 24px !important; }
        h2 { font-size: 18px !important; }
        h3 { font-size: 16px !important; }
        p { font-size: 13px !important; }
    }
    
    /* Small Mobile (< 480px) */
    @media screen and (max-width: 480px) {
        h1 { font-size: 20px !important; }
        h2 { font-size: 16px !important; }
        h3 { font-size: 14px !important; }
        p { font-size: 12px !important; }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* CONTAINER & SPACING */
    /* ═══════════════════════════════════════════════════════════ */
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 1rem !important;
    }
    
    @media screen and (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-bottom: 0.5rem !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* KPI CARDS RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════ */
    
    .kpi-card {
        background: linear-gradient(145deg, #0d1117, #111827) !important;
        border: 1px solid #1f2937 !important;
        border-radius: 12px !important;
        padding: 12px 14px !important;
        position: relative !important;
        overflow: hidden !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    
    .kpi-card::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 4px !important;
        height: 100% !important;
        background: linear-gradient(180deg, #6366f1, #8b5cf6) !important;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.15) !important;
    }
    
    .kpi-icon { font-size: 14px !important; margin-bottom: 4px !important; }
    .kpi-label { font-size: 9px !important; font-weight: 600 !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; color: #6b7280 !important; margin-bottom: 2px !important; }
    .kpi-value { font-size: 18px !important; font-weight: 800 !important; color: #f9fafb !important; }
    .kpi-sub { font-size: 10px !important; color: #10b981 !important; margin-top: 3px !important; }
    
    @media screen and (max-width: 768px) {
        .kpi-icon { font-size: 12px !important; }
        .kpi-label { font-size: 8px !important; }
        .kpi-value { font-size: 16px !important; }
        .kpi-sub { font-size: 9px !important; }
    }
    
    @media screen and (max-width: 480px) {
        .kpi-card {
            padding: 10px 12px !important;
        }
        .kpi-icon { font-size: 11px !important; }
        .kpi-label { font-size: 7px !important; }
        .kpi-value { font-size: 14px !important; }
        .kpi-sub { font-size: 8px !important; }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* CHARTS RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════ */
    
    .plotly-container {
        width: 100% !important;
        overflow-x: auto !important;
    }
    
    @media screen and (max-width: 768px) {
        .plotly-container {
            max-width: 100% !important;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* COLUMNS & GRIDS RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════ */
    
    /* Ensure columns wrap properly on mobile */
    @media screen and (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            margin-bottom: 1rem !important;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* FILTERS RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════ */
    
    .filter-row {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    @media screen and (max-width: 768px) {
        .filter-row {
            gap: 0.5rem;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* SELECTBOX & INPUT RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════ */
    
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        width: 100% !important;
    }
    
    @media screen and (max-width: 768px) {
        .stSelectbox > div > div > input,
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            font-size: 14px !important;
            padding: 10px 12px !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        .stSelectbox > div > div > input,
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            font-size: 12px !important;
            padding: 8px 10px !important;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* BUTTON RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════ */
    
    .stButton > button {
        width: 100% !important;
        transition: all 0.2s !important;
    }
    
    @media screen and (max-width: 768px) {
        .stButton > button {
            font-size: 13px !important;
            padding: 10px 14px !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        .stButton > button {
            font-size: 12px !important;
            padding: 8px 12px !important;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* TABLE RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════ */
    
    [role="row"] {
        display: flex;
        flex-wrap: wrap;
    }
    
    @media screen and (max-width: 768px) {
        [data-testid="stDataFrame"] {
            font-size: 11px !important;
        }
        [data-testid="stDataFrame"] th,
        [data-testid="stDataFrame"] td {
            padding: 6px 8px !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        [data-testid="stDataFrame"] {
            font-size: 10px !important;
        }
        [data-testid="stDataFrame"] th,
        [data-testid="stDataFrame"] td {
            padding: 4px 6px !important;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* SIDEBAR RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════ */
    
    section[data-testid="stSidebar"] {
        z-index: 999 !important;
        transition: width 0.3s ease !important;
    }
    
    @media screen and (max-width: 768px) {
        section[data-testid="stSidebar"] {
            width: 45px !important;
            min-width: 45px !important;
            max-width: 45px !important;
        }
        section[data-testid="stSidebar"]:hover {
            width: 180px !important;
            min-width: 180px !important;
            max-width: 180px !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        section[data-testid="stSidebar"] {
            width: 40px !important;
            min-width: 40px !important;
            max-width: 40px !important;
        }
        section[data-testid="stSidebar"]:hover {
            width: 160px !important;
            min-width: 160px !important;
            max-width: 160px !important;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* METRICS RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════ */
    
    @media screen and (max-width: 768px) {
        [data-testid="metric-container"] {
            flex: 1 1 calc(50% - 0.5rem) !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        [data-testid="metric-container"] {
            flex: 1 1 100% !important;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════ */
    /* EXPANDERS RESPONSIVE */
    /* ═══════════════════════════════════════════════════════════ */
    
    .streamlit-expanderHeader {
        transition: all 0.2s !important;
    }
    
    @media screen and (max-width: 768px) {
        .streamlit-expanderHeader {
            font-size: 13px !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        .streamlit-expanderHeader {
            font-size: 12px !important;
        }
    }
    </style>
    """

def apply_mobile_styles():
    """Apply mobile-responsive styles to the app"""
    st.markdown(get_responsive_styles(), unsafe_allow_html=True)


# Helper function to create responsive metric columns
def create_responsive_columns(num_cols=3):
    """
    Create responsive columns that stack on mobile
    
    Usage:
        cols = create_responsive_columns(3)
        with cols[0]:
            st.metric("Label", "Value")
    """
    if 1100 > 768:  # Mobile
        return st.columns(1)
    elif 1100 > 1024:  # Tablet
        return st.columns(2)
    else:  # Desktop
        return st.columns(num_cols)

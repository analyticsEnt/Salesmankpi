import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

@st.cache_resource
def get_engine():
    host     = "db34081.public.databaseasp.net"
    port     = 3306
    database = "db34081"
    username = "db34081"
    password = quote_plus(st.secrets["DB_PASSWORD"])
    return create_engine(
        f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}",
        pool_pre_ping=True, pool_recycle=3600,
    )

NUMERIC_COLS = [
    'Target', 'LM_Target', 'Current_Month', 'LMTD_Sales', 'Forcast',
    'Forcast_ACh_age', 'LMTD_Ach_age', 'Cx_Mapped', 'CMACX',
    'Salesage_From_TOP_10_CX', 'Salesage_From_TOP_25_CX',
    'CM_Daily_Ordering_CX', 'CM_Daily_Ordering_CX_age', 'LM_Daily_Ordering_CX',
    'Churned_CX', 'LMTD_Sales_Churned_cx', 'Degrowth_CX', 'Growth_CX',
    'Revived_CX', 'Revived_Cx_Sales', 'Revived_Cx_Sales_age',
    'New_CX', 'New_Cx_Sales', 'New_Cx_Sales_age',
    'Total_Outstanding', 'Overdue_Value', 'OD_age', 'CX_Locked',
]

@st.cache_data(ttl=300, show_spinner=False)
def load_data(role, region, unit, asm_code):
    engine = get_engine()
    df = pd.read_sql_table("area_sales_man", engine)

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'Created_At' in df.columns:
        df['Created_At'] = pd.to_datetime(df['Created_At'], errors='coerce')

    if role != 'Admin':
        if region != 'ALL' and 'Region' in df.columns:
            df = df[df['Region'] == region]
        if unit != 'ALL' and 'Unit' in df.columns:
            df = df[df['Unit'] == unit]
        if asm_code != 'ALL' and 'ASM_Code' in df.columns:
            df = df[df['ASM_Code'] == asm_code]

    return df


def fmt_amt(n):
    """Money-style values: 291.1m, 20.3k, plain otherwise (no currency symbol, matches sample)."""
    if pd.isna(n):
        return "0.0"
    n = float(n)
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}m"
    if abs(n) >= 1_000:
        return f"{n/1_000:.1f}k"
    return f"{n:.1f}"

def fmt_count(n):
    """Count-style values: 20.3k if >=1000, else plain one-decimal."""
    if pd.isna(n):
        return "0.0"
    n = float(n)
    if abs(n) >= 1_000:
        return f"{n/1_000:.1f}k"
    return f"{n:.1f}"

def fmt_pct(n):
    if pd.isna(n):
        return "0.0"
    return f"{n:.1f}"

def safe_div(numer, denom):
    return (numer / denom * 100) if denom else 0.0

def weighted_avg(df, value_col, weight_col):
    """Used ONLY for the 3 % metrics we can't exactly recompute from raw
    sums (Sales% Top10/25 CX, CM Daily Ordering CX %) — the source formula
    for these needs data (e.g. working-days elapsed) not present in this
    table, so this is a weighted-average approximation, not an exact figure."""
    if len(df) == 0:
        return 0.0
    w = df[weight_col]
    if w.sum() == 0:
        return df[value_col].mean()
    return (df[value_col] * w).sum() / w.sum()


def show():
    st.markdown("""
    <style>
    .kpi-card {
        background:linear-gradient(145deg,#0d1117,#111827);
        border:1px solid #1f2937; border-radius:12px;
        padding:12px 10px; position:relative; overflow:hidden;
        transition:transform 0.2s,box-shadow 0.2s;
    }
    .kpi-card::before {
        content:''; position:absolute; top:0; left:0;
        width:4px; height:100%;
        background:var(--accent, linear-gradient(180deg,#6366f1,#8b5cf6));
    }
    .kpi-card:hover { transform:translateY(-3px); box-shadow:0 12px 30px rgba(99,102,241,0.15); }
    .kpi-label { font-size:10px; font-weight:600; letter-spacing:1px; text-transform:uppercase; color:#6b7280; margin-bottom:4px; }
    .kpi-value { font-size:20px; font-weight:800; color:#f9fafb; }

    .kpi-green  { --accent: linear-gradient(180deg,#10b981,#059669); }
    .kpi-green  .kpi-value { color:#34d399; }
    .kpi-orange { --accent: linear-gradient(180deg,#f59e0b,#d97706); }
    .kpi-orange .kpi-value { color:#fbbf24; }
    .kpi-red    { --accent: linear-gradient(180deg,#ef4444,#dc2626); }
    .kpi-red    .kpi-value { color:#f87171; }
    .kpi-blue   { --accent: linear-gradient(180deg,#3b82f6,#2563eb); }
    .kpi-blue   .kpi-value { color:#60a5fa; }

    .period-banner {
        background:linear-gradient(135deg,#0d1117,#111827);
        border:1px solid #1f2937; border-left:4px solid #6366f1;
        border-radius:14px; padding:12px 20px; margin-bottom:18px;
        display:flex; gap:36px; align-items:center; flex-wrap:wrap;
    }
    .pb-label { font-size:10px; font-weight:600; letter-spacing:1px; text-transform:uppercase; color:#6b7280; margin-bottom:2px; }
    .pb-value  { font-size:13px; font-weight:700; color:#a5b4fc; }
    </style>
    """, unsafe_allow_html=True)

    full_name = st.session_state.get('full_name', 'User')
    role      = st.session_state.get('role', 'ASM')
    region    = st.session_state.get('region', 'ALL')
    unit      = st.session_state.get('unit', 'ALL')
    asm_code  = st.session_state.get('asm_code', 'ALL')

    with st.spinner("Loading data..."):
        df_full = load_data(role, region, unit, asm_code)

    # ── Header ────────────────────────────────────────────────────
    title_col, banner_col = st.columns([2.4, 3.6])
    with title_col:
        st.markdown(
            "<div style='font-size:26px;font-weight:800;color:#f9fafb;margin-bottom:4px;'>📊 Sales Analysis</div>",
            unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:13px;color:#6b7280;margin-bottom:14px;'>"
            f"Welcome back, {full_name} • {role} • Region: {region} • Unit: {unit}</div>",
            unsafe_allow_html=True)

    # ── Filters: Region / Unit / Area Sales Man (cascading) ─────────
    filt_cols = st.columns([1.5, 1.8, 2.7])

    if 'Region' in df_full.columns and role == 'Admin':
        sel_regions = filt_cols[0].multiselect(
            "Region", sorted(df_full['Region'].dropna().unique().tolist()),
            default=[], placeholder="All Regions", key="s_reg")
    else:
        sel_regions = []

    unit_pool = df_full.copy()
    if sel_regions and 'Region' in unit_pool.columns:
        unit_pool = unit_pool[unit_pool['Region'].isin(sel_regions)]

    if 'Unit' in df_full.columns:
        sel_units = filt_cols[1].multiselect(
            "Unit", sorted(unit_pool['Unit'].dropna().unique().tolist()),
            default=[], placeholder="All Units", key="s_unit")
    else:
        sel_units = []

    asm_pool = unit_pool.copy()
    if sel_units and 'Unit' in asm_pool.columns:
        asm_pool = asm_pool[asm_pool['Unit'].isin(sel_units)]

    if 'Area_Sales_Man' in df_full.columns:
        sel_asms = filt_cols[2].multiselect(
            "Area Sales Man", sorted(asm_pool['Area_Sales_Man'].dropna().unique().tolist()),
            default=[], placeholder="All ASMs", key="s_asm")
    else:
        sel_asms = []

    # ── Apply filters ────────────────────────────────────────────────
    df = df_full.copy()
    if sel_regions and 'Region' in df.columns:
        df = df[df['Region'].isin(sel_regions)]
    if sel_units and 'Unit' in df.columns:
        df = df[df['Unit'].isin(sel_units)]
    if sel_asms and 'Area_Sales_Man' in df.columns:
        df = df[df['Area_Sales_Man'].isin(sel_asms)]

    # ── "Updated As On" = latest Created_At in the filtered data ────
    if 'Created_At' in df.columns and df['Created_At'].notna().any():
        updated_as_on = df['Created_At'].max().strftime('%d %b %Y, %I:%M %p')
    else:
        updated_as_on = "N/A"

    user_text = f"{full_name} ({role} • {region} • {unit})"
    banner_col.markdown(f"""
    <div class="period-banner" style="margin-top:6px;">
        <div><div class="pb-label">📅 Updated As On</div>
        <div class="pb-value">{updated_as_on}</div></div>
        <div><div class="pb-label">👤 User</div>
        <div class="pb-value">{user_text}</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if len(df) == 0:
        st.warning("No data matches the selected filters.")
        return

    # ── Aggregate metrics ─────────────────────────────────────────
    s = lambda col: df[col].sum() if col in df.columns else 0.0

    target        = s('Target')
    lm_target     = s('LM_Target')
    current_month = s('Current_Month')
    lmtd_sales    = s('LMTD_Sales')
    forcast       = s('Forcast')
    cx_mapped     = s('Cx_Mapped')
    cmacx         = s('CMACX')
    cm_daily      = s('CM_Daily_Ordering_CX')
    lm_daily      = s('LM_Daily_Ordering_CX')
    churned_cx    = s('Churned_CX')
    lmtd_churned  = s('LMTD_Sales_Churned_cx')
    degrowth_cx   = s('Degrowth_CX')
    growth_cx     = s('Growth_CX')
    revived_cx    = s('Revived_CX')
    revived_sales = s('Revived_Cx_Sales')
    new_cx        = s('New_CX')
    new_cx_sales  = s('New_Cx_Sales')
    total_od      = s('Total_Outstanding')
    overdue       = s('Overdue_Value')
    cx_locked     = s('CX_Locked')

    # Exact recomputations (verified against raw source formulas)
    ach_pct           = safe_div(current_month, target)
    forcast_ach_pct   = safe_div(forcast, target)
    lmtd_ach_pct      = safe_div(lmtd_sales, lm_target)
    revived_sales_pct = safe_div(revived_sales, current_month)
    new_sales_pct     = safe_div(new_cx_sales, current_month)
    od_pct            = safe_div(overdue, total_od)

    # Approximated (weighted average) — see weighted_avg() docstring
    top10_pct = weighted_avg(df, 'Salesage_From_TOP_10_CX', 'Current_Month') if 'Salesage_From_TOP_10_CX' in df.columns else 0.0
    top25_pct = weighted_avg(df, 'Salesage_From_TOP_25_CX', 'Current_Month') if 'Salesage_From_TOP_25_CX' in df.columns else 0.0
    cm_daily_pct = weighted_avg(df, 'CM_Daily_Ordering_CX_age', 'CMACX') if 'CM_Daily_Ordering_CX_age' in df.columns else 0.0

    # ── Render KPI grid — 4 rows x 7 metrics, matching the sample layout ──
    row1 = [
        ("kpi-green", "Target",        fmt_amt(target)),
        ("kpi-green", "Current Month", fmt_amt(current_month)),
        ("kpi-green", "Ach %",         fmt_pct(ach_pct)),
        ("kpi-green", "Forcast",       fmt_amt(forcast)),
        ("kpi-green", "Forcast Ach %", fmt_pct(forcast_ach_pct)),
        ("kpi-green", "LMTD Sales",    fmt_amt(lmtd_sales)),
        ("kpi-green", "LMTD Ach %",    fmt_pct(lmtd_ach_pct)),
    ]
    row2 = [
        ("kpi-orange", "Cx Mapped",              fmt_count(cx_mapped)),
        ("kpi-orange", "Active Customer",        fmt_count(cmacx)),
        ("kpi-orange", "Sales% From TOP 10 CX",  fmt_pct(top10_pct)),
        ("kpi-orange", "Sales% From TOP 25 CX",  fmt_pct(top25_pct)),
        ("kpi-orange", "CM Daily Ordering CX",   fmt_count(cm_daily)),
        ("kpi-orange", "CM Daily Ordering CX %", fmt_pct(cm_daily_pct)),
        ("kpi-orange", "LM Daily Ordering CX",   fmt_count(lm_daily)),
    ]
    row3 = [
        ("kpi-red", "Churned CX",             fmt_count(churned_cx)),
        ("kpi-red", "LMTD Sales Churned_cx",  fmt_amt(lmtd_churned)),
        ("kpi-red", "Degrowth CX",            fmt_count(degrowth_cx)),
        ("kpi-red", "Growth CX",              fmt_count(growth_cx)),
        ("kpi-red", "Revived CX",             fmt_count(revived_cx)),
        ("kpi-red", "Revived Cx Sales",       fmt_amt(revived_sales)),
        ("kpi-red", "Revived Cx Sales %",     fmt_pct(revived_sales_pct)),
    ]
    row4 = [
        ("kpi-blue", "New CX",              fmt_count(new_cx)),
        ("kpi-blue", "New Cx Sales",        fmt_amt(new_cx_sales)),
        ("kpi-blue", "New Cx Sales %",      fmt_pct(new_sales_pct)),
        ("kpi-blue", "Total Outstanding",   fmt_amt(total_od)),
        ("kpi-blue", "Overdue Value",       fmt_amt(overdue)),
        ("kpi-blue", "OD %",                fmt_pct(od_pct)),
        ("kpi-blue", "CX_Locked",           fmt_count(cx_locked)),
    ]

    for row in [row1, row2, row3, row4]:
        cols = st.columns(7)
        for col, (cls, label, val) in zip(cols, row):
            col.markdown(f"""
            <div class="kpi-card {cls}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
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
    'Current_Month', 'Sales_Deficit', 'Total_Outstanding', 'Overdue_Value',
    '30_Days', '31_to_60', '61_to_90', 'G90',
]

@st.cache_data(ttl=300, show_spinner=False)
def load_data(role, region, unit, asm_code):
    engine = get_engine()
    df = pd.read_sql_table("customer_wise", engine)

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if role != 'Admin':
        if region != 'ALL' and 'Region' in df.columns:
            df = df[df['Region'] == region]
        if unit != 'ALL' and 'Unit' in df.columns:
            df = df[df['Unit'] == unit]
        if asm_code != 'ALL' and 'ASM_Code' in df.columns:
            df = df[df['ASM_Code'] == asm_code]

    return df


def fmt_inr(n):
    """Rupee amount using Indian digit grouping (lakh/crore style),
    e.g. 3789468 -> ₹37,89,468 -- matches the sample screenshot exactly."""
    if pd.isna(n):
        n = 0
    n = int(round(n))
    neg = n < 0
    n = abs(n)
    s = str(n)
    if len(s) <= 3:
        grouped = s
    else:
        last3 = s[-3:]
        rest = s[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        grouped = ",".join(parts) + "," + last3
    return ("-" if neg else "") + "₹" + grouped

def fmt_count(n):
    if pd.isna(n):
        return "0"
    return f"{int(n):,}"

def fmt_pct(n):
    if pd.isna(n):
        return "0%"
    return f"{round(n)}%"

def safe_pct(numer, denom):
    return (numer / denom * 100) if denom else 0.0


def show():
    st.markdown("""
    <style>
    /* ─── Force filter rows onto one line even on mobile ──────────
       Same marker + :has() technique used on the Sales page: targets
       ONLY the wrapped filter row, overriding Streamlit's default
       column-stacking behavior below ~768px. */
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-marker) [data-testid="stHorizontalBlock"] {
        display: grid !important;
        gap: 10px !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-marker) [data-testid="stColumn"] {
        width: auto !important;
        min-width: 0 !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-3) [data-testid="stHorizontalBlock"] {
        grid-template-columns: 1fr 1fr 1fr !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-4) [data-testid="stHorizontalBlock"] {
        grid-template-columns: 1fr 1fr !important;
    }
    @media screen and (min-width: 900px) {
        div[data-testid="stVerticalBlock"]:has(> div .filter-row-4) [data-testid="stHorizontalBlock"] {
            grid-template-columns: 1fr 1fr 1fr 1fr !important;
        }
    }

    /* ─── Section title ──────────────────────────────────────────── */
    .sec-title {
        font-size: 15px; font-weight: 800; color: #f3f4f6;
        margin: 18px 0 10px 0; padding: 0;
    }

    /* ─── Responsive KPI grid (same pattern as the Sales page) ─────
       CSS Grid reflows on its own -- 7 across on desktop, fewer on
       narrower screens -- instead of a wide HTML table that can't
       reflow at all on mobile. Font sizes use clamp() so text
       auto-shrinks/grows with the available card width. */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 10px;
        margin-bottom: 8px;
    }
    .kpi-card {
        background:linear-gradient(145deg,#0d1117,#111827);
        border:1px solid #1f2937; border-radius:12px;
        padding:10px 8px; position:relative; overflow:hidden;
        transition:transform 0.2s,box-shadow 0.2s;
    }
    .kpi-card::before {
        content:''; position:absolute; top:0; left:0;
        width:4px; height:100%;
        background:var(--accent, linear-gradient(180deg,#6366f1,#8b5cf6));
    }
    .kpi-card:hover { transform:translateY(-3px); box-shadow:0 12px 30px rgba(99,102,241,0.15); }
    .kpi-label {
        font-size: clamp(8px, 1.6vw, 10px);
        font-weight: 600; letter-spacing: 0.6px; text-transform: uppercase;
        color: #6b7280; margin-bottom: 4px; line-height: 1.25;
        overflow-wrap: normal; word-break: keep-all; hyphens: none;
    }
    .kpi-value {
        font-size: clamp(13px, 3.2vw, 19px);
        font-weight: 800; color: #f9fafb; line-height: 1.1;
    }
    .kpi-orange { --accent: linear-gradient(180deg,#f59e0b,#d97706); }
    .kpi-orange .kpi-value { color:#fbbf24; }
    .kpi-green  { --accent: linear-gradient(180deg,#10b981,#059669); }
    .kpi-green  .kpi-value { color:#34d399; }
    .kpi-highlight .kpi-value { color:#f87171 !important; }

    @media screen and (max-width: 1100px) {
        .kpi-grid { grid-template-columns: repeat(4, 1fr); }
    }
    @media screen and (max-width: 768px) {
        .kpi-grid { grid-template-columns: repeat(3, 1fr); gap: 7px; }
        .kpi-card { padding: 8px 6px; }
    }
    @media screen and (max-width: 480px) {
        .kpi-grid { grid-template-columns: repeat(3, 1fr); gap: 5px; }
        .kpi-card { padding: 7px 5px; border-radius: 9px; }
        .kpi-card::before { width: 3px; }
        .kpi-label { font-size: clamp(6.5px, 2.1vw, 8px); margin-bottom: 2px; }
        .kpi-value { font-size: clamp(11px, 3.6vw, 15px); }
    }
    </style>
    """, unsafe_allow_html=True)

    full_name = st.session_state.get('full_name', 'User')
    role      = st.session_state.get('role', 'ASM')
    region    = st.session_state.get('region', 'ALL')
    unit      = st.session_state.get('unit', 'ALL')
    asm_code  = st.session_state.get('asm_code', 'ALL')

    with st.spinner("Loading data..."):
        df_full = load_data(role, region, unit, asm_code)

    # ── Region + Unit + ASM filters (forced onto one row) ───────────
    with st.container():
        st.markdown('<div class="filter-row-marker filter-row-3" style="display:none;"></div>', unsafe_allow_html=True)
        f1 = st.columns([1, 1, 1, 1])

        if 'Region' in df_full.columns and role == 'Admin':
            sel_regions = f1[0].multiselect(
                "Region", sorted(df_full['Region'].dropna().unique().tolist()),
                default=[], placeholder="All Regions", key="cw_reg")
        else:
            sel_regions = []

        unit_pool = df_full.copy()
        if sel_regions and 'Region' in unit_pool.columns:
            unit_pool = unit_pool[unit_pool['Region'].isin(sel_regions)]

        if 'Unit' in df_full.columns:
            sel_units = f1[1].multiselect(
                "Unit", sorted(unit_pool['Unit'].dropna().unique().tolist()),
                default=[], placeholder="All Units", key="cw_unit")
        else:
            sel_units = []

        asm_pool = unit_pool.copy()
        if sel_units and 'Unit' in asm_pool.columns:
            asm_pool = asm_pool[asm_pool['Unit'].isin(sel_units)]

        if 'Area_Sales_Man' in df_full.columns:
            sel_asms = f1[2].multiselect(
                "Area Sales Man", sorted(asm_pool['Area_Sales_Man'].dropna().unique().tolist()),
                default=[], placeholder="All ASMs", key="cw_asm")
        else:
            sel_asms = []


        asm_pool = unit_pool.copy()
        if sel_units and 'Unit' in asm_pool.columns:
            asm_pool = asm_pool[asm_pool['Unit'].isin(sel_units)]

        if 'Area_Sales_Man' in df_full.columns:
            sel_asms = f1[3].multiselect(
                "Area Sales Man", sorted(asm_pool['Area_Sales_Man'].dropna().unique().tolist()),
                default=[], placeholder="All ASMs", key="cw_asm")
        else:
            sel_asms = []

    # ── Customer_Type / Mis_Remarks / Reason / Receivables_Health ───
    detail_pool = asm_pool.copy()
    if sel_asms and 'Area_Sales_Man' in detail_pool.columns:
        detail_pool = detail_pool[detail_pool['Area_Sales_Man'].isin(sel_asms)]

    with st.container():
        st.markdown('<div class="filter-row-marker filter-row-4" style="display:none;"></div>', unsafe_allow_html=True)
        f2 = st.columns([1, 1, 1, 1])

        sel_cust_type = f2[0].multiselect(
            "Customer_Type", sorted(detail_pool['Customer_Type'].dropna().unique().tolist()),
            default=[], placeholder="Customer_Type", key="cw_custtype") if 'Customer_Type' in detail_pool.columns else []

        sel_mis = f2[1].multiselect(
            "Mis Remarks", sorted(detail_pool['Mis_Remarks'].dropna().unique().tolist()),
            default=[], placeholder="Mis Remarks", key="cw_mis") if 'Mis_Remarks' in detail_pool.columns else []

        sel_reason = f2[2].multiselect(
            "Reason", sorted(detail_pool['Reason'].dropna().unique().tolist()),
            default=[], placeholder="Reason", key="cw_reason") if 'Reason' in detail_pool.columns else []

        sel_recv = f2[3].multiselect(
            "Receivables Health", sorted(detail_pool['Receivables_Health'].dropna().unique().tolist()),
            default=[], placeholder="Receivables H...", key="cw_recv") if 'Receivables_Health' in detail_pool.columns else []
        

    # ── Apply all filters ────────────────────────────────────────────
    df = df_full.copy()
    if sel_regions and 'Region' in df.columns:
        df = df[df['Region'].isin(sel_regions)]
    if sel_units and 'Unit' in df.columns:
        df = df[df['Unit'].isin(sel_units)]
    if sel_asms and 'Area_Sales_Man' in df.columns:
        df = df[df['Area_Sales_Man'].isin(sel_asms)]
    if sel_cust_type and 'Customer_Type' in df.columns:
        df = df[df['Customer_Type'].isin(sel_cust_type)]
    if sel_mis and 'Mis_Remarks' in df.columns:
        df = df[df['Mis_Remarks'].isin(sel_mis)]
    if sel_reason and 'Reason' in df.columns:
        df = df[df['Reason'].isin(sel_reason)]
    if sel_recv and 'Receivables_Health' in df.columns:
        df = df[df['Receivables_Health'].isin(sel_recv)]

    if len(df) == 0:
        st.warning("No data matches the selected filters.")
        return
    # ══════════════════════════════════════════════════════════════
    # TABLE 1 — Customer Sales & Outstanding Detail
    # ══════════════════════════════════════════════════════════════
    st.markdown("<div class='sec-title'>Customer Sales &amp; Outstanding</div>", unsafe_allow_html=True)

    t1_rename = {
        'CustCode': 'CustCode',
        'Customer': 'Customer',
        'LMTD_Sales': 'LMTD Sales',
        'Current_Month': 'Current Month',
        'CmtdSku': 'CmtdSku',
        'LlmtdSku': 'LlmtdSku',
        'T10SkuVConage': 'T10SkuVCon%',
        'T25SkuVConage': 'T25SkuVCon%',
        'Total_Outstanding': 'OS',
        'Overdue_Value': 'OD',
        'Receivable_Days': 'Receivable Days',
        'ODage': 'OD%',
    }
    t1_cols = [c for c in t1_rename if c in df.columns]
    table1_df = df[t1_cols].rename(columns=t1_rename).reset_index(drop=True)

    event1 = st.dataframe(
        table1_df.head(500), use_container_width=True, hide_index=True,
        on_select="rerun", selection_mode="single-row", key="cm_table1",
    )

    if len(df) > 500:
        st.caption(f"Showing first 500 of {len(df):,} matching rows.")

    # Determine which customer (if any) was clicked in Table 1
    selected_custcode = None
    if event1 and event1.selection and event1.selection.rows:
        row_idx = event1.selection.rows[0]
        selected_custcode = table1_df.iloc[row_idx]['CustCode']

    # ══════════════════════════════════════════════════════════════
    # TABLE 2 — Growth Opportunity Detail (filtered by Table 1 click)
    # ══════════════════════════════════════════════════════════════
    st.markdown("<div class='sec-title'>Growth Opportunity</div>", unsafe_allow_html=True)

    if selected_custcode is not None:
        st.markdown(
            f"<div style='font-size:12px;color:#a5b4fc;margin-bottom:6px;'>"
            f"Showing details for the customer selected in the table above "
            f"(CustCode: <b>{selected_custcode}</b>).</div>",
            unsafe_allow_html=True)
        table2_source = df[df['CustCode'] == selected_custcode] if 'CustCode' in df.columns else df
    else:
        st.markdown(
            "<div style='font-size:12px;color:#6b7280;margin-bottom:6px;'>"
            "Click a row in the table above to filter this to a single customer.</div>",
            unsafe_allow_html=True)
        table2_source = df

    t2_rename = {
        'CX_Code': 'CX_Code',
        'Customer': 'Customer',
        'MktBy_Max': 'Large Company',
        'Max_Sku': 'Large Sku',
        'SKU_vicinity': 'Sku Opportunity',
        'Manufacture_vicinity': 'Manufacture Opportunity',
    }
    t2_cols = [c for c in t2_rename if c in table2_source.columns]
    table2_df = table2_source[t2_cols].rename(columns=t2_rename).reset_index(drop=True)

    st.dataframe(table2_df.head(500), use_container_width=True, hide_index=True)
    if len(table2_source) > 500:
        st.caption(f"Showing first 500 of {len(table2_source):,} matching rows.")
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

    /* ─── Section title, zero margin so it sits flush on the table ── */
    .sec-title {
        font-size: 15px; font-weight: 800; color: #f3f4f6;
        margin: 18px 0 0 0; padding: 0;
    }

    /* ─── Summary tables (matches the sample screenshot structure) ── */
    .summary-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0 0 4px 0;
        table-layout: fixed;
        font-size: 12.5px;
    }
    .summary-table td {
        border: 1px solid #1f2937;
        padding: 8px 6px;
        text-align: center;
        vertical-align: middle;
        color: #e5e7eb;
        word-wrap: break-word;
    }
    .summary-table .title-cell {
        color: #ffffff;
        font-weight: 800;
        font-size: 13px;
        line-height: 1.3;
    }
    .summary-table .col-header {
        font-weight: 700;
        font-size: 10.5px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .summary-table .col-value {
        font-weight: 800;
        font-size: 15px;
    }
    .summary-table.orange .title-cell { background: #b45309; }
    .summary-table.orange .col-header { background: rgba(217,119,6,0.15); color: #fbbf24; }
    .summary-table.orange .col-value  { background: rgba(217,119,6,0.05); }
    .summary-table.orange .highlight { color: #f87171; }

    .summary-table.green .title-cell { background: #047857; }
    .summary-table.green .col-header { background: rgba(16,185,129,0.15); color: #34d399; }
    .summary-table.green .col-value  { background: rgba(16,185,129,0.05); }
    .summary-table.green .highlight  { color: #f87171; }

    @media screen and (max-width: 768px) {
        .summary-table { font-size: 10px; }
        .summary-table td { padding: 6px 3px; }
        .summary-table .title-cell { font-size: 11px; }
        .summary-table .col-header { font-size: 8.5px; }
        .summary-table .col-value { font-size: 12px; }
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
        f1 = st.columns([1, 1, 1])

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
    # SECTION 1 — Customer Trends & Business Impact
    # ══════════════════════════════════════════════════════════════
    total_customers = df['CustCode'].count() if 'CustCode' in df.columns else len(df)
    customers_ordered = (df['Current_Month'] > 0).sum() if 'Current_Month' in df.columns else 0
    ordered_pct = safe_pct(customers_ordered, total_customers)

    churn_this_month = (df['Mis_Remarks'] == '1.Churn This Month').sum() if 'Mis_Remarks' in df.columns else 0
    churn_this_month_pct = safe_pct(churn_this_month, total_customers)

    churn_gt1_month = (df['Mis_Remarks'] == 'Churned').sum() if 'Mis_Remarks' in df.columns else 0
    churn_gt1_month_pct = safe_pct(churn_gt1_month, total_customers)

    degrowth_customers = (df['Mis_Remarks'] == 'Degrowth').sum() if 'Mis_Remarks' in df.columns else 0
    degrowth_pct = safe_pct(degrowth_customers, total_customers)

    shortfall_mask = df['Mis_Remarks'].isin(['Degrowth', '1.Churn This Month']) if 'Mis_Remarks' in df.columns else pd.Series([], dtype=bool)
    sales_shortfall = df.loc[shortfall_mask, 'Sales_Deficit'].sum() if 'Sales_Deficit' in df.columns else 0

    st.markdown("<div class='sec-title'>Customer Trends &amp; Business Impact</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <table class="summary-table orange">
        <tr>
            <td rowspan="2" class="title-cell" style="width:11%;">Customer Trends<br>&amp; Business Impact</td>
            <td class="col-header">Total Customers</td>
            <td class="col-header">Customers Ordered</td>
            <td class="col-header">Ordered %</td>
            <td class="col-header">CHURN This Month</td>
            <td class="col-header">% CMR Churn this Month</td>
            <td class="col-header">CHUN &gt; 1 month</td>
            <td class="col-header">% CHUN &gt; 1 month</td>
            <td class="col-header">Degrown Customers</td>
            <td class="col-header">Degrown%</td>
            <td class="col-header">Short fall of Sales</td>
        </tr>
        <tr>
            <td class="col-value">{fmt_count(total_customers)}</td>
            <td class="col-value">{fmt_count(customers_ordered)}</td>
            <td class="col-value">{fmt_pct(ordered_pct)}</td>
            <td class="col-value">{fmt_count(churn_this_month)}</td>
            <td class="col-value">{fmt_pct(churn_this_month_pct)}</td>
            <td class="col-value">{fmt_count(churn_gt1_month)}</td>
            <td class="col-value">{fmt_pct(churn_gt1_month_pct)}</td>
            <td class="col-value">{fmt_count(degrowth_customers)}</td>
            <td class="col-value">{fmt_pct(degrowth_pct)}</td>
            <td class="col-value highlight">{fmt_inr(sales_shortfall)}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # SECTION 2 — Outstanding
    # ══════════════════════════════════════════════════════════════
    total_outstanding = df['Total_Outstanding'].sum() if 'Total_Outstanding' in df.columns else 0

    cx_gt90 = (df['G90'] > 0).sum() if 'G90' in df.columns else 0
    os_gt90 = df['G90'].sum() if 'G90' in df.columns else 0
    os_gt90_pct = safe_pct(os_gt90, total_outstanding)

    os_60_90 = df['61_to_90'].sum() if '61_to_90' in df.columns else 0
    os_60_90_pct = safe_pct(os_60_90, total_outstanding)

    os_30_60 = df['31_to_60'].sum() if '31_to_60' in df.columns else 0
    os_30_60_pct = safe_pct(os_30_60, total_outstanding)

    os_0_30 = df['30_Days'].sum() if '30_Days' in df.columns else 0
    os_0_30_pct = safe_pct(os_0_30, total_outstanding)

    st.markdown("<div class='sec-title'>Outstanding</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <table class="summary-table green">
        <tr>
            <td rowspan="2" class="title-cell" style="width:11%;">Outstanding</td>
            <td class="col-header">#customers with &gt;90 Days</td>
            <td class="col-header">OS Value &gt;90 Days</td>
            <td class="col-header">%</td>
            <td class="col-header">OS Value 60-90 Days</td>
            <td class="col-header">%</td>
            <td class="col-header">OS Value 30-60 Days</td>
            <td class="col-header">%</td>
            <td class="col-header">OS Value 0-30 Days</td>
            <td class="col-header">%</td>
            <td class="col-header">Total Outstanding</td>
        </tr>
        <tr>
            <td class="col-value">{fmt_count(cx_gt90)}</td>
            <td class="col-value highlight">{fmt_inr(os_gt90)}</td>
            <td class="col-value">{fmt_pct(os_gt90_pct)}</td>
            <td class="col-value highlight">{fmt_inr(os_60_90)}</td>
            <td class="col-value">{fmt_pct(os_60_90_pct)}</td>
            <td class="col-value">{fmt_inr(os_30_60)}</td>
            <td class="col-value">{fmt_pct(os_30_60_pct)}</td>
            <td class="col-value">{fmt_inr(os_0_30)}</td>
            <td class="col-value">{fmt_pct(os_0_30_pct)}</td>
            <td class="col-value">{fmt_inr(total_outstanding)}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
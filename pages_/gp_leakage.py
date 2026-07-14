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
    'Current_Month', 'LMTD_Sales', 'CmtdSku', 'LlmtdSku',
    'T10SkuVConage', 'T25SkuVConage', 'Total_Outstanding', 'Overdue_Value',
    'Receivable_Days', 'OSage', 'ODage',
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


def show():
    st.markdown("""
    <style>
    /* ─── Force filter rows onto one line even on mobile ──────────
       Marker + :has() technique: targets ONLY the wrapped filter
       row, overriding Streamlit's default column-stacking behavior
       below ~768px. Both filter rows now have 4 items each, so they
       share one identical grid rule -- 2-across by default, 4-across
       once there's enough width (>=900px). */
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-marker) [data-testid="stHorizontalBlock"] {
        display: grid !important;
        gap: 10px !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-marker) [data-testid="stColumn"] {
        width: 100% !important;
        min-width: 0 !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-4) [data-testid="stHorizontalBlock"] {
        grid-template-columns: 1fr 1fr !important;
    }
    @media screen and (min-width: 900px) {
        div[data-testid="stVerticalBlock"]:has(> div .filter-row-4) [data-testid="stHorizontalBlock"] {
            grid-template-columns: 1fr 1fr 1fr 1fr !important;
        }
    }

    /* ─── Stretch every level inside the filter column so the actual
       dropdown fills it, regardless of what Streamlit's internal
       select-wrapper class/testid happens to be named in this
       version. Targets EVERY div nested inside the column instead of
       guessing a specific class name. */
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-marker) [data-testid="stColumn"] > div,
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-marker) [data-testid="stColumn"] div[class] {
        width: 100% !important;
    }

    .sec-title {
        font-size: 15px; font-weight: 800; color: #f3f4f6;
        margin: 18px 0 10px 0; padding: 0;
    }

    /* ─── Consistent filter label/value font sizes across pages ──── */
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-marker) label[data-testid="stWidgetLabel"] p {
        font-size: 13px !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .filter-row-marker) [data-baseweb="select"] * {
        font-size: 13px !important;
    }

    /* ─── Wrap-text table (used for Table 3) ────────────────────────
       st.dataframe can't wrap cell text -- it always single-lines and
       truncates with an ellipsis. This plain HTML table gives full
       control via white-space:normal / word-wrap so long Sku/
       Manufacture Opportunity text wraps across multiple lines. */
    .wrap-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12.5px;
        table-layout: fixed;
    }
    .wrap-table th {
        background: rgba(99,102,241,0.12);
        color: #a5b4fc;
        font-weight: 700;
        text-align: left;
        padding: 8px 10px;
        border: 1px solid #1f2937;
        white-space: normal;
        word-wrap: break-word;
    }
    .wrap-table td {
        color: #e5e7eb;
        padding: 8px 10px;
        border: 1px solid #1f2937;
        white-space: normal;
        word-wrap: break-word;
        vertical-align: top;
    }
    .wrap-table tr:nth-child(even) td {
        background: rgba(255,255,255,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

    role      = st.session_state.get('role', 'ASM')
    region    = st.session_state.get('region', 'ALL')
    unit      = st.session_state.get('unit', 'ALL')
    asm_code  = st.session_state.get('asm_code', 'ALL')

    with st.spinner("Loading data..."):
        df_full = load_data(role, region, unit, asm_code)

    # ── Region + Unit + ASM + Customer (all one row, 4 columns) ─────
    # Customer cascades from Region -> Unit -> ASM: e.g. picking ASM
    # "xyz" narrows the Customer list to only that ASM's customers.
    with st.container():
        st.markdown('<div class="filter-row-marker filter-row-4" style="display:none;"></div>', unsafe_allow_html=True)
        f1 = st.columns([1.2, 1.2, 1.5, 2.8])

        if 'Region' in df_full.columns and role == 'Admin':
            sel_regions = f1[0].multiselect(
                "Region", sorted(df_full['Region'].dropna().unique().tolist()),
                default=[], placeholder="All Regions", key="cm_reg")
        else:
            sel_regions = []

        unit_pool = df_full.copy()
        if sel_regions and 'Region' in unit_pool.columns:
            unit_pool = unit_pool[unit_pool['Region'].isin(sel_regions)]

        if 'Unit' in df_full.columns:
            sel_units = f1[1].multiselect(
                "Unit", sorted(unit_pool['Unit'].dropna().unique().tolist()),
                default=[], placeholder="All Units", key="cm_unit")
        else:
            sel_units = []

        asm_pool = unit_pool.copy()
        if sel_units and 'Unit' in asm_pool.columns:
            asm_pool = asm_pool[asm_pool['Unit'].isin(sel_units)]

        if 'Area_Sales_Man' in df_full.columns:
            sel_asms = f1[2].multiselect(
                "Area Sales Man", sorted(asm_pool['Area_Sales_Man'].dropna().unique().tolist()),
                default=[], placeholder="All ASMs", key="cm_asm")
        else:
            sel_asms = []

        cust_pool = asm_pool.copy()
        if sel_asms and 'Area_Sales_Man' in cust_pool.columns:
            cust_pool = cust_pool[cust_pool['Area_Sales_Man'].isin(sel_asms)]

        if 'Customer' in df_full.columns:
            sel_customers = f1[3].multiselect(
                "Customer", sorted(cust_pool['Customer'].dropna().unique().tolist()),
                default=[], placeholder="All Customers", key="cm_customer")
        else:
            sel_customers = []

    # ── Customer_Type / Mis_Remarks / Reason / Receivables_Health ───
    detail_pool = cust_pool.copy()
    if sel_customers and 'Customer' in detail_pool.columns:
        detail_pool = detail_pool[detail_pool['Customer'].isin(sel_customers)]

    with st.container():
        st.markdown('<div class="filter-row-marker filter-row-4" style="display:none;"></div>', unsafe_allow_html=True)
        f2 = st.columns([1, 1, 1, 1])

        sel_cust_type = f2[0].multiselect(
            "Customer_Type", sorted(detail_pool['Customer_Type'].dropna().unique().tolist()),
            default=[], placeholder="Customer_Type", key="cm_custtype") if 'Customer_Type' in detail_pool.columns else []

        sel_mis = f2[1].multiselect(
            "Mis Remarks", sorted(detail_pool['Mis_Remarks'].dropna().unique().tolist()),
            default=[], placeholder="Mis Remarks", key="cm_mis") if 'Mis_Remarks' in detail_pool.columns else []

        sel_reason = f2[2].multiselect(
            "Reason", sorted(detail_pool['Reason'].dropna().unique().tolist()),
            default=[], placeholder="Reason", key="cm_reason") if 'Reason' in detail_pool.columns else []

        sel_recv = f2[3].multiselect(
            "Pin Code", sorted(detail_pool['Pin_Code'].dropna().unique().tolist()),
            default=[], placeholder="Pin Code", key="cm_recv") if 'Pin_Code' in detail_pool.columns else []

    # ── Apply all filters ────────────────────────────────────────────
    df = df_full.copy()
    if sel_regions and 'Region' in df.columns:
        df = df[df['Region'].isin(sel_regions)]
    if sel_units and 'Unit' in df.columns:
        df = df[df['Unit'].isin(sel_units)]
    if sel_asms and 'Area_Sales_Man' in df.columns:
        df = df[df['Area_Sales_Man'].isin(sel_asms)]
    if sel_customers and 'Customer' in df.columns:
        df = df[df['Customer'].isin(sel_customers)]
    if sel_cust_type and 'Customer_Type' in df.columns:
        df = df[df['Customer_Type'].isin(sel_cust_type)]
    if sel_mis and 'Mis_Remarks' in df.columns:
        df = df[df['Mis_Remarks'].isin(sel_mis)]
    if sel_reason and 'Reason' in df.columns:
        df = df[df['Reason'].isin(sel_reason)]
    if sel_recv and 'Pin_Code' in df.columns:
        df = df[df['Pin_Code'].isin(sel_recv)]

    if len(df) == 0:
        st.warning("No data matches the selected filters.")
        return

    # ══════════════════════════════════════════════════════════════
    # TABLE 1 — Customer Sales & Outstanding Detail
    # ══════════════════════════════════════════════════════════════
    st.markdown("<div class='sec-title'>Customer Sales &amp; Outstanding</div>", unsafe_allow_html=True)

    t1_rename = {
        'CX_Code': 'CX_Code',
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
        selected_custcode = table1_df.iloc[row_idx]['CX_Code'] if 'CX_Code' in table1_df.columns else None

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
        table2_source = df[df['CX_Code'] == selected_custcode] if 'CX_Code' in df.columns else df
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
    }
    t2_cols = [c for c in t2_rename if c in table2_source.columns]
    table2_df = table2_source[t2_cols].rename(columns=t2_rename).reset_index(drop=True)

    st.dataframe(table2_df.head(5), use_container_width=True, hide_index=True)
    if len(table2_source) > 5:
        st.caption(f"Showing first 5 of {len(table2_source):,} matching rows.")

    # ══════════════════════════════════════════════════════════════
    # TABLE 3 — Growth Opportunity Detail (filtered by Table 1 click)
    # Rendered as HTML (not st.dataframe) so long text wraps onto
    # multiple lines instead of being truncated with an ellipsis.
    # ══════════════════════════════════════════════════════════════
    st.markdown("<div class='sec-title'>Growth Opportunity</div>", unsafe_allow_html=True)

    if selected_custcode is not None:
        st.markdown(
            f"<div style='font-size:12px;color:#a5b4fc;margin-bottom:6px;'>"
            f"Showing details for the customer selected in the table above "
            f"(CustCode: <b>{selected_custcode}</b>).</div>",
            unsafe_allow_html=True)
        table3_source = df[df['CX_Code'] == selected_custcode] if 'CX_Code' in df.columns else df
    else:
        st.markdown(
            "<div style='font-size:12px;color:#6b7280;margin-bottom:6px;'>"
            "Click a row in the table above to filter this to a single customer.</div>",
            unsafe_allow_html=True)
        table3_source = df

    t3_rename = {
        'SKU_vicinity': 'Sku Opportunity',
        'Manufacture_vicinity': 'Manufacture Opportunity',
    }
    t3_cols = [c for c in t3_rename if c in table3_source.columns]
    table3_df = table3_source[t3_cols].rename(columns=t3_rename).reset_index(drop=True).head(2)

    header_html = "".join(f"<th>{c}</th>" for c in table3_df.columns)
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{'' if pd.isna(v) else v}</td>" for v in row) + "</tr>"
        for row in table3_df.itertuples(index=False)
    )
    st.markdown(
        f"<table class='wrap-table'><tr>{header_html}</tr>{rows_html}</table>",
        unsafe_allow_html=True,
    )
    if len(table3_source) > 2:
        st.caption(f"Showing first 2 of {len(table3_source):,} matching rows.")
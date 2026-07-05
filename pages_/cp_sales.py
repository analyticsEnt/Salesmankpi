from io import BytesIO
import textwrap

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


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _text_to_pdf_stream(lines, page_width=612, page_height=792, margin=40, font_size=9, leading=12):
    x = margin
    y = page_height - margin
    content = ["BT", f"/F1 {font_size} Tf", f"{x} {y} Td"]
    for idx, line in enumerate(lines):
        content.append(f"({_pdf_escape(line)}) Tj")
        if idx < len(lines) - 1:
            content.append(f"0 -{leading} Td")
    content.append("ET")
    return "\n".join(content).encode("latin-1")


def build_pdf_bytes(df):
    max_chars = 90
    columns = [str(c) for c in df.columns]
    header = " | ".join(columns)
    rows = []
    for row in df.itertuples(index=False, name=None):
        rows.append(" | ".join("" if pd.isna(v) else str(v) for v in row))

    lines = ["Customer Details", "", header, ""]
    for row in rows:
        if len(row) > max_chars:
            row = row[: max_chars - 3] + "..."
        lines.append(row)

    lines_per_page = int((792 - 80) / 14)
    page_chunks = [lines[i : i + lines_per_page] for i in range(0, len(lines), lines_per_page)]

    pdf_objects = []
    page_ids = []
    stream_ids = []

    for chunk in page_chunks:
        stream = _text_to_pdf_stream(chunk)
        stream_ids.append(len(pdf_objects) + 1)
        pdf_objects.append(("stream", stream))

    font_id = len(pdf_objects) + 1
    pdf_objects.append(("font", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"))

    for stream_id in stream_ids:
        page_ids.append(len(pdf_objects) + 1)
        pdf_objects.append(("page", f"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> /MediaBox [0 0 612 792] /Contents {stream_id} 0 R >>".encode("latin-1")))

    kids = b" ".join(f"{pid} 0 R".encode("latin-1") for pid in page_ids)
    pages_dict = f"<< /Type /Pages /Kids [ {kids.decode('latin-1')} ] /Count {len(page_ids)} >>".encode("latin-1")
    pdf_objects.insert(0, ("pages", pages_dict))
    pdf_objects.insert(0, ("catalog", b"<< /Type /Catalog /Pages 2 0 R >>"))

    output = BytesIO()
    output.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    offsets = []
    for idx, (_, content) in enumerate(pdf_objects, start=1):
        offsets.append(output.tell())
        output.write(f"{idx} 0 obj\n".encode("latin-1"))
        if _ == "stream":
            output.write(f"<< /Length {len(content)} >>\nstream\n".encode("latin-1"))
            output.write(content)
            output.write(b"\nendstream\nendobj\n")
        else:
            output.write(content)
            output.write(b"\nendobj\n")

    xref_start = output.tell()
    output.write(f"xref\n0 {len(pdf_objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for offset in offsets:
        output.write(f"{offset:010d} 00000 n \n".encode("latin-1"))
    output.write(b"trailer\n")
    output.write(f"<< /Size {len(pdf_objects) + 1} /Root 1 0 R >>\n".encode("latin-1"))
    output.write(b"startxref\n")
    output.write(f"{xref_start}\n".encode("latin-1"))
    output.write(b"%%EOF")

    return output.getvalue()


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
    section1_cards = [
        ("", "Total CX",           fmt_count(total_customers)),
        ("", "Ordered CX",         fmt_count(customers_ordered)),
        ("", "Ordered %",          fmt_pct(ordered_pct)),
        ("", "Churn (MTD)",        fmt_count(churn_this_month)),
        ("", "Churn MTD %",        fmt_pct(churn_this_month_pct)),
        ("", "Churn &gt;1M",       fmt_count(churn_gt1_month)),
        ("", "Churn &gt;1M %",     fmt_pct(churn_gt1_month_pct)),
        ("", "Degrowth CX",        fmt_count(degrowth_customers)),
        ("", "Degrowth %",         fmt_pct(degrowth_pct)),
        ("kpi-highlight", "Sales Shortfall", fmt_inr(sales_shortfall)),
    ]
    cards_html_1 = "".join(
        f"""<div class="kpi-card kpi-orange {extra}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
            </div>"""
        for extra, label, val in section1_cards
    )
    st.markdown(f'<div class="kpi-grid">{cards_html_1}</div>', unsafe_allow_html=True)

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
    section2_cards = [
        ("", "CX &gt;90D",           fmt_count(cx_gt90)),
        ("kpi-highlight", "OS &gt;90D", fmt_inr(os_gt90)),
        ("", "%",                    fmt_pct(os_gt90_pct)),
        ("kpi-highlight", "OS 60-90D", fmt_inr(os_60_90)),
        ("", "%",                    fmt_pct(os_60_90_pct)),
        ("", "OS 30-60D",            fmt_inr(os_30_60)),
        ("", "%",                    fmt_pct(os_30_60_pct)),
        ("", "OS 0-30D",             fmt_inr(os_0_30)),
        ("", "%",                    fmt_pct(os_0_30_pct)),
        ("", "Total O/S",            fmt_inr(total_outstanding)),
    ]
    cards_html_2 = "".join(
        f"""<div class="kpi-card kpi-green {extra}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
            </div>"""
        for extra, label, val in section2_cards
    )
    st.markdown(f'<div class="kpi-grid">{cards_html_2}</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # CUSTOMER DETAIL TABLE
    # ══════════════════════════════════════════════════════════════
    st.markdown("<div class='sec-title'>Customer Details</div>", unsafe_allow_html=True)

    table_df = df.copy()

    display_cols = [c for c in [
        'LPD','CustCode', 'Customer', 'Customer_Type', 'Mis_Remarks'
        , 'Receivables_Health','Last_Month' ,'Current_Month', 'Sales_Deficit',
        'Total_Outstanding', 'Overdue_Value',
    ] if c in table_df.columns]

    display_df = table_df[display_cols].head(500).copy()

    export_cols = st.columns([1, 1, 1])
    with export_cols[0]:
        csv_bytes = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name="customer_details.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with export_cols[1]:
        pdf_bytes = build_pdf_bytes(display_df)
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name="customer_details.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.dataframe(
        display_df,
        use_container_width=True, hide_index=True,
    )
    if len(table_df) > 500:
        st.caption(f"Showing first 500 of {len(table_df):,} matching rows.")
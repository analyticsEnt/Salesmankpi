import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from urllib.parse import quote_plus

COLORS = px.colors.qualitative.Vivid

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


def show():
    st.markdown("""
    <style>
    /* ─── Force filter rows onto one line even on mobile ──────────
       Same marker + :has() technique used elsewhere: targets ONLY
       the wrapped row, overriding Streamlit's default column-
       stacking behavior below ~768px. */
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

    /* ─── Force chart rows onto one line on desktop, one PER ROW
       on mobile -- explicit override rather than relying on
       Streamlit's default stacking, which wasn't kicking in
       reliably for plotly_chart elements. ────────────────────── */
    div[data-testid="stVerticalBlock"]:has(> div .chart-row-marker) [data-testid="stHorizontalBlock"] {
        display: grid !important;
        gap: 14px !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .chart-row-marker) [data-testid="stColumn"] {
        width: auto !important;
        min-width: 0 !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .chart-row-3) [data-testid="stHorizontalBlock"] {
        grid-template-columns: 1fr 1fr 1fr !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .chart-row-2) [data-testid="stHorizontalBlock"] {
        grid-template-columns: 1fr 1fr !important;
    }
    @media screen and (max-width: 768px) {
        div[data-testid="stVerticalBlock"]:has(> div .chart-row-3) [data-testid="stHorizontalBlock"],
        div[data-testid="stVerticalBlock"]:has(> div .chart-row-2) [data-testid="stHorizontalBlock"] {
            grid-template-columns: 1fr !important;
        }
    }

    /* ─── Section title ──────────────────────────────────────────── */
    .sec-title {
        font-size: 15px; font-weight: 800; color: #f3f4f6;
        margin: 18px 0 10px 0; padding: 0;
    }
    </style>
    """, unsafe_allow_html=True)

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
                default=[], placeholder="All Regions", key="fy_reg")
        else:
            sel_regions = []

        unit_pool = df_full.copy()
        if sel_regions and 'Region' in unit_pool.columns:
            unit_pool = unit_pool[unit_pool['Region'].isin(sel_regions)]

        if 'Unit' in df_full.columns:
            sel_units = f1[1].multiselect(
                "Unit", sorted(unit_pool['Unit'].dropna().unique().tolist()),
                default=[], placeholder="All Units", key="fy_unit")
        else:
            sel_units = []

        asm_pool = unit_pool.copy()
        if sel_units and 'Unit' in asm_pool.columns:
            asm_pool = asm_pool[asm_pool['Unit'].isin(sel_units)]

        if 'Area_Sales_Man' in df_full.columns:
            sel_asms = f1[2].multiselect(
                "Area Sales Man", sorted(asm_pool['Area_Sales_Man'].dropna().unique().tolist()),
                default=[], placeholder="All ASMs", key="fy_asm")
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
            default=[], placeholder="Customer_Type", key="fy_custtype") if 'Customer_Type' in detail_pool.columns else []

        sel_mis = f2[1].multiselect(
            "Mis Remarks", sorted(detail_pool['Mis_Remarks'].dropna().unique().tolist()),
            default=[], placeholder="Mis Remarks", key="fy_mis") if 'Mis_Remarks' in detail_pool.columns else []

        sel_reason = f2[2].multiselect(
            "Reason", sorted(detail_pool['Reason'].dropna().unique().tolist()),
            default=[], placeholder="Reason", key="fy_reason") if 'Reason' in detail_pool.columns else []

        sel_recv = f2[3].multiselect(
            "Receivables Health", sorted(detail_pool['Receivables_Health'].dropna().unique().tolist()),
            default=[], placeholder="Receivables H...", key="fy_recv") if 'Receivables_Health' in detail_pool.columns else []

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
    # CUSTOMER INSIGHTS — mixed chart types
    # ══════════════════════════════════════════════════════════════
    st.markdown("<div class='sec-title'>Customer Insights</div>", unsafe_allow_html=True)

    def bar_chart(data, cat_col, value_col, agg_label, title, bar_color, chart_key):
        """Horizontal bar: Count of customers + a monetary metric (MTD Sales
        or MTD Deficit) on a secondary top axis. Legend sits BELOW the
        chart (not above) so it never collides with the title or the
        secondary axis's tick labels."""
        if cat_col not in data.columns:
            return
        grp = data.groupby(cat_col, as_index=False).agg(
            Count=('CustCode', 'count'),
            Value=(value_col, 'sum'),
        ).sort_values('Value', ascending=True)
        if grp.empty:
            return

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=grp[cat_col], x=grp['Count'], name='Customers',
            orientation='h', marker_color=bar_color, opacity=0.9,
        ))
        fig.add_trace(go.Bar(
            y=grp[cat_col], x=grp['Value'], name=agg_label,
            orientation='h', marker_color='#f59e0b', opacity=0.55,
            xaxis='x2',
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=13, color='#e5e7eb'), y=0.97),
            template='plotly_dark', barmode='group',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=340,
            margin=dict(t=70, b=60, l=10, r=10),
            legend=dict(orientation='h', yanchor='top', y=-0.15, font=dict(size=9)),
            xaxis=dict(showgrid=False, tickfont=dict(size=8)),
            xaxis2=dict(overlaying='x', side='top', showgrid=False, tickfont=dict(size=8)),
            yaxis=dict(tickfont=dict(size=9)),
            font=dict(size=10, color='#9ca3af'),
        )
        st.plotly_chart(fig, use_container_width=True, key=chart_key)

    def donut_chart(data, cat_col, title, chart_key):
        """A single clean, formal donut -- kept simple for Status only."""
        if cat_col not in data.columns:
            return
        vc = data[cat_col].dropna().value_counts().reset_index()
        vc.columns = [cat_col, 'Count']
        if vc.empty:
            return
        fig = px.pie(
            vc, names=cat_col, values='Count', hole=0.55,
            color_discrete_sequence=COLORS, template='plotly_dark',
        )
        fig.update_traces(textposition='inside', textinfo='percent')
        fig.update_layout(
            title=dict(text=title, font=dict(size=13, color='#e5e7eb'), y=0.97),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation='h', yanchor='top', y=-0.1, font=dict(size=9)),
            margin=dict(t=70, b=40, l=10, r=10), height=340,
            font=dict(size=10, color='#9ca3af'),
        )
        st.plotly_chart(fig, use_container_width=True, key=chart_key)

    with st.container():
        st.markdown('<div class="chart-row-marker chart-row-3" style="display:none;"></div>', unsafe_allow_html=True)
        ins_row1 = st.columns([1, 1, 1])
        with ins_row1[0]:
            bar_chart(df, 'Customer_Type', 'Current_Month', 'MTD Sales',
                      'Customer Type', '#6366f1', 'chart_custtype')
        with ins_row1[1]:
            bar_chart(df, 'Mis_Remarks', 'Sales_Deficit', 'MTD Deficit',
                      'MIS Remarks', '#ef4444', 'chart_mis')
        with ins_row1[2]:
            donut_chart(df, 'Status', 'Status', 'chart_status')

    with st.container():
        st.markdown('<div class="chart-row-marker chart-row-2" style="display:none;"></div>', unsafe_allow_html=True)
        ins_row2 = st.columns([1, 1])
        with ins_row2[0]:
            bar_chart(df, 'Reason', 'Current_Month', 'MTD Sales',
                      'Reason', '#10b981', 'chart_reason')
        with ins_row2[1]:
            bar_chart(df, 'Receivables_Health', 'Total_Outstanding', 'Total Outstanding',
                      'Receivables Health', '#f97316', 'chart_recv')
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import io

@st.cache_resource
def get_engine():
    host     = "db31521.public.databaseasp.net"
    port     = 3306
    database = "db31521"
    username = "db31521"
    password = quote_plus(st.secrets["DB_PASSWORD"])
    return create_engine(
        f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}",
        pool_pre_ping=True, pool_recycle=3600,
    )

@st.cache_data(ttl=300, show_spinner=False)
def load_data(role, region, unit, asm_code):
    engine = get_engine()
    df = pd.read_sql_table("datewise_sales", engine)
    for col in ['Net_Cost','Net_Discount','Net_Sale','Net_Scheme']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if 'Date' in df.columns:
        df['Date']  = pd.to_datetime(df['Date'], errors='coerce')
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        df['Year']  = df['Date'].dt.year.astype(str)
    if 'Customer_Type' in df.columns:
        mapping = {
            'WHOLE SELLER': 'WHOLESELLER',
            'E-COMMERCE': 'E-COM',
            'ENTERO GROUP': 'ENT_GROUP',
            'THERYCO': 'THERYCO'
        }
        df['CX_Group'] = df['Customer_Type'].map(mapping).fillna('TRADE')
    if role != 'Admin':
        if region != 'ALL' and 'Region' in df.columns:
            df = df[df['Region'] == region]
        if unit != 'ALL' and 'Unit' in df.columns:
            df = df[df['Unit'] == unit]
        if asm_code != 'ALL' and 'ASM_Code' in df.columns:
            df = df[df['ASM_Code'] == asm_code]
    return df

def fmt(n):
    if abs(n) >= 1_000_000_000: return f"₹{n/1_000_000_000:.2f}B"
    if abs(n) >= 1_000_000:     return f"₹{n/1_000_000:.2f}M"
    if abs(n) >= 1_000:         return f"₹{n/1_000:.2f}K"
    return f"₹{n:.0f}"

COLORS = px.colors.qualitative.Vivid

def show():
    st.markdown("""
    <style>
    .kpi-card {
        background:linear-gradient(145deg,#0d1117,#111827);
        border:1px solid #1f2937; border-radius:18px;
        padding:20px; position:relative; overflow:hidden;
        transition:transform 0.2s,box-shadow 0.2s;
    }
    .kpi-card::before {
        content:''; position:absolute; top:0; left:0;
        width:4px; height:100%;
        background:linear-gradient(180deg,#6366f1,#8b5cf6);
    }
    .kpi-card:hover { transform:translateY(-3px); box-shadow:0 12px 30px rgba(99,102,241,0.15); }
    .kpi-icon  { font-size:18px; margin-bottom:6px; }
    .kpi-label { font-size:10px; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; color:#6b7280; margin-bottom:4px; }
    .kpi-value { font-size:22px; font-weight:800; color:#f9fafb; }
    .kpi-sub   { font-size:11px; color:#10b981; margin-top:3px; }
    .period-banner {
        background:linear-gradient(135deg,#0d1117,#111827);
        border:1px solid #1f2937; border-left:4px solid #6366f1;
        border-radius:14px; padding:12px 20px; margin-bottom:18px;
        display:flex; gap:36px; align-items:center; flex-wrap:wrap;
    }
    .pb-label { font-size:10px; font-weight:600; letter-spacing:1px; text-transform:uppercase; color:#6b7280; margin-bottom:2px; }
    .pb-value  { font-size:13px; font-weight:700; color:#a5b4fc; }
    .sec-header {
        font-size:11px; font-weight:700; letter-spacing:2px; text-transform:uppercase;
        color:#6366f1; margin:22px 0 10px; padding-bottom:8px; border-bottom:1px solid #1a1f35;
    }
    .stTabs [data-baseweb="tab-list"] {
        background:#0d1117 !important; border-radius:12px !important;
        padding:5px !important; border:1px solid #1f2937 !important; gap:3px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background:transparent !important; border-radius:9px !important;
        color:#6b7280 !important; font-weight:600 !important;
        font-size:13px !important; padding:9px 16px !important; border:none !important;
    }
    .stTabs [aria-selected="true"] {
        background:linear-gradient(135deg,#6366f1,#8b5cf6) !important;
        color:white !important; box-shadow:0 4px 12px rgba(99,102,241,0.3) !important;
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] { display:none !important; }
    div[role="radiogroup"], [data-baseweb="radio-group"] > div {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 0.75rem !important;
        align-items: center !important;
    }
    div[role="radiogroup"] > label,
    div[role="radiogroup"] > div {
        display: inline-flex !important;
        flex-direction: row !important;
        align-items: center !important;
        margin-bottom: 0 !important;
    }
    div[role="radiogroup"] > label > div,
    div[role="radiogroup"] > label > div > div {
        display: inline-flex !important;
        flex-direction: row !important;
        align-items: center !important;
    }
    div[role="radiogroup"] input[type="radio"] {
        margin-right: 0.5rem !important;
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

    # Page title + period/user card with date filters on the same row
    title_col, banner_col, from_col, to_col = st.columns([2.4, 2.6, 1, 1])
    with title_col:
        st.markdown("<div style='font-size:26px;font-weight:800;color:#f9fafb;margin-bottom:4px;'>📅 FY Sales Analysis</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:13px;color:#6b7280;margin-bottom:14px;'>Welcome back, {full_name} • {role} • Region: {region} • Unit: {unit}</div>", unsafe_allow_html=True)

    # ── Header Filters ───────────────────────────────────────────────────────
    if 'Date' in df_full.columns:
        min_d = df_full['Date'].min().date()
        max_d = df_full['Date'].max().date()
        from_date = from_col.date_input("From Date", value=min_d, min_value=min_d, max_value=max_d, key="s_from")
        to_date   = to_col.date_input("To Date",   value=max_d, min_value=min_d, max_value=max_d, key="s_to")
    else:
        from_date = to_date = None

    # Region/Unit/CX Group/Customer Type filters on the next row
    region_unit_cols = st.columns([1.5, 1.8, 3.8, 1.8])

    if 'Region' in df_full.columns and role == 'Admin':
        sel_regions = region_unit_cols[0].multiselect("Region",
                                                     df_full['Region'].dropna().unique().tolist(),
                                                     default=[],
                                                     key="s_reg")
    else:
        sel_regions = []

    if 'Unit' in df_full.columns:
        unit_options = df_full['Unit'].dropna().unique().tolist()
        if sel_regions and 'Region' in df_full.columns:
            unit_options = df_full[df_full['Region'].isin(sel_regions)]['Unit'].dropna().unique().tolist()
        sel_units = region_unit_cols[1].multiselect("Unit",
                                                   sorted(unit_options),
                                                   default=[],
                                                   placeholder="All Units",
                                                   key="s_unit")
    else:
        sel_units = []

    if 'CX_Group' in df_full.columns:
        cx_options = df_full['CX_Group'].dropna().unique().tolist()
        default_cx = [x for x in cx_options if x in ['TRADE', 'E-COM', 'WHOLESELLER']]
        sel_cx_group = region_unit_cols[2].multiselect("CX Group",
                                                      sorted(cx_options),
                                                      default=["WHOLESELLER","E-COM","TRADE"] if role != 'Admin' else default_cx,
                                                      placeholder="All CX Groups",
                                                      key="s_cx_group")
    else:
        sel_cx_group = []

    if 'Customer_Type' in df_full.columns:
        customer_filter = df_full.copy()
        if sel_cx_group and 'CX_Group' in df_full.columns:
            customer_filter = customer_filter[customer_filter['CX_Group'].isin(sel_cx_group)]
        if sel_regions and 'Region' in df_full.columns:
            customer_filter = customer_filter[customer_filter['Region'].isin(sel_regions)]
        if sel_units and 'Unit' in df_full.columns:
            customer_filter = customer_filter[customer_filter['Unit'].isin(sel_units)]
        customer_options = customer_filter['Customer_Type'].dropna().unique().tolist()
        sel_customer_types = region_unit_cols[3].multiselect("Customer Type",
                                                            sorted(customer_options),
                                                            default=[],
                                                            placeholder="All Customer Types",
                                                            key="s_cust_type")
    else:
        sel_customer_types = []

    # ── Apply Filters ─────────────────────────────────────────────────────────
    df = df_full.copy()
    if from_date and to_date and 'Date' in df.columns:
        df = df[(df['Date'].dt.date >= from_date) & (df['Date'].dt.date <= to_date)]
    if sel_regions and 'Region' in df.columns:
        df = df[df['Region'].isin(sel_regions)]
    if sel_units and 'Unit' in df.columns:
        df = df[df['Unit'].isin(sel_units)]
    if sel_cx_group and 'CX_Group' in df.columns:
        df = df[df['CX_Group'].isin(sel_cx_group)]
    if sel_customer_types and 'Customer_Type' in df.columns:
        df = df[df['Customer_Type'].isin(sel_customer_types)]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_sale     = df['Net_Sale'].sum()     if 'Net_Sale'     in df.columns else 0
    total_cost     = df['Net_Cost'].sum()     if 'Net_Cost'     in df.columns else 0
    total_discount = df['Net_Discount'].sum() if 'Net_Discount' in df.columns else 0
    total_scheme   = df['Net_Scheme'].sum()   if 'Net_Scheme'   in df.columns else 0
    profit  = total_sale - total_cost
    gp_pct  = (profit / total_sale * 100)        if total_sale else 0
    dis_pct = (total_discount / total_sale * 100) if total_sale else 0

    # Top-right period/user card
    period_text = f"{from_date.strftime('%d %b %Y')} → {to_date.strftime('%d %b %Y')}" if from_date and to_date else "All time"
    user_text = f"{full_name} ({role} • {region} • {unit})"
    banner_col.markdown(f"""
    <div class="period-banner" style="margin-top:6px;">
        <div><div class="pb-label">📅 Period</div>
        <div class="pb-value">{period_text}</div></div>
        <div><div class="pb-label">👤 User</div>
        <div class="pb-value">{user_text}</div></div>
    </div>""", unsafe_allow_html=True)

    # KPI Row
    k = st.columns(6)
    for col, icon, label, val, sub in [
        (k[0], "💰", "NET SALES",    fmt(total_sale),     ""),
        (k[1], "📦", "NET COST",     fmt(total_cost),     ""),
        (k[2], "🏷️", "DISCOUNT",    fmt(total_discount), f"{dis_pct:.2f}%"),
        (k[3], "🎁", "SCHEME",       fmt(total_scheme),   ""),
        (k[4], "📈", "GROSS PROFIT", fmt(profit),         ""),
        (k[5], "💹", "GP %",         f"{gp_pct:.2f}%",   ""),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            {'<div class="kpi-sub">' + sub + '</div>' if sub else ''}
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌍  Region", "🏢  Unit", "👤  ASM", "👥  Customer", "📅  Trend"
    ])

    def export_excel(dataframe, filename, key):
        buf = io.BytesIO()
        dataframe.to_excel(buf, index=False)
        st.download_button("📥 Export to Excel", buf.getvalue(),
                           file_name=filename, mime="application/vnd.ms-excel", key=key)

    # Tab 1: Region
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            if 'Region' in df.columns:
                rdf = df.groupby('Region', as_index=False)['Net_Sale'].sum().sort_values('Net_Sale', ascending=False)
                fig = px.bar(rdf, x='Region', y='Net_Sale', color='Region',
                             title='Region-wise Net Sales', color_discrete_sequence=COLORS,
                             template='plotly_dark', text_auto='.2s')
                fig.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            if 'Region' in df.columns:
                fig2 = px.pie(rdf, names='Region', values='Net_Sale', title='Region Share',
                              hole=0.45, color_discrete_sequence=COLORS, template='plotly_dark')
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
        if 'State' in df.columns:
            sdf = df.groupby('State', as_index=False)['Net_Sale'].sum().sort_values('Net_Sale', ascending=False).head(15)
            fig3 = px.bar(sdf, x='Net_Sale', y='State', orientation='h', color='Net_Sale',
                          color_continuous_scale='Purples', title='Top 15 States',
                          template='plotly_dark', text_auto='.2s')
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig3, use_container_width=True)
        if 'Region' in df.columns:
            st.markdown("<div class='sec-header'>Region Summary</div>", unsafe_allow_html=True)
            rtbl = df.groupby('Region').agg(
                Sales=('Net_Sale','sum'), Discount=('Net_Discount','sum'),
                Cost=('Net_Cost','sum'), Scheme=('Net_Scheme','sum')
            ).reset_index()
            rtbl['Profit'] = rtbl['Sales'] - rtbl['Cost']
            rtbl['GP %']   = (rtbl['Profit'] / rtbl['Sales'] * 100).round(2)
            rtbl['Dis %']  = (rtbl['Discount'] / rtbl['Sales'] * 100).round(2)
            export_excel(rtbl, "region_summary.xlsx", "exp_r")
            for c in ['Sales','Discount','Cost','Scheme','Profit']:
                rtbl[c] = rtbl[c].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(rtbl, use_container_width=True, hide_index=True)

    # Tab 2: Unit
    with tab2:
        if 'Unit' in df.columns:
            udf = df.groupby('Unit', as_index=False)['Net_Sale'].sum().sort_values('Net_Sale', ascending=False).head(20)
            fig = px.bar(udf, x='Net_Sale', y='Unit', orientation='h', color='Net_Sale',
                         color_continuous_scale='Blues', title='Unit-wise Net Sales (Top 20)',
                         template='plotly_dark', text_auto='.2s')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("<div class='sec-header'>Unit Summary</div>", unsafe_allow_html=True)
            utbl = df.groupby('Unit').agg(
                Sales=('Net_Sale','sum'), Discount=('Net_Discount','sum'),
                Cost=('Net_Cost','sum'), Scheme=('Net_Scheme','sum')
            ).reset_index().sort_values('Sales', ascending=False)
            utbl['Profit'] = utbl['Sales'] - utbl['Cost']
            utbl['GP %']   = (utbl['Profit'] / utbl['Sales'] * 100).round(2)
            utbl['Dis %']  = (utbl['Discount'] / utbl['Sales'] * 100).round(2)
            export_excel(utbl, "unit_summary.xlsx", "exp_u")
            for c in ['Sales','Discount','Cost','Scheme','Profit']:
                utbl[c] = utbl[c].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(utbl, use_container_width=True, hide_index=True)

    # Tab 3: ASM
    with tab3:
        if 'Area_Sales_Man' in df.columns:
            adf = df.groupby('Area_Sales_Man', as_index=False)['Net_Sale'].sum().sort_values('Net_Sale', ascending=False).head(20)
            fig = px.bar(adf, x='Net_Sale', y='Area_Sales_Man', orientation='h', color='Net_Sale',
                         color_continuous_scale='Greens', title='ASM-wise Net Sales (Top 20)',
                         template='plotly_dark', text_auto='.2s')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("<div class='sec-header'>ASM Summary</div>", unsafe_allow_html=True)
            atbl = df.groupby(['Area_Sales_Man','Unit'], as_index=False).agg(
                Sales=('Net_Sale','sum'), Discount=('Net_Discount','sum'), Cost=('Net_Cost','sum')
            ).sort_values('Sales', ascending=False)
            atbl['Profit'] = atbl['Sales'] - atbl['Cost']
            atbl['GP %']   = (atbl['Profit'] / atbl['Sales'] * 100).round(2)
            atbl['Dis %']  = (atbl['Discount'] / atbl['Sales'] * 100).round(2)
            export_excel(atbl, "asm_summary.xlsx", "exp_a")
            for c in ['Sales','Discount','Cost','Profit']:
                atbl[c] = atbl[c].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(atbl, use_container_width=True, hide_index=True)

    # Tab 4: Customer
    with tab4:
        c1, c2 = st.columns(2)
        with c1:
            if 'Customer_Type' in df.columns:
                ctdf = df.groupby('Customer_Type', as_index=False)['Net_Sale'].sum().sort_values('Net_Sale', ascending=False)
                fig = px.pie(ctdf, names='Customer_Type', values='Net_Sale', title='Customer Type Share',
                             hole=0.4, color_discrete_sequence=COLORS, template='plotly_dark')
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            if 'Customer_Type' in df.columns:
                fig2 = px.bar(ctdf, x='Customer_Type', y='Net_Sale', color='Customer_Type',
                              title='Customer Type Sales', color_discrete_sequence=COLORS,
                              template='plotly_dark', text_auto='.2s')
                fig2.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
        if 'Customer' in df.columns:
            st.markdown("<div class='sec-header'>Top 50 Customers</div>", unsafe_allow_html=True)
            cust = df.groupby(['Customer','Customer_Type'], as_index=False).agg(
                Sales=('Net_Sale','sum'), Discount=('Net_Discount','sum')
            ).sort_values('Sales', ascending=False).head(50)
            cust['Dis %'] = (cust['Discount'] / cust['Sales'] * 100).round(2)
            export_excel(cust, "customer_summary.xlsx", "exp_c")
            cust['Sales']    = cust['Sales'].apply(lambda x: f"₹{x:,.0f}")
            cust['Discount'] = cust['Discount'].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(cust, use_container_width=True, hide_index=True)

    # Tab 5: Trend
    with tab5:
        if 'Month' in df.columns:
            mdf = df.groupby('Month', as_index=False).agg(
                Net_Sale=('Net_Sale','sum'), Net_Discount=('Net_Discount','sum'),
                Net_Cost=('Net_Cost','sum')
            ).sort_values('Month')
            mdf['Profit'] = mdf['Net_Sale'] - mdf['Net_Cost']
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=mdf['Month'], y=mdf['Net_Sale'], mode='lines+markers',
                                     name='Net Sale', line=dict(color='#6366f1', width=3), marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=mdf['Month'], y=mdf['Profit'], mode='lines+markers',
                                     name='Profit', line=dict(color='#10b981', width=2, dash='dot'), marker=dict(size=6)))
            fig.add_trace(go.Bar(x=mdf['Month'], y=mdf['Net_Discount'], name='Discount',
                                 marker_color='#f59e0b', opacity=0.5, yaxis='y2'))
            fig.update_layout(title='Month-wise Sales Trend', template='plotly_dark',
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              yaxis2=dict(overlaying='y', side='right', showgrid=False),
                              legend=dict(orientation='h', yanchor='bottom', y=1.02))
            st.plotly_chart(fig, use_container_width=True)
            if 'Region' in df.columns:
                mrdf = df.groupby(['Month','Region'], as_index=False)['Net_Sale'].sum().sort_values('Month')
                fig2 = px.line(mrdf, x='Month', y='Net_Sale', color='Region',
                               title='Month-wise by Region', markers=True,
                               color_discrete_sequence=COLORS, template='plotly_dark')
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
            if 'Unit' in df.columns:
                mudf = df.groupby(['Month','Unit'], as_index=False)['Net_Sale'].sum().sort_values('Month')
                fig3 = px.line(mudf, x='Month', y='Net_Sale', color='Unit',
                               title='Month-wise by Unit', markers=True,
                               color_discrete_sequence=COLORS, template='plotly_dark')
                fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig3, use_container_width=True)

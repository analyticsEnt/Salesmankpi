import streamlit as st

def show_dashboard():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=DM+Mono&display=swap');
    * { font-family: 'Outfit', sans-serif !important; }
    .stApp { background: #060818; }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="collapsedControl"] { display: none !important; }
    span[data-testid="stIconMaterial"] { display: none !important; }

    section[data-testid="stSidebar"] {
        background: #0a0d1a !important;
        border-right: 1px solid #1a1f35 !important;
        width: 35px !important;
        min-width: 35px !important;
        max-width: 35px !important;
        transition: width 0.3s ease, opacity 0.3s ease !important;
        z-index: 999 !important;
        opacity: 0.25 !important;
    }
    section[data-testid="stSidebar"]:hover {
        width: 220px !important;
        min-width: 220px !important;
        max-width: 220px !important;
        opacity: 1 !important;
    }

    .user-badge {
        background: linear-gradient(135deg, #1e1f4b, #1a1035);
        border: 1px solid #6366f1; border-radius: 12px;
        padding: 12px 16px; margin-bottom: 8px;
    }
    div[data-testid="stRadio"] > div { gap: 0px !important; }
    div[data-testid="stRadio"] label {
        background: transparent !important; border-radius: 10px !important;
        padding: 6px 12px !important; cursor: pointer !important;
        transition: all 0.2s !important; border: 1px solid transparent !important;
        width: 100% !important;
        margin: 2px 0 !important;        
    }
    div[data-testid="stRadio"] label:hover { background: #1a1f35 !important; }
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: linear-gradient(135deg, #1e1f4b, #1a1035) !important;
        border-color: #6366f1 !important;
    }
    div[data-testid="stRadio"] label p {
        font-size: 13px !important; font-weight: 600 !important; color: #9ca3af !important;
        margin: 0 !important;
    }
    div[data-testid="stRadio"] label[data-checked="true"] p { color: #818cf8 !important; }
    .stButton > button {
        background: linear-gradient(135deg, #1e1f4b, #1a1035) !important;
        color: #818cf8 !important; border: 1px solid #6366f1 !important;
        border-radius: 10px !important; font-weight: 600 !important;
    }
    
    .sidebar-header {
        text-align: center;
        padding: 12px 0 8px;
        margin-bottom: 6px;
    }
    
    .sidebar-header-icon {
        font-size: 28px;
        margin-bottom: 4px;
    }
    
    .sidebar-header-title {
        font-size: 16px;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sidebar-header-subtitle {
        font-size: 8px;
        color: #374151;
        letter-spacing: 1px;
        margin-top: 1px;
    }
    
    /* Mobile Responsive Styles */
    @media screen and (max-width: 768px) {
        section[data-testid="stSidebar"] {
            width: 50px !important;
            min-width: 50px !important;
            max-width: 50px !important;
        }
        section[data-testid="stSidebar"]:hover {
            width: 200px !important;
            min-width: 200px !important;
            max-width: 200px !important;
        }
        
        .user-badge {
            display: none !important;
        }
        
        .sidebar-header {
            padding: 8px 0 4px;
            margin-bottom: 2px;
        }
        
        .sidebar-header-icon {
            font-size: 20px;
            margin-bottom: 2px;
        }
        
        .sidebar-header-title {
            font-size: 12px;
        }
        
        .sidebar-header-subtitle {
            font-size: 7px;
            margin-top: 0px;
        }
        
        div[data-testid="stRadio"] label {
            padding: 3px 6px !important;
            margin: 1px 0 !important;
        }
        
        div[data-testid="stRadio"] label p {
            font-size: 10px !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        section[data-testid="stSidebar"] {
            width: 45px !important;
            min-width: 45px !important;
            max-width: 45px !important;
        }
        section[data-testid="stSidebar"]:hover {
            width: 170px !important;
            min-width: 170px !important;
            max-width: 170px !important;
        }
        
        .sidebar-header-icon {
            font-size: 18px;
        }
        
        .sidebar-header-title {
            font-size: 10px;
        }
        
        div[data-testid="stRadio"] label {
            padding: 2px 4px !important;
        }
        
        div[data-testid="stRadio"] label p {
            font-size: 9px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    full_name = st.session_state.get('full_name', 'User')
    role      = st.session_state.get('role', 'ASM')

    with st.sidebar:
        # Header - Compact Logo & Title
        st.markdown("""
        <div class='sidebar-header'>
            <div class='sidebar-header-icon'>💊</div>
            <div class='sidebar-header-title'>ENT-SalesPulse</div>
            <div class='sidebar-header-subtitle'>PHARMA INTELLIGENCE</div>
        </div>
        """, unsafe_allow_html=True)

        # User Badge - Hidden on mobile
        st.markdown(f"""
        <div class='user-badge'>
            <div style='font-size:9px; color:#6b7280; margin-bottom:1px; letter-spacing:0.5px;'>👤 {full_name}</div>
            <div style='font-size:10px; color:#6366f1; font-weight:600;'>{role}</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation Menu
        page = st.radio("nav", [
            "📊  Sales",
            "💊  CP Sales",
            "📅  FY Sales",
            "📈  Sales Metrics",
            "💰  Outstanding",
            "📉  L10D Trend",
        ], label_visibility="collapsed", key="main_nav")

        # Bottom Section
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

        st.markdown("<div style='text-align:center;color:#1f2937;font-size:9px;margin-top:12px;'>SalesPulse v2.0</div>", unsafe_allow_html=True)

    # ── Page Routing ──────────────────────────────────────────────────────────
    if page == "📊  Sales":
        from pages_.sales import show
        show()
    elif page == "💊  CP Sales":
        from pages_.cp_sales import show
        show()
    elif page == "📅  FY Sales":
        from pages_.fy_sales import show
        show()
    elif page == "📈  Sales Metrics":
        from pages_.sales_metrics import show
        show()
    elif page == "💰  Outstanding":
        from pages_.outstanding import show
        show()
    elif page == "📉  L10D Trend":
        from pages_.l10d_trend import show
        show()

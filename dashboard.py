import streamlit as st

def show_dashboard():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "menu"   # start on the menu screen

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=DM+Mono&display=swap');
    * { font-family: 'Outfit', sans-serif !important; }
    .stApp { background: #060818; }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="collapsedControl"] { display: none !important; }
    span[data-testid="stIconMaterial"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    div[data-testid="stRadio"] { display: none !important; }

    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div.element-container { margin: 0 !important; }
    div[data-testid="stMarkdownContainer"] { margin: 0 !important; }
    div[data-testid="stElementContainer"] { margin: 0 !important; }

    /* Full width on desktop; only narrow it down on mobile so the
       menu screen looks like a tidy phone-app list. */
    .block-container {
        padding-top: 1.25rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }
    @media screen and (max-width: 768px) {
        .block-container {
            max-width: 640px !important;
            margin: 0 auto !important;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
        }
    }

    /* ─── App-style logo header (shown on both menu & page views) ─── */
    .app-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 6px 2px 18px 2px;
    }
    .app-logo { display: flex; align-items: center; gap: 10px; }
    .app-logo-icon { font-size: 28px; }
    .app-logo-text {
        font-size: 17px; font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .app-user { font-size: 11px; color: #9ca3af; text-align: right; }
    .app-user b { color: #e5e7eb; }

    /* ─── MENU SCREEN — vertical list of app-style tiles ─────────── */
    .menu-section-label {
        font-size: 11px; font-weight: 700; letter-spacing: 1.5px;
        text-transform: uppercase; color: #6b7280; margin: 4px 0 10px 4px;
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stButton"] button {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        background: linear-gradient(145deg,#0d1117,#111827) !important;
        border: 1px solid #1f2937 !important;
        border-left: 4px solid #6366f1 !important;
        border-radius: 14px !important;
        color: #e5e7eb !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 18px 20px !important;
        margin-bottom: 10px !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stButton"] button:hover {
        border-left-color: #a855f7 !important;
        background: linear-gradient(145deg,#131826,#161d2e) !important;
        transform: translateX(3px) !important;
        cursor: pointer !important;
    }
    /* Logout tile styled distinctly (red-ish accent) */
    .logout-tile div[data-testid="stButton"] button {
        border-left-color: #ef4444 !important;
        color: #fca5a5 !important;
    }
    .logout-tile div[data-testid="stButton"] button:hover {
        border-left-color: #f87171 !important;
        background: linear-gradient(145deg,#1a1112,#1f1416) !important;
    }

    /* ─── PAGE VIEW — sticky mini top bar with compact Home button ── */
    div[data-testid="stVerticalBlock"]:has(> div .page-topbar-marker) {
        position: sticky !important;
        top: 0 !important;
        z-index: 999 !important;
        background: #060818 !important;
        padding-bottom: 8px !important;
        margin-bottom: 6px !important;
        border-bottom: 1px solid #1a1f35 !important;
    }
    /* Home button: single-line pill, never stretched, never wrapped */
    .page-topbar-marker + div div[data-testid="stButton"] button {
        width: auto !important;
        min-width: 90px !important;
        white-space: nowrap !important;
        background: rgba(99,102,241,0.1) !important;
        border: 1px solid #6366f1 !important;
        border-radius: 8px !important;
        color: #a5b4fc !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        padding: 6px 14px !important;
        margin-bottom: 0 !important;
    }
    .page-topbar-marker + div div[data-testid="stButton"] button:hover {
        background: rgba(99,102,241,0.2) !important;
        transform: none !important;
    }
    .page-title-text {
        font-size: 15px; font-weight: 700; color: #f3f4f6;
        display: flex; align-items: center; margin-top: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    full_name = st.session_state.get('full_name', 'User')
    role      = st.session_state.get('role', 'ASM')

    nav_items = [
        ("sales",      "📊", "Sales"),
        ("cp_sales",   "💊", "CP Sales"),
        ("fy_sales",   "📅", "FY Sales"),
        ("metrics",    "📈", "Sales Metrics"),
        ("outstanding","💰", "Outstanding"),
        ("trend",      "📉", "L10D Trend"),
    ]
    page_titles = {k: f"{icon}  {label}" for k, icon, label in nav_items}

    # ══════════════════════════════════════════════════════════════
    # MENU SCREEN
    # ══════════════════════════════════════════════════════════════
    if st.session_state.current_page == "menu":
        st.markdown(f"""
        <div class='app-header'>
            <div class='app-logo'>
                <div class='app-logo-icon'>💊</div>
                <div class='app-logo-text'>ENT-SalesPulse</div>
            </div>
            <div class='app-user'>👤 <b>{full_name}</b><br>{role}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='menu-section-label'>Reports</div>", unsafe_allow_html=True)

        for key, icon, label in nav_items:
            if st.button(f"{icon}   {label}", key=f"menu_{key}", use_container_width=True):
                st.session_state.current_page = key
                st.rerun()

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='logout-tile'>", unsafe_allow_html=True)
        if st.button("🚪   Logout", key="menu_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return  # don't render any page content on the menu screen

    # ══════════════════════════════════════════════════════════════
    # PAGE VIEW — sticky Home bar + the selected page's content
    # ══════════════════════════════════════════════════════════════
    page = st.session_state.current_page

    with st.container():
        st.markdown('<div class="page-topbar-marker" style="display:none;"></div>', unsafe_allow_html=True)
        top_l, top_r = st.columns([1, 8])
        with top_l:
            if st.button("🏠 Home", key="btn_home"):
                st.session_state.current_page = "menu"
                st.rerun()
        with top_r:
            st.markdown(f"<div class='page-title-text'>{page_titles.get(page,'')}</div>", unsafe_allow_html=True)

    if page == "sales":
        from pages_.sales import show
        show()
    elif page == "cp_sales":
        from pages_.cp_sales import show
        show()
    elif page == "fy_sales":
        from pages_.fy_sales import show
        show()
    elif page == "metrics":
        from pages_.gp_leakage import show
        show()
    elif page == "outstanding":
        from pages_.outstanding import show
        show()
    elif page == "trend":
        from pages_.l10d_trend import show
        show()
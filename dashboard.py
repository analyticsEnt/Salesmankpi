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

    /* Hide sidebar completely */
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Top Navigation Bar - Always visible */
    .top-nav-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #0a0d1a, #111827);
        border-bottom: 1px solid #1a1f35;
        z-index: 999;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }

    .top-nav-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 20px;
        border-bottom: 1px solid #1a1f35;
    }

    .top-nav-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .top-nav-logo-icon {
        font-size: 32px;
    }

    .top-nav-logo-text {
        font-size: 18px;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .top-nav-user {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 12px;
        color: #9ca3af;
    }

    .top-nav-user-name {
        color: #e5e7eb;
        font-weight: 600;
    }

    .top-nav-user-role {
        color: #6366f1;
        font-weight: 600;
        font-size: 10px;
    }

    .top-nav-items {
        display: flex;
        gap: 8px;
        padding: 0 20px 12px 20px;
        overflow-x: auto;
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
    }

    .top-nav-items::-webkit-scrollbar {
        height: 4px;
    }

    .top-nav-items::-webkit-scrollbar-thumb {
        background: #6366f1;
        border-radius: 4px;
    }

    .top-nav-button {
        background: transparent;
        color: #9ca3af;
        border: 1px solid #1a1f35;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        white-space: nowrap;
        transition: all 0.2s;
        flex-shrink: 0;
    }

    .top-nav-button:hover {
        border-color: #6366f1;
        color: #818cf8;
    }

    .top-nav-button.active {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border-color: #6366f1;
    }

    .top-nav-logout {
        background: linear-gradient(135deg, #1e1f4b, #1a1035);
        color: #818cf8;
        border: 1px solid #6366f1;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        flex-shrink: 0;
    }

    .top-nav-logout:hover {
        background: linear-gradient(135deg, #2d2f5b, #251545);
        box-shadow: 0 0 12px rgba(99, 102, 241, 0.3);
    }

    /* Adjust main content to account for top nav */
    section[data-testid="stMain"] {
        padding-top: 160px !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 1rem !important;
    }

    /* Tablet Responsive */
    @media screen and (max-width: 1024px) {
        .top-nav-header {
            padding: 10px 16px;
        }

        .top-nav-logo-icon {
            font-size: 28px;
        }

        .top-nav-logo-text {
            font-size: 16px;
        }

        .top-nav-items {
            padding: 0 16px 10px 16px;
            gap: 6px;
        }

        .top-nav-button,
        .top-nav-logout {
            padding: 6px 12px;
            font-size: 11px;
        }

        section[data-testid="stMain"] {
            padding-top: 140px !important;
        }

        .block-container {
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }
    }

    /* Mobile Responsive */
    @media screen and (max-width: 768px) {
        .top-nav-header {
            padding: 8px 12px;
            margin-bottom: 4px;
        }

        .top-nav-logo {
            gap: 8px;
        }

        .top-nav-logo-icon {
            font-size: 24px;
        }

        .top-nav-logo-text {
            font-size: 14px;
        }

        .top-nav-user {
            font-size: 10px;
            display: none;
        }

        .top-nav-items {
            padding: 0 12px 8px 12px;
            gap: 4px;
        }

        .top-nav-button,
        .top-nav-logout {
            padding: 5px 10px;
            font-size: 10px;
        }

        section[data-testid="stMain"] {
            padding-top: 120px !important;
        }

        .block-container {
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* Small Mobile */
    @media screen and (max-width: 480px) {
        .top-nav-header {
            padding: 6px 8px;
            margin-bottom: 2px;
        }

        .top-nav-logo {
            gap: 6px;
        }

        .top-nav-logo-icon {
            font-size: 20px;
        }

        .top-nav-logo-text {
            font-size: 12px;
        }

        .top-nav-items {
            padding: 0 8px 6px 8px;
            gap: 3px;
        }

        .top-nav-button,
        .top-nav-logout {
            padding: 4px 8px;
            font-size: 9px;
        }

        section[data-testid="stMain"] {
            padding-top: 110px !important;
        }

        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
    }
    </style>
    
    <script>
    // Navigation functionality
    document.addEventListener('DOMContentLoaded', function() {
        const navButtons = document.querySelectorAll('.top-nav-button');
        navButtons.forEach(button => {
            button.addEventListener('click', function() {
                navButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
            });
        });
    });
    </script>
    """, unsafe_allow_html=True)

    full_name = st.session_state.get('full_name', 'User')
    role      = st.session_state.get('role', 'ASM')

    # ══════════════════════════════════════════════════════════════
    # TOP NAVIGATION BAR
    # ══════════════════════════════════════════════════════════════
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        st.markdown("""
        <div class='top-nav-container'>
            <div class='top-nav-header'>
                <div class='top-nav-logo'>
                    <div class='top-nav-logo-icon'>💊</div>
                    <div class='top-nav-logo-text'>ENT-SalesPulse</div>
                </div>
                <div class='top-nav-user'>
                    <span>👤</span>
                    <span class='top-nav-user-name'>{}</span>
                    <span style='color: #4b5563;'>•</span>
                    <span class='top-nav-user-role'>{}</span>
                </div>
            </div>
            <div class='top-nav-items'>
                <button class='top-nav-button active' onclick="document.querySelector('input[value=\\'📊  Sales\\']').click();">📊 Sales</button>
                <button class='top-nav-button' onclick="document.querySelector('input[value=\\'💊  CP Sales\\']').click();">💊 CP Sales</button>
                <button class='top-nav-button' onclick="document.querySelector('input[value=\\'📅  FY Sales\\']').click();">📅 FY Sales</button>
                <button class='top-nav-button' onclick="document.querySelector('input[value=\\'📈  Sales Metrics\\']').click();">📈 Metrics</button>
                <button class='top-nav-button' onclick="document.querySelector('input[value=\\'💰  Outstanding\\']').click();">💰 Outstanding</button>
                <button class='top-nav-button' onclick="document.querySelector('input[value=\\'📉  L10D Trend\\']').click();">📉 L10D Trend</button>
                <button class='top-nav-logout' id='logout_btn_top'>🚪 Logout</button>
            </div>
        </div>
        """.format(full_name, role), unsafe_allow_html=True)

    with col2:
        pass

    with col3:
        pass

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # HIDDEN NAVIGATION (for Streamlit page routing)
    # ══════════════════════════════════════════════════════════════
    page = st.radio("nav", [
        "📊  Sales",
        "💊  CP Sales",
        "📅  FY Sales",
        "📈  Sales Metrics",
        "💰  Outstanding",
        "📉  L10D Trend",
    ], label_visibility="collapsed", key="main_nav", horizontal=True)

    # Logout button handler
    if st.button("", key="logout_btn_hidden"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

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

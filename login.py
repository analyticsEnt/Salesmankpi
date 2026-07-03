import streamlit as st
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

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

def verify_user(username: str, password: str):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT * FROM users WHERE username=:u AND password=:p"),
                {"u": username, "p": password}
            ).fetchone()
        if row:
            return dict(row._mapping)
        return None
    except Exception as e:
        st.error(f"DB error: {e}")
        return None

def show_login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Outfit', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #060818, #0d1117, #060818); }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .stTextInput > div > div > input {
        background: #161b2e !important; border: 1.5px solid #1f2937 !important;
        border-radius: 14px !important; color: #f9fafb !important;
        padding: 14px 18px !important; font-size: 15px !important; height: 52px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important; border: none !important;
        border-radius: 14px !important; font-size: 16px !important;
        font-weight: 700 !important; height: 54px !important;
        margin-top: 8px !important;
        box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
    }
    .stButton > button:hover { transform: translateY(-2px) !important; }
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom:8px;'>
            <div style='font-size:48px; margin-bottom:10px;'>💊</div>
            <div style='font-size:32px; font-weight:800;
                background:linear-gradient(135deg,#818cf8,#c084fc);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
                Entero SalesPulse
            </div>
            <div style='font-size:12px; color:#4b5563; letter-spacing:1px; margin-bottom:36px;'>
                PHARMA SALES INTELLIGENCE PLATFORM
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='font-size:11px;font-weight:600;letter-spacing:1px;color:#6b7280;margin-bottom:1px;'>USERNAME</div>", unsafe_allow_html=True)
        username = st.text_input("u", placeholder="Enter your username", key="usr", label_visibility="collapsed")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:11px;font-weight:600;letter-spacing:1px;color:#6b7280;margin-bottom:1px;'>PASSWORD</div>", unsafe_allow_html=True)
        password = st.text_input("p", placeholder="Enter your password", type="password", key="pwd", label_visibility="collapsed")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", use_container_width=True, key="signin"):
            if not username or not password:
                st.error("⚠️ Please enter both username and password.")
            else:
                with st.spinner("Authenticating..."):
                    user = verify_user(username.strip(), password.strip())
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user      = user
                    st.session_state.full_name = user.get('full_name', username)
                    st.session_state.role      = user.get('role', 'ASM')
                    st.session_state.region    = user.get('region', 'ALL')
                    st.session_state.unit      = user.get('unit', 'ALL')
                    st.session_state.asm_code  = user.get('asm_code', 'ALL')
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

        st.markdown("""
        <div style='text-align:center;color:#1f2937;font-size:12px;margin-top:28px;'>
            © 2026 SalesPulse • Entero Healthcare
        </div>
        """, unsafe_allow_html=True)

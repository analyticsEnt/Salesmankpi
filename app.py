import streamlit as st

st.set_page_config(
    page_title="Ent_Retail Sales Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Remove all gaps and hide collapse button
st.markdown("""
<style>
[data-testid="collapsedControl"] { display: none !important; }
span[data-testid="stIconMaterial"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }
.stApp > header { display: none !important; }

.block-container {
    padding-top: 1.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}

/* Main content expands when sidebar collapses */
section[data-testid="stMain"] {
    transition: margin-left 0.3s ease, width 0.3s ease !important;
}

section[data-testid="stSidebar"]:not(:hover) ~ section[data-testid="stMain"],
section[data-testid="stSidebar"][aria-expanded="false"] ~ section[data-testid="stMain"] {
    margin-left: 35px !important;
    width: calc(100% - 35px) !important;
}
</style>
""", unsafe_allow_html=True)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.logged_in:
    from login import show_login
    show_login()
else:
    from dashboard import show_dashboard
    show_dashboard()

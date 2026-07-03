import streamlit as st

def coming_soon(page_name, icon, description):
    st.markdown(f"""
    <style>
    .stApp {{ background: #060818; }}
    </style>
    <div style='display:flex;flex-direction:column;align-items:center;
        justify-content:center;min-height:70vh;text-align:center;padding:40px;'>
        <div style='font-size:72px;margin-bottom:24px;'>{icon}</div>
        <div style='font-size:34px;font-weight:800;color:#f9fafb;
            margin-bottom:12px;letter-spacing:-0.5px;'>{page_name}</div>
        <div style='font-size:15px;color:#4b5563;max-width:420px;
            margin-bottom:36px;line-height:1.7;'>{description}</div>
        <div style='background:linear-gradient(135deg,#1e1f4b,#1a1035);
            border:1px solid #6366f1;border-radius:16px;
            padding:18px 36px;font-size:14px;font-weight:700;
            color:#818cf8;letter-spacing:1.5px;'>
            🚧 &nbsp; DASHBOARD COMING SOON
        </div>
    </div>
    """, unsafe_allow_html=True)

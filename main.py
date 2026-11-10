import streamlit as st

# Pi Domain Verification Key output
st.text("5cbce2829c97aff62dd9a70a71f397e4591d20f7cd081d29bc63c2304b16a49bca9b11bcc7bf0e919c1c8715ac679f3eac82128809d1e7713d44264d4ebda598")

import streamlit as st
import sqlite3
from database import init_db
from shop_owner_app import render_shop_owner_app
from dealer_app import render_dealer_app
from customer_app import render_customer_app
from translations import get_text

st.set_page_config(page_title="PiPOS B2B & Inventory Ecosystem", layout="wide")

conn = init_db()
c = conn.cursor()

st.sidebar.title("🌐 Language / භාෂාව")
selected_language = st.sidebar.selectbox(
    "Select Language / භාෂාව තෝරන්න", 
    ["English", "සිංහල (Sinhala)", "한국어 (Korean)", "日本語 (Japanese)", "हिन्दी (Hindi)", "Bahasa Indonesia", "Filipino (Tagalog)", "Bahasa Melayu"]
)

st.sidebar.markdown("---")
st.sidebar.title(f"🔐 {get_text(selected_language, 'role_select')}")

role = st.sidebar.selectbox(
    get_text(selected_language, 'role_select'), 
    [get_text(selected_language, 'shop_owner'), get_text(selected_language, 'dealer'), get_text(selected_language, 'customer')]
)

pi_user = st.sidebar.text_input(get_text(selected_language, 'wallet_id'), value="pi_user_01")

st.sidebar.markdown("---")
st.sidebar.info(f"💡 **{get_text(selected_language, 'master_wallet')}**\n`GDXHKMBBL3UZB3KBUYUOBZ5LARU7V7WU6YU25NF5Z3IRSMI3JLHIR36L`")

if role == get_text(selected_language, 'shop_owner'):
    render_shop_owner_app(conn, c, pi_user, selected_language)
elif role == get_text(selected_language, 'dealer'):
    render_dealer_app(conn, c, pi_user, selected_language)
elif role == get_text(selected_language, 'customer'):
    render_customer_app(conn, c, pi_user, selected_language)

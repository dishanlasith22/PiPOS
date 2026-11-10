import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode  # බාර්කෝඩ් කියවීමට (සංස්කරණය: අවශ්‍ය නම් pip install pyzbar opencv-python-headless)

st.subheader("📷 Product Barcode & QR Scanner")

# ජංගම දුරකථන කැමරාවෙන් ෆොටෝ එකක් හෝ ලයිව් කැමරාවෙන් කැප්චර් කිරීම
camera_image = st.camera_input("Scan Dealer / Product Barcode")

if camera_image is not None:
    # Bytes වලින් එන ඉන්පුට් එක OpenCV ඉමේජ් එකක් බවට හැරවීම
    bytes_data = camera_image.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # බාර්කෝඩ් හෝ QR කෝඩ් ඩිකෝඩ් කිරීම
    decoded_objects = decode(cv2_img)
    
    if decoded_objects:
        for obj in decoded_objects:
            barcode_data = obj.data.decode('utf-8')
            barcode_type = obj.type
            st.success(f"✅ Successfully Scanned! ({barcode_type})")
            st.write(f"**Item Code / Data:** `{barcode_data}`")
            
            # මෙතැනට ඔබගේ ඩේටාබේස් එකෙන් අදාළ අයිතමය (Item) සෙවීමට හෝ Cart එකට එකතු කිරීමට අවශ්‍ය ලොජික් එක දමන්න
    else:
        st.warning("⚠️ No barcode detected. Please try scanning again clearly.")

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


import streamlit as st
import streamlit.components.v1 as components

st.subheader("📷 Live Barcode & QR Scanner")

# පසුපස කැමරාව (Back Camera) පාවිච්චි කරන ස්කෑනර් කෝඩ් එක
scanner_code = """
<div style="width: 100%; max-width: 400px; margin: auto;" id="reader"></div>
<script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
<script>
function onScanSuccess(decodedText, decodedResult) {
    document.getElementById('scanned-result').innerHTML = "<b style='color:green; font-size:18px;'>✅ Scanned Code: " + decodedText + "</b>";
    console.log(`Code matched = ${decodedText}`);
}

function onScanFailure(error) {
    // Silent failure while scanning
}

let html5QrcodeScanner = new Html5QrcodeScanner(
    "reader", 
    { 
        fps: 10, 
        qrbox: { width: 250, height: 100 },
        facingMode: "environment"  // පසුපස කැමරාව (Back Camera) සඳහා
    }, 
    false
);
html5QrcodeScanner.render(onScanSuccess, onScanFailure);
</script>

<div id="scanned-result" style="text-align: center; margin-top: 15px; padding: 10px; background: #f0f2f6; border-radius: 8px;">
    📷 Point back camera at barcode...
</div>
"""

components.html(scanner_code, height=450)


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

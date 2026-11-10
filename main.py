import streamlit as st
import streamlit.components.v1 as components

st.subheader("📷 Live Barcode & QR Scanner")

# ජංගම දුරකථන කැමරාවෙන් සජීවීව බාර්කෝඩ් ස්කෑන් කරන JavaScript කෝඩ් එක
scanner_code = """
<div style="width: 100%; max-width: 400px; margin: auto;" id="reader"></div>
<script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
<script>
function onScanSuccess(decodedText, decodedResult) {
    // බාර්කෝඩ් එක සාර්ථකව ස්කෑන් වූ පසු පෙන්වන අංකය
    document.getElementById('scanned-result').innerHTML = "<b style='color:green; font-size:18px;'>✅ Scanned Code: " + decodedText + "</b>";
    
    // මෙහිදී කෝඩ් එක Streamlit වෙත යැවීම සඳහා අවශ්‍ය ලොජික් එක ක්‍රියාත්මක කළ හැක
    console.log(`Code matched = ${decodedText}`);
}

function onScanFailure(error) {
    // ස්කෑන් වන අතරතුර දෝෂ සිදු නොවීමට (Quiet failure)
}

let html5QrcodeScanner = new Html5QrcodeScanner(
    "reader", { fps: 10, qrbox: { width: 250, height: 100 } }, /* verbose= */ false);
html5QrcodeScanner.render(onScanSuccess, onScanFailure);
</script>

<div id="scanned-result" style="text-align: center; margin-top: 15px; padding: 10px; background: #f0f2f6; border-radius: 8px;">
    📷 Point camera at barcode to scan...
</div>
"""

# Streamlit ඇප් එක තුළ මෙම කැමරා ස්කෑනරය පෙන්වීම
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

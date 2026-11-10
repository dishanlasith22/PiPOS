import streamlit as st
import streamlit.components.v1 as components

st.subheader("📷 PiPOS Professional Scanner (Stock In & Billing)")

# ටැබ් දෙකකට වෙන් කිරීම (1. Stock In - ඩීලර් බඩු ඇතුළත් කිරීම, 2. Billing - බිල් කිරීම)
tab1, tab2 = st.tabs(["📦 1. Stock In (Dealer Register)", "🛒 2. POS Billing (Shop Sale)"])

with tab1:
    st.markdown("### 📥 Dealer Stock In - Scan New Items")
    st.info("ඩීලර් විසින් අලුත් බඩු ස්කෑන් කර පළමු වතාවට ඩේටාබේස් එකට ඇතුළත් කරන තැන.")
    
    # ඩීලර් සඳහා ස්කෑනරය ටොගල් කිරීම
    if 'stock_scanner' not in st.session_state:
        st.session_state.stock_scanner = False

    if not st.session_state.stock_scanner:
        if st.button("📷 Open Stock Scanner", type="primary"):
            st.session_state.stock_scanner = True
            st.rerun()
    else:
        if st.button("❌ Close Stock Scanner", type="secondary"):
            st.session_state.stock_scanner = False
            st.rerun()

    if st.session_state.stock_scanner:
        stock_scanner_html = """
        <div style="width: 100%; max-width: 400px; margin: auto; text-align: center;">
            <div style="width: 100%; height: 300px; border: 3px solid #00E676; border-radius: 12px; background: #000;" id="stock-reader"></div>
        </div>
        
        <!-- Beep Audio Element -->
        <audio id="beep-sound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>

        <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
        <script>
        function onScanSuccess(decodedText, decodedResult) {
            // Play Beep Sound
            var audio = document.getElementById('beep-sound');
            if(audio) { audio.play(); }

            const inputField = window.parent.document.querySelector('input[aria-label="Scanned Barcode (Stock In)"]');
            if (inputField) {
                inputField.value = decodedText;
                inputField.dispatchEvent(new Event('input', { bubbles: true }));
            }
            document.getElementById('stock-result').innerHTML = "<b style='color:green; font-size:18px;'>✅ Scanned: " + decodedText + "</b>";
        }

        let html5QrCode = new Html5Qrcode("stock-reader");
        html5QrCode.start(
            { facingMode: "environment" },
            { fps: 15, qrbox: { width: 280, height: 280 } },
            onScanSuccess
        ).catch(err => { console.log(err); });
        </script>
        <div id="stock-result" style="text-align: center; margin-top: 10px; color: green; font-weight: bold;"></div>
        """
        components.html(stock_scanner_html, height=380)

    # ඩීලර් ස්කෑන් කර ලබාගන්නා අංකය වැටෙන තැන
    stock_barcode = st.text_input("Scanned Barcode (Stock In)", placeholder="Scan or type barcode...")
    
    if stock_barcode:
        st.success(f"📦 New Barcode Detected: **{stock_barcode}**")
        with st.form("register_form"):
            item_name = st.text_input("Item Name (e.g. Cinnamon 100g)")
            item_price = st.number_input("Unit Price (Rs.)", min_value=0.0)
            item_stock = st.number_input("Initial Stock Quantity", min_value=1, value=10)
            submit_btn = st.form_submit_button("Save to Database")
            
            if submit_btn:
                st.success(f"Successfully registered '{item_name}' with barcode {stock_barcode}!")

with tab2:
    st.markdown("### 💳 POS Billing - Scan & Sell")
    st.info("සාප්පු හිමියා බිල් ಮಾಡುವ විට බඩු ස්කෑන් කරන තැන.")
    
    if 'bill_scanner' not in st.session_state:
        st.session_state.bill_scanner = False

    if not st.session_state.bill_scanner:
        if st.button("📷 Open Billing Scanner", type="primary"):
            st.session_state.bill_scanner = True
            st.rerun()
    else:
        if st.button("❌ Close Billing Scanner", type="secondary"):
            st.session_state.bill_scanner = False
            st.rerun()

    if st.session_state.bill_scanner:
        billing_scanner_html = """
        <div style="width: 100%; max-width: 400px; margin: auto; text-align: center;">
            <div style="width: 100%; height: 300px; border: 3px solid #2979FF; border-radius: 12px; background: #000;" id="billing-reader"></div>
import streamlit as st
import streamlit.components.v1 as components

st.subheader("📷 PiPOS Advanced Barcode & QR Scanner")

if 'scanner_active' not in st.session_state:
    st.session_state.scanner_active = False

col1, col2 = st.columns([1, 1])
with col1:
    if not st.session_state.scanner_active:
        if st.button("📷 Open Pro Scanner", type="primary", use_container_width=True):
            st.session_state.scanner_active = True
            st.rerun()
with col2:
    if st.session_state.scanner_active:
        if st.button("❌ Close Scanner", type="secondary", use_container_width=True):
            st.session_state.scanner_active = False
            st.rerun()

if st.session_state.scanner_active:
    # වැඩි දියුණු කළ Native Barcode Detector HTML5 කෝඩ් එක (వක්‍ර කෝඩ් සඳහා වඩාත් නිරවද්‍යයි)
    advanced_scanner_html = """
    <div style="width: 100%; max-width: 400px; margin: auto; text-align: center;">
        <div style="width: 100%; height: 320px; border: 3px solid #FF3D00; border-radius: 12px; background: #000; position: relative;" id="reader"></div>
    </div>
    
    <audio id="beep-sound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"></audio>

    <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
    <script>
    function onScanSuccess(decodedText, decodedResult) {
        var audio = document.getElementById('beep-sound');
        if(audio) { audio.play(); }

        const inputField = window.parent.document.querySelector('input[type="text"]');
        if (inputField) {
            inputField.value = decodedText;
            inputField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        
        document.getElementById('scanned-result').innerHTML = "<b style='color:green; font-size:18px;'>✅ Scanned Successfully: " + decodedText + "</b>";
    }

    let html5QrcodeScanner = new Html5QrcodeScanner(
        "reader", 
        { 
            fps: 20, 
            qrbox: { width: 300, height: 120 },
            facingMode: "environment",
            experimentalFeatures: {
                useBarCodeDetectorIfSupported: true
            }
        }, 
        false
    );
    html5QrcodeScanner.render(onScanSuccess, (err) => {});
    </script>
    
    <div id="scanned-result" style="text-align: center; margin-top: 15px; padding: 10px; background: #fff3e0; border-radius: 8px; color: #e65100; font-weight: bold;">
        📱 Point camera at curved barcode steadily...
    </div>
    """
    components.html(advanced_scanner_html, height=500)

st.markdown("---")

# ස්කෑන් වන හෝ අතින් ක්ෂණිකව සකස් කළ හැකි අංකය
scanned_barcode = st.text_input("Scanned Barcode / Item Code", placeholder="Scan item or verify code here...")

if scanned_barcode:
    st.success(st.markdown(f"🔍 Active Code to Process: **`{scanned_barcode}`**"))
    # මෙතැනින් ඉදිරියට ඩේටාබේස් ලොජික් එක ක්‍රියාත්මක කරගත හැක.





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

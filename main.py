import streamlit as st
import streamlit.components.v1 as components
# ඔබ Supabase භාවිතා කරන නිසා පහත පරිදි කනෙක්ට් කරගත හැක (ඔබේ සෙටප් එක අනුව)
# from supabase import create_client

st.subheader("🛒 PiPOS B2B Billing & Barcode Scanner")

# Streamlit හි Session State හරහා කැමරාව ඔන්/ඕෆ් කිරීම පාලනය කිරීම
if 'scanner_active' not in st.session_state:
    st.session_state.scanner_active = False

# සාප්පු සවාරි කරත්තය (Cart) සඳහා session state එකක් පවත්වා ගැනීම
if 'cart' not in st.session_state:
    st.session_state.cart = []

# කැමරාව ඕන්/ඕෆ් කිරීමට බට්න්
col1, col2 = st.columns([1, 1])
with col1:
    if not st.session_state.scanner_active:
        if st.button("📷 Open Barcode Scanner", type="primary", use_container_width=True):
            st.session_state.scanner_active = True
            st.rerun()
with col2:
    if st.session_state.scanner_active:
        if st.button("❌ Close Scanner", type="secondary", use_container_width=True):
            st.session_state.scanner_active = False
            st.rerun()

# කැමරාව ඇක්ටිව් වී ඇත්නම් HTML5 ස්කෑනරය පෙන්වීම
if st.session_state.scanner_active:
    scanner_html = """
    <div style="width: 100%; max-width: 400px; margin: auto; border: 2px solid #ff4b4b; border-radius: 10px; padding: 10px; background: #fff;" id="reader"></div>
    <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
    <script>
    function onScanSuccess(decodedText, decodedResult) {
        const inputField = window.parent.document.querySelector('input[type="text"]');
        if (inputField) {
            inputField.value = decodedText;
            inputField.dispatchEvent(new Event('input', { bubbles: true }));
        }
        document.getElementById('scanned-result').innerHTML = "<b style='color:green; font-size:18px;'>✅ Scanned: " + decodedText + "</b>";
    }

    let html5QrcodeScanner = new Html5QrcodeScanner(
        "reader", 
        { fps: 10, qrbox: { width: 250, height: 100 }, facingMode: "environment" }, 
        false
    );
    html5QrcodeScanner.render(onScanSuccess, () => {});
    </script>
    <div id="scanned-result" style="text-align: center; margin-top: 15px; padding: 10px; background: #e6f4ea; border-radius: 8px; color: #137333;">
        📷 Back camera is active. Point at barcode...
    </div>
    """
    components.html(scanner_html, height=480)

st.markdown("---")

# බාර්කෝඩ් අංකය ඇතුළත් වන ප්‍රධාන ඉන්පුට් එක
scanned_barcode = st.text_input("Active Barcode / Item Code", placeholder="Scan using camera or type here...")

# --- ඩේටාබේස් ලොජික් එක (Database & Item Lookup Logic) ---
if scanned_barcode:
    # 1. Supabase හෝ Local Database එකෙන් අයිතමය සෙවීම
    # (උදාහරණයක් ලෙස අපිට Supabase query එකක් මෙලෙස ලිවිය හැක:)
    # response = supabase.table("products").select("*").eq("barcode", scanned_barcode).execute()
    # item_data = response.data[0] if response.data else None

    # (දැන් පරීක්ෂා කර බැලීමට ඩමී ඩේටා (Dummy data) උදාහරණයක් පහත දැක්වේ:)
    sample_database = {
        "6928802587458": {"name": "Cinnamon Export Grade (100g)", "price": 450.00, "stock": 50},
        "4790012001234": {"name": "Black Pepper Pure (250g)", "price": 350.00, "stock": 30}
    }
    
    item_data = sample_database.get(scanned_barcode)

    if item_data:
        st.success(f"🎉 Item Found: **{item_data['name']}** | Price: **Rs. {item_data['price']}**")
        
        # බිල්පත් කරත්තයට (Cart) අයිතමය එකතු කිරීමේ බටන් එක
        if st.button("➕ Add to Bill Cart"):
            st.session_state.cart.append({
                "code": scanned_barcode,
                "name": item_data['name'],
                "price": item_data['price'],
                "qty": 1
            })
            st.toast("Item added to cart successfully!", icon="🛒")
    else:
        st.error(f"⚠️ Barcode '{scanned_barcode}' not found in database! Please register the item.")

# --- බිල්පත් සාරාංශය (Billing Cart & Total Summary) ---
if st.session_state.cart:
    st.markdown("### 🛍️ Current Bill Cart")
    total_amount = 0
    
    for idx, cart_item in enumerate(st.session_state.cart):
        col_a, col_b, col_c = st.columns([3, 1, 1])
        with col_a:
            st.write(f"**{cart_item['name']}** (Rs. {cart_item['price']})")
        with col_b:
            st.write(f"Qty: {cart_item['qty']}")
        with col_c:
            total_amount += cart_item['price'] * cart_item['qty']
            st.write(f"Rs. {cart_item['price'] * cart_item['qty']}")

    st.markdown(f"### **Total Payable: Rs. {total_amount:.2f}**")
    
    if st.button("💳 Complete Payment (Pi Pay / Cash)", type="primary"):
        st.balloons()
        st.success("✅ Transaction completed successfully! Order synced with dealer.")
        st.session_state.cart = [] # Cart එක හිස් කිරීම




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

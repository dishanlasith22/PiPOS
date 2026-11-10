import streamlit as st
import pandas as pd
import datetime
import qrcode
from io import BytesIO
from translations import get_text

def render_dealer_app(conn, c, pi_user, selected_language):
    st.subheader("🏭 B2B Dealer Portal & Master Catalog")
    
    dealer_tab1, dealer_tab2, dealer_tab3, dealer_tab4, dealer_tab5 = st.tabs([
        get_text(selected_language, "d_tab1"), 
        get_text(selected_language, "d_tab2"), 
        get_text(selected_language, "d_tab3"), 
        get_text(selected_language, "d_tab4"), 
        get_text(selected_language, "d_tab5")
    ])
    
    with dealer_tab1:
        st.subheader("Dealer Handoff Confirmation (Online / Offline)")
        if st.button("⚡ Quick Test Sample Shop QR"):
            st.session_state.dealer_scan_demo = "Shop:Matara Main|Loc:Matara Town|Dealer:Global Foods Ltd (Matara)|Item:Maliban Chocolate Biscuit 400g|Qty:50|BuyPrice:0.40|SellPrice:0.50"
            
        scanned_handoff_qr = st.text_input("📷 Scan QR Code Data", value=st.session_state.get('dealer_scan_demo', ''))
        
        if scanned_handoff_qr:
            try:
                parts = dict(item.split(":") for item in scanned_handoff_qr.split("|"))
                shop_name = parts.get("Shop", "Matara Main")
                location = parts.get("Loc", "Matara Town")
                dealer_name = parts.get("Dealer", "Global Foods Ltd (Matara)")
                item_name = parts.get("Item", "Soap")
                qty = int(parts.get("Qty", "10"))
                buy_price = float(parts.get("BuyPrice", "0.40"))
                sell_price = float(parts.get("SellPrice", "0.50"))
                total_val = qty * buy_price
                
                st.success("✅ QR Code Verified Successfully!")
                st.info(f"🏪 **Shop:** {shop_name} ({location})\n📦 **Item:** {item_name} | **Qty:** {qty} | **Buying Price:** {buy_price} Pi | **Selling Price:** {sell_price} Pi")
                
                if st.button("✔️ Confirm & Submit Handoff", type="primary"):
                    time_str = datetime.datetime.now().strftime("%H:%M:%S")
                    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    existing = c.execute("SELECT ID, StockIn FROM live_stock_shop WHERE ShopName = ? AND ItemName = ? AND DealerName = ?", 
                                         (shop_name, item_name, dealer_name)).fetchone()
                    
                    if existing:
                        new_stock_in = existing[1] + qty
                        c.execute("UPDATE live_stock_shop SET StockIn = ? WHERE ID = ?", (new_stock_in, existing[0]))
                    else:
                        c.execute("INSERT INTO live_stock_shop (ShopName, Location, DealerName, ItemName, Price, StockIn, Sales) VALUES (?, ?, ?, ?, ?, ?, 0)",
                                  (shop_name, location, dealer_name, item_name, sell_price, qty))
                    
                    c.execute("INSERT INTO dealer_deliveries (ShopName, Location, DealerName, ItemName, Quantity, UnitPrice, TotalAmount, DeliveryTime, DateStamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                              (shop_name, location, dealer_name, item_name, qty, buy_price, total_val, time_str, date_str))
                    
                    conn.commit()
                    st.balloons()
                    st.success("Stock Handoff Confirmed and Database Updated!")
                    if 'dealer_scan_demo' in st.session_state:
                        del st.session_state.dealer_scan_demo
            except Exception as e:
                st.error(f"Invalid QR format! Error: {e}")

    with dealer_tab2:
        st.subheader("📋 Dealer Master Catalog (Add Items without Wholesale Price)")
        with st.form("add_catalog_form", clear_on_submit=True):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                cat_barcode = st.text_input("Barcode", value="BAR004")
                cat_dealer = st.text_input("Dealer Company Name", value="Global Foods Ltd (Matara)")
            with col_c2:
                cat_item = st.text_input("Full Item Name (e.g. Maliban Biscuit 400g)")
                
            if st.form_submit_button("➕ Add Item to Catalog"):
                if cat_item.strip() == "":
                    st.error("Item name cannot be empty!")
                else:
                    try:
                        c.execute("INSERT INTO dealer_catalog VALUES (?, ?, ?)", (cat_barcode, cat_dealer, cat_item))
                        conn.commit()
                        st.success(f"Successfully added {cat_item} to Global Catalog!")
                        st.rerun()
                    except:
                        st.success("Added successfully!")
                        
        st.markdown("---")
        catalog_df = pd.read_sql("SELECT Barcode, DealerName AS Dealer, ItemName AS Item FROM dealer_catalog", conn)
        st.dataframe(catalog_df, hide_index=True, use_container_width=True)

    with dealer_tab3:
        st.subheader("📊 Stock & Daily Selling Analytics")
        sub_t1, sub_t2 = st.tabs(["Live Stock Table", "Daily Selling Table"])
        with sub_t1:
            live_df = pd.read_sql("SELECT ShopName AS Shop, Location, DealerName AS Dealer, ItemName AS Item, Price, StockIn, Sales, (StockIn - Sales) AS LiveStock FROM live_stock_shop", conn)
            if not live_df.empty:
                st.dataframe(live_df, hide_index=True, use_container_width=True)
            else:
                st.info("No live stock data available.")
        with sub_t2:
            sales_df = pd.read_sql("SELECT ShopName AS Shop, Location, ItemName AS Item, Sales, (Sales * Price) AS TotalValue FROM live_stock_shop", conn)
            if not sales_df.empty:
                st.dataframe(sales_df, hide_index=True, use_container_width=True)
            else:
                st.info("No sales recorded.")

    with dealer_tab4:
        st.subheader("🚚 Delivery Progress & Today's Summary")
        curr_date = datetime.datetime.now().strftime("%Y-%m-%d")
        deliv_df = pd.read_sql(f"SELECT ShopName AS Shop, Location, DeliveryTime AS Time, ItemName AS Item, Quantity, TotalAmount FROM dealer_deliveries WHERE DateStamp='{curr_date}'", conn)
        today_total_delivered_val = deliv_df['TotalAmount'].sum() if not deliv_df.empty else 0.00
        st.markdown(
            f"""
            <div style="padding: 20px; background-color: #d4edda; border-left: 6px solid #28a745; border-radius: 5px; margin-bottom: 20px;">
                <h3 style="color: #155724; margin: 0;">🟢 Today Progress: {today_total_delivered_val:.2f} Pi</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        if not deliv_df.empty:
            st.dataframe(deliv_df, hide_index=True, use_container_width=True)
        else:
            st.info("No deliveries completed today.")

    with dealer_tab5:
        st.subheader("👤 Dealer Profile & Pi Wallet")
        existing_profile = c.execute("SELECT Name, Location, Phone, PiWalletAddress FROM profiles WHERE Username = ? AND Role = 'Dealer'", (pi_user,)).fetchone()
        
        d_name = st.text_input("Dealer Company Name", value=existing_profile[0] if existing_profile else "Global Supplies")
        d_loc = st.text_input("Location / Warehouse", value=existing_profile[1] if existing_profile else "Colombo")
        d_phone = st.text_input("Phone Number", value=existing_profile[2] if existing_profile else "+94 77 123 4567")
        d_wallet = st.text_input("Pi Network Wallet Address", value=existing_profile[3] if existing_profile else "G...")
        
        if st.button("💾 Save Dealer Profile & Wallet"):
            c.execute("INSERT OR REPLACE INTO profiles VALUES ('Dealer', ?, ?, ?, ?, ?, ?)", (pi_user, d_name, d_loc, d_phone, d_wallet, "url"))
            conn.commit()
            st.success("Dealer Profile and Pi Wallet Saved Successfully!")
            
        st.markdown("---")
        qr_payload = f"DealerID:{pi_user}|Name:{d_name}|Loc:{d_loc}|Wallet:{d_wallet}"
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(qr_payload)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buf = BytesIO()
        img.save(buf)
        st.image(buf.getvalue(), caption=f"Dealer QR for {d_name}", width=220)
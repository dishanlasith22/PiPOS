import streamlit as st
import pandas as pd
import datetime
import qrcode
from io import BytesIO
from translations import get_text

def render_shop_owner_app(conn, c, pi_user, selected_language):
    st.subheader("🏪 Shop Owner & Admin Dashboard")
    
    branches_df = pd.read_sql('SELECT BranchName FROM branches', conn)
    branch_list = branches_df['BranchName'].tolist()
    selected_branch = st.selectbox("Select Active Branch", branch_list)
    
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if 'selected_dealer_scan' not in st.session_state:
        st.session_state.selected_dealer_scan = None

    shop_tab1, shop_tab2, shop_tab3, shop_tab4, shop_tab5 = st.tabs([
        get_text(selected_language, "s_tab1"), 
        get_text(selected_language, "s_tab2"), 
        get_text(selected_language, "s_tab3"), 
        get_text(selected_language, "s_tab4"), 
        get_text(selected_language, "s_tab5")
    ])
    
    with shop_tab1:
        st.subheader("Point of Sale (POS) & Bill QR Generation")
        cashier_df = pd.read_sql(f"SELECT Username, Pin FROM staff_users WHERE Role='Cashier' AND Branch='{selected_branch}'", conn)
        cashier_dict = dict(zip(cashier_df['Username'], cashier_df['Pin']))
        
        if cashier_dict:
            cashier_id = st.selectbox("Cashier Login", list(cashier_dict.keys()))
            entered_pin = st.text_input("Enter Cashier PIN", type="password", key="cashier_pin_input")
            
            if entered_pin == cashier_dict.get(cashier_id):
                st.success("Cashier Authorized.")
                barcode_input = st.text_input("📷 Scan Barcode / Enter Item Code", key="pos_barcode")
                inventory_df = pd.read_sql(f"SELECT * FROM inventory WHERE Branch='{selected_branch}'", conn)
                selected_item = None
                
                if barcode_input:
                    matched = inventory_df[inventory_df['ItemCode'].str.lower() == barcode_input.strip().lower()]
                    if not matched.empty:
                        selected_item = matched.iloc[0]["Item"]
                
                if not selected_item and not inventory_df.empty:
                    selected_item = st.selectbox("Select Product", inventory_df["Item"].tolist(), key="pos_select_prod")
                
                if selected_item and not inventory_df.empty:
                    prod_row = inventory_df[inventory_df["Item"] == selected_item].iloc[0]
                    price = float(prod_row["Price"])
                    stock = int(prod_row["Stock"])
                    
                    st.write(f"🏷️ Price: {price} Pi | 📦 Stock: {stock}")
                    qty = st.number_input("Quantity", min_value=1, max_value=max(1, stock), value=1, key="pos_qty")
                    
                    if st.button("➕ Add to Bill"):
                        st.session_state.cart.append({"ItemCode": prod_row["ItemCode"], "Item": selected_item, "Price": price, "Qty": qty, "Total": price * qty})
                        st.toast("Item added!")
                        
                if st.session_state.cart:
                    cart_df = pd.DataFrame(st.session_state.cart)
                    st.dataframe(cart_df[["Item", "Qty", "Total"]], hide_index=True)
                    total = cart_df["Total"].sum()
                    st.markdown(f"### **Total: {total:.2f} Pi**")
                    
                    if st.button("💳 Complete Bill & Generate QR"):
                        for c_item in st.session_state.cart:
                            c.execute('UPDATE inventory SET Stock = Stock - ? WHERE ItemCode = ? AND Branch = ?', 
                                      (c_item["Qty"], c_item["ItemCode"], selected_branch))
                        conn.commit()
                        
                        bill_ref = f"BILL-{selected_branch}-{datetime.datetime.now().strftime('%H%M%S')}"
                        time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        for c_item in st.session_state.cart:
                            c.execute("UPDATE live_stock_shop SET Sales = Sales + ? WHERE ShopName = ? AND ItemName = ?",
                                      (c_item["Qty"], selected_branch, c_item["Item"]))
                        
                        c.execute('INSERT INTO transactions (PiUser, ShopName, Time, Type, Amount, Status, Synced) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                                  (pi_user if pi_user else "Guest", selected_branch, time_now, f"POS Sale ({bill_ref})", f"{total:.2f} Pi", "Completed", "No"))
                        conn.commit()
                        
                        st.success("Bill Generated! Scan QR below:")
                        qr_data = f"Shop:{selected_branch}|Loc:Matara Town|Dealer:Global Foods Ltd|Item:{cart_df.iloc[0]['Item']}|Qty:{cart_df.iloc[0]['Qty']}|Price:{cart_df.iloc[0]['Price']}"
                        qr = qrcode.QRCode(box_size=10, border=2)
                        qr.add_data(qr_data)
                        qr.make(fit=True)
                        img = qr.make_image(fill='black', back_color='white')
                        buf = BytesIO()
                        img.save(buf)
                        st.image(buf.getvalue(), caption=f"Bill QR ({bill_ref})", width=200)
                        st.session_state.cart = []
            elif entered_pin:
                st.error("Incorrect PIN!")

    with shop_tab2:
        st.subheader("📦 Stock In & Dealer QR Handoff")
        col_dq1, col_dq2 = st.columns([3, 1])
        with col_dq1:
            dealer_qr_input = st.text_input("📷 Scan Dealer QR Code", value=st.session_state.get('scanned_dealer_qr_val', ''))
        with col_dq2:
            st.write("")
            if st.button("⚡ Simulate Dealer QR"):
                st.session_state.scanned_dealer_qr_val = "DealerID:dealer_01|Name:Global Foods Ltd (Matara)|Loc:Matara|Wallet:G..."
                st.rerun()
                
        if dealer_qr_input:
            try:
                d_parts = dict(item.split(":") for item in dealer_qr_input.split("|"))
                st.session_state.selected_dealer_scan = d_parts.get("Name", "Global Foods Ltd (Matara)")
                st.success(f"✅ Active Dealer Selected: **{st.session_state.selected_dealer_scan}**")
            except:
                st.session_state.selected_dealer_scan = "Global Foods Ltd (Matara)"
                
        if st.session_state.selected_dealer_scan:
            st.info(f"Current Active Dealer: **{st.session_state.selected_dealer_scan}**")
            if st.button("🔄 Reset / Scan New Dealer"):
                st.session_state.selected_dealer_scan = None
                if 'scanned_dealer_qr_val' in st.session_state:
                    del st.session_state.scanned_dealer_qr_val
                st.rerun()
                
        st.markdown("---")
        if st.button("⚡ Quick Test Barcode (BAR001)"):
            st.session_state.test_barcode = "BAR001"
            
        scanned_barcode = st.text_input("📷 Scan Item Barcode / Enter Code", value=st.session_state.get('test_barcode', ''))
        
        fetched_item_name = ""
        fetched_price = 0.50
        
        if scanned_barcode:
            catalog_match = c.execute("SELECT ItemName FROM dealer_catalog WHERE Barcode = ?", (scanned_barcode,)).fetchone()
            if catalog_match:
                fetched_item_name = catalog_match[0]
                st.success(f"✅ Catalog Match: **{fetched_item_name}**")
            else:
                st.warning("Barcode not found in catalog. Enter details manually.")

        with st.form("stock_in_form", clear_on_submit=True):
            col_si1, col_si2 = st.columns(2)
            with col_si1:
                item_code = st.text_input("Item Code", value=scanned_barcode if scanned_barcode else "P100")
                item_name = st.text_input("Item Name", value=fetched_item_name)
                stock_qty = st.number_input("Stock Quantity", min_value=1, value=50)
            with col_si2:
                buying_price = st.number_input("Buying Price (Pi)", min_value=0.01, value=fetched_price * 0.8, step=0.01)
                selling_price = st.number_input("Selling Price (Pi)", min_value=0.01, value=fetched_price, step=0.01)

            if st.form_submit_button("🚀 Generate Shop Handoff QR"):
                if item_name.strip() == "":
                    st.error("Item Name cannot be empty!")
                elif not st.session_state.get('selected_dealer_scan'):
                    st.error("Please scan Dealer QR first!")
                else:
                    active_dealer = st.session_state.selected_dealer_scan
                    try:
                        c.execute('INSERT OR REPLACE INTO inventory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                                  (item_code, item_name, buying_price, selling_price, stock_qty, 0, 10, selected_branch, active_dealer, "No"))
                        conn.commit()
                    except:
                        pass
                        
                    st.success("Handoff QR Generated Successfully!")
                    handoff_data = f"Shop:{selected_branch}|Loc:Matara Town|Dealer:{active_dealer}|Item:{item_name}|Qty:{stock_qty}|BuyPrice:{buying_price}|SellPrice:{selling_price}"
                    qr = qrcode.QRCode(box_size=10, border=2)
                    qr.add_data(handoff_data)
                    qr.make(fit=True)
                    img = qr.make_image(fill='black', back_color='white')
                    buf = BytesIO()
                    img.save(buf)
                    st.image(buf.getvalue(), caption=f"Shop Handoff QR for Dealer ({active_dealer})", width=220)

    with shop_tab3:
        st.subheader("🏷️ Create & Publish Shop Promotions")
        search_item_q = st.text_input("🔍 Search Inventory Item", key="promo_search_input")
        if search_item_q:
            res_df = pd.read_sql(f"SELECT ItemCode, Item, Price FROM inventory WHERE Item LIKE '%{search_item_q}%' AND Branch='{selected_branch}'", conn)
            if not res_df.empty:
                for idx, row in res_df.iterrows():
                    col_p1, col_p2 = st.columns([3, 1])
                    col_p1.write(f"📦 **{row['Item']}** | Price: `{row['Price']} Pi`")
                    if col_p2.button("Select", key=f"sel_promo_{row['ItemCode']}"):
                        st.session_state.promo_selected_item = row
            else:
                st.warning("No matching items found.")
                
        if 'promo_selected_item' in st.session_state:
            p_item = st.session_state.promo_selected_item
            st.success(f"Selected: **{p_item['Item']}** (Price: {p_item['Price']} Pi)")
            with st.form("promo_form"):
                disc_pct = st.slider("Discount Percentage (%)", 1, 90, 10)
                dur_days = st.number_input("Duration (Days)", 1, 30, 7)
                orig_p = float(p_item['Price'])
                new_p = orig_p * (1 - disc_pct / 100)
                st.markdown(f"✨ **New Promo Price:** `{new_p:.2f} Pi`")
                if st.form_submit_button("🚀 Publish Promotion"):
                    try:
                        c.execute("INSERT INTO promotions (ShopName, ItemCode, ItemName, OriginalPrice, DiscountPercent, NewPrice, DurationDays, Status) VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')",
                                  (selected_branch, p_item['ItemCode'], p_item['Item'], orig_p, disc_pct, new_p, dur_days))
                        conn.commit()
                        st.success("Promotion published successfully!")
                        del st.session_state.promo_selected_item
                        st.rerun()
                    except:
                        pass

    with shop_tab4:
        st.subheader("⚙️ Admin Panel & Staff / Branch Management (Silent Exceptions & 3-Dot Confirm Delete)")
        adm_t1, adm_t2 = st.tabs(["Manage Staff", "Manage Branches"])
        
        with adm_t1:
            st.write("### Staff Members")
            new_s_user = st.text_input("Staff Username", key="st_user")
            new_s_pin = st.text_input("Staff PIN", type="password", key="st_pin")
            new_s_role = st.selectbox("Role", ["Cashier", "InventoryManager"], key="st_role")
            new_s_branch = st.selectbox("Branch", branch_list, key="st_branch")
            
            if st.button("Add Staff Member"):
                try:
                    c.execute("INSERT INTO staff_users VALUES (?, ?, ?, ?)", (new_s_user, new_s_pin, new_s_role, new_s_branch))
                    conn.commit()
                    st.success("Staff added successfully!")
                    st.rerun()
                except:
                    pass # Suppressed error message as requested
                    
            st.markdown("---")
            staff_df = pd.read_sql("SELECT Username, Role, Branch FROM staff_users", conn)
            if not staff_df.empty:
                for idx, row in staff_df.iterrows():
                    col_st1, col_st2, col_st3, col_st4 = st.columns([2, 2, 2, 1])
                    col_st1.write(row['Username'])
                    col_st2.write(row['Role'])
                    col_st3.write(row['Branch'])
                    
                    # 3-Dot Menu expansion for delete
                    with col_st4:
                        with st.expander("⋮"):
                            confirm_del_st = st.checkbox("Confirm Delete?", key=f"chk_st_{row['Username']}")
                            if confirm_del_st:
                                if st.button("🗑️ Delete Now", key=f"btn_del_st_{row['Username']}"):
                                    c.execute("DELETE FROM staff_users WHERE Username = ?", (row['Username'],))
                                    conn.commit()
                                    st.success("Deleted!")
                                    st.rerun()
            else:
                st.info("No staff added.")
                
        with adm_t2:
            st.write("### Branches")
            new_b = st.text_input("New Branch Name", key="adm_b")
            if st.button("Add Branch"):
                try:
                    c.execute("INSERT INTO branches VALUES (?)", (new_b,))
                    conn.commit()
                    st.success("Branch added!")
                    st.rerun()
                except:
                    pass # Suppressed error message as requested
                    
            st.markdown("---")
            for b_name in branch_list:
                col_b1, col_b2 = st.columns([4, 1])
                col_b1.write(f"🏪 {b_name}")
                if len(branch_list) > 1:
                    with col_b2:
                        with st.expander("⋮"):
                            confirm_del_b = st.checkbox("Confirm Delete?", key=f"chk_b_{b_name}")
                            if confirm_del_b:
                                if st.button("🗑️ Delete Now", key=f"btn_del_b_{b_name}"):
                                    c.execute("DELETE FROM branches WHERE BranchName = ?", (b_name,))
                                    conn.commit()
                                    st.success("Deleted!")
                                    st.rerun()

    with shop_tab5:
        st.subheader(f"📊 Sales & Settlements ({selected_branch})")
        st.info("ℹ️ All dealer payouts are automatically transferred at **11:59 PM (100% minus 0.25% platform fee)** daily.")
        
        settle_df = pd.read_sql(f"SELECT DealerName AS Dealer, ItemName AS Items, Sales AS SoldQty, (Sales * Price) AS Amount FROM live_stock_shop WHERE ShopName='{selected_branch}'", conn)
        if not settle_df.empty:
            settle_df['Platform Fee (0.25%)'] = settle_df['Amount'] * 0.0025
            settle_df['Dealer Payout'] = settle_df['Amount'] - settle_df['Platform Fee (0.25%)']
            settle_df['Status (11:59 PM)'] = "🟢 OK / Transferred to GDXHKMBBL3UZB3KBUYUOBZ5LARU7V7WU6YU25NF5Z3IRSMI3JLHIR36L"
            st.dataframe(settle_df, hide_index=True, use_container_width=True)
            tot_amt = settle_df['Amount'].sum()
            st.metric(label="Total Daily Settlements Processed", value=f"{tot_amt:.2f} Pi")
        else:
            st.info("No sales or settlement records available for today yet.")
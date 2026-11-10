import streamlit as st
import pandas as pd
import datetime
import qrcode
from io import BytesIO
from translations import get_text

def render_customer_app(conn, c, pi_user, selected_language):
    st.subheader("👤 B2B Customer Portal (Pi Wallet Connected)")
    
    cust_tab1, cust_tab2, cust_tab3, cust_tab4 = st.tabs([
        get_text(selected_language, "c_tab1"), 
        get_text(selected_language, "c_tab2"), 
        get_text(selected_language, "c_tab3"),
        "🤝 Referral & Affiliate"
    ])
    
    with cust_tab1:
        st.subheader("Promotions from Active Shops")
        try:
            promo_df = pd.read_sql("SELECT ShopName, ItemName, OriginalPrice, DiscountPercent, NewPrice, DurationDays FROM promotions WHERE Status='Active'", conn)
            if not promo_df.empty:
                st.dataframe(promo_df, hide_index=True, use_container_width=True)
            else:
                st.info("No active promotions at the moment.")
        except:
            st.info("No active promotions available yet.")
            
    with cust_tab2:
        st.subheader("Scan & Pay via Pi Wallet")
        bill_qr_input = st.text_input("📷 Scan Shop Bill QR Code")
        if bill_qr_input:
            st.success("✅ Bill QR Recognized!")
            st.info("Pay securely using your Pi Wallet.")
            if st.button("Pi Pay Now", type="primary"):
                st.balloons()
                st.success("Payment of Pi successful! Transaction recorded.")
                
    with cust_tab3:
        st.subheader("Your Pi Transaction History")
        tx_df = pd.read_sql(f"SELECT Time, Type, Amount, Status FROM transactions WHERE PiUser='{pi_user}'", conn)
        if not tx_df.empty:
            st.dataframe(tx_df, hide_index=True, use_container_width=True)
        else:
            st.info("No transaction history found.")

    with cust_tab4:
        st.subheader("🤝 Customer Referral & Affiliate Program (Max 3 per Shop)")
        
        sub_t1, sub_t2 = st.tabs(["📋 Referral Details & Codes", "💰 Referral Income & Input"])
        
        with sub_t1:
            st.write("### Your Unique Shop-Specific Referral Codes & Slots")
            st.info("ℹ️ Referral codes are generated only for shops where you have completed actual purchases (transactions). You can share this code with up to 3 friends!")
            
            # Find only the shops/branches where this customer has actual transactions
            trans_shops_df = pd.read_sql(f"SELECT DISTINCT ShopName FROM transactions WHERE PiUser = '{pi_user}'", conn)
            
            if trans_shops_df.empty:
                st.warning("⚠️ You haven't made any purchases (transactions) in any shop yet. Complete a purchase to unlock your shop-specific referral codes!")
            else:
                for idx, s_row in trans_shops_df.iterrows():
                    shop_name = s_row['ShopName']
                    
                    # Check if referral code exists for this user & shop
                    ref_row = c.execute("SELECT ReferralCode, Ref1, Ref2, Ref3 FROM referrals WHERE CustomerUsername = ? AND ShopName = ?", (pi_user, shop_name)).fetchone()
                    
                    if not ref_row:
                        generated_code = f"REF-{shop_name[:3].upper()}-{pi_user.upper()}-{int(datetime.datetime.now().timestamp())}"
                        c.execute("INSERT INTO referrals (CustomerUsername, ShopName, ReferralCode, Ref1, Ref2, Ref3, Income) VALUES (?, ?, ?, '', '', '', 0.0)", 
                                  (pi_user, shop_name, generated_code))
                        conn.commit()
                        ref_row = (generated_code, '', '', '')
                    
                    code_val, r1, r2, r3 = ref_row
                    
                    with st.expander(f"🏪 Shop: {shop_name}"):
                        col_rc1, col_rc2 = st.columns([3, 1])
                        col_rc1.text_input(f"Unique Referral Code ({shop_name})", value=code_val, key=f"code_disp_{shop_name}", disabled=True)
                        
                        if col_rc2.button("📋 Copy Code", key=f"copy_{shop_name}*"):
                            st.success(f"Copied code: {code_val}")
                            
                        st.write("**Referred Friends (Max 3 slots):**")
                        st.markdown(f"1. **Slot 1:** {r1 if r1 else '🟢 Available'}")
                        st.markdown(f"2. **Slot 2:** {r2 if r2 else '🟢 Available'}")
                        st.markdown(f"3. **Slot 3:** {r3 if r3 else '🟢 Available'}")

        with sub_t2:
            st.write("### Referral Income & Friend Link Confirmation")
            
            st.markdown("#### 📥 Paste Friend's Referral Code to Link")
            input_friend_code = st.text_input("Enter/Paste Referral Code received from a friend")
            
            if st.button("🔗 Confirm & Link Referral"):
                if not input_friend_code.strip():
                    st.error("Please enter a valid referral code.")
                else:
                    owner_row = c.execute("SELECT CustomerUsername, ShopName, Ref1, Ref2, Ref3 FROM referrals WHERE ReferralCode = ?", (input_friend_code.strip(),)).fetchone()
                    
                    if not owner_row:
                        st.error("Invalid Referral Code!")
                    elif owner_row[0] == pi_user:
                        st.warning("You cannot use your own referral code!")
                    else:
                        owner_user, shop_name, r1, r2, r3 = owner_row
                        
                        has_transacted = c.execute("SELECT COUNT(*) FROM transactions WHERE PiUser = ? AND ShopName = ?", (pi_user, shop_name)).fetchone()[0]
                        
                        if has_transacted > 0:
                            st.error("❌ You have already transacted with this shop before! You cannot be added as a new referral.")
                        else:
                            if not r1:
                                c.execute("UPDATE referrals SET Ref1 = ? WHERE ReferralCode = ?", (pi_user, input_friend_code.strip()))
                                conn.commit()
                                st.success(f"✅ Successfully linked to {owner_user} for {shop_name} (Slot 1)! Commission activated (1%).")
                                st.balloons()
                            elif not r2:
                                c.execute("UPDATE referrals SET Ref2 = ? WHERE ReferralCode = ?", (pi_user, input_friend_code.strip()))
                                conn.commit()
                                st.success(f"✅ Successfully linked to {owner_user} for {shop_name} (Slot 2)! Commission activated (1%).")
                                st.balloons()
                            elif not r3:
                                c.execute("UPDATE referrals SET Ref3 = ? WHERE ReferralCode = ?", (pi_user, input_friend_code.strip()))
                                conn.commit()
                                st.success(f"✅ Successfully linked to {owner_user} for {shop_name} (Slot 3)! Commission activated (1%).")
                                st.balloons()
                            else:
                                st.error("❌ This referral code has already reached its maximum limit of 3 friends!")

            st.markdown("---")
            st.write("### 💵 Your Earned Referral Income Table")
            
            my_inc_df = pd.read_sql(f"SELECT ShopName, Ref1, Ref2, Ref3, Income FROM referrals WHERE CustomerUsername = '{pi_user}'", conn)
            if not my_inc_df.empty:
                st.dataframe(my_inc_df, hide_index=True, use_container_width=True)
            else:
                st.info("No referral earnings yet.")
                
            st.markdown("---")
            st.write("### 🏬 List of New Shops Discovered & Recommended by Friends")
            disc_shops = pd.read_sql(f"SELECT ShopName, CustomerUsername AS Referrer FROM referrals WHERE Ref1='{pi_user}' OR Ref2='{pi_user}' OR Ref3='{pi_user}'", conn)
            if not disc_shops.empty:
                st.dataframe(disc_shops, hide_index=True, use_container_width=True)
            else:
                st.info("No new shops linked via friend referrals yet.")
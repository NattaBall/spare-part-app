# To run this app, ensure 'streamlit' is installed via: pip install streamlit
import pandas as pd
import os
from datetime import datetime
import sys

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None
    sys.stderr.write("Streamlit is not installed. Please run 'pip install streamlit' to use the app.\n")

if st:
    # Initial Setup
    st.set_page_config(page_title="Spare Part Manager", layout="wide")
    st.title("📦 Spare Part Management System")

    # File Storage
    DB_FILE = "spare_parts.csv"
    BACKUP_FILE = "backup_spare_parts.csv"
    GITHUB_IMAGE_URL = "https://raw.githubusercontent.com/NattaBall/spare-part-app/main/images"

    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Part No", "Name", "Category", "Stock", "Image Path", "History"])
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)

    def save_data():
        df.to_csv(BACKUP_FILE, index=False)
        df.to_csv(DB_FILE, index=False)

    def restore_backup():
        if os.path.exists(BACKUP_FILE):
            return pd.read_csv(BACKUP_FILE)
        return df

    def get_image_url(image_path):
        if pd.isna(image_path) or str(image_path).strip().lower() in ["", "none", "nan"]:
            return f"{GITHUB_IMAGE_URL}/no_image.png"
        return f"{GITHUB_IMAGE_URL}/{image_path}"
    
# Section: Login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    # ✅ CSS Background Login
    st.markdown(
        """
        <style>
        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-image: url('https://raw.githubusercontent.com/NattaBall/spare-part-app/main/images/login%20background.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            z-index: 0;
            opacity: 0.4;
            filter: blur(5px) brightness(0.7);
        }
        .block-container {
            position: relative;
            z-index: 1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🔒 กรุณาเข้าสู่ระบบ")
    username = st.text_input("ชื่อผู้ใช้")
    password = st.text_input("รหัสผ่าน", type="password")

    if st.button("เข้าสู่ระบบดิ้"):
        if username == "Admin" and password == "1234":
            st.session_state["logged_in"] = True
            st.success("✅ เข้าสู่ระบบสำเร็จ ใจเย็นๆ กรุณารอสักครู่...")
            st.rerun()
        else:
            st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้องจร้าา")

            
else:
    # ✅ โหลด UI หลักตรงนี้เท่านั้น เมื่อ login แล้ว
    st.sidebar.title("📂 เมนู")

    # Sidebar: Navigation
    menu = st.sidebar.radio("📂 เมนู", [
        "📦 รายการอะไหล่ พร้อมรูปภาพ",
        "🔍 ค้นหา / กรองอะไหล่",
        "➕ เพิ่ม / แก้ไข / ลบ อะไหล่",
        "📤 เบิก / เติมสต๊อก",
        "📝 แก้ไขประวัติสต๊อก",
        "♻️ กู้คืนรายการล่าสุด",
        "📁 อัปโหลดรายการอะไหล่",
        "📊 Dashboard",
        "📁 Export รายงาน"
    ])

    # Page 1: List with Images
    if menu == "📦 รายการอะไหล่ พร้อมรูปภาพ":
        st.subheader("รายการอะไหล่")
        for _, row in df.iterrows():
            col1, col2 = st.columns([1, 4])
            with col1:
                image_url = get_image_url(row["Image Path"])
                st.image(image_url, width=100)
            with col2:
                st.markdown(f"**{row['Part No']} - {row['Name']}**")
                st.caption(f"หมวดหมู่: {row['Category']} | คงเหลือ: {row['Stock']}")

    # Page 2: Filter
    elif menu == "🔍 ค้นหา / กรองอะไหล่":
        st.subheader("ค้นหาอะไหล่")
        search = st.text_input("🔍 ค้นหาด้วย Part No หรือ ชื่อ")
        cat_filter = st.selectbox("เลือกหมวดหมู่", ["All"] + sorted(df["Category"].dropna().unique()))

        filtered = df[df["Part No"].str.contains(search, case=False, na=False) | df["Name"].str.contains(search, case=False, na=False)]
        if cat_filter != "All":
            filtered = filtered[filtered["Category"] == cat_filter]

        st.dataframe(filtered)

    # Page 3: Add/Edit/Delete
    elif menu == "➕ เพิ่ม / แก้ไข / ลบ อะไหล่":
        st.subheader("เพิ่ม / แก้ไข / ลบ")
        action = st.radio("เลือกการกระทำ", ["เพิ่ม", "แก้ไข", "ลบ"])
        selected_name = st.selectbox("เลือกรายการ (สำหรับแก้/ลบ)", ["-"] + list(df["Name"]))

        if selected_name != "-" and action == "แก้ไข":
            selected_rows = df[df["Name"] == selected_name]
            if not selected_rows.empty:
                selected_row = selected_rows.iloc[0]
                part_no = st.text_input("Part No", selected_row["Part No"])
                name = st.text_input("ชื่ออะไหล่", selected_row["Name"])
                category = st.text_input("หมวดหมู่", selected_row["Category"])
                stock = st.number_input("จำนวนคงเหลือ", value=int(selected_row["Stock"]))
                image_path = st.text_input("ชื่อไฟล์รูปภาพ (เช่น 1.png) โดยเก็บไว้ในโฟลเดอร์ images/", value=selected_row["Image Path"])
            else:
                st.warning("ไม่พบรายการที่เลือก")
                part_no = name = category = image_path = ""
                stock = 0
        else:
            part_no = st.text_input("Part No")
            name = st.text_input("ชื่ออะไหล่")
            category = st.text_input("หมวดหมู่")
            stock = st.number_input("จำนวนคงเหลือ", 0)
            image_path = st.text_input("ชื่อไฟล์รูปภาพ (เช่น 1.png) โดยเก็บไว้ในโฟลเดอร์ images/")

        if action == "เพิ่ม" and st.button("บันทึกเพิ่มใหม่"):
            if part_no in df["Part No"].values:
                st.warning("Part No นี้มีอยู่แล้ว กรุณาใช้รหัสใหม่")
            else:
                df.loc[len(df)] = [part_no, name, category, stock, image_path, ""]
                save_data()
                st.success("เพิ่มเรียบร้อยแล้ว")

        elif action == "แก้ไข" and selected_name != "-" and st.button("บันทึกการแก้ไข"):
            idx = df[df["Name"] == selected_name].index
            if not idx.empty:
                df.loc[idx[0], ["Part No", "Name", "Category", "Stock", "Image Path"]] = [part_no, name, category, stock, image_path]

                save_data()
                st.success("แก้ไขสำเร็จ")

        elif action == "ลบ" and selected_name != "-" and st.button("ลบรายการ"):
            df.drop(df[df["Name"] == selected_name].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
            save_data()
            st.success("ลบสำเร็จ")

    # Page 4: Issue/Add Stock
    elif menu == "📤 เบิก / เติมสต๊อก":
        st.subheader("เบิก / เติมสต๊อก")
        selected_name = st.selectbox("เลือกชื่ออะไหล่", df["Name"])
        idx = df[df["Name"] == selected_name].index[0]

        st.markdown(f"**Part No:** {df.loc[idx, 'Part No']}")
        st.markdown(f"**คงเหลือ:** {df.loc[idx, 'Stock']}")
        st.image(get_image_url(df.loc[idx, "Image Path"]), width=150)

        qty = st.number_input("จำนวน", 0)
        user = st.text_input("ชื่อผู้ดำเนินการ")
        action = st.radio("เลือกประเภท", ["เบิก", "เติม"])

        if st.button("บันทึกการดำเนินการ"):
            current_stock = df.loc[idx, "Stock"]

            if action == "เบิก" and qty > current_stock:
                st.error("❌ ไม่สามารถเบิกได้ เนื่องจากจำนวนที่เบิกมากกว่าคงเหลือ")
            else:
                new_stock = current_stock - qty if action == "เบิก" else current_stock + qty
                df.loc[idx, "Stock"] = new_stock
                history_entry = f"{datetime.now()} | {action} {qty} by {user}\n"
                existing_history = str(df.loc[idx, "History"]) if pd.notnull(df.loc[idx, "History"]) else ""
                df.loc[idx, "History"] = existing_history + history_entry
                save_data()
                st.success("ดำเนินการเรียบร้อย")

    # Page 5: Edit Stock History
    elif menu == "📝 แก้ไขประวัติสต๊อก":
        st.subheader("แก้ไขประวัติสต๊อก")
        selected_name = st.selectbox("เลือกชื่ออะไหล่ที่ต้องการแก้ไขประวัติ", df["Name"])
        idx = df[df["Name"] == selected_name].index[0]

        st.markdown(f"**Part No:** {df.loc[idx, 'Part No']}")
        st.markdown(f"**Stock ปัจจุบัน:** {df.loc[idx, 'Stock']}")
        history_text = st.text_area("ประวัติเดิม", value=df.loc[idx, "History"], height=200)
        new_stock = st.number_input("แก้ไขจำนวนสต๊อก (ถ้าต้องการ)", value=int(df.loc[idx, "Stock"]))

        if st.button("บันทึกการแก้ไข"):
            df.loc[idx, "History"] = history_text
            df.loc[idx, "Stock"] = new_stock
            save_data()
            st.success("แก้ไขเรียบร้อยแล้ว")

    # Page 6: Restore Backup
    elif menu == "♻️ กู้คืนรายการล่าสุด":
        st.subheader("♻️ กู้คืนข้อมูลรายการอะไหล่ล่าสุด")
        if st.button("🔄 ดึงข้อมูลจากไฟล์ backup_spare_parts.csv"):
            df = restore_backup()
            save_data()
            st.success("กู้คืนข้อมูลล่าสุดเรียบร้อยแล้ว")

    # Page 7: Upload CSV
    elif menu == "📁 อัปโหลดรายการอะไหล่":
        st.subheader("อัปโหลดไฟล์ CSV รายการอะไหล่")
        uploaded_file = st.file_uploader("เลือกรายการไฟล์ .csv ที่ต้องการนำเข้า", type=["csv"])
        if uploaded_file is not None:
            try:
                new_df = pd.read_csv(uploaded_file, encoding="utf-8")
                if new_df.empty:
                    raise ValueError("CSV file is empty")
            except (UnicodeDecodeError, ValueError):
                try:
                    new_df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
                    if new_df.empty:
                        raise ValueError("CSV file is empty")
                except Exception as e:
                    st.error(f"ไม่สามารถอ่านไฟล์ได้: {e}")
                    new_df = None

            if new_df is not None:
                required_cols = ["Part No", "Name", "Category", "Stock", "Image Path", "History"]
                if all(col in new_df.columns for col in required_cols):
                    df = pd.concat([df, new_df], ignore_index=True)
                    save_data()
                    st.success("เพิ่มข้อมูลจากไฟล์เรียบร้อยแล้ว")
                else:
                    st.error(f"คอลัมน์ในไฟล์ไม่ตรงกับที่ระบบต้องการ: {required_cols}")

    # Page 8: Dashboard
    elif menu == "📊 Dashboard":
        st.subheader("Dashboard")
        st.metric("รายการทั้งหมด", len(df))
        st.metric("หมวดหมู่", len(df["Category"].unique()))
        st.metric("สต๊อกรวม", df["Stock"].sum())
        st.bar_chart(df.groupby("Category")["Stock"].sum())

    # Page 9: Export
    elif menu == "📁 Export รายงาน":
        st.subheader("Export รายงาน")
        file_name = f"spare_part_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(file_name, index=False)
        with open(file_name, "rb") as f:
            st.download_button("📥 ดาวน์โหลดไฟล์ Excel", f, file_name, mime="application/vnd.ms-excel")

# Logout Button
if "logged_in" in st.session_state and st.session_state["logged_in"]:
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 ออกจากระบบ", type="primary"):
        st.session_state["logged_in"] = False
        st.rerun()

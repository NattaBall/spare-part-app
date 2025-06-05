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

    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Part No", "Name", "Category", "Stock", "Image Path", "History"])
        df.to_csv(DB_FILE, index=False)
    else:
        df = pd.read_csv(DB_FILE)

    def save_data():
        df.to_csv(BACKUP_FILE, index=False)  # backup before save
        df.to_csv(DB_FILE, index=False)

    def restore_backup():
        if os.path.exists(BACKUP_FILE):
            return pd.read_csv(BACKUP_FILE)
        return df

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
        for i, row in df.iterrows():
            col1, col2 = st.columns([1, 4])
            with col1:
                image_path = os.path.join("images", str(row["Image Path"])) if row["Image Path"] else None
                if image_path and os.path.exists(image_path):
                    st.image(image_path, width=100)
                else:
                    st.warning("No image")
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
        selected_part = st.selectbox("เลือกรายการ (สำหรับแก้/ลบ)", ["-"] + list(df["Part No"]))

        part_no = st.text_input("Part No")
        name = st.text_input("ชื่ออะไหล่")
        category = st.text_input("หมวดหมู่")
        stock = st.number_input("จำนวนคงเหลือ", 0)
        image_path = st.text_input("ชื่อไฟล์รูปภาพ (เช่น 1.png) โดยเก็บไว้ในโฟลเดอร์ images/")

        if action == "เพิ่ม" and st.button("บันทึกเพิ่มใหม่"):
            df.loc[len(df)] = [part_no, name, category, stock, image_path, ""]
            save_data()
            st.success("เพิ่มเรียบร้อยแล้ว")

        elif action == "แก้ไข" and selected_part != "-" and st.button("บันทึกการแก้ไข"):
            idx = df[df["Part No"] == selected_part].index[0]
            df.loc[idx] = [part_no, name, category, stock, image_path, df.loc[idx, "History"]]
            save_data()
            st.success("แก้ไขสำเร็จ")

        elif action == "ลบ" and selected_part != "-" and st.button("ลบรายการ"):
            df.drop(df[df["Part No"] == selected_part].index, inplace=True)
            save_data()
            st.success("ลบสำเร็จ")

    # Page 4: Issue/Add Stock
    elif menu == "📤 เบิก / เติมสต๊อก":
        st.subheader("เบิก / เติมสต๊อก")
        selected_name = st.selectbox("เลือกชื่ออะไหล่", df["Name"])
        idx = df[df["Name"] == selected_name].index[0]

        st.markdown(f"**Part No:** {df.loc[idx, 'Part No']}")
        st.markdown(f"**คงเหลือ:** {df.loc[idx, 'Stock']}")
        img_path = os.path.join("images", str(df.loc[idx, "Image Path"]))
        if os.path.exists(img_path):
            st.image(img_path, width=150)
        else:
            st.warning("ไม่พบรูปภาพ")

        qty = st.number_input("จำนวน", 0)
        user = st.text_input("ชื่อผู้ดำเนินการ")
        action = st.radio("เลือกประเภท", ["เบิก", "เติม"])

        if st.button("บันทึกการดำเนินการ"):
            current_stock = df.loc[idx, "Stock"]
            new_stock = current_stock - qty if action == "เบิก" else current_stock + qty
            df.loc[idx, "Stock"] = new_stock
            history_entry = f"{datetime.now()} | {action} {qty} by {user}\n"
            existing_history = str(df.loc[idx, "History"]) if pd.notnull(df.loc[idx, "History"]) else ""
            df.loc[idx, "History"] = existing_history + history_entry
            save_data()
            st.success("ดำเนินการเรียบร้อย")

    # Page 4.5: Edit Stock History
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

    # Page 4.75: Restore
    elif menu == "♻️ กู้คืนรายการล่าสุด":
        st.subheader("♻️ กู้คืนข้อมูลรายการอะไหล่ล่าสุด")
        if st.button("🔄 ดึงข้อมูลจากไฟล์ backup_spare_parts.csv"):
            df = restore_backup()
            save_data()
            st.success("กู้คืนข้อมูลล่าสุดเรียบร้อยแล้ว")

    # Page 5: Upload CSV
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

    # Page 6: Dashboard
    elif menu == "📊 Dashboard":
        st.subheader("Dashboard")
        st.metric("รายการทั้งหมด", len(df))
        st.metric("หมวดหมู่", len(df["Category"].unique()))
        st.metric("สต๊อกรวม", df["Stock"].sum())
        st.bar_chart(df.groupby("Category")["Stock"].sum())

    # Page 7: Export
    elif menu == "📁 Export รายงาน":
        st.subheader("Export รายงาน")
        file_name = f"spare_part_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(file_name, index=False)
        with open(file_name, "rb") as f:
            st.download_button("📥 ดาวน์โหลดไฟล์ Excel", f, file_name, mime="application/vnd.ms-excel")
else:
    sys.stderr.write("Streamlit is not available in this environment. Please run this code in your local machine with Streamlit installed.\n")

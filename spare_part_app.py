# To run this app, ensure 'streamlit' is installed via: pip install streamlit
import pandas as pd
import os
from datetime import datetime

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None
    import sys
    print("Streamlit is not installed. Please run 'pip install streamlit' to use the app.", file=sys.stderr)

if st:
    # Initial Setup
    st.set_page_config(page_title="Spare Part Manager", layout="wide")
    st.title("📦 Spare Part Management System")

    # File Storage
    DB_FILE = "spare_parts.csv"
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["Part No", "Name", "Category", "Stock", "Image Path", "History"])
        df.to_csv(DB_FILE, index=False)

    df = pd.read_csv(DB_FILE)

    def save_data():
        df.to_csv(DB_FILE, index=False)

    # Sidebar: Navigation
    menu = st.sidebar.radio("📂 เมนู", [
        "📦 รายการอะไหล่ พร้อมรูปภาพ",
        "🔍 ค้นหา / กรองอะไหล่",
        "➕ เพิ่ม / แก้ไข / ลบ อะไหล่",
        "📤 เบิก / เติมสต๊อก",
        "📊 Dashboard",
        "📁 Export รายงาน"
    ])

    # Page 1: List with Images
    if menu == "📦 รายการอะไหล่ พร้อมรูปภาพ":
        st.subheader("รายการอะไหล่")
        for i, row in df.iterrows():
            col1, col2 = st.columns([1, 4])
            with col1:
                if os.path.exists(str(row["Image Path"])):
                    st.image(row["Image Path"], width=100)
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
        image_path = st.text_input("Path รูป (เช่น C:/imgs/1.png)")

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
        selected_part = st.selectbox("เลือก Part No", df["Part No"])
        qty = st.number_input("จำนวน", 0)
        user = st.text_input("ชื่อผู้ดำเนินการ")
        action = st.radio("เลือกประเภท", ["เบิก", "เติม"])

        if st.button("บันทึกการดำเนินการ"):
            idx = df[df["Part No"] == selected_part].index[0]
            current_stock = df.loc[idx, "Stock"]
            new_stock = current_stock - qty if action == "เบิก" else current_stock + qty
            df.loc[idx, "Stock"] = new_stock
            df.loc[idx, "History"] += f"{datetime.now()} | {action} {qty} by {user}\n"
            save_data()
            st.success("ดำเนินการเรียบร้อย")

    # Page 5: Dashboard
    elif menu == "📊 Dashboard":
        st.subheader("Dashboard")
        st.metric("รายการทั้งหมด", len(df))
        st.metric("หมวดหมู่", len(df["Category"].unique()))
        st.metric("สต๊อกรวม", df["Stock"].sum())
        st.bar_chart(df.groupby("Category")["Stock"].sum())

    # Page 6: Export
    elif menu == "📁 Export รายงาน":
        st.subheader("Export รายงาน")
        file_name = f"spare_part_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(file_name, index=False)
        with open(file_name, "rb") as f:
            st.download_button("📥 ดาวน์โหลดไฟล์ Excel", f, file_name, mime="application/vnd.ms-excel")
else:
    print("Streamlit is not available in this environment. Please run this code in your local machine with Streamlit installed.")

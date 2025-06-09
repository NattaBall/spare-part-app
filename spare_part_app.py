# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# Set page config
st.set_page_config(page_title="Spare Part Manager", layout="wide")

# Inject CSS transition effect (iOS-like with slide-in and fade-in effects)
st.markdown("""
    <style>
    html, body, [class^="css"]  {
        scroll-behavior: smooth;
        transition: all 0.8s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    .element-container {
        animation: fadeSlideIn 1s ease forwards;
        border-radius: 10px;
        box-shadow: 0 8px 20px rgba(0,0,0,0);
        opacity: 0;
    }
    .stButton button, .stSelectbox div, .stRadio div, .stTextInput input, .stNumberInput input {
        transition: all 0.6s ease-in-out !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        animation: fadeSlideIn 1.2s ease forwards;
        opacity: 0;
    }
    .stButton button:hover {
        transform: scale(1.05);
        background-color: #00b894 !important;
        color: white !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border: 2px solid #0984e3 !important;
        box-shadow: 0 0 8px rgba(9,132,227,0.3);
    }
    .stTextInput input, .stNumberInput input {
        background-color: #2c2c2c !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: none !important;
    }
    .stApp {
        transition: all 0.8s ease-in-out !important;
    }
    /* Remove box shadow on login screen */
    body:has(.stTextInput input[name='รหัสผ่าน']) .element-container {
        box-shadow: none !important;
    }
    body:has(.stTextInput input[name='รหัสผ่าน']) input {
        background-color: #2c2c2c !important;
        color: white !important;
        box-shadow: none !important;
        border: 1px solid #666 !important;
    }

    @keyframes fadeSlideIn {
        0% {
            opacity: 0;
            transform: translateY(40px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const inputEls = document.querySelectorAll("input");
        inputEls.forEach((input, idx) => {
            input.addEventListener("keypress", function(e) {
                if (e.key === "Enter") {
                    const buttons = document.querySelectorAll("button");
                    if (buttons.length > 0) buttons[0].click();
                }
            });
        });
    });
    </script>
""", unsafe_allow_html=True)

st.title("\U0001F4E6 Spare Part Management System")

# File paths
DB_FILE = "spare_parts_extended.csv"
BACKUP_FILE = "backup_spare_parts_extended.csv"
IMAGE_BASE_URL = "https://raw.githubusercontent.com/NattaBall/spare-part-app/main/images"

# Expected columns
columns = [
    "No.", "Name", "Part no.", "QCB Part no.", "Part description", "Parent equipment Part Number",
    "Manufacturer/Supplier", "Current incentary", "Safety Stock", "Key-core part (Y/N)",
    "Storage place", "Image Path", "History"
]

# Load data
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=columns)
    df.to_csv(DB_FILE, index=False)
else:
    df = pd.read_csv(DB_FILE)

# Helper functions
def save_data():
    df.to_csv(DB_FILE, index=False)
    df.to_csv(BACKUP_FILE, index=False)

def restore_data():
    if os.path.exists(BACKUP_FILE):
        return pd.read_csv(BACKUP_FILE)
    return df

def get_image_url(image_path):
    if pd.isna(image_path) or str(image_path).strip() == "":
        return f"{IMAGE_BASE_URL}/no_image.png"
    return f"{IMAGE_BASE_URL}/{image_path}"

def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

# Login section
# (The rest of the app remains unchanged)
    
# Login section
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("""
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
            opacity: 0.4;
            filter: blur(5px) brightness(0.7);
            z-index: 0;
        }
        .block-container {
            position: relative;
            z-index: 1;
        }
        </style>
    """, unsafe_allow_html=True)
    st.subheader("\U0001F512 กรุณาเข้าสู่ระบบ")
    username = st.text_input("ชื่อผู้ใช้")
    password = st.text_input("รหัสผ่าน", type="password")
    if st.button("เข้าสู่ระบบดิ้"):
        if username == "admin" and password == "Quasar@2025":
            st.session_state["logged_in"] = True
            st.success("✅ เข้าสู่ระบบสำเร็จ รอสักครู่...")
            st.rerun()
        else:
            st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
else:
    menu = st.sidebar.radio("\U0001F4C1 เมนู", [
        "\U0001F4E6 รายการอะไหล่", "\U0001F50D ค้นหา", "➕ เพิ่ม/แก้ไข/ลบ", "\U0001F4E4 เบิก/เติม",
        "\U0001F4DD แก้ไขประวัติ", "♻️ กู้คืนข้อมูล", "\U0001F4C1 อัปโหลด CSV", "\U0001F4CA Dashboard", "\U0001F4E5 ดาวน์โหลด"
    ])

    if menu == "\U0001F4E6 รายการอะไหล่":
        st.subheader("\U0001F4E6 รายการอะไหล่ทั้งหมด")
        parent_list = sorted(df["Parent equipment Part Number"].dropna().unique())
        selected_parent = st.selectbox("เลือกกลุ่มเครื่องจักร (Parent Equipment)", ["ทั้งหมด"] + parent_list)
        keyword = st.text_input("\U0001F50D ค้นหาด้วยชื่อหรือ Part no.")
        filtered_df = df.copy()
        if selected_parent != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["Parent equipment Part Number"] == selected_parent]
        if keyword:
            filtered_df = filtered_df[
                filtered_df["Part no."].str.contains(keyword, case=False, na=False) |
                filtered_df["Name"].str.contains(keyword, case=False, na=False)
            ]
        if filtered_df.empty:
            st.warning("ไม่พบอะไหล่ที่ตรงกับเงื่อนไข")
        else:
            for _, row in filtered_df.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.image(get_image_url(row["Image Path"]), width=100)
                    with col2:
                        st.markdown(f"**{row['Part no.']} - {row['Name']}**")
                        st.caption(f"{row['Part description']} | คงเหลือ: {safe_float(row['Current incentary'])}")
                        st.caption(f"ตำแหน่งเก็บ: {row['Storage place']}")

    elif menu == "\U0001F50D ค้นหา":
        st.subheader("\U0001F50D ค้นหาอะไหล่")
        keyword = st.text_input("ค้นหาจาก Part no. หรือ Name")
        results = df[df["Part no."].str.contains(keyword, case=False, na=False) |
                     df["Name"].str.contains(keyword, case=False, na=False)].copy()
        def highlight_low(row):
            try:
                return ['background-color: #ffcccc; color: red; font-weight: bold;' if row["Current incentary"] < row["Safety Stock"] else '' for _ in row]
            except:
                return ['' for _ in row]
        st.dataframe(results.style.apply(highlight_low, axis=1))

    elif menu == "➕ เพิ่ม/แก้ไข/ลบ":
        st.subheader("➕ เพิ่ม / แก้ไข / ลบ อะไหล่")
        action = st.radio("เลือกการกระทำ", ["เพิ่ม", "แก้ไข", "ลบ"])
        selected = st.selectbox("เลือกรายการ", ["-"] + list(df["Name"]))
        row_data = dict.fromkeys(columns, "")
        if selected != "-" and action in ["แก้ไข", "ลบ"]:
            row_data = df[df["Name"] == selected].iloc[0].to_dict()
        inputs = {}
        for col in columns:
            if "Current incentary" in col or "Safety Stock" in col:
                inputs[col] = st.number_input(col, value=safe_float(row_data.get(col)))
            else:
                inputs[col] = st.text_input(col, value=row_data.get(col, ""))
        if action == "เพิ่ม" and st.button("บันทึกเพิ่ม"):
            df.loc[len(df)] = inputs
            save_data()
            st.success("✅ เพิ่มรายการสำเร็จแล้ว")
        elif action == "แก้ไข" and selected != "-" and st.button("บันทึกแก้ไข"):
            idx = df[df["Name"] == selected].index
            for col in columns:
                df.loc[idx, col] = inputs[col]
            save_data()
            st.success("✅ แก้ไขเรียบร้อย")
        elif action == "ลบ" and selected != "-" and st.button("ลบรายการ"):
            df.drop(df[df["Name"] == selected].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
            save_data()
            st.success("🗑️ ลบเรียบร้อยแล้ว")

    elif menu == "\U0001F4E4 เบิก/เติม":
        st.subheader("\U0001F4E4 เบิก / เติมสต๊อก")
        selected = st.selectbox("เลือกอะไหล่", df["Name"])
        idx = df[df["Name"] == selected].index[0]
        st.image(get_image_url(df.loc[idx, "Image Path"]), width=150)
        st.info(f"คงเหลือปัจจุบัน: **{safe_float(df.loc[idx, 'Current incentary'])}**")
        qty = st.number_input("จำนวน", 0)
        user = st.text_input("ชื่อผู้ดำเนินการ")
        action = st.radio("เลือกการดำเนินการ", ["เบิก", "เติม"])
        if st.button("ดำเนินการ"):
            current = safe_float(df.loc[idx, "Current incentary"])
            if action == "เบิก" and qty > current:
                st.error("❌ คงเหลือไม่พอเบิก")
            else:
                new_val = current - qty if action == "เบิก" else current + qty
                df.loc[idx, "Current incentary"] = new_val
                hist = str(df.loc[idx, "History"]) or ""
                df.loc[idx, "History"] = hist + f"{datetime.now()} | {action} {qty} by {user}\n"
                save_data()
                st.success("✅ สำเร็จแล้ว")

    elif menu == "\U0001F4DD แก้ไขประวัติ":
        st.subheader("\U0001F4DD แก้ไขประวัติ")
        selected = st.selectbox("เลือกอะไหล่", df["Name"])
        idx = df[df["Name"] == selected].index[0]
        new_hist = st.text_area("ประวัติใหม่", value=df.loc[idx, "History"], height=200)
        new_stock = st.number_input("แก้ไขจำนวน", value=safe_float(df.loc[idx, "Current incentary"]))
        if st.button("บันทึก"):
            df.loc[idx, "History"] = new_hist
            df.loc[idx, "Current incentary"] = new_stock
            save_data()
            st.success("✅ บันทึกแล้ว")

    elif menu == "♻️ กู้คืนข้อมูล":
        if st.button("\U0001F501 กู้คืนจาก Backup"):
            df = restore_data()
            save_data()
            st.success("✅ กู้คืนเรียบร้อยแล้ว")

    elif menu == "\U0001F4C1 อัปโหลด CSV":
        uploaded = st.file_uploader("อัปโหลดไฟล์ CSV", type=["csv"])
        if uploaded:
            new_df = pd.read_csv(uploaded)
            if all(col in new_df.columns for col in columns):
                df = pd.concat([df, new_df], ignore_index=True)
                save_data()
                st.success("✅ เพิ่มข้อมูลเรียบร้อย")
            else:
                st.error("❌ คอลัมน์ในไฟล์ไม่ตรง")

    elif menu == "\U0001F4CA Dashboard":
        st.subheader("\U0001F4CA Dashboard")
        st.metric("จำนวนอะไหล่ทั้งหมด", len(df))
        st.metric("ผู้ผลิตทั้งหมด", df["Manufacturer/Supplier"].nunique())
        st.metric("รวมจำนวนคงเหลือ", df["Current incentary"].sum())
        grouped = df.groupby("Parent equipment Part Number")["Current incentary"].sum().reset_index()
        st.bar_chart(grouped.rename(columns={"Current incentary": "ยอดคงเหลือ"}).set_index("Parent equipment Part Number"))

    elif menu == "\U0001F4E5 ดาวน์โหลด":
        file_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(file_name, index=False)
        with open(file_name, "rb") as f:
            st.download_button("\U0001F4E5 ดาวน์โหลด Excel", f, file_name, mime="application/vnd.ms-excel")

    if st.sidebar.button("\U0001F6AA ออกจากระบบ"):
        st.session_state["logged_in"] = False
        st.rerun()

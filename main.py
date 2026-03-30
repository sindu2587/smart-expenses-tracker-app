import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# ================= CONFIG =================
st.set_page_config(page_title="Smart Expense Tracker", layout="wide")

# ✅ USERNAME
username = st.text_input("Enter your name")

if username == "":
    st.warning("Please enter your name")
    st.stop()

# ✅ FILE PER USER
FILE = f"{username}.csv"

# ================= LOAD DATA =================
def load_data():
    try:
        if os.path.exists(FILE):
            df = pd.read_csv(FILE)
            if list(df.columns) != ["date","category","amount","type","note"]:
                return pd.DataFrame(columns=["date","category","amount","type","note"])
            return df
        return pd.DataFrame(columns=["date","category","amount","type","note"])
    except:
        return pd.DataFrame(columns=["date","category","amount","type","note"])

# ================= SAVE DATA =================
def save_data(df):
    df.to_csv(FILE, index=False)

df = load_data()

# ================= UI =================
st.title("💳 Smart Expense Tracker")

# ================= SIDEBAR =================
st.sidebar.header("➕ Add Transaction")

category = st.sidebar.selectbox("Category", ["Food","Travel","Shopping","Bills","Other"])
amount = st.sidebar.number_input("Amount", min_value=0.0)

# ✅ NOTE INPUT
note = st.sidebar.text_input("Note")

type_ = st.sidebar.selectbox("Type", ["expense","income"])

if st.sidebar.button("Add"):
    new = pd.DataFrame([[datetime.now(), category, amount, type_, note]],
                       columns=["date","category","amount","type","note"])
    df = pd.concat([df, new], ignore_index=True)
    save_data(df)
    st.success("Added successfully")
    st.rerun()   # ✅ AUTO REFRESH

# ================= SEARCH =================
st.subheader("🔍 Search & Filter")

search = st.text_input("Search by category")

categories = df["category"].dropna().unique().tolist() if not df.empty else []
filter_cat = st.selectbox("Filter by Category", ["All"] + categories)

if search:
    df = df[df["category"].str.contains(search, case=False, na=False)]

if filter_cat != "All":
    df = df[df["category"] == filter_cat]

# ================= DASHBOARD =================
st.subheader("📈 Dashboard")

income = df[df["type"] == "income"]["amount"].sum()
expense = df[df["type"] == "expense"]["amount"].sum()
savings = income - expense

col1, col2, col3 = st.columns(3)
col1.metric("Income", f"₹{income}")
col2.metric("Expense", f"₹{expense}")
col3.metric("Savings", f"₹{savings}")

# ================= PIE CHART =================
st.subheader("📊 Expense Distribution")

exp_df = df[df["type"] == "expense"]

if not exp_df.empty:
    pie = exp_df.groupby("category")["amount"].sum()
    fig, ax = plt.subplots()
    ax.pie(pie, labels=pie.index, autopct='%1.1f%%')
    st.pyplot(fig)
else:
    st.warning("No expense data")

# ================= AI PREDICTION =================
st.subheader("🤖 AI Prediction")

if not exp_df.empty:
    avg = exp_df["amount"].mean()
    st.info(f"Estimated next expense: ₹{round(avg,2)}")
else:
    st.info("No data for prediction")

# ================= TABLE =================
st.subheader("📋 Data Table")
st.dataframe(df)

# ================= DELETE =================
st.subheader("❌ Delete Transaction")

if not df.empty:
    df_with_index = df.reset_index()

    selected_rows = st.multiselect(
        "Select row(s) to delete",
        df_with_index["index"]
    )

    if st.button("Delete Selected"):
        df = df.drop(selected_rows).reset_index(drop=True)
        save_data(df)
        st.success("Selected row(s) deleted successfully")
        st.rerun()   # ✅ AUTO REFRESH

# ================= EXPORT =================
st.download_button("⬇ Download CSV",
                   df.to_csv(index=False),
                   "expenses.csv")

import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ================= CONFIG =================
st.set_page_config(page_title="Smart Expense Tracker", layout="wide")

FILE = "data.csv"

# ================= LOGIN =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid login")

if not st.session_state.logged_in:
    login()
    st.stop()

# ================= LOAD DATA =================
def load_data():
    try:
        if os.path.exists(FILE):
            df = pd.read_csv(FILE)
            if list(df.columns) != ["date","category","amount","type"]:
                return pd.DataFrame(columns=["date","category","amount","type"])
            return df
        return pd.DataFrame(columns=["date","category","amount","type"])
    except:
        return pd.DataFrame(columns=["date","category","amount","type"])

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
type_ = st.sidebar.selectbox("Type", ["expense","income"])

if st.sidebar.button("Add"):
    new = pd.DataFrame([[datetime.now(), category, amount, type_]],
                       columns=["date","category","amount","type"])
    df = pd.concat([df, new], ignore_index=True)
    save_data(df)
    st.success("Added successfully")

# ================= SEARCH & FILTER =================
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

# ================= BAR CHART =================
st.subheader("📊 Expense Analysis")

exp_df = df[df["type"] == "expense"]

if not exp_df.empty:
    chart = exp_df.groupby("category")["amount"].sum()
    st.bar_chart(chart)
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

# ================= EXPORT =================
st.download_button("⬇ Download CSV",
                   df.to_csv(index=False),
                   "expenses.csv")
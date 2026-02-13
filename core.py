import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="SaaS Executive Dashboard", layout="wide")

# ===============================
# WHITE PAGE CSS
# ===============================
st.markdown("""
<style>

/* Entire app background */
.stApp {
    background-color: white;
}

/* Cards */
.card {
    background:white;
    padding:20px;
    border-radius:14px;
    box-shadow:0 6px 18px rgba(0,0,0,0.08);
    margin-bottom:20px;
}

.card-title {
    font-size:15px;
    font-weight:600;
    margin-bottom:8px;
}

.metric-value {
    font-size:26px;
    font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# DB CONNECTION
# ===============================
def get_connection():
    return mysql.connector.connect(
        host="interchange.proxy.rlwy.net",
        user="root",
        password="LOlfCNnACCeqbgODDpXkhQpRXbAVCZBP",
        database="railway",
        port=56864
    )

conn = get_connection()

def scalar(q):
    return pd.read_sql(q, conn).iloc[0][0]

# ===============================
# HEADER
# ===============================
st.title("📊 SaaS Executive Dashboard")

view_mode = st.selectbox("View Mode", ["Monthly","Daily"])

def group(view, col):
    if view == "Monthly":
        return f"DATE_FORMAT({col}, '%Y-%m')"
    return f"DATE({col})"

# ===============================
# KPI DATA
# ===============================
total_users = scalar("SELECT COUNT(*) FROM users")
active_users = scalar("SELECT COUNT(*) FROM users WHERE status='active'")
revenue_total = scalar("SELECT IFNULL(SUM(amount),0) FROM payments")
active_subs = scalar("SELECT COUNT(*) FROM subscriptions WHERE status='active'")
api_calls = scalar("SELECT IFNULL(SUM(calls_made),0) FROM api_usage")
avg_rating = scalar("SELECT IFNULL(AVG(rating),0) FROM feedback")

# ===============================
# KPI ROW
# ===============================
cols = st.columns(6)
metrics = [
    ("Users", total_users),
    ("Active Users", active_users),
    ("Revenue ₹", f"{revenue_total:,.0f}"),
    ("Subscriptions", active_subs),
    ("API Calls", api_calls),
    ("Avg Rating", round(avg_rating,2))
]

for col,(title,val) in zip(cols, metrics):
    with col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{val}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# REVENUE
# ===============================
grp_pay = group(view_mode, "payment_date")

df_rev = pd.read_sql(f"""
SELECT {grp_pay} period, SUM(amount) total
FROM payments GROUP BY period ORDER BY period
""", conn)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">Revenue Trend</div>', unsafe_allow_html=True)

fig = px.line(df_rev, x="period", y="total")
st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# USER GROWTH
# ===============================
grp_users = group(view_mode, "signup_date")

df_users = pd.read_sql(f"""
SELECT {grp_users} period, COUNT(*) total
FROM users GROUP BY period ORDER BY period
""", conn)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">User Growth</div>', unsafe_allow_html=True)

fig2 = px.line(df_users, x="period", y="total")
st.plotly_chart(fig2, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

conn.close()

import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Executive Dashboard", layout="wide")

# ===============================
# CSS STYLE
# ===============================
st.markdown("""
<style>
body { background:#eef2f7; }

.card {
    background:white;
    padding:20px;
    border-radius:16px;
    box-shadow:0 6px 18px rgba(0,0,0,0.08);
    margin-bottom:20px;
}

.card-title {
    font-size:16px;
    font-weight:600;
    margin-bottom:10px;
}

.metric-value {
    font-size:28px;
    font-weight:700;
}

.small-note {
    color:green;
    font-size:14px;
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
# DATA LOAD
# ===============================
total_users = scalar("SELECT COUNT(*) FROM users")

users_growth = pd.read_sql("""
SELECT DATE_FORMAT(signup_date,'%Y-%m') period,
COUNT(*) total
FROM users
GROUP BY period ORDER BY period
""", conn)

weekly_sales = pd.read_sql("""
SELECT DAYNAME(payment_date) day,
SUM(amount) total
FROM payments
GROUP BY day
""", conn)

task_status = pd.read_sql("""
SELECT status, COUNT(*) total
FROM users
GROUP BY status
""", conn)

activities = pd.read_sql("""
SELECT activity_type, activity_time
FROM activity_logs
ORDER BY activity_time DESC
LIMIT 5
""", conn)

# ===============================
# ROW 1
# ===============================
col1, col2 = st.columns(2)

# ---------- Key Metrics ----------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Key Metrics</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="metric-value">{total_users:,}</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="small-note">▲ Growth Active Users</div>',
                unsafe_allow_html=True)

    fig1 = px.line(users_growth, x="period", y="total")
    fig1.update_layout(template="simple_white", height=200)

    st.plotly_chart(fig1, use_container_width=True, key="growth_chart")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Weekly Sales ----------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Weekly Sales</div>', unsafe_allow_html=True)

    fig2 = px.bar(weekly_sales, x="day", y="total")
    fig2.update_layout(template="simple_white", height=260)

    st.plotly_chart(fig2, use_container_width=True, key="weekly_sales")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# ROW 2
# ===============================
col3, col4 = st.columns(2)

# ---------- Task Overview ----------
with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Task Overview</div>', unsafe_allow_html=True)

    fig3 = px.pie(
        task_status,
        names="status",
        values="total",
        hole=0.6
    )

    fig3.update_layout(template="simple_white", height=260)

    st.plotly_chart(fig3, use_container_width=True, key="task_overview")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Recent Activities ----------
with col4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Recent Activities</div>', unsafe_allow_html=True)

    st.dataframe(activities, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

conn.close()

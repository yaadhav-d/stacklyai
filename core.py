import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Executive Dashboard",
    layout="wide"
)

# ===============================
# CSS – CARD STYLE
# ===============================
st.markdown("""
<style>
body { background:#0b1220; }

.dashboard-card {
    background: linear-gradient(160deg,#111827,#020617);
    padding:20px;
    border-radius:18px;
    box-shadow:0 12px 30px rgba(0,0,0,0.7);
    margin-bottom:20px;
}

.dashboard-title {
    font-size:14px;
    color:#9ca3af;
    margin-bottom:6px;
}

.dashboard-value {
    font-size:24px;
    font-weight:700;
    margin-bottom:8px;
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

def scalar(query):
    return pd.read_sql(query, conn).iloc[0][0]

# ===============================
# HEADER
# ===============================
st.title("Executive Sales Intelligence")

# ===============================
# GLOBAL FILTER
# ===============================
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
avg_rating = scalar("SELECT IFNULL(AVG(rating),0) FROM feedback")

# ===============================
# REVENUE DATA
# ===============================
grp = group(view_mode, "payment_date")

df_rev = pd.read_sql(f"""
SELECT {grp} period,
       SUM(amount) total
FROM payments
GROUP BY period
ORDER BY period
""", conn)

# ===============================
# ROW 1
# ===============================
col1, col2 = st.columns([2,1])

# Revenue trend
with col1:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-title">Revenue</div>', unsafe_allow_html=True)

    fig = px.line(df_rev, x="period", y="total")
    fig.update_traces(line=dict(width=4))
    fig.update_layout(template="plotly_dark", height=260)

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Mini bars
with col2:
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-title">Total Sales</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dashboard-value">₹ {revenue_total:,.0f}</div>',
                unsafe_allow_html=True)

    fig2 = px.bar(df_rev.tail(7), x="period", y="total")
    fig2.update_layout(template="plotly_dark", height=260)

    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# ROW 2 – DONUT METRICS
# ===============================
c3, c4, c5 = st.columns(3)

def donut(title, percent):
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="dashboard-title">{title}</div>',
                unsafe_allow_html=True)

    fig = px.pie(
        values=[percent,100-percent],
        names=["Value",""],
        hole=0.75
    )

    fig.update_layout(
        template="plotly_dark",
        height=250,
        showlegend=False
    )

    fig.update_traces(textinfo="none")

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

success_rate = round((active_users/total_users)*100,1) if total_users else 0
return_rate = round((active_subs/total_users)*100,1) if total_users else 0
rating_score = round((avg_rating/5)*100,1)

with c3:
    donut("Successful Users", success_rate)

with c4:
    donut("Returning Users", return_rate)

with c5:
    donut("Rating Score", rating_score)

conn.close()

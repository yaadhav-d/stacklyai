import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="SaaS Executive Dashboard", layout="wide")

# ===============================
# LIGHT SaaS CSS
# ===============================
st.markdown("""
<style>
body { background:#f5f7fb; }

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

hr {margin:10px 0 20px 0;}
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
# REVENUE + WEEKLY SALES
# ===============================
grp_pay = group(view_mode, "payment_date")

df_rev = pd.read_sql(f"""
SELECT {grp_pay} period, SUM(amount) total
FROM payments GROUP BY period ORDER BY period
""", conn)

weekly_sales = pd.read_sql("""
SELECT DAYNAME(payment_date) day, SUM(amount) total
FROM payments GROUP BY day
""", conn)

c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Revenue Trend</div>', unsafe_allow_html=True)
    fig = px.line(df_rev, x="period", y="total")
    fig.update_layout(template="simple_white", height=260)
    st.plotly_chart(fig, use_container_width=True, key="rev")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Weekly Sales</div>', unsafe_allow_html=True)
    fig2 = px.bar(weekly_sales, x="day", y="total")
    fig2.update_layout(template="simple_white", height=260)
    st.plotly_chart(fig2, use_container_width=True, key="weekly")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# USER GROWTH + API USAGE
# ===============================
grp_users = group(view_mode, "signup_date")
grp_api = group(view_mode, "usage_date")

df_users = pd.read_sql(f"""
SELECT {grp_users} period, COUNT(*) total
FROM users GROUP BY period ORDER BY period
""", conn)

df_api = pd.read_sql(f"""
SELECT {grp_api} period, SUM(calls_made) total
FROM api_usage GROUP BY period ORDER BY period
""", conn)

c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">User Growth</div>', unsafe_allow_html=True)
    fig3 = px.line(df_users, x="period", y="total")
    fig3.update_layout(template="simple_white", height=260)
    st.plotly_chart(fig3, use_container_width=True, key="users")
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">API Usage</div>', unsafe_allow_html=True)
    fig4 = px.bar(df_api, x="period", y="total")
    fig4.update_layout(template="simple_white", height=260)
    st.plotly_chart(fig4, use_container_width=True, key="api")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# SUBSCRIPTIONS + RATINGS
# ===============================
grp_sub = group(view_mode, "start_date")

df_sub = pd.read_sql(f"""
SELECT {grp_sub} period, COUNT(*) total
FROM subscriptions GROUP BY period ORDER BY period
""", conn)

df_rating = pd.read_sql("""
SELECT rating, COUNT(*) total
FROM feedback GROUP BY rating ORDER BY rating
""", conn)

c5, c6 = st.columns(2)

with c5:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Subscriptions</div>', unsafe_allow_html=True)
    fig5 = px.bar(df_sub, x="period", y="total")
    fig5.update_layout(template="simple_white", height=260)
    st.plotly_chart(fig5, use_container_width=True, key="subs")
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Ratings Distribution</div>', unsafe_allow_html=True)
    fig6 = px.pie(df_rating, names="rating", values="total", hole=0.6)
    fig6.update_layout(template="simple_white", height=260)
    st.plotly_chart(fig6, use_container_width=True, key="rating")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# TASK OVERVIEW + ACTIVITIES
# ===============================
task_status = pd.read_sql("""
SELECT status, COUNT(*) total
FROM users GROUP BY status
""", conn)

activities = pd.read_sql("""
SELECT activity_type, activity_time
FROM activity_logs
ORDER BY activity_time DESC
LIMIT 5
""", conn)

c7, c8 = st.columns(2)

with c7:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Task Overview</div>', unsafe_allow_html=True)
    fig7 = px.pie(task_status, names="status", values="total", hole=0.6)
    fig7.update_layout(template="simple_white", height=260)
    st.plotly_chart(fig7, use_container_width=True, key="tasks")
    st.markdown('</div>', unsafe_allow_html=True)

with c8:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Recent Activities</div>', unsafe_allow_html=True)
    st.dataframe(activities, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

conn.close()

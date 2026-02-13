import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="Executive Intelligence Dashboard", layout="wide")

# ===============================
# CSS (UNCHANGED VISUAL STYLE)
# ===============================
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background-color: #0E1117;
    color: #FFFFFF;
}
.metric-card {
    padding:22px;
    border-radius:16px;
    box-shadow:0 8px 30px rgba(0,0,0,0.8);
    transition:all 0.3s ease-in-out;
    color:white;
}
.metric-card:hover {
    transform:translateY(-6px);
    box-shadow:0 12px 40px rgba(0,0,0,1);
}
.kpi-mrr{background:#059669;}
.kpi-arpu{background:#2563EB;}
.kpi-churn{background:#DC2626;}
.kpi-active{background:#0D9488;}
.kpi-api{background:#D97706;}
.kpi-health{background:#7C3AED;}

.metric-title{font-size:13px;color:#9CA3AF;}
.metric-value{font-size:30px;font-weight:700;}
.section-title{font-size:22px;font-weight:600;margin-top:30px;}
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

# ===============================
# GLOBAL VIEW FILTER
# ===============================
st.markdown("<h1>🚀 Executive Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

GLOBAL_VIEW = st.selectbox(
    "Global View Mode",
    ["Monthly", "Daily"]
)

def get_group(view, column):
    if view == "Monthly":
        return f"DATE_FORMAT({column}, '%Y-%m')"
    return f"DATE({column})"

# ===============================
# KPI DATA
# ===============================
def scalar(q):
    return pd.read_sql(q, conn).iloc[0][0]

total_users = scalar("SELECT COUNT(*) FROM users")
active_users = scalar("SELECT COUNT(*) FROM users WHERE status='active'")
total_revenue = scalar("SELECT IFNULL(SUM(amount),0) FROM payments")
active_subs = scalar("SELECT COUNT(*) FROM subscriptions WHERE status='active'")
api_calls = scalar("SELECT IFNULL(SUM(calls_made),0) FROM api_usage")
avg_rating = scalar("SELECT ROUND(IFNULL(AVG(rating),0),2) FROM feedback")

def metric_card(title, value, css):
    st.markdown(f"""
    <div class="metric-card {css}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
c5,c6 = st.columns(2)

with c1: metric_card("Total Users", total_users, "kpi-mrr")
with c2: metric_card("Active Users", active_users, "kpi-active")
with c3: metric_card("Revenue (₹)", f"{total_revenue:,.0f}", "kpi-arpu")
with c4: metric_card("Subscriptions", active_subs, "kpi-health")
with c5: metric_card("API Calls", api_calls, "kpi-api")
with c6: metric_card("Avg Rating ⭐", avg_rating, "kpi-churn")

# ===============================
# USER GROWTH
# ===============================
st.markdown("<div class='section-title'>User Growth</div>", unsafe_allow_html=True)

grp1 = get_group(GLOBAL_VIEW, "signup_date")

df1 = pd.read_sql(f"""
SELECT {grp1} period, COUNT(*) total
FROM users GROUP BY period ORDER BY period
""", conn)

df1["ma"] = df1["total"].rolling(3).mean()

fig1 = px.line(df1, x="period", y="total", markers=True)
fig1.add_scatter(x=df1["period"], y=df1["ma"],
                 mode="lines", name="Moving Avg",
                 line=dict(dash="dash"))
fig1.update_layout(template="plotly_dark")

st.plotly_chart(fig1, use_container_width=True)

# ===============================
# ACTIVE USERS
# ===============================
st.markdown("<div class='section-title'>Active Users</div>", unsafe_allow_html=True)

grp2 = get_group(GLOBAL_VIEW, "signup_date")

df2 = pd.read_sql(f"""
SELECT {grp2} period, COUNT(*) total
FROM users WHERE status='active'
GROUP BY period ORDER BY period
""", conn)

fig2 = px.area(df2, x="period", y="total")
fig2.update_layout(template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

# ===============================
# REVENUE
# ===============================
st.markdown("<div class='section-title'>Revenue Trend</div>", unsafe_allow_html=True)

grp3 = get_group(GLOBAL_VIEW, "payment_date")

df3 = pd.read_sql(f"""
SELECT {grp3} period, SUM(amount) total
FROM payments GROUP BY period ORDER BY period
""", conn)

fig3 = px.area(df3, x="period", y="total")
fig3.update_layout(template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

# ===============================
# SUBSCRIPTIONS
# ===============================
st.markdown("<div class='section-title'>Subscriptions</div>", unsafe_allow_html=True)

grp4 = get_group(GLOBAL_VIEW, "start_date")

df4 = pd.read_sql(f"""
SELECT {grp4} period, COUNT(*) total
FROM subscriptions GROUP BY period ORDER BY period
""", conn)

fig4 = px.bar(df4, x="period", y="total")
fig4.update_layout(template="plotly_dark")
st.plotly_chart(fig4, use_container_width=True)

# ===============================
# API USAGE
# ===============================
st.markdown("<div class='section-title'>API Usage</div>", unsafe_allow_html=True)

grp5 = get_group(GLOBAL_VIEW, "usage_date")

df5 = pd.read_sql(f"""
SELECT {grp5} period, SUM(calls_made) total
FROM api_usage GROUP BY period ORDER BY period
""", conn)

fig5 = px.bar(df5, x="period", y="total")
fig5.update_layout(template="plotly_dark")
st.plotly_chart(fig5, use_container_width=True)

# ===============================
# RATINGS
# ===============================
st.markdown("<div class='section-title'>Ratings Distribution</div>", unsafe_allow_html=True)

df6 = pd.read_sql("""
SELECT rating, COUNT(*) total
FROM feedback GROUP BY rating ORDER BY rating
""", conn)

fig6 = px.pie(df6, names="rating", values="total", hole=0.45)
fig6.update_layout(template="plotly_dark")
st.plotly_chart(fig6, use_container_width=True)

# ===============================
# GLOBAL COMBINED
# ===============================
st.markdown("<div class='section-title'>Global Combined</div>", unsafe_allow_html=True)

gx = get_group(GLOBAL_VIEW, "payment_date")
gy = get_group(GLOBAL_VIEW, "signup_date")

pay = pd.read_sql(f"""
SELECT {gx} period, SUM(amount) revenue
FROM payments GROUP BY period ORDER BY period
""", conn)

usr = pd.read_sql(f"""
SELECT {gy} period, COUNT(*) users
FROM users GROUP BY period ORDER BY period
""", conn)

global_df = pd.merge(pay, usr, on="period", how="outer").fillna(0)

figg = go.Figure()
figg.add_trace(go.Scatter(x=global_df["period"],
                           y=global_df["revenue"],
                           name="Revenue"))
figg.add_trace(go.Scatter(x=global_df["period"],
                           y=global_df["users"],
                           name="Users",
                           yaxis="y2"))

figg.update_layout(template="plotly_dark",
                   yaxis2=dict(overlaying="y", side="right"))

st.plotly_chart(figg, use_container_width=True)

conn.close()

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
# CSS (YOUR STYLE PRESERVED)
# ===============================
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background-color: #0E1117;
    color: #FFFFFF;
}

.metric-card {
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.8);
    transition: all 0.3s ease-in-out;
    color: white;
}
.metric-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 40px rgba(0,0,0,1);
}
.kpi-mrr { background: #059669; }
.kpi-arpu { background: #2563EB; }
.kpi-churn { background: #DC2626; }
.kpi-active { background: #0D9488; }
.kpi-api { background: #D97706; }
.kpi-health { background: #7C3AED; }

.metric-title {
    font-size: 13px;
    color: #9CA3AF;
}
.metric-value {
    font-size: 30px;
    font-weight: 700;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 30px;
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

# ===============================
# HEADER
# ===============================
st.markdown("<h1>🚀 Executive Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ===============================
# KPI DATA
# ===============================
total_users = pd.read_sql("SELECT COUNT(*) FROM users", conn).iloc[0][0]
active_users = pd.read_sql("SELECT COUNT(*) FROM users WHERE status='active'", conn).iloc[0][0]
total_revenue = pd.read_sql("SELECT IFNULL(SUM(amount),0) FROM payments", conn).iloc[0][0]
active_subs = pd.read_sql("SELECT COUNT(*) FROM subscriptions WHERE status='active'", conn).iloc[0][0]
api_calls = pd.read_sql("SELECT IFNULL(SUM(calls_made),0) FROM api_usage", conn).iloc[0][0]
avg_rating = pd.read_sql("SELECT ROUND(IFNULL(AVG(rating),0),2) FROM feedback", conn).iloc[0][0]

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
# GROUP FUNCTION
# ===============================
def get_group(view, column):
    if view == "Daily":
        return f"DATE({column})"
    elif view == "Weekly":
        return f"YEARWEEK({column},1)"
    else:
        return f"DATE_FORMAT({column}, '%Y-%m')"

# ===============================
# USER GROWTH
# ===============================
# ------------------------------
# ADVANCED SELECTBOX CSS
# ------------------------------
st.markdown("""
<style>

.section-title {
    font-size:22px;
    font-weight:600;
    margin-bottom:10px;
}

/* Selectbox container */
div[data-testid="stSelectbox"] > div {
    background: linear-gradient(145deg, #1f2937, #111827);
    border-radius: 12px;
    padding: 6px;
    border: 1px solid #374151;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}

/* Label */
div[data-testid="stSelectbox"] label {
    font-weight: 600;
    color: #9ca3af;
}

/* Selected value */
div[data-testid="stSelectbox"] div[role="button"] {
    color: white;
    font-size: 15px;
}

/* Hover glow */
div[data-testid="stSelectbox"] div[role="button"]:hover {
    border-color: #3b82f6;
    box-shadow: 0 0 8px rgba(59,130,246,0.6);
}

/* Dropdown menu */
div[role="listbox"] {
    background-color: #111827;
    border-radius: 10px;
}

/* Dropdown hover */
div[role="option"]:hover {
    background-color: #2563eb !important;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ------------------------------
# SECTION TITLE
# ------------------------------
st.markdown("<div class='section-title'>User Growth</div>", unsafe_allow_html=True)


# ------------------------------
# VIEW SELECTOR
# ------------------------------
view1 = st.selectbox(
    "User View",
    ["Monthly",  "Daily"],
    key="u1"
)

grp1 = get_group(view1, "signup_date")


# ------------------------------
# DATA QUERY
# ------------------------------
df1 = pd.read_sql(f"""
SELECT {grp1} as period, COUNT(*) as total
FROM users
GROUP BY period
ORDER BY period
""", conn)


# ------------------------------
# METRICS CALCULATION
# ------------------------------
df1["growth_pct"] = df1["total"].pct_change() * 100
df1["growth_pct"] = df1["growth_pct"].fillna(0)

df1["ma"] = df1["total"].rolling(3).mean()


# ------------------------------
# ADVANCED CHART
# ------------------------------
# ------------------------------
# BAR + TREND CHART
# ------------------------------
fig1 = go.Figure()

# User bars
fig1.add_trace(go.Bar(
    x=df1["period"],
    y=df1["total"],
    name="Users",
    opacity=0.75
))

# Moving average trend
fig1.add_trace(go.Scatter(
    x=df1["period"],
    y=df1["ma"],
    mode="lines+markers",
    name="Trend",
    line=dict(width=3)
))

fig1.update_layout(
    template="plotly_dark",
    hovermode="x unified",
    xaxis_title="Period",
    yaxis_title="Users",
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis=dict(rangeslider=dict(visible=False))

)

st.plotly_chart(fig1, use_container_width=True)

# ===============================
# ACTIVE USERS
# ===============================
st.markdown("<div class='section-title'>Active User Analytics</div>", unsafe_allow_html=True)

# -----------------------
# VIEW SELECTOR
# -----------------------


# -----------------------
# LOCATION FILTER
# -----------------------


# -----------------------
# USER TYPE FILTER
# -----------------------

# -----------------------
# AGE GROUP LOGIC
# -----------------------
age_case = """
CASE
    WHEN age < 20 THEN 'Under 20'
    WHEN age BETWEEN 20 AND 29 THEN '20-29'
    WHEN age BETWEEN 30 AND 39 THEN '30-39'
    WHEN age BETWEEN 40 AND 49 THEN '40-49'
    ELSE '50+'
END
"""



# -----------------------
# QUERY
# -----------------------
df2 = pd.read_sql(f"""
SELECT
    {age_case} as age_group,
    COUNT(*) as total
FROM users
WHERE status='active'
GROUP BY age_group
ORDER BY age_group
""", conn)


# -----------------------
# ADVANCED AREA CHART
# -----------------------
# -----------------------
# DONUT CHART
# -----------------------

# Aggregate totals by age group
donut_df = df2

fig2 = px.pie(
    donut_df,
    names="age_group",
    values="total",
    title="Active Users by Age Group",
    hole=0.55,
    color_discrete_sequence=px.colors.qualitative.Bold
)

fig2.update_layout(
    template="plotly_dark",
    margin=dict(l=20, r=20, t=50, b=20)
)

fig2.update_traces(
    textinfo="percent+label",
    pull=[0.03] * len(donut_df)
)

st.plotly_chart(fig2, use_container_width=True)

# ===============================
# REVENUE
# ===============================

st.markdown("""
<style>

/* Section title */
.section-title {
    font-size:22px;
    font-weight:600;
    margin-bottom:12px;
}

/* Label styling */
div[data-testid="stSelectbox"] label {
    font-size:14px;
    font-weight:600;
    color:#9aa4b2;
    margin-bottom:6px;
}

/* Selectbox container */
div[data-testid="stSelectbox"] > div {
    background: linear-gradient(145deg, #111827, #1f2937);
    border-radius: 14px;
    padding: 8px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.04),
        0 6px 20px rgba(0,0,0,0.45);
    transition: all 0.25s ease;
}

/* Selected value */
div[data-testid="stSelectbox"] div[role="button"] {
    color: #f9fafb;
    font-size: 15px;
    padding: 6px;
}

/* Hover glow */
div[data-testid="stSelectbox"] > div:hover {
    border: 1px solid #2563eb;
    box-shadow: 0 0 10px rgba(37,99,235,0.45);
}

/* Dropdown */
div[role="listbox"] {
    background: #0f172a;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* Options */
div[role="option"] {
    padding: 10px;
    border-radius: 8px;
}

/* Hover option */
div[role="option"]:hover {
    background: #2563eb !important;
    color: white;
}

/* Selected option */
div[aria-selected="true"] {
    background: #1d4ed8 !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------
# SECTION TITLE
# -----------------------
st.markdown("<div class='section-title'>Revenue Trend</div>", unsafe_allow_html=True)

# -----------------------
# VIEW FILTER
# -----------------------
view3 = st.selectbox(
    "Revenue View",
    ["Monthly", "Daily"],
    key="u3"
)

grp3 = get_group(view3, "p.payment_date")

# -----------------------
# LOCATION FILTER
# --------------------

# -----------------------
# FILTER CONDITIONS
# -----------------------

# -----------------------
# QUERY
# -----------------------
df3 = pd.read_sql(f"""
SELECT
    {grp3} as period,
    SUM(p.amount) as total
FROM payments p
GROUP BY period
ORDER BY period
""", conn)


# -----------------------
# REVENUE CHART
# -----------------------
fig3 = go.Figure()

fig3.add_trace(go.Scatter(
    x=df3["period"],
    y=df3["total"],
    mode="lines",
    line=dict(width=3, color="#FF2D2D"),  # bright red line
    fill="tozeroy",
    fillcolor="rgba(255,45,45,0.25)",     # red glow fill
    name="Revenue"
))


fig3.update_layout(
    template="plotly_dark",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis_title="Period",
    yaxis_title="Revenue",
    showlegend=False
)

st.plotly_chart(fig3, use_container_width=True)


# ===============================
# SUBSCRIPTIONS
# ===============================
st.markdown("""
<style>

/* Section title */
.section-title {
    font-size:22px;
    font-weight:600;
    margin-bottom:12px;
}

/* Label */
div[data-testid="stSelectbox"] label {
    font-weight:600;
    color:#9aa4b2;
    margin-bottom:6px;
}

/* Rounded pill selectbox */
div[data-testid="stSelectbox"] > div {
    background: linear-gradient(145deg,#0f172a,#1e293b);
    border-radius: 30px;
    padding: 10px 14px;
    border: 1px solid rgba(255,255,255,0.08);
    transition: all .25s ease;
}

/* Selected value */
div[data-testid="stSelectbox"] div[role="button"] {
    color: white;
    font-size: 15px;
}

/* Hover glow */
div[data-testid="stSelectbox"] > div:hover {
    border: 1px solid #3b82f6;
    box-shadow: 0 0 12px rgba(59,130,246,0.5);
}

/* Dropdown */
div[role="listbox"] {
    background: #0f172a;
    border-radius: 16px;
}

/* Dropdown options */
div[role="option"] {
    padding: 10px;
    border-radius: 10px;
}

/* Hover option */
div[role="option"]:hover {
    background:#2563eb !important;
    color:white;
}

</style>
""", unsafe_allow_html=True)

# -----------------------
# SECTION TITLE
# -----------------------
st.markdown("<div class='section-title'>Subscriptions Trend</div>", unsafe_allow_html=True)

# -----------------------
# VIEW FILTER
# -----------------------
view4 = st.selectbox(
    "Subscription View",
    ["Monthly", "Daily"],
    key="sub_view"
)

grp4 = get_group(view4, "s.start_date")

# -----------------------
# LOCATION FILTER
# -----------------------
loc_df = pd.read_sql(
    "SELECT DISTINCT location FROM users",
    conn
)

location_list = ["All"] + loc_df["location"].dropna().tolist()

selected_location = st.selectbox(
    "Location",
    location_list,
    key="sub_location"
)

# -----------------------
# USER TYPE FILTER
# -----------------------
user_types = ["All", "Company", "Student", "Skill Development"]

selected_type = st.selectbox(
    "User Type",
    user_types,
    key="sub_user_type"
)

# -----------------------
# FILTER CONDITIONS
# -----------------------
filters = ""

if selected_location != "All":
    filters += f" AND u.location = '{selected_location}'"

if selected_type != "All":
    filters += f" AND u.user_type = '{selected_type}'"

# -----------------------
# DATA QUERY
# -----------------------
df4 = pd.read_sql(f"""
SELECT
    {grp4} as period,
    u.user_type,
    COUNT(*) as total
FROM subscriptions s
JOIN users u ON u.user_id = s.user_id
WHERE 1=1
{filters}
GROUP BY period, u.user_type
ORDER BY period
""", conn)

# -----------------------
# COLORFUL BAR CHART
# -----------------------
fig4 = px.bar(
    df4,
    x="period",
    y="total",
    color="user_type",
    barmode="stack",
    title="Subscription Trend by User Type",
    color_discrete_sequence=px.colors.qualitative.Bold
)

fig4.update_layout(
    template="plotly_dark",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis_title="Period",
    yaxis_title="Subscriptions"
)

st.plotly_chart(fig4, use_container_width=True)


# ===============================
# API USAGE
st.markdown("<div class='section-title'>API Usage Analytics</div>", unsafe_allow_html=True)

# -----------------------
# DATE GROUP FUNCTION
# -----------------------
def get_group(view, column):
    if view == "Monthly":
        return f"DATE_FORMAT({column}, '%Y-%m-01')"
    return f"DATE({column})"

# -----------------------
# LAYOUT
# -----------------------
col_filter, col_chart = st.columns([1, 3])

# -----------------------
# FILTER PANEL
# -----------------------
with col_filter:

    view5 = st.selectbox(
        "Usage View",
        ["Monthly", "Daily"],
        key="api_view"
    )

    grp5 = get_group(view5, "a.usage_date")


    selected_type = st.selectbox(
        "User Type",
        ["All", "Company", "Student", "Skill Development"],
        key="api_user_type"
    )

# -----------------------
# BUILD FILTERS
# -----------------------
conditions = []

if selected_type != "All":
    conditions.append(f"u.user_type = '{selected_type}'")

where_clause = ""
if conditions:
    where_clause = "WHERE " + " AND ".join(conditions)

# -----------------------
# QUERY
# -----------------------
query = """
SELECT SUM(a.calls_made) AS total_calls
FROM api_usage a
LEFT JOIN users u
    ON u.user_id = a.user_id
"""

if conditions:
    query += " WHERE " + " AND ".join(conditions)

df5 = pd.read_sql(query, conn)


# -----------------------
# CHART PANEL
# -----------------------
total_calls = df5["total_calls"].iloc[0] or 0

fig5 = go.Figure(go.Indicator(
    mode="gauge+number",
    value=total_calls,
    title={'text': "API Calls Usage"},
    gauge={
        'axis': {'range': [None, total_calls * 1.5 if total_calls else 100]},
        'bar': {'color': "#22c55e"},
        'steps': [
            {'range': [0, total_calls * 0.5], 'color': "#1f2937"},
            {'range': [total_calls * 0.5, total_calls], 'color': "#334155"},
        ],
    }
))

fig5.update_layout(
    template="plotly_dark",
    margin=dict(l=20, r=20, t=50, b=20)
)

st.plotly_chart(fig5, use_container_width=True)


# ===============================
# RATINGS
# ===============================
# --------------------------
# RATINGS CSS STYLE
# --------------------------
st.markdown("""
<style>

/* Section Title */
.section-title {
    font-size:22px;
    font-weight:600;
    margin-top:30px;
    margin-bottom:12px;
    color:#f3f4f6;
}

/* Chart container card */
div[data-testid="stPlotlyChart"] {
    background: linear-gradient(160deg,#020617,#020617);
    padding:18px;
    border-radius:18px;
    border:1px solid rgba(255,255,255,0.06);
    box-shadow:0 8px 25px rgba(0,0,0,0.6);
}

/* Smooth animation feel */
div[data-testid="stPlotlyChart"]:hover {
    box-shadow:0 12px 35px rgba(37,99,235,0.25);
    transition:0.3s ease;
}

</style>
""", unsafe_allow_html=True)

# --------------------------
# SECTION TITLE
# --------------------------
st.markdown("<div class='section-title'>Ratings Distribution</div>", unsafe_allow_html=True)

# --------------------------
# DATA QUERY
# --------------------------
df6 = pd.read_sql("""
SELECT rating, COUNT(*) AS total
FROM feedback
GROUP BY rating
ORDER BY rating
""", conn)

# --------------------------
# PIE / DONUT CHART
# --------------------------
fig6 = px.pie(
    df6,
    names="rating",
    values="total",
    title="User Rating Distribution",
    hole=0.45,  # donut effect
    color_discrete_sequence=px.colors.qualitative.Bold
)

fig6.update_layout(
    template="plotly_dark",
    margin=dict(l=20, r=20, t=50, b=20)
)

fig6.update_traces(
    textinfo="percent+label",
    pull=[0.03]*len(df6)  # slight separation
)

st.plotly_chart(fig6, use_container_width=True)


# ===============================
# GLOBAL COMBINED
# ===============================
st.markdown("<div class='section-title'>Global Combined</div>", unsafe_allow_html=True)

# --------------------------
# VIEW FILTER
# --------------------------
gview = st.selectbox(
    "View Type",
    ["Monthly", "Daily"],
    key="global_view"
)

# --------------------------
# AXIS OPTIONS
# --------------------------
axis_options = {
    "Revenue": {
        "table": "payments",
        "date_col": "payment_date",
        "value": "SUM(amount)",
        "label": "Revenue"
    },
    "Users": {
        "table": "users",
        "date_col": "signup_date",
        "value": "COUNT(*)",
        "label": "Users"
    },
    "API Calls": {
        "table": "api_usage",
        "date_col": "usage_date",
        "value": "SUM(calls_made)",
        "label": "API Calls"
    },
    "Subscriptions": {
        "table": "subscriptions",
        "date_col": "start_date",
        "value": "COUNT(*)",
        "label": "Subscriptions"
    }
}

# --------------------------
# AXIS SELECTORS
# --------------------------
x_metric = st.selectbox("X Metric", list(axis_options.keys()), key="x_axis")
y_metric = st.selectbox("Y Metric", list(axis_options.keys()), key="y_axis")

x_conf = axis_options[x_metric]
y_conf = axis_options[y_metric]

gx = get_group(gview, x_conf["date_col"])
gy = get_group(gview, y_conf["date_col"])

# --------------------------
# DATA QUERIES
# --------------------------
df_x = pd.read_sql(f"""
SELECT {gx} as period,
       {x_conf['value']} as value
FROM {x_conf['table']}
GROUP BY period
ORDER BY period
""", conn)

df_y = pd.read_sql(f"""
SELECT {gy} as period,
       {y_conf['value']} as value
FROM {y_conf['table']}
GROUP BY period
ORDER BY period
""", conn)

# --------------------------
# MERGE DATA
# --------------------------
global_df = pd.merge(df_x, df_y, on="period", how="outer")
global_df.columns = ["period", "x_value", "y_value"]
global_df = global_df.fillna(0)

global_df["period"] = pd.to_datetime(global_df["period"])

# --------------------------
# CHART
# --------------------------
figg = go.Figure()

figg.add_trace(go.Scatter(
    x=global_df["period"],
    y=global_df["x_value"],
    name=x_metric,
    mode="lines"
))

figg.add_trace(go.Scatter(
    x=global_df["period"],
    y=global_df["y_value"],
    name=y_metric,
    yaxis="y2",
    mode="lines"
))

figg.update_layout(
    template="plotly_dark",
    hovermode="x unified",
    yaxis2=dict(
        overlaying="y",
        side="right"
    ),
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(figg, use_container_width=True)


conn.close()

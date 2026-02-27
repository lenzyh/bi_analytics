import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
from faker import Faker
from streamlit_option_menu import option_menu
import sqlite3
import json

# Page configuration
st.set_page_config(
    page_title="BI Analytics Platform Demo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f0f4ff 0%, #e8ecff 100%);
    }
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'selected_data_source' not in st.session_state:
    st.session_state.selected_data_source = 'PostgreSQL - Main Analytics'


class DataGenerator:
    def __init__(self):
        self.fake = Faker()
        Faker.seed(42)

    def generate_daily_data(self, days=30):
        rng = np.random.default_rng(42)
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        data = []
        for date in dates:
            base_sessions = 1000 + int(rng.integers(-200, 300))
            weekend_factor = 0.7 if date.weekday() >= 5 else 1.0
            sessions = int(base_sessions * weekend_factor)
            page_views = sessions * float(rng.uniform(2.5, 4.5))
            users = int(sessions * float(rng.uniform(0.7, 0.9)))
            data.append({
                'date': date,
                'sessions': sessions,
                'page_views': int(page_views),
                'users': users,
                'bounce_rate': float(rng.uniform(0.35, 0.55)),
                'avg_duration': float(rng.uniform(180, 420)),
                'conversions': int(sessions * float(rng.uniform(0.02, 0.05)))
            })
        return pd.DataFrame(data)

    def generate_hourly_data(self):
        rng = np.random.default_rng(42)
        data = []
        for hour in range(24):
            if 0 <= hour <= 6: base_factor = 0.3
            elif 7 <= hour <= 9: base_factor = 0.8
            elif 10 <= hour <= 17: base_factor = 1.0
            elif 18 <= hour <= 22: base_factor = 0.9
            else: base_factor = 0.5
            sessions = int(100 * base_factor * float(rng.uniform(0.8, 1.2)))
            data.append({
                'hour': f"{hour:02d}:00",
                'sessions': sessions,
                'page_views': int(sessions * float(rng.uniform(2.0, 4.0))),
                'users': int(sessions * 0.8)
            })
        return pd.DataFrame(data)

    def generate_revenue_data(self, days=90):
        rng = np.random.default_rng(42)
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        data = []
        for date in dates:
            revenue = float(rng.uniform(5000, 15000))
            transactions = int(rng.integers(50, 200))
            user_count = int(rng.integers(800, 1200))
            data.append({
                'date': date,
                'revenue': revenue,
                'transactions': transactions,
                'arpu': revenue / max(user_count, 1),
                'mrr': revenue * 30,
                'new_customers': int(rng.integers(20, 80)),
                'churn_rate': float(rng.uniform(0.02, 0.08))
            })
        return pd.DataFrame(data)

    def generate_user_acquisition_data(self):
        rng = np.random.default_rng(42)
        channels_config = {
            'Organic Search': {'users': (800, 1200), 'cpu': 0},
            'Paid Search':    {'users': (600, 900),  'cpu': (35, 55)},
            'Social Media':   {'users': (300, 600),  'cpu': (25, 45)},
            'Email':          {'users': (200, 400),  'cpu': (5, 15)},
            'Referral':       {'users': (150, 350),  'cpu': 0},
            'Direct':         {'users': (100, 300),  'cpu': 0},
        }
        data = []
        for channel, cfg in channels_config.items():
            lo, hi = cfg['users']
            users = int(rng.integers(lo, hi))
            cost = 0.0 if cfg['cpu'] == 0 else users * float(rng.uniform(*cfg['cpu']))
            data.append({
                'channel': channel,
                'users': users,
                'cost': cost,
                'cpa': cost / users if users > 0 else 0,
                'conversion_rate': float(rng.uniform(0.02, 0.08))
            })
        return pd.DataFrame(data)

    def generate_retention_data(self):
        rng = np.random.default_rng(42)
        cohorts = []
        for i in range(6):
            month = (datetime.now() - timedelta(days=30 * i)).strftime('%Y-%m')
            cohort_size = int(rng.integers(800, 1500))
            cohorts.append({
                'cohort': month,
                'cohort_size': cohort_size,
                'day_1': cohort_size * float(rng.uniform(0.65, 0.75)),
                'day_7': cohort_size * float(rng.uniform(0.45, 0.55)),
                'day_30': cohort_size * float(rng.uniform(0.25, 0.35)),
                'day_90': cohort_size * float(rng.uniform(0.15, 0.25))
            })
        return pd.DataFrame(cohorts)


@st.cache_data
def get_cached_daily_data(days=30):
    return DataGenerator().generate_daily_data(days)

@st.cache_data
def get_cached_hourly_data():
    return DataGenerator().generate_hourly_data()

@st.cache_data
def get_cached_revenue_data(days=90):
    return DataGenerator().generate_revenue_data(days)

@st.cache_data
def get_cached_acquisition_data():
    return DataGenerator().generate_user_acquisition_data()

@st.cache_data
def get_cached_retention_data():
    return DataGenerator().generate_retention_data()


def _pct_delta(series: pd.Series, window: int = 7) -> str:
    if len(series) < window * 2:
        return "N/A"
    curr = series.iloc[-window:].sum()
    prev = series.iloc[-window * 2:-window].sum()
    if prev == 0:
        return "N/A"
    pct = (curr - prev) / prev * 100
    return f"{pct:+.1f}%"


def authenticate():
    st.markdown('<div class="main-header">🔐 BI Analytics Platform</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Login to Access Dashboard")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="demo: admin")
            password = st.text_input("Password", type="password", placeholder="demo: password")
            _, col_b, _ = st.columns([1, 1, 1])
            with col_b:
                login_button = st.form_submit_button("Login", use_container_width=True)
            if login_button:
                if username == "admin" and password == "password":
                    st.session_state.authenticated = True
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use username: admin, password: password")
        st.info("**Demo Credentials:**\n- Username: admin\n- Password: password")


def show_data_source_selector():
    st.sidebar.markdown("### 🗄️ Data Source Configuration")
    data_sources = [
        "PostgreSQL - Main Analytics",
        "MySQL - User Analytics",
        "SQLite - Application Logs",
        "BigQuery - Marketing Data"
    ]
    selected_source = st.sidebar.selectbox(
        "Select Data Source",
        data_sources,
        index=data_sources.index(st.session_state.selected_data_source)
    )
    st.session_state.selected_data_source = selected_source
    st.sidebar.success(f"✅ Connected to {selected_source}")

    st.sidebar.markdown("### 📅 Date Range")
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )
    st.sidebar.markdown("### 🔍 Filters")
    region   = st.sidebar.selectbox("Region",      ["All Regions", "North America", "Europe", "Asia", "South America"])
    platform = st.sidebar.selectbox("Platform",    ["All Platforms", "Web", "iOS", "Android", "Desktop"])
    device   = st.sidebar.selectbox("Device Type", ["All Devices", "Desktop", "Mobile", "Tablet"])

    if st.sidebar.button("Apply Filters", use_container_width=True):
        st.cache_data.clear()
        st.sidebar.success("Filters applied & data refreshed!")

    return {'data_source': selected_source, 'date_range': date_range,
            'region': region, 'platform': platform, 'device': device}


def show_metric_cards(data: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4)
    total_sessions  = data['sessions'].sum()
    total_users     = data['users'].sum()
    avg_bounce_rate = data['bounce_rate'].mean()
    avg_duration    = data['avg_duration'].mean()

    mid = len(data) // 2
    prev_b = data['bounce_rate'].iloc[:mid].mean()
    curr_b = data['bounce_rate'].iloc[mid:].mean()
    bounce_delta = f"{(curr_b - prev_b) * 100:+.1f}%" if prev_b else "N/A"

    with col1: st.metric("Total Sessions",      f"{total_sessions:,}",                          _pct_delta(data['sessions']))
    with col2: st.metric("Unique Users",         f"{total_users:,}",                             _pct_delta(data['users']))
    with col3: st.metric("Bounce Rate",          f"{avg_bounce_rate:.1%}",                       bounce_delta)
    with col4: st.metric("Avg Session Duration", f"{int(avg_duration//60)}m {int(avg_duration%60)}s", _pct_delta(data['avg_duration']))


def show_daily_analysis():
    st.markdown("## 📈 Daily Summary")
    with st.spinner("Loading daily data..."):
        daily_data  = get_cached_daily_data(30)
        hourly_data = get_cached_hourly_data()

    show_metric_cards(daily_data)
    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(daily_data, x='date', y='sessions', title="Sessions Over Time",
                      color_discrete_sequence=['#1f77b4'])
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(hourly_data, x='hour', y='sessions', title="Sessions by Hour",
                     color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📊 Detailed Daily Metrics")
    dd = daily_data.copy()
    dd['date']         = dd['date'].dt.strftime('%Y-%m-%d')
    dd['bounce_rate']  = dd['bounce_rate'].apply(lambda x: f"{x:.1%}")
    dd['avg_duration'] = dd['avg_duration'].apply(lambda x: f"{int(x//60)}m {int(x%60)}s")
    st.dataframe(dd[['date','sessions','page_views','users','bounce_rate','avg_duration','conversions']],
                 use_container_width=True)


def show_weekly_analysis():
    st.markdown("## 📊 Weekly Summary")
    with st.spinner("Loading weekly data..."):
        daily_data = get_cached_daily_data(28)

    daily_data['week'] = daily_data['date'].dt.isocalendar().week
    weekly_data = daily_data.groupby('week').agg(
        sessions=('sessions','sum'), page_views=('page_views','sum'),
        users=('users','sum'), conversions=('conversions','sum')
    ).reset_index()
    weekly_data['week'] = weekly_data['week'].apply(lambda x: f"Week {x}")

    def wow(col):
        if len(weekly_data) < 2: return "N/A"
        c, p = weekly_data[col].iloc[-1], weekly_data[col].iloc[-2]
        return f"{(c-p)/p*100:+.1f}%" if p else "N/A"

    conv_rate = weekly_data['conversions'].iloc[-1] / weekly_data['sessions'].iloc[-1] if weekly_data['sessions'].iloc[-1] else 0
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Weekly Sessions",    f"{weekly_data['sessions'].iloc[-1]:,}",    wow('sessions'))
    with col2: st.metric("Weekly Users",       f"{weekly_data['users'].iloc[-1]:,}",       wow('users'))
    with col3: st.metric("Conversion Rate",    f"{conv_rate:.2%}")
    with col4: st.metric("Weeks Tracked",      str(len(weekly_data)))

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(weekly_data, x='week', y='sessions', title="Sessions by Week",
                     color_discrete_sequence=['#2ca02c'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.line(weekly_data, x='week', y='conversions', title="Conversions by Week",
                      color_discrete_sequence=['#d62728'])
        st.plotly_chart(fig, use_container_width=True)


def show_monthly_analysis():
    st.markdown("## 📅 Monthly Summary")
    with st.spinner("Loading monthly data..."):
        monthly_data = get_cached_daily_data(90)

    monthly_data['month'] = monthly_data['date'].dt.to_period('M')
    ms = monthly_data.groupby('month').agg(
        sessions=('sessions','sum'), users=('users','sum'), page_views=('page_views','sum')
    ).reset_index()
    ms['month'] = ms['month'].astype(str)

    def mom(col):
        if len(ms) < 2: return "N/A"
        c, p = ms[col].iloc[-1], ms[col].iloc[-2]
        return f"{(c-p)/p*100:+.1f}%" if p else "N/A"

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Monthly Active Users", f"{ms['users'].iloc[-1]:,}",      mom('users'))
    with col2: st.metric("Monthly Sessions",     f"{ms['sessions'].iloc[-1]:,}",   mom('sessions'))
    with col3: st.metric("Page Views",           f"{ms['page_views'].iloc[-1]:,}", mom('page_views'))
    with col4: st.metric("Months Tracked",       str(len(ms)))

    col1, col2 = st.columns(2)
    with col1:
        fig = px.area(ms, x='month', y='users', title="Monthly Active Users",
                      color_discrete_sequence=['#9467bd'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(ms, x='month', y='sessions', title="Sessions by Month",
                     color_discrete_sequence=['#8c564b'])
        st.plotly_chart(fig, use_container_width=True)


def show_monetization_analysis():
    st.markdown("## 💰 Monetization")
    with st.spinner("Loading revenue data..."):
        revenue_data = get_cached_revenue_data(90)

    total_revenue = revenue_data['revenue'].sum()
    avg_arpu      = revenue_data['arpu'].mean()
    mrr           = revenue_data['revenue'].tail(30).mean() * 30
    mrr_prev      = revenue_data['revenue'].iloc[-60:-30].mean() * 30
    mrr_delta     = f"{(mrr-mrr_prev)/mrr_prev*100:+.1f}%" if mrr_prev else "N/A"

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Revenue",             f"${total_revenue:,.0f}", _pct_delta(revenue_data['revenue'], 30))
    with col2: st.metric("Monthly Recurring Revenue", f"${mrr:,.0f}",          mrr_delta)
    with col3: st.metric("Avg Revenue Per User",      f"${avg_arpu:.2f}")
    with col4: st.metric("Avg Daily Transactions",    f"{int(revenue_data['transactions'].mean())}")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(revenue_data.tail(30), x='date', y='revenue',
                      title="Revenue (Last 30 Days)", color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(revenue_data.tail(30), x='transactions', y='revenue',
                         title="Revenue vs Transactions", trendline="ols",
                         color_discrete_sequence=['#2ca02c'])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 💳 Revenue Breakdown")
    rb = pd.DataFrame({
        'Product':    ['Premium Plan', 'Basic Plan', 'Enterprise', 'Add-ons', 'One-time'],
        'Revenue':    [45000, 28000, 85000, 12000, 8000],
        'Percentage': [25.1, 15.6, 47.5, 6.7, 4.5]
    })
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(rb, values='Revenue', names='Product', title="Revenue by Product", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.dataframe(rb, use_container_width=True)


def show_custom_analysis():
    st.markdown("## 🔧 Custom Analysis")
    st.markdown("### SQL Query Editor")

    sample_queries = {
        "Daily Sessions": """SELECT \n    DATE(start_time) as date,\n    COUNT(*) as sessions,\n    COUNT(DISTINCT user_id) as unique_users,\n    AVG(duration_seconds) as avg_duration\nFROM user_sessions \nWHERE start_time >= CURRENT_DATE - INTERVAL '30 days'\nGROUP BY DATE(start_time)\nORDER BY date DESC;""",
        "Revenue by Product": """SELECT \n    product_id,\n    COUNT(*) as transactions,\n    SUM(amount) as total_revenue,\n    AVG(amount) as avg_transaction_value\nFROM revenue_events \nWHERE created_at >= CURRENT_DATE - INTERVAL '7 days'\nGROUP BY product_id\nORDER BY total_revenue DESC\nLIMIT 10;""",
        "User Retention": """SELECT \n    DATE_TRUNC('month', signup_date) as cohort_month,\n    COUNT(*) as cohort_size,\n    COUNT(CASE WHEN last_active >= signup_date + INTERVAL '1 day' THEN 1 END) as day_1_retained\nFROM user_metrics \nWHERE signup_date >= CURRENT_DATE - INTERVAL '6 months'\nGROUP BY DATE_TRUNC('month', signup_date)\nORDER BY cohort_month DESC;"""
    }

    selected_query = st.selectbox("Choose a sample query:", list(sample_queries.keys()))
    sql_query = st.text_area("SQL Query:", value=sample_queries[selected_query], height=200,
                              help="Only SELECT statements are allowed.")

    col1, col2, _ = st.columns([1, 1, 4])
    with col1: execute_button  = st.button("Execute Query", type="primary")
    with col2: validate_button = st.button("Validate Query")

    if validate_button:
        if sql_query.strip().upper().startswith('SELECT'):
            st.success("✅ Query syntax is valid")
        else:
            st.error("❌ Only SELECT queries are allowed")

    if execute_button:
        if not sql_query.strip().upper().startswith('SELECT'):
            st.error("❌ Only SELECT queries are allowed for security reasons")
            return
        with st.spinner("Executing query..."):
            rng = np.random.default_rng(99)
            if "user_sessions" in sql_query.lower():
                mock_data = pd.DataFrame({
                    'date': pd.date_range(end=datetime.now(), periods=10, freq='D'),
                    'sessions': rng.integers(800, 1500, 10),
                    'unique_users': rng.integers(600, 1200, 10),
                    'avg_duration': rng.integers(180, 420, 10)
                })
            elif "revenue" in sql_query.lower():
                mock_data = pd.DataFrame({
                    'product_id': [f'PROD_{i:03d}' for i in range(1, 11)],
                    'transactions': rng.integers(50, 200, 10),
                    'total_revenue': rng.integers(5000, 25000, 10),
                    'avg_transaction_value': rng.uniform(25, 150, 10).round(2)
                })
            else:
                mock_data = pd.DataFrame({
                    'cohort_month': pd.date_range(end=datetime.now(), periods=6, freq='ME'),
                    'cohort_size': rng.integers(800, 1500, 6),
                    'day_1_retained': rng.integers(500, 1000, 6)
                })
            st.dataframe(mock_data, use_container_width=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.info(f"**Rows returned:** {len(mock_data)}")
            with c2: st.info(f"**Execution time:** {rng.integers(150, 800)}ms")
            with c3: st.info(f"**Data source:** {st.session_state.selected_data_source}")


def show_user_acquisition():
    st.markdown("## 👥 User Acquisition")
    with st.spinner("Loading acquisition data..."):
        aq = get_cached_acquisition_data()

    total_users  = aq['users'].sum()
    total_cost   = aq['cost'].sum()
    avg_cpa      = total_cost / total_users if total_users > 0 else 0
    organic_pct  = aq[aq['cost'] == 0]['users'].sum() / total_users * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total New Users",      f"{total_users:,}")
    with col2: st.metric("Acquisition Cost",     f"${total_cost:,.0f}")
    with col3: st.metric("Cost Per Acquisition", f"${avg_cpa:.2f}")
    with col4: st.metric("Organic Share",        f"{organic_pct:.1f}%")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(aq, x='channel', y='users', title="User Acquisition by Channel",
                     color='users', color_continuous_scale='viridis')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        paid = aq[aq['cost'] > 0]
        fig = px.bar(paid, x='channel', y='cpa', title="CPA by Paid Channel",
                     color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📊 Channel Performance Details")
    dd = aq.copy()
    dd['cost'] = dd['cost'].apply(lambda x: f"${x:,.0f}")
    dd['cpa']  = dd['cpa'].apply(lambda x: f"${x:.2f}" if x > 0 else "Free")
    dd['conversion_rate'] = dd['conversion_rate'].apply(lambda x: f"{x:.2%}")
    st.dataframe(dd, use_container_width=True)


def show_retention_analysis():
    st.markdown("## 🔄 User Retention")
    with st.spinner("Loading retention data..."):
        ret = get_cached_retention_data()

    avg_d1  = (ret['day_1']  / ret['cohort_size']).mean() * 100
    avg_d7  = (ret['day_7']  / ret['cohort_size']).mean() * 100
    avg_d30 = (ret['day_30'] / ret['cohort_size']).mean() * 100
    avg_d90 = (ret['day_90'] / ret['cohort_size']).mean() * 100

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Day 1 Retention",  f"{avg_d1:.1f}%")
    with col2: st.metric("Day 7 Retention",  f"{avg_d7:.1f}%")
    with col3: st.metric("Day 30 Retention", f"{avg_d30:.1f}%")
    with col4: st.metric("Day 90 Retention", f"{avg_d90:.1f}%")

    curve = pd.DataFrame({
        'Day':            ['Day 0', 'Day 1', 'Day 7', 'Day 14', 'Day 30', 'Day 60', 'Day 90'],
        'Retention Rate': [100, avg_d1, avg_d7, (avg_d7+avg_d30)/2, avg_d30, (avg_d30+avg_d90)/2, avg_d90],
    })
    curve['Users'] = (curve['Retention Rate'] / 100 * 1000).round(0).astype(int)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(curve, x='Day', y='Retention Rate', title="User Retention Curve",
                      color_discrete_sequence=['#1f77b4'], markers=True)
        fig.update_layout(yaxis_title="Retention Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(curve, x='Day', y='Users', title="Retained Users by Day",
                     color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📊 Cohort Analysis")
    dr = ret.copy()
    for c in ['day_1','day_7','day_30','day_90']:
        dr[f'{c}_rate'] = (dr[c] / dr['cohort_size'] * 100).round(1)
    dr = dr[['cohort','cohort_size','day_1_rate','day_7_rate','day_30_rate','day_90_rate']]
    dr.columns = ['Cohort','Size','Day 1 (%)','Day 7 (%)','Day 30 (%)','Day 90 (%)']
    st.dataframe(dr, use_container_width=True)


def main():
    if not st.session_state.authenticated:
        authenticate()
        return

    st.markdown('<div class="main-header">📊 BI Analytics Platform Demo</div>', unsafe_allow_html=True)
    filters = show_data_source_selector()

    selected_module = option_menu(
        menu_title=None,
        options=["Daily","Weekly","Monthly","Monetization","Acquisition","Retention","Custom"],
        icons=["calendar-day","calendar-week","calendar-month","currency-dollar","people","arrow-repeat","code-slash"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#1f77b4", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#1f77b4"},
        }
    )

    if   selected_module == "Daily":        show_daily_analysis()
    elif selected_module == "Weekly":       show_weekly_analysis()
    elif selected_module == "Monthly":      show_monthly_analysis()
    elif selected_module == "Monetization": show_monetization_analysis()
    elif selected_module == "Acquisition":  show_user_acquisition()
    elif selected_module == "Retention":    show_retention_analysis()
    elif selected_module == "Custom":       show_custom_analysis()

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1: st.info(f"**Data Source:** {filters['data_source']}")
    with col2: st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col3:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.success("Data refreshed!")
            st.rerun()


if __name__ == "__main__":
    main()
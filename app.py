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
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
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
        random.seed(42)
        np.random.seed(42)
    
    def generate_daily_data(self, days=30):
        """Generate daily analytics data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        data = []
        
        for date in dates:
            # Simulate realistic daily patterns
            base_sessions = 1000 + random.randint(-200, 300)
            weekend_factor = 0.7 if date.weekday() >= 5 else 1.0
            
            sessions = int(base_sessions * weekend_factor)
            page_views = sessions * random.uniform(2.5, 4.5)
            users = int(sessions * random.uniform(0.7, 0.9))
            bounce_rate = random.uniform(0.35, 0.55)
            avg_duration = random.uniform(180, 420)  # seconds
            
            data.append({
                'date': date,
                'sessions': sessions,
                'page_views': int(page_views),
                'users': users,
                'bounce_rate': bounce_rate,
                'avg_duration': avg_duration,
                'conversions': int(sessions * random.uniform(0.02, 0.05))
            })
        
        return pd.DataFrame(data)
    
    def generate_hourly_data(self):
        """Generate hourly data for today"""
        hours = range(24)
        data = []
        
        for hour in hours:
            # Simulate realistic hourly patterns
            if 0 <= hour <= 6:
                base_factor = 0.3
            elif 7 <= hour <= 9:
                base_factor = 0.8
            elif 10 <= hour <= 17:
                base_factor = 1.0
            elif 18 <= hour <= 22:
                base_factor = 0.9
            else:
                base_factor = 0.5
            
            sessions = int(100 * base_factor * random.uniform(0.8, 1.2))
            page_views = sessions * random.uniform(2.0, 4.0)
            
            data.append({
                'hour': f"{hour:02d}:00",
                'sessions': sessions,
                'page_views': int(page_views),
                'users': int(sessions * 0.8)
            })
        
        return pd.DataFrame(data)
    
    def generate_revenue_data(self, days=90):
        """Generate revenue and monetization data"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        data = []
        
        for date in dates:
            revenue = random.uniform(5000, 15000)
            transactions = random.randint(50, 200)
            arpu = revenue / max(random.randint(800, 1200), 1)
            
            data.append({
                'date': date,
                'revenue': revenue,
                'transactions': transactions,
                'arpu': arpu,
                'mrr': revenue * 30,  # Simplified MRR calculation
                'new_customers': random.randint(20, 80),
                'churn_rate': random.uniform(0.02, 0.08)
            })
        
        return pd.DataFrame(data)
    
    def generate_user_acquisition_data(self):
        """Generate user acquisition channel data"""
        channels = ['Organic Search', 'Paid Search', 'Social Media', 'Email', 'Referral', 'Direct']
        data = []
        
        for channel in channels:
            if channel == 'Organic Search':
                users = random.randint(800, 1200)
                cost = 0
            elif channel == 'Paid Search':
                users = random.randint(600, 900)
                cost = users * random.uniform(35, 55)
            elif channel == 'Social Media':
                users = random.randint(300, 600)
                cost = users * random.uniform(25, 45)
            elif channel == 'Email':
                users = random.randint(200, 400)
                cost = users * random.uniform(5, 15)
            elif channel == 'Referral':
                users = random.randint(150, 350)
                cost = 0
            else:  # Direct
                users = random.randint(100, 300)
                cost = 0
            
            cpa = cost / users if users > 0 else 0
            
            data.append({
                'channel': channel,
                'users': users,
                'cost': cost,
                'cpa': cpa,
                'conversion_rate': random.uniform(0.02, 0.08)
            })
        
        return pd.DataFrame(data)
    
    def generate_retention_data(self):
        """Generate user retention cohort data"""
        cohorts = []
        for i in range(6):
            month = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m')
            cohort_size = random.randint(800, 1500)
            
            cohorts.append({
                'cohort': month,
                'cohort_size': cohort_size,
                'day_1': cohort_size * random.uniform(0.65, 0.75),
                'day_7': cohort_size * random.uniform(0.45, 0.55),
                'day_30': cohort_size * random.uniform(0.25, 0.35),
                'day_90': cohort_size * random.uniform(0.15, 0.25)
            })
        
        return pd.DataFrame(cohorts)

# Initialize data generator
@st.cache_data
def get_data_generator():
    return DataGenerator()

data_gen = get_data_generator()

def authenticate():
    """Simple authentication for demo"""
    st.markdown('<div class="main-header">🔐 BI Analytics Platform</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login to Access Dashboard")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username (demo: admin)")
            password = st.text_input("Password", type="password", placeholder="Enter password (demo: password)")
            
            col_a, col_b, col_c = st.columns([1, 1, 1])
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
    """Data source selection and validation"""
    st.sidebar.markdown("### 🗄️ Data Source Configuration")
    
    # Data source selection
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
    
    # Connection status
    st.sidebar.success(f"✅ Connected to {selected_source}")
    
    # Date range selector
    st.sidebar.markdown("### 📅 Date Range")
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )
    
    # Filters
    st.sidebar.markdown("### 🔍 Filters")
    
    region = st.sidebar.selectbox(
        "Region",
        ["All Regions", "North America", "Europe", "Asia", "South America"]
    )
    
    platform = st.sidebar.selectbox(
        "Platform", 
        ["All Platforms", "Web", "iOS", "Android", "Desktop"]
    )
    
    device = st.sidebar.selectbox(
        "Device Type",
        ["All Devices", "Desktop", "Mobile", "Tablet"]
    )
    
    # Apply filters button
    if st.sidebar.button("Apply Filters", use_container_width=True):
        st.sidebar.success("Filters applied successfully!")
    
    return {
        'data_source': selected_source,
        'date_range': date_range,
        'region': region,
        'platform': platform,
        'device': device
    }

def show_metric_cards(data):
    """Display KPI metric cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    total_sessions = data['sessions'].sum()
    total_users = data['users'].sum()
    avg_bounce_rate = data['bounce_rate'].mean()
    avg_duration = data['avg_duration'].mean()
    
    with col1:
        st.metric(
            label="Total Sessions",
            value=f"{total_sessions:,}",
            delta=f"+{random.randint(5, 15)}%"
        )
    
    with col2:
        st.metric(
            label="Unique Users", 
            value=f"{total_users:,}",
            delta=f"+{random.randint(3, 12)}%"
        )
    
    with col3:
        st.metric(
            label="Bounce Rate",
            value=f"{avg_bounce_rate:.1%}",
            delta=f"-{random.uniform(1, 5):.1f}%"
        )
    
    with col4:
        st.metric(
            label="Avg Session Duration",
            value=f"{int(avg_duration//60)}m {int(avg_duration%60)}s",
            delta=f"+{random.randint(2, 8)}%"
        )

def show_daily_analysis():
    """Daily analysis dashboard"""
    st.markdown("## 📈 Daily Summary")
    
    # Generate data
    daily_data = data_gen.generate_daily_data(30)
    hourly_data = data_gen.generate_hourly_data()
    
    # Show metric cards
    show_metric_cards(daily_data)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Daily Sessions Trend")
        fig = px.line(daily_data, x='date', y='sessions', 
                     title="Sessions Over Time",
                     color_discrete_sequence=['#1f77b4'])
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Hourly Traffic Distribution")
        fig = px.bar(hourly_data, x='hour', y='sessions',
                    title="Sessions by Hour",
                    color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.markdown("### 📊 Detailed Daily Metrics")
    
    # Format the data for display
    display_data = daily_data.copy()
    display_data['date'] = display_data['date'].dt.strftime('%Y-%m-%d')
    display_data['bounce_rate'] = display_data['bounce_rate'].apply(lambda x: f"{x:.1%}")
    display_data['avg_duration'] = display_data['avg_duration'].apply(lambda x: f"{int(x//60)}m {int(x%60)}s")
    
    st.dataframe(
        display_data[['date', 'sessions', 'page_views', 'users', 'bounce_rate', 'avg_duration', 'conversions']],
        use_container_width=True
    )

def show_weekly_analysis():
    """Weekly analysis dashboard"""
    st.markdown("## 📊 Weekly Summary")
    
    # Generate weekly aggregated data
    daily_data = data_gen.generate_daily_data(28)  # 4 weeks
    daily_data['week'] = daily_data['date'].dt.isocalendar().week
    weekly_data = daily_data.groupby('week').agg({
        'sessions': 'sum',
        'page_views': 'sum', 
        'users': 'sum',
        'conversions': 'sum'
    }).reset_index()
    weekly_data['week'] = weekly_data['week'].apply(lambda x: f"Week {x}")
    
    # Weekly metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Weekly Sessions", f"{weekly_data['sessions'].iloc[-1]:,}", "+12.5%")
    with col2:
        st.metric("Weekly Users", f"{weekly_data['users'].iloc[-1]:,}", "+8.3%")
    with col3:
        st.metric("Conversion Rate", "2.8%", "+0.3%")
    with col4:
        st.metric("Week-over-Week Growth", "+15.2%", "+2.1%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Weekly Sessions Comparison")
        fig = px.bar(weekly_data, x='week', y='sessions',
                    title="Sessions by Week",
                    color_discrete_sequence=['#2ca02c'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Weekly Conversions")
        fig = px.line(weekly_data, x='week', y='conversions',
                     title="Conversions by Week", 
                     color_discrete_sequence=['#d62728'])
        st.plotly_chart(fig, use_container_width=True)

def show_monthly_analysis():
    """Monthly analysis dashboard"""
    st.markdown("## 📅 Monthly Summary")
    
    # Generate monthly data
    monthly_data = data_gen.generate_daily_data(90)
    monthly_data['month'] = monthly_data['date'].dt.to_period('M')
    monthly_summary = monthly_data.groupby('month').agg({
        'sessions': 'sum',
        'users': 'sum',
        'page_views': 'sum'
    }).reset_index()
    monthly_summary['month'] = monthly_summary['month'].astype(str)
    
    # Monthly metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Active Users", "54,800", "+18.2%")
    with col2:
        st.metric("Monthly Sessions", "125,400", "+22.1%")
    with col3:
        st.metric("Page Views", "485,200", "+15.8%")
    with col4:
        st.metric("Month-over-Month Growth", "+19.5%", "+3.2%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Monthly User Growth")
        fig = px.area(monthly_summary, x='month', y='users',
                     title="Monthly Active Users",
                     color_discrete_sequence=['#9467bd'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Monthly Sessions Trend")
        fig = px.bar(monthly_summary, x='month', y='sessions',
                    title="Sessions by Month",
                    color_discrete_sequence=['#8c564b'])
        st.plotly_chart(fig, use_container_width=True)

def show_monetization_analysis():
    """Monetization analysis dashboard"""
    st.markdown("## 💰 Monetization")
    
    # Generate revenue data
    revenue_data = data_gen.generate_revenue_data(90)
    
    # Revenue metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = revenue_data['revenue'].sum()
    avg_arpu = revenue_data['arpu'].mean()
    mrr = revenue_data['revenue'].tail(30).mean() * 30
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}", "+24.5%")
    with col2:
        st.metric("Monthly Recurring Revenue", f"${mrr:,.0f}", "+18.3%")
    with col3:
        st.metric("Average Revenue Per User", f"${avg_arpu:.2f}", "+12.1%")
    with col4:
        st.metric("Customer Lifetime Value", "$890", "+8.7%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Daily Revenue Trend")
        fig = px.line(revenue_data.tail(30), x='date', y='revenue',
                     title="Revenue Over Time",
                     color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Revenue vs Transactions")
        fig = px.scatter(revenue_data.tail(30), x='transactions', y='revenue',
                        title="Revenue vs Transaction Volume",
                        color_discrete_sequence=['#2ca02c'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Revenue breakdown
    st.markdown("### 💳 Revenue Breakdown")
    
    revenue_breakdown = pd.DataFrame({
        'Product': ['Premium Plan', 'Basic Plan', 'Enterprise', 'Add-ons', 'One-time'],
        'Revenue': [45000, 28000, 85000, 12000, 8000],
        'Percentage': [25.1, 15.6, 47.5, 6.7, 4.5]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(revenue_breakdown, values='Revenue', names='Product',
                    title="Revenue by Product")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(revenue_breakdown, use_container_width=True)

def show_custom_analysis():
    """Custom analysis with SQL editor"""
    st.markdown("## 🔧 Custom Analysis")
    
    # SQL Query Editor
    st.markdown("### SQL Query Editor")
    
    # Sample queries
    sample_queries = {
        "Daily Sessions": """SELECT 
    DATE(start_time) as date,
    COUNT(*) as sessions,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(duration_seconds) as avg_duration
FROM user_sessions 
WHERE start_time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(start_time)
ORDER BY date DESC;""",
        
        "Revenue by Product": """SELECT 
    product_id,
    COUNT(*) as transactions,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction_value
FROM revenue_events 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY product_id
ORDER BY total_revenue DESC
LIMIT 10;""",
        
        "User Retention": """SELECT 
    DATE_TRUNC('month', signup_date) as cohort_month,
    COUNT(*) as cohort_size,
    COUNT(CASE WHEN last_active >= signup_date + INTERVAL '1 day' THEN 1 END) as day_1_retained
FROM user_metrics 
WHERE signup_date >= CURRENT_DATE - INTERVAL '6 months'
GROUP BY DATE_TRUNC('month', signup_date)
ORDER BY cohort_month DESC;"""
    }
    
    # Query selector
    selected_query = st.selectbox("Choose a sample query:", list(sample_queries.keys()))
    
    # SQL Editor
    sql_query = st.text_area(
        "SQL Query:",
        value=sample_queries[selected_query],
        height=200,
        help="Write your SQL query here. Only SELECT statements are allowed."
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        execute_button = st.button("Execute Query", type="primary")
    
    with col2:
        validate_button = st.button("Validate Query")
    
    if validate_button:
        if sql_query.strip().upper().startswith('SELECT'):
            st.success("✅ Query syntax is valid")
        else:
            st.error("❌ Only SELECT queries are allowed")
    
    if execute_button:
        if sql_query.strip().upper().startswith('SELECT'):
            # Simulate query execution with mock results
            st.markdown("### Query Results")
            
            # Generate mock results based on query type
            if "user_sessions" in sql_query.lower():
                mock_data = pd.DataFrame({
                    'date': pd.date_range(end=datetime.now(), periods=10, freq='D'),
                    'sessions': np.random.randint(800, 1500, 10),
                    'unique_users': np.random.randint(600, 1200, 10),
                    'avg_duration': np.random.randint(180, 420, 10)
                })
            elif "revenue" in sql_query.lower():
                mock_data = pd.DataFrame({
                    'product_id': [f'PROD_{i:03d}' for i in range(1, 11)],
                    'transactions': np.random.randint(50, 200, 10),
                    'total_revenue': np.random.randint(5000, 25000, 10),
                    'avg_transaction_value': np.random.uniform(25, 150, 10).round(2)
                })
            else:
                mock_data = pd.DataFrame({
                    'cohort_month': pd.date_range(end=datetime.now(), periods=6, freq='M'),
                    'cohort_size': np.random.randint(800, 1500, 6),
                    'day_1_retained': np.random.randint(500, 1000, 6)
                })
            
            st.dataframe(mock_data, use_container_width=True)
            
            # Query execution info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Rows returned:** {len(mock_data)}")
            with col2:
                st.info(f"**Execution time:** {random.randint(150, 800)}ms")
            with col3:
                st.info(f"**Data source:** {st.session_state.selected_data_source}")
        else:
            st.error("❌ Only SELECT queries are allowed for security reasons")

def show_user_acquisition():
    """User acquisition analysis"""
    st.markdown("## 👥 User Acquisition")
    
    # Generate acquisition data
    acquisition_data = data_gen.generate_user_acquisition_data()
    
    # Acquisition metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_users = acquisition_data['users'].sum()
    total_cost = acquisition_data['cost'].sum()
    avg_cpa = total_cost / total_users if total_users > 0 else 0
    
    with col1:
        st.metric("Total New Users", f"{total_users:,}", "+15.3%")
    with col2:
        st.metric("Acquisition Cost", f"${total_cost:,.0f}", "+8.2%")
    with col3:
        st.metric("Cost Per Acquisition", f"${avg_cpa:.2f}", "-12.5%")
    with col4:
        st.metric("Organic Share", "42.3%", "+3.1%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Users by Channel")
        fig = px.bar(acquisition_data, x='channel', y='users',
                    title="User Acquisition by Channel",
                    color='users',
                    color_continuous_scale='viridis')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Cost Per Acquisition by Channel")
        paid_channels = acquisition_data[acquisition_data['cost'] > 0]
        fig = px.bar(paid_channels, x='channel', y='cpa',
                    title="CPA by Paid Channel",
                    color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.markdown("### 📊 Channel Performance Details")
    display_data = acquisition_data.copy()
    display_data['cost'] = display_data['cost'].apply(lambda x: f"${x:,.0f}")
    display_data['cpa'] = display_data['cpa'].apply(lambda x: f"${x:.2f}" if x > 0 else "Free")
    display_data['conversion_rate'] = display_data['conversion_rate'].apply(lambda x: f"{x:.2%}")
    
    st.dataframe(display_data, use_container_width=True)

def show_retention_analysis():
    """User retention analysis"""
    st.markdown("## 🔄 User Retention")
    
    # Generate retention data
    retention_data = data_gen.generate_retention_data()
    
    # Retention metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Day 1 Retention", "68.5%", "+2.3%")
    with col2:
        st.metric("Day 7 Retention", "52.1%", "+1.8%")
    with col3:
        st.metric("Day 30 Retention", "38.2%", "+0.9%")
    with col4:
        st.metric("Average Retention", "52.9%", "+1.5%")
    
    # Retention curve
    st.markdown("### 📈 Retention Curve")
    
    retention_curve = pd.DataFrame({
        'Day': ['Day 0', 'Day 1', 'Day 7', 'Day 14', 'Day 30', 'Day 60', 'Day 90'],
        'Retention Rate': [100, 68.5, 52.1, 45.2, 38.2, 28.1, 22.3],
        'Users': [1000, 685, 521, 452, 382, 281, 223]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(retention_curve, x='Day', y='Retention Rate',
                     title="User Retention Curve",
                     color_discrete_sequence=['#1f77b4'])
        fig.update_layout(yaxis_title="Retention Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(retention_curve, x='Day', y='Users',
                    title="Retained Users by Day",
                    color_discrete_sequence=['#ff7f0e'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Cohort analysis
    st.markdown("### 📊 Cohort Analysis")
    
    # Format retention data for display
    display_retention = retention_data.copy()
    for col in ['day_1', 'day_7', 'day_30', 'day_90']:
        display_retention[f'{col}_rate'] = (display_retention[col] / display_retention['cohort_size'] * 100).round(1)
    
    display_retention = display_retention[['cohort', 'cohort_size', 'day_1_rate', 'day_7_rate', 'day_30_rate', 'day_90_rate']]
    display_retention.columns = ['Cohort', 'Size', 'Day 1 (%)', 'Day 7 (%)', 'Day 30 (%)', 'Day 90 (%)']
    
    st.dataframe(display_retention, use_container_width=True)

def main():
    """Main application"""
    
    if not st.session_state.authenticated:
        authenticate()
        return
    
    # Header
    st.markdown('<div class="main-header">📊 BI Analytics Platform Demo</div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    filters = show_data_source_selector()
    
    # Main navigation
    selected_module = option_menu(
        menu_title=None,
        options=["Daily", "Weekly", "Monthly", "Monetization", "Acquisition", "Retention", "Custom"],
        icons=["calendar-day", "calendar-week", "calendar-month", "currency-dollar", "people", "arrow-repeat", "code-slash"],
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
    
    # Show selected analysis
    if selected_module == "Daily":
        show_daily_analysis()
    elif selected_module == "Weekly":
        show_weekly_analysis()
    elif selected_module == "Monthly":
        show_monthly_analysis()
    elif selected_module == "Monetization":
        show_monetization_analysis()
    elif selected_module == "Acquisition":
        show_user_acquisition()
    elif selected_module == "Retention":
        show_retention_analysis()
    elif selected_module == "Custom":
        show_custom_analysis()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Data Source:** {filters['data_source']}")
    with col2:
        st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col3:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.success("Data refreshed successfully!")
            st.rerun()

if __name__ == "__main__":
    main()
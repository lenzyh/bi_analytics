# BI Analytics Platform Demo

A comprehensive Business Intelligence Analytics Platform demo built with Streamlit to showcase key BI features and capabilities for client presentations.

## 🚀 Features

### Core Analytics Modules
- **Daily Summary**: Hourly traffic analysis, session metrics, KPI cards
- **Weekly Summary**: Week-over-week comparisons, trend analysis
- **Monthly Summary**: Monthly active users, growth metrics, seasonal patterns
- **Monetization**: Revenue tracking, MRR/ARR, ARPU, customer lifetime value
- **User Acquisition**: Channel performance, cost per acquisition, conversion rates
- **User Retention**: Cohort analysis, retention curves, churn tracking
- **Custom Analysis**: SQL query editor with sample queries and validation

### Key Features
- 🔐 **Authentication System**: Simple login (demo: admin/password)
- 🗄️ **Data Source Management**: Multiple database connections simulation
- 📊 **Interactive Visualizations**: Plotly charts with real-time data
- 🔍 **Advanced Filtering**: Date range, region, platform, device filters
- 📈 **KPI Dashboards**: Metric cards with trend indicators
- 💻 **SQL Query Editor**: Custom query execution with syntax validation
- 📱 **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

### Quick Start with uv (Recommended)

1. **Install uv** (if not already installed)
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or with pip
   pip install uv
   ```

2. **Clone or download the demo files**
   ```bash
   cd bi_analytics_demo
   ```

3. **Create virtual environment and install dependencies**
   ```bash
   uv sync
   ```

4. **Run the application**
   ```bash
   # Option 1: Using uv run (recommended)
   uv run streamlit run app.py
   
   # Option 2: Using the launcher script
   uv run python run_demo.py
   
   # Option 3: Activate environment manually
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   streamlit run app.py
   ```

5. **Access the demo**
   - Open your browser to `http://localhost:8501`
   - Login with credentials: `admin` / `password`

### Alternative Setup (Traditional pip)

If you prefer using pip instead of uv:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## 📦 Project Structure

```
bi_analytics_demo/
├── app.py                 # Main Streamlit application
├── run_demo.py           # Demo launcher script
├── pyproject.toml        # Project configuration (uv)
├── requirements.txt      # Dependencies (pip fallback)
├── .python-version       # Python version specification
├── uv.lock              # Dependency lock file
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── README.md            # This file
```

## 📊 Demo Data

The application generates realistic mock data for demonstration purposes:

- **User Sessions**: 30 days of daily session data with realistic patterns
- **Revenue Data**: 90 days of revenue, transactions, and monetization metrics
- **User Acquisition**: Multi-channel acquisition data with costs and conversion rates
- **Retention Analysis**: Cohort-based retention data with time-series analysis
- **Hourly Patterns**: Realistic hourly traffic distribution

## 🎯 Use Cases Demonstrated

### 1. Executive Dashboard
- High-level KPIs and metrics
- Trend analysis and growth indicators
- Revenue and monetization tracking

### 2. Marketing Analytics
- User acquisition channel performance
- Cost per acquisition optimization
- Conversion funnel analysis

### 3. Product Analytics
- User engagement and retention
- Feature usage patterns
- Cohort-based analysis

### 4. Custom Analysis
- SQL query builder and executor
- Ad-hoc data exploration
- Custom metric definitions

## 🔧 Technical Architecture

### Frontend
- **Streamlit**: Web application framework
- **Plotly**: Interactive data visualizations
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations

### Data Generation
- **Faker**: Realistic fake data generation
- **Random**: Statistical data simulation
- **DateTime**: Time-series data handling

### Features Demonstrated
- **Database Schema Introspection**: Simulated table/column validation
- **Metric Validation**: Check if selected metrics exist in database
- **Query Execution**: Safe SQL query execution with syntax validation
- **Caching**: Streamlit caching for performance optimization
- **Error Handling**: Graceful error handling and user feedback

## 📋 Demo Script for Client Presentation

### 1. Introduction (2 minutes)
- "This is our BI Analytics Platform demo showcasing enterprise-grade analytics capabilities"
- Login demonstration with authentication
- Overview of the modular architecture

### 2. Data Source Management (3 minutes)
- Show multiple data source connections (PostgreSQL, MySQL, SQLite, BigQuery)
- Demonstrate filter system (date range, region, platform, device)
- Explain real-time connection status and validation

### 3. Core Analytics Modules (10 minutes)

**Daily Analysis:**
- Real-time KPI cards with trend indicators
- Hourly traffic distribution charts
- Detailed metrics table with drill-down capability

**Weekly/Monthly Analysis:**
- Period-over-period comparisons
- Growth trend visualization
- Seasonal pattern analysis

**Monetization Dashboard:**
- Revenue tracking and forecasting
- MRR/ARR calculations
- Customer lifetime value analysis
- Revenue breakdown by product/segment

### 4. Advanced Features (8 minutes)

**User Acquisition:**
- Multi-channel attribution analysis
- Cost per acquisition optimization
- ROI calculation by marketing channel

**Retention Analysis:**
- Cohort-based retention curves
- Churn prediction and analysis
- User lifecycle tracking

**Custom SQL Editor:**
- Live query execution
- Syntax validation and error handling
- Pre-built query templates
- Security features (read-only access)

### 5. Technical Capabilities (5 minutes)
- Database schema introspection
- Metric validation against database structure
- Query performance optimization
- Error handling and user feedback
- Responsive design demonstration

### 6. Scalability & Enterprise Features (2 minutes)
- Multi-tenant architecture ready
- Role-based access control
- Audit logging capabilities
- API-first design for integrations

## 🔒 Security Features Demonstrated

- **Authentication**: User login system
- **Query Validation**: Only SELECT statements allowed
- **Input Sanitization**: SQL injection prevention
- **Access Control**: Role-based permissions (simulated)
- **Audit Logging**: Query execution tracking

## 📈 Performance Features

- **Caching**: Intelligent data caching for faster load times
- **Lazy Loading**: On-demand data generation
- **Query Optimization**: Efficient data processing
- **Responsive UI**: Fast, interactive user interface

## 🎨 Customization Options

The demo can be easily customized for specific client needs:

- **Branding**: Colors, logos, and styling
- **Data Sources**: Add specific database connections
- **Metrics**: Custom KPIs and business metrics
- **Visualizations**: Industry-specific chart types
- **Workflows**: Custom analysis workflows

## 📞 Next Steps

After the demo, discuss:

1. **Custom Implementation**: Tailored solution for client's specific needs
2. **Data Integration**: Connecting to client's existing databases
3. **Advanced Features**: AI/ML analytics, predictive modeling
4. **Deployment**: Cloud infrastructure and scaling options
5. **Training**: User training and documentation
6. **Support**: Ongoing maintenance and support plans

## 🚀 Production Considerations

For actual implementation, consider:

- **Database Connections**: Real database integration with connection pooling
- **Authentication**: Enterprise SSO integration (SAML, OAuth)
- **Performance**: Query optimization and caching strategies
- **Security**: Data encryption, access controls, audit trails
- **Scalability**: Microservices architecture, load balancing
- **Monitoring**: Application performance monitoring and alerting

---

**Demo Credentials:**
- Username: `admin`
- Password: `password`

**Contact Information:**
- For technical questions about implementation
- For custom demo requests
- For pricing and licensing information
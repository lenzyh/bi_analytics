# ══════════════════════════════════════════════════════════════════════════════
# Web3 BI Dashboard - CEX Growth Insights
# Demonstrates: Data extraction, dashboards, trend analysis, insights, LLM agent
# ══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import requests
import json
import time
import hashlib
import re

# Conditional imports with fallback
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

try:
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.feature_extraction.text import CountVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Web3 BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS - Dark Theme
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Brand colors: primary green #00d4aa, dark bg #0d1117 */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4aa, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
        letter-spacing: 1px;
    }
    .sub-header {
        font-size: 1rem;
        color: #8b949e;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #1a2332 100%);
        border: 1px solid #30363d;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.3rem 0;
    }
    .kpi-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00d4aa;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #8b949e;
        margin-top: 0.2rem;
    }
    .live-badge {
        background: #00d4aa;
        color: #0d1117;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    .demo-badge {
        background: #f0883e;
        color: #0d1117;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    .section-divider {
        border-top: 1px solid #30363d;
        margin: 1.5rem 0;
    }
    /* Plotly chart dark bg override */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
    /* Streamlit tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        color: #8b949e;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a2332;
        color: #00d4aa;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    /* Table styling */
    .dataframe {
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'language' not in st.session_state:
    st.session_state.language = 'English'
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'deepseek_api_key' not in st.session_state:
    st.session_state.deepseek_api_key = ''
if 'cryptopanic_token' not in st.session_state:
    st.session_state.cryptopanic_token = ''

# ══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS (English + Mandarin)
# CEX terminology throughout
# ══════════════════════════════════════════════════════════════════════════════

TRANSLATIONS = {
    'English': {
        'title': 'Web3 BI Dashboard',
        'subtitle': 'CEX Growth Insights | Data Analytics Platform',
        'login': 'Login to Dashboard',
        'username': 'Username',
        'password': 'Password',
        'login_btn': 'Login',
        # Sidebar
        'language_label': 'Language',
        'date_range': 'Date Range',
        'coin_filter': 'Coin Filter',
        'channel_filter': 'Channel Filter',
        'region_filter': 'Region Filter',
        'api_keys': 'API Configuration',
        'cryptopanic_token': 'CryptoPanic Token (optional)',
        'deepseek_key': 'DeepSeek API Key',
        'refresh_data': 'Refresh All Data',
        'all_coins': 'All Coins',
        'all_channels': 'All Channels',
        'all_regions': 'All Regions',
        # Tabs
        'tab_metrics': 'Core Metrics',
        'tab_sentiment': 'News & Sentiment',
        'tab_agent': 'BI Agent',
        # KPIs - CEX specific
        'trading_volume_24h': '24h Trading Volume',
        'dau': 'Daily Active Users',
        'wau': 'Weekly Active Users',
        'mau': 'Monthly Active Users',
        'retention_d1': 'D1 Retention',
        'fee_revenue': 'Fee Revenue (30d)',
        'avg_spread': 'Avg Spread (bps)',
        # Sub-tabs
        'volume_revenue': 'Volume & Revenue',
        'user_growth': 'User Growth',
        'acq_channels': 'Acquisition Channels',
        'retention': 'Retention',
        'order_quality': 'Order Quality',
        'real_time_prices': 'Real-Time Prices',
        # Charts
        'daily_volume_by_coin': 'Daily Trading Volume by Coin',
        'fee_revenue_trend': 'Daily Fee Revenue',
        'volume_by_coin': 'Volume Distribution by Coin',
        'volume_heatmap': 'Volume Heatmap (Coin x Weekday)',
        'active_users_trend': 'Active Users Trend',
        'period_selector': 'Period',
        'new_users_by_channel': 'New Registrations by Channel',
        'user_funnel': 'User Conversion Funnel',
        'users_by_channel': 'Users by Acquisition Channel',
        'cac_by_channel': 'CAC by Channel',
        'channel_performance': 'Channel Performance',
        'retention_curve': 'Retention Curve',
        'cohort_heatmap': 'Cohort Retention Heatmap',
        'exec_time_trend': 'Avg Execution Time (ms)',
        'spread_by_coin': 'Avg Spread by Coin (bps)',
        'fill_rate': 'Fill Rate by Coin',
        # Sentiment
        'latest_news': 'Latest Crypto News',
        'sentiment_gauges': 'Sentiment by Coin',
        'sentiment_trend': 'Daily Sentiment Trend',
        'sentiment_by_coin': 'Sentiment Score by Coin',
        'sentiment_dist': 'Sentiment Distribution',
        'topic_modeling': 'Topic Modeling (LDA)',
        'num_topics': 'Number of Topics',
        'topic_words': 'Top Words per Topic',
        'topic_dist': 'Topic Distribution',
        # Agent
        'bi_agent_title': 'BI Agent',
        'bi_agent_desc': 'Ask questions about exchange data, trends, and insights',
        'quick_ask': 'Quick Questions',
        'agent_placeholder': 'Ask about trading volume, user trends, sentiment...',
        'no_api_key': 'Enter your DeepSeek API key in the sidebar to enable the BI Agent.',
        # Table headers
        'rank': 'Rank',
        'coin': 'Coin',
        'price': 'Price',
        'change_1h': '1h %',
        'change_24h': '24h %',
        'change_7d': '7d %',
        'market_cap': 'Market Cap',
        'volume_24h': '24h Volume',
        'sparkline': '7d Chart',
        # Footer
        'data_source': 'Data Source',
        'last_updated': 'Last Updated',
        # Channels - maps to CEX channel operations
        'organic': 'Organic',
        'kol_referral': 'KOL Referral',
        'paid_ads': 'Paid Ads',
        'social_media': 'Social Media',
        'airdrop': 'Airdrop Campaign',
    },
    'Mandarin': {
        'title': 'Web3 BI 数据看板',
        'subtitle': 'CEX 增长洞察 | 数据分析平台',
        'login': '登录数据看板',
        'username': '用户名',
        'password': '密码',
        'login_btn': '登录',
        'language_label': '语言',
        'date_range': '日期范围',
        'coin_filter': '币种筛选',
        'channel_filter': '渠道筛选',
        'region_filter': '地区筛选',
        'api_keys': 'API 配置',
        'cryptopanic_token': 'CryptoPanic Token (可选)',
        'deepseek_key': 'DeepSeek API Key',
        'refresh_data': '刷新数据',
        'all_coins': '全部币种',
        'all_channels': '全部渠道',
        'all_regions': '全部地区',
        'tab_metrics': '核心指标',
        'tab_sentiment': '新闻与情绪',
        'tab_agent': 'BI 智能助手',
        'trading_volume_24h': '24h 交易量',
        'dau': '日活跃用户',
        'wau': '周活跃用户',
        'mau': '月活跃用户',
        'retention_d1': '次日留存率',
        'fee_revenue': '手续费收入 (30天)',
        'avg_spread': '平均价差 (bps)',
        'volume_revenue': '交易量与收入',
        'user_growth': '用户增长',
        'acq_channels': '获客渠道',
        'retention': '用户留存',
        'order_quality': '订单质量',
        'real_time_prices': '实时行情',
        'daily_volume_by_coin': '按币种每日交易量',
        'fee_revenue_trend': '每日手续费收入',
        'volume_by_coin': '各币种交易量分布',
        'volume_heatmap': '交易量热力图 (币种 x 星期)',
        'active_users_trend': '活跃用户趋势',
        'period_selector': '周期',
        'new_users_by_channel': '按渠道新增注册',
        'user_funnel': '用户转化漏斗',
        'users_by_channel': '按渠道获客用户数',
        'cac_by_channel': '各渠道获客成本',
        'channel_performance': '渠道表现',
        'retention_curve': '留存曲线',
        'cohort_heatmap': '队列留存热力图',
        'exec_time_trend': '平均执行时间 (ms)',
        'spread_by_coin': '各币种平均价差 (bps)',
        'fill_rate': '各币种成交率',
        'latest_news': '最新加密货币新闻',
        'sentiment_gauges': '各币种情绪',
        'sentiment_trend': '每日情绪趋势',
        'sentiment_by_coin': '各币种情绪得分',
        'sentiment_dist': '情绪分布',
        'topic_modeling': '主题建模 (LDA)',
        'num_topics': '主题数量',
        'topic_words': '每个主题的关键词',
        'topic_dist': '主题分布',
        'bi_agent_title': 'BI 智能助手',
        'bi_agent_desc': '询问交易所数据、趋势和洞察',
        'quick_ask': '快捷问题',
        'agent_placeholder': '询问交易量、用户趋势、情绪分析...',
        'no_api_key': '请在侧边栏输入 DeepSeek API Key 以启用 BI 智能助手。',
        'rank': '排名',
        'coin': '币种',
        'price': '价格',
        'change_1h': '1h %',
        'change_24h': '24h %',
        'change_7d': '7d %',
        'market_cap': '市值',
        'volume_24h': '24h 成交量',
        'sparkline': '7日走势',
        'data_source': '数据来源',
        'last_updated': '最后更新',
        'organic': '自然流量',
        'kol_referral': 'KOL 推荐',
        'paid_ads': '付费广告',
        'social_media': '社交媒体',
        'airdrop': '空投活动',
    }
}

def t(key):
    """Translation helper - bilingual support"""
    return TRANSLATIONS.get(st.session_state.language, TRANSLATIONS['English']).get(key, key)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

COINS = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX", "DOT", "MATIC"]
COIN_WEIGHTS = [0.30, 0.25, 0.10, 0.08, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03]
COIN_AVG_TRADE = {"BTC": 5000, "ETH": 2000, "SOL": 800, "BNB": 1000, "XRP": 500,
                  "ADA": 300, "DOGE": 200, "AVAX": 600, "DOT": 400, "MATIC": 250}
CHANNELS = ["Organic", "KOL Referral", "Paid Ads", "Social Media", "Airdrop Campaign"]
CHANNEL_WEIGHTS = [0.35, 0.20, 0.20, 0.15, 0.10]
CHANNEL_CAC = {"Organic": 0, "KOL Referral": 25, "Paid Ads": 45, "Social Media": 30, "Airdrop Campaign": 15}
REGIONS = ["Asia", "Europe", "North America", "South America", "Africa", "Oceania"]
REGION_WEIGHTS = [0.45, 0.25, 0.15, 0.08, 0.04, 0.03]
SCALE_FACTOR = 10  # Scale display metrics to represent platform-level data

# CoinGecko coin ID mapping for API
COINGECKO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "BNB": "binancecoin",
    "XRP": "ripple", "ADA": "cardano", "DOGE": "dogecoin", "AVAX": "avalanche-2",
    "DOT": "polkadot", "MATIC": "matic-network"
}

PLOTLY_DARK_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e6edf3'),
        xaxis=dict(gridcolor='#30363d', zerolinecolor='#30363d'),
        yaxis=dict(gridcolor='#30363d', zerolinecolor='#30363d'),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )
)

def apply_dark_theme(fig):
    """Apply dark theme to a Plotly figure."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e6edf3', size=12),
        xaxis=dict(gridcolor='#30363d', zerolinecolor='#30363d'),
        yaxis=dict(gridcolor='#30363d', zerolinecolor='#30363d'),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# CEX DATA GENERATOR
# Generates realistic CEX trading data for dashboard demo
# Supports daily data extraction and dashboard KPIs per job description
# ══════════════════════════════════════════════════════════════════════════════

class CEXDataGenerator:
    """Generate realistic centralized exchange data for CEX analytics."""

    def __init__(self, seed=42):
        random.seed(seed)
        np.random.seed(seed)

    def generate_trades_df(self, days=30):
        """Generate trade records. ~4000 trades/day, scaled x10 for display.
        CEX relevance: daily data extraction, trading volume analysis."""
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        records = []
        for day_offset in range(days):
            date = end_date - timedelta(days=days - 1 - day_offset)
            is_weekend = date.weekday() >= 5
            base_trades = int(4000 * (0.7 if is_weekend else 1.0) * np.random.uniform(0.85, 1.15))

            coins = np.random.choice(COINS, size=base_trades, p=COIN_WEIGHTS)
            channels = np.random.choice(CHANNELS, size=base_trades, p=CHANNEL_WEIGHTS)
            trade_types = np.random.choice(["spot", "futures"], size=base_trades, p=[0.70, 0.30])

            for i in range(base_trades):
                coin = coins[i]
                avg = COIN_AVG_TRADE[coin]
                volume = max(10, avg * np.random.lognormal(0, 0.8))
                fee_rate = np.random.uniform(0.0008, 0.0012)
                records.append({
                    'date': date,
                    'user_id': f"U{np.random.randint(1, 100000):05d}",
                    'coin': coin,
                    'volume_usd': round(volume, 2),
                    'fee': round(volume * fee_rate, 2),
                    'channel': channels[i],
                    'trade_type': trade_types[i],
                })

        return pd.DataFrame(records)

    def generate_users_df(self, n_users=10000):
        """Generate user registration data.
        CEX relevance: user growth metrics, DAU/WAU/MAU, acquisition cost analysis."""
        end_date = datetime.now()
        reg_dates = [end_date - timedelta(days=int(np.random.exponential(60))) for _ in range(n_users)]
        last_actives = [rd + timedelta(days=min(int(np.random.exponential(15)), (end_date - rd).days))
                        for rd in reg_dates]
        # Clamp last_active to not exceed now
        last_actives = [min(la, end_date) for la in last_actives]

        regions = np.random.choice(REGIONS, size=n_users, p=REGION_WEIGHTS)
        channels = np.random.choice(CHANNELS, size=n_users, p=CHANNEL_WEIGHTS)
        kyc = np.random.choice(["Verified", "Pending", "Not Started"], size=n_users, p=[0.60, 0.25, 0.15])
        vip = np.random.choice([0, 1, 2, 3, 4, 5], size=n_users, p=[0.70, 0.15, 0.08, 0.04, 0.02, 0.01])

        return pd.DataFrame({
            'user_id': [f"U{i:05d}" for i in range(1, n_users + 1)],
            'registration_date': reg_dates,
            'last_active': last_actives,
            'region': regions,
            'channel': channels,
            'kyc_status': kyc,
            'vip_level': vip,
        })

    def generate_order_book_metrics(self, days=30):
        """Generate order book quality metrics per coin per day.
        CEX relevance: liquidity monitoring, execution quality dashboard."""
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        records = []
        for day_offset in range(days):
            date = end_date - timedelta(days=days - 1 - day_offset)
            for coin in COINS:
                base_spread = {"BTC": 3, "ETH": 4, "SOL": 8, "BNB": 6}.get(coin, 10)
                records.append({
                    'date': date,
                    'coin': coin,
                    'avg_spread_bps': round(base_spread * np.random.uniform(0.8, 1.3), 1),
                    'avg_exec_time_ms': round(np.random.uniform(50, 180), 0),
                    'fill_rate': round(np.random.uniform(0.95, 0.995), 3),
                })
        return pd.DataFrame(records)

    def generate_retention_cohorts(self):
        """Generate monthly retention cohort data.
        CEX relevance: user retention analysis, cohort-based growth tracking."""
        cohorts = []
        for i in range(6):
            month = (datetime.now() - timedelta(days=30 * i)).strftime('%Y-%m')
            size = np.random.randint(2000, 5000)
            # Crypto retention is typically lower than general apps
            d1 = round(np.random.uniform(0.40, 0.55), 3)
            d7 = round(np.random.uniform(0.25, 0.35), 3)
            d14 = round(np.random.uniform(0.18, 0.28), 3)
            d30 = round(np.random.uniform(0.12, 0.22), 3)
            cohorts.append({
                'cohort': month, 'cohort_size': size,
                'd1': d1, 'd7': d7, 'd14': d14, 'd30': d30
            })
        return pd.DataFrame(cohorts)

    def generate_news_corpus(self, n=150):
        """Generate realistic crypto news headlines as fallback.
        CEX relevance: sentiment analysis, market intelligence."""
        templates_positive = [
            "{coin} surges {pct}% as institutional adoption accelerates",
            "Exchange reports record {coin} trading volume amid market rally",
            "{coin} breaks key resistance level, analysts predict further gains",
            "Major bank announces {coin} custody service, boosting market confidence",
            "{coin} ecosystem sees explosive DeFi growth, TVL hits new ATH",
            "Regulatory clarity for {coin} drives positive market sentiment",
            "{coin} network upgrade completed successfully, transaction fees drop 40%",
            "Exchange launches {coin} staking program with competitive APY",
            "Whale accumulation of {coin} signals long-term bullish outlook",
            "{coin} partnership with Fortune 500 company announced",
        ]
        templates_negative = [
            "{coin} drops {pct}% amid broader market sell-off concerns",
            "Security vulnerability found in {coin} protocol raises concerns",
            "Regulatory crackdown threatens {coin} adoption in key markets",
            "{coin} faces network congestion issues, users report delays",
            "Large {coin} holder liquidated, triggering cascade of sell orders",
            "FUD spreads as {coin} faces potential delisting from exchanges",
            "{coin} development team faces internal disputes, roadmap delayed",
            "Market analysts warn of potential {coin} bear cycle ahead",
        ]
        templates_neutral = [
            "{coin} consolidates near ${price} level as traders await catalyst",
            "Exchange adds new {coin} trading pairs for Asian markets",
            "{coin} trading volume remains steady at ${vol}M daily average",
            "Analysis: What {coin} on-chain data reveals about market direction",
            "Exchange implements enhanced KYC for {coin} derivatives trading",
            "{coin} hash rate reaches new milestone, network security strengthens",
            "Weekly recap: {coin} price action and key technical levels",
            "Industry report: {coin} market share among top exchanges analyzed",
        ]
        sources = ["CoinDesk", "CoinTelegraph", "The Block", "Decrypt", "Bloomberg Crypto",
                    "Reuters Digital", "Exchange Research", "Messari", "Glassnode", "CryptoSlate"]

        np.random.seed(42)
        news = []
        for i in range(n):
            coin = np.random.choice(COINS)
            pct = np.random.randint(2, 25)
            price = np.random.randint(100, 70000)
            vol = np.random.randint(50, 500)
            sentiment_type = np.random.choice(["positive", "negative", "neutral"], p=[0.4, 0.25, 0.35])

            if sentiment_type == "positive":
                template = np.random.choice(templates_positive)
            elif sentiment_type == "negative":
                template = np.random.choice(templates_negative)
            else:
                template = np.random.choice(templates_neutral)

            title = template.format(coin=coin, pct=pct, price=price, vol=vol)
            pub_date = datetime.now() - timedelta(hours=np.random.randint(1, 72 * 5))

            news.append({
                'title': title,
                'description': f"Detailed analysis of {coin} market dynamics and trading patterns on the exchange.",
                'published_at': pub_date.isoformat(),
                'source': {'title': np.random.choice(sources)},
                'currencies': [{'code': coin}],
            })

        return sorted(news, key=lambda x: x['published_at'], reverse=True)


# ══════════════════════════════════════════════════════════════════════════════
# CACHED DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def load_trades_data(days=30):
    gen = CEXDataGenerator(seed=42)
    return gen.generate_trades_df(days)

@st.cache_data(ttl=600)
def load_users_data():
    gen = CEXDataGenerator(seed=42)
    return gen.generate_users_df()

@st.cache_data(ttl=600)
def load_order_book_data(days=30):
    gen = CEXDataGenerator(seed=42)
    return gen.generate_order_book_metrics(days)

@st.cache_data(ttl=600)
def load_retention_data():
    gen = CEXDataGenerator(seed=42)
    return gen.generate_retention_cohorts()

@st.cache_data(ttl=600)
def load_news_corpus():
    gen = CEXDataGenerator(seed=42)
    return gen.generate_news_corpus()

# ══════════════════════════════════════════════════════════════════════════════
# API INTEGRATION LAYER
# CoinGecko for live prices, CryptoPanic for news, with graceful fallbacks
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60)
def fetch_coingecko_prices():
    """Fetch top 20 coins from CoinGecko free API. No key required.
    Returns (data_list, is_live). Caches 60s to respect rate limits."""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": "true",
            "price_change_percentage": "1h,24h,7d"
        }
        resp = requests.get(url, params=params, timeout=10,
                            headers={"Accept": "application/json"})
        resp.raise_for_status()
        return resp.json(), True
    except Exception:
        return _fallback_prices(), False


def _fallback_prices():
    """Static fallback price data when CoinGecko is unreachable."""
    np.random.seed(int(datetime.now().hour))
    fallback = [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 67500,
         "market_cap": 1325000000000, "total_volume": 28000000000, "market_cap_rank": 1},
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum", "current_price": 3450,
         "market_cap": 415000000000, "total_volume": 14000000000, "market_cap_rank": 2},
        {"id": "solana", "symbol": "sol", "name": "Solana", "current_price": 145,
         "market_cap": 63000000000, "total_volume": 2800000000, "market_cap_rank": 5},
        {"id": "binancecoin", "symbol": "bnb", "name": "BNB", "current_price": 580,
         "market_cap": 87000000000, "total_volume": 1500000000, "market_cap_rank": 4},
        {"id": "ripple", "symbol": "xrp", "name": "XRP", "current_price": 0.62,
         "market_cap": 34000000000, "total_volume": 1200000000, "market_cap_rank": 6},
        {"id": "cardano", "symbol": "ada", "name": "Cardano", "current_price": 0.45,
         "market_cap": 16000000000, "total_volume": 400000000, "market_cap_rank": 9},
        {"id": "dogecoin", "symbol": "doge", "name": "Dogecoin", "current_price": 0.12,
         "market_cap": 17000000000, "total_volume": 800000000, "market_cap_rank": 8},
        {"id": "avalanche-2", "symbol": "avax", "name": "Avalanche", "current_price": 35,
         "market_cap": 13000000000, "total_volume": 500000000, "market_cap_rank": 12},
        {"id": "polkadot", "symbol": "dot", "name": "Polkadot", "current_price": 7.2,
         "market_cap": 10000000000, "total_volume": 300000000, "market_cap_rank": 14},
        {"id": "matic-network", "symbol": "matic", "name": "Polygon", "current_price": 0.72,
         "market_cap": 7000000000, "total_volume": 350000000, "market_cap_rank": 16},
    ]
    # Add sparkline and change percentages to fallback
    for coin in fallback:
        base = coin["current_price"]
        coin["sparkline_in_7d"] = {"price": [base * (1 + np.random.uniform(-0.05, 0.05)) for _ in range(168)]}
        coin["price_change_percentage_1h_in_currency"] = round(np.random.uniform(-2, 2), 2)
        coin["price_change_percentage_24h_in_currency"] = round(np.random.uniform(-5, 8), 2)
        coin["price_change_percentage_7d_in_currency"] = round(np.random.uniform(-10, 15), 2)
    return fallback


@st.cache_data(ttl=300)
def fetch_crypto_news(auth_token=""):
    """Fetch crypto news from CryptoPanic free API. Falls back to generated news."""
    if auth_token:
        try:
            url = "https://cryptopanic.com/api/free/v1/posts/"
            params = {"auth_token": auth_token, "public": "true", "kind": "news"}
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if results:
                return results, True
        except Exception:
            pass
    return load_news_corpus(), False


# ══════════════════════════════════════════════════════════════════════════════
# SENTIMENT ANALYSIS ENGINE
# VADER sentiment on crypto news - maps to CEX market intelligence
# ══════════════════════════════════════════════════════════════════════════════

COIN_KEYWORDS = {
    "BTC": ["btc", "bitcoin"], "ETH": ["eth", "ethereum"], "SOL": ["sol", "solana"],
    "BNB": ["bnb", "binance coin"], "XRP": ["xrp", "ripple"], "ADA": ["ada", "cardano"],
    "DOGE": ["doge", "dogecoin"], "AVAX": ["avax", "avalanche"], "DOT": ["dot", "polkadot"],
    "MATIC": ["matic", "polygon"],
}

def extract_coins_from_text(text):
    """Extract mentioned coins from news text."""
    text_lower = text.lower()
    found = []
    for coin, keywords in COIN_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(coin)
    return found if found else ["GENERAL"]


@st.cache_data(ttl=300)
def analyze_sentiment(news_items):
    """Run VADER sentiment on news corpus. Returns DataFrame with scores."""
    if not VADER_AVAILABLE:
        # Fallback: simple keyword-based sentiment
        results = []
        for item in news_items:
            title = item.get('title', '')
            pos_words = ['surge', 'rally', 'gain', 'bull', 'boost', 'record', 'positive', 'growth', 'breakout', 'adoption']
            neg_words = ['drop', 'crash', 'sell', 'bear', 'fear', 'hack', 'risk', 'decline', 'crackdown', 'vulnerability']
            title_lower = title.lower()
            pos_count = sum(1 for w in pos_words if w in title_lower)
            neg_count = sum(1 for w in neg_words if w in title_lower)
            compound = (pos_count - neg_count) * 0.3
            compound = max(-1, min(1, compound))
            label = "Bullish" if compound > 0.05 else ("Bearish" if compound < -0.05 else "Neutral")
            coins = extract_coins_from_text(title)
            pub = item.get('published_at', datetime.now().isoformat())
            source = item.get('source', {})
            if isinstance(source, dict):
                source = source.get('title', 'Unknown')
            results.append({
                'title': title, 'published_at': pub, 'source': source,
                'compound': round(compound, 3), 'pos': max(0, compound),
                'neg': max(0, -compound), 'neu': 1 - abs(compound),
                'sentiment_label': label, 'coins': coins
            })
        return pd.DataFrame(results)

    analyzer = SentimentIntensityAnalyzer()
    results = []
    for item in news_items:
        title = item.get('title', '')
        desc = item.get('description', '')
        text = f"{title}. {desc}"
        scores = analyzer.polarity_scores(text)
        compound = scores['compound']
        label = "Bullish" if compound > 0.05 else ("Bearish" if compound < -0.05 else "Neutral")
        coins = extract_coins_from_text(text)

        # Handle source field (may be dict from CryptoPanic or str from fallback)
        pub = item.get('published_at', datetime.now().isoformat())
        source = item.get('source', {})
        if isinstance(source, dict):
            source = source.get('title', 'Unknown')

        results.append({
            'title': title, 'published_at': pub, 'source': source,
            'compound': round(compound, 3), 'pos': round(scores['pos'], 3),
            'neg': round(scores['neg'], 3), 'neu': round(scores['neu'], 3),
            'sentiment_label': label, 'coins': coins,
        })
    return pd.DataFrame(results)


# ══════════════════════════════════════════════════════════════════════════════
# TOPIC MODELING ENGINE
# LDA on news corpus - demonstrates NLP skills
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def run_topic_modeling(texts, n_topics=5, n_top_words=10):
    """Run LDA topic modeling. Returns topics list and doc-topic distributions."""
    if not SKLEARN_AVAILABLE or len(texts) < 10:
        return [], np.array([])

    vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english')
    try:
        doc_term_matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return [], np.array([])

    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=10)
    lda.fit(doc_term_matrix)

    feature_names = vectorizer.get_feature_names_out()
    topics = []
    for idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[-n_top_words:][::-1]
        words = [feature_names[i] for i in top_indices]
        weights = [float(topic[i]) for i in top_indices]
        topics.append({"topic_id": idx, "label": f"Topic {idx + 1}", "words": words, "weights": weights})

    doc_topics = lda.transform(doc_term_matrix)
    return topics, doc_topics


# ══════════════════════════════════════════════════════════════════════════════
# DEEPSEEK LLM AGENT
# Conversational BI agent using DeepSeek API (OpenAI-compatible)
# CEX relevance: actionable insights, deep-dive analyses
# ══════════════════════════════════════════════════════════════════════════════

def build_data_context(trades_df, users_df):
    """Build text summary of exchange data for LLM context window."""
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)

    # Active users
    dau = users_df[users_df['last_active'].dt.date == yesterday.date()].shape[0]
    mau = users_df[users_df['last_active'] >= (now - timedelta(days=30))].shape[0]

    # Volume stats
    vol_by_coin = trades_df.groupby('coin')['volume_usd'].sum().sort_values(ascending=False)
    vol_by_channel = trades_df.groupby('channel')['volume_usd'].sum().sort_values(ascending=False)
    daily_vol = trades_df.groupby('date')['volume_usd'].sum()
    total_fees = trades_df['fee'].sum()

    context = f"""=== Exchange Data Summary (Last 30 Days) ===
Total Trading Volume: ${trades_df['volume_usd'].sum() * SCALE_FACTOR:,.0f}
Total Trades: {len(trades_df) * SCALE_FACTOR:,}
Daily Active Users (yesterday): {dau * SCALE_FACTOR:,}
Monthly Active Users: {mau * SCALE_FACTOR:,}
Total Registered Users: {len(users_df) * SCALE_FACTOR:,}
Total Fee Revenue: ${total_fees * SCALE_FACTOR:,.0f}

Top Coins by Volume (USD):
{(vol_by_coin * SCALE_FACTOR).head(5).to_string()}

Volume by Acquisition Channel:
{(vol_by_channel * SCALE_FACTOR).to_string()}

Daily Volume Trend (last 7 days):
{(daily_vol.tail(7) * SCALE_FACTOR).to_string()}

User Regions:
{users_df['region'].value_counts().to_string()}

KYC Status Distribution:
{users_df['kyc_status'].value_counts().to_string()}
"""
    return context


def query_deepseek(user_question, context_summary, api_key):
    """Send question to DeepSeek API with exchange data context."""
    if not OPENAI_AVAILABLE:
        return "OpenAI library not installed. Run: pip install openai", False

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

    system_prompt = f"""You are a senior data analyst at a cryptocurrency exchange.
You have access to the following data:

{context_summary}

Guidelines:
1. Reference specific numbers from the data in your analysis
2. Provide actionable insights relevant to CEX growth
3. If the user asks for a chart, return Python code using plotly (create a figure named 'fig')
4. Format currency and percentages clearly
5. Consider CEX-specific factors: trading volume trends, user acquisition channels, retention, market share
6. Respond in the same language as the question"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.chat_history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_question})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=2000,
            temperature=0.7,
        )
        return response.choices[0].message.content, True
    except Exception as e:
        return f"DeepSeek API error: {str(e)}", False


def try_execute_plotly_code(response_text):
    """Extract and safely execute Plotly code from LLM response."""
    if "```python" not in response_text:
        return None
    try:
        code_block = response_text.split("```python")[1].split("```")[0]
        local_vars = {"px": px, "go": go, "pd": pd, "np": np, "make_subplots": make_subplots}
        exec(code_block, {"__builtins__": {}}, local_vars)
        fig = local_vars.get("fig")
        if fig is not None:
            apply_dark_theme(fig)
        return fig
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ══════════════════════════════════════════════════════════════════════════════

def authenticate():
    """Branded login screen."""
    st.markdown('<div class="main-header">Web3 BI Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">CEX Growth Insights | Data Analytics Platform</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"### {t('login')}")
        with st.form("login_form"):
            username = st.text_input(t('username'), placeholder="admin")
            password = st.text_input(t('password'), type="password", placeholder="password")
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_b:
                login_btn = st.form_submit_button(t('login_btn'), use_container_width=True)
            if login_btn:
                if username == "admin" and password == "password":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use: admin / password")
        st.info("**Demo Credentials:** admin / password")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# Filters and API configuration for dashboard
# ══════════════════════════════════════════════════════════════════════════════

def show_sidebar():
    """Render sidebar with filters and API key inputs."""
    # Language
    lang = st.sidebar.selectbox(
        f"🌐 {t('language_label')}",
        ['English', 'Mandarin'],
        index=0 if st.session_state.language == 'English' else 1
    )
    if lang != st.session_state.language:
        st.session_state.language = lang
        st.rerun()

    st.sidebar.markdown("---")

    # Date range
    st.sidebar.markdown(f"### 📅 {t('date_range')}")
    date_range = st.sidebar.date_input(
        t('date_range'),
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now(),
        label_visibility="collapsed"
    )

    # Coin filter
    st.sidebar.markdown(f"### 🪙 {t('coin_filter')}")
    selected_coins = st.sidebar.multiselect(
        t('coin_filter'), COINS, default=COINS, label_visibility="collapsed"
    )
    if not selected_coins:
        selected_coins = COINS

    # Channel filter - CEX channel ops
    st.sidebar.markdown(f"### 📢 {t('channel_filter')}")
    selected_channels = st.sidebar.multiselect(
        t('channel_filter'), CHANNELS, default=CHANNELS, label_visibility="collapsed"
    )
    if not selected_channels:
        selected_channels = CHANNELS

    # Region filter
    st.sidebar.markdown(f"### 🌍 {t('region_filter')}")
    selected_regions = st.sidebar.multiselect(
        t('region_filter'), REGIONS, default=REGIONS, label_visibility="collapsed"
    )
    if not selected_regions:
        selected_regions = REGIONS

    # API Keys
    st.sidebar.markdown("---")
    with st.sidebar.expander(f"🔑 {t('api_keys')}", expanded=False):
        cp_token = st.text_input(t('cryptopanic_token'), value=st.session_state.cryptopanic_token,
                                  type="password", key="cp_tok")
        ds_key = st.text_input(t('deepseek_key'), value=st.session_state.deepseek_api_key,
                                type="password", key="ds_key")
        st.session_state.cryptopanic_token = cp_token
        st.session_state.deepseek_api_key = ds_key

    # Refresh button
    if st.sidebar.button(f"🔄 {t('refresh_data')}", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    return {
        'date_range': date_range,
        'coins': selected_coins,
        'channels': selected_channels,
        'regions': selected_regions,
    }


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: CORE METRICS
# Trading volume, user growth, channels, retention, order quality, live prices
# CEX relevance: "build dashboards", "analyze growth trends"
# ══════════════════════════════════════════════════════════════════════════════

def show_core_metrics(trades_df, users_df, filters):
    """Render Core Metrics tab with CEX KPIs and sub-tabs."""

    # Filter data by selected coins and channels
    tdf = trades_df[trades_df['coin'].isin(filters['coins']) & trades_df['channel'].isin(filters['channels'])]
    udf = users_df[users_df['channel'].isin(filters['channels']) & users_df['region'].isin(filters['regions'])]

    now = datetime.now()
    yesterday = (now - timedelta(days=1)).date()

    # ── KPI Cards ──
    total_vol = tdf['volume_usd'].sum() * SCALE_FACTOR
    total_fees = tdf['fee'].sum() * SCALE_FACTOR
    dau = udf[udf['last_active'].dt.date == yesterday].shape[0] * SCALE_FACTOR
    mau = udf[udf['last_active'] >= (now - timedelta(days=30))].shape[0] * SCALE_FACTOR

    ob_df = load_order_book_data()
    avg_spread = ob_df[ob_df['coin'].isin(filters['coins'])]['avg_spread_bps'].mean()

    ret_df = load_retention_data()
    avg_d1 = ret_df['d1'].mean() * 100

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric(t('trading_volume_24h'), f"${total_vol / 30:,.0f}", "+8.2%")
    c2.metric(t('dau'), f"{dau:,}", "+5.1%")
    c3.metric(t('mau'), f"{mau:,}", "+12.3%")
    c4.metric(t('retention_d1'), f"{avg_d1:.1f}%", "+1.8%")
    c5.metric(t('fee_revenue'), f"${total_fees:,.0f}", "+15.4%")
    c6.metric(t('avg_spread'), f"{avg_spread:.1f}", "-0.8")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Sub-tabs ──
    sub1, sub2, sub3, sub4, sub5, sub6 = st.tabs([
        t('volume_revenue'), t('user_growth'), t('acq_channels'),
        t('retention'), t('order_quality'), t('real_time_prices')
    ])

    # ── Volume & Revenue ──
    with sub1:
        _show_volume_revenue(tdf)

    # ── User Growth ──
    with sub2:
        _show_user_growth(udf, tdf)

    # ── Acquisition Channels ──
    with sub3:
        _show_acquisition_channels(udf, tdf)

    # ── Retention ──
    with sub4:
        _show_retention(ret_df)

    # ── Order Quality ──
    with sub5:
        _show_order_quality(ob_df, filters)

    # ── Real-Time Prices ──
    with sub6:
        _show_real_time_prices()


def _show_volume_revenue(tdf):
    """Volume & Revenue sub-tab."""
    col1, col2 = st.columns(2)

    # Daily volume by coin (stacked area)
    daily_coin_vol = tdf.groupby(['date', 'coin'])['volume_usd'].sum().reset_index()
    daily_coin_vol['volume_usd'] *= SCALE_FACTOR
    with col1:
        fig = px.area(daily_coin_vol, x='date', y='volume_usd', color='coin',
                      title=t('daily_volume_by_coin'),
                      color_discrete_sequence=px.colors.qualitative.Set2)
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Daily fee revenue
    daily_fees = tdf.groupby('date')['fee'].sum().reset_index()
    daily_fees['fee'] *= SCALE_FACTOR
    with col2:
        fig = px.bar(daily_fees, x='date', y='fee', title=t('fee_revenue_trend'),
                     color_discrete_sequence=['#00d4aa'])
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    # Volume by coin (pie)
    coin_vol = tdf.groupby('coin')['volume_usd'].sum().reset_index()
    with col3:
        fig = px.pie(coin_vol, values='volume_usd', names='coin',
                     title=t('volume_by_coin'),
                     color_discrete_sequence=px.colors.qualitative.Set2)
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Volume heatmap (coin x weekday)
    tdf_copy = tdf.copy()
    tdf_copy['weekday'] = tdf_copy['date'].dt.day_name()
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = tdf_copy.groupby(['coin', 'weekday'])['volume_usd'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='coin', columns='weekday', values='volume_usd')
    heatmap_pivot = heatmap_pivot.reindex(columns=weekday_order)
    with col4:
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale='Viridis',
            text=np.round(heatmap_pivot.values / 1e6, 1),
            texttemplate="%{text}M",
            textfont={"size": 10},
        ))
        fig.update_layout(title=t('volume_heatmap'))
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


def _show_user_growth(udf, tdf):
    """User Growth sub-tab - active user trends, registration funnel."""
    col1, col2 = st.columns(2)

    now = datetime.now()

    with col1:
        # Period selector: Daily / Weekly / Monthly
        period = st.radio(t('period_selector'), ['Daily', 'Weekly', 'Monthly'], horizontal=True, key='au_period')

        if period == 'Daily':
            # DAU over 30 days
            au_data = []
            for i in range(30):
                day = (now - timedelta(days=29 - i)).date()
                count = udf[udf['last_active'].dt.date == day].shape[0] * SCALE_FACTOR
                au_data.append({'date': day, 'Active Users': count})
            au_df = pd.DataFrame(au_data)
            label = t('dau')
        elif period == 'Weekly':
            # WAU over 12 weeks
            au_data = []
            for i in range(12):
                week_end = (now - timedelta(weeks=11 - i)).date()
                week_start = week_end - timedelta(days=6)
                count = udf[(udf['last_active'].dt.date >= week_start) & (udf['last_active'].dt.date <= week_end)].drop_duplicates('user_id').shape[0] * SCALE_FACTOR
                au_data.append({'date': week_end, 'Active Users': count})
            au_df = pd.DataFrame(au_data)
            label = t('wau')
        else:
            # MAU over 6 months
            au_data = []
            for i in range(6):
                month_end = (now - timedelta(days=30 * (5 - i))).date()
                month_start = month_end - timedelta(days=29)
                count = udf[(udf['last_active'].dt.date >= month_start) & (udf['last_active'].dt.date <= month_end)].drop_duplicates('user_id').shape[0] * SCALE_FACTOR
                au_data.append({'date': month_end, 'Active Users': count})
            au_df = pd.DataFrame(au_data)
            label = t('mau')

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=au_df['date'], y=au_df['Active Users'], name=label,
                                 line=dict(color='#00d4aa', width=2),
                                 fill='tozeroy', fillcolor='rgba(0,212,170,0.1)'))
        fig.update_layout(title=f"{t('active_users_trend')} — {label}")
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    # New registrations by channel (last 30 days)
    recent_users = udf[udf['registration_date'] >= (now - timedelta(days=30))]
    reg_by_channel = recent_users.groupby([recent_users['registration_date'].dt.date, 'channel']).size().reset_index(name='count')
    reg_by_channel['count'] *= SCALE_FACTOR
    with col2:
        fig = px.bar(reg_by_channel, x='registration_date', y='count', color='channel',
                     title=t('new_users_by_channel'),
                     color_discrete_sequence=px.colors.qualitative.Set2)
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    # User funnel: Registered -> KYC Verified -> Traded -> Active (7d)
    total_users = len(udf) * SCALE_FACTOR
    kyc_verified = udf[udf['kyc_status'] == 'Verified'].shape[0] * SCALE_FACTOR
    # Cap traders to fraction of registered users (realistic: ~30-40% of users trade)
    traders = min(tdf['user_id'].nunique() * SCALE_FACTOR, int(total_users * 0.35))
    active_7d = udf[udf['last_active'] >= (now - timedelta(days=7))].shape[0] * SCALE_FACTOR

    fig = go.Figure(go.Funnel(
        y=['Registered', 'KYC Verified', 'Traded (30d)', 'Active (7d)'],
        x=[total_users, kyc_verified, traders, active_7d],
        textinfo="value+percent initial",
        marker=dict(color=['#00d4aa', '#00b4d8', '#f0883e', '#e6edf3']),
    ))
    fig.update_layout(title=t('user_funnel'))
    apply_dark_theme(fig)
    st.plotly_chart(fig, use_container_width=True)


def _show_acquisition_channels(udf, tdf):
    """Acquisition Channels sub-tab - channel ops dashboard."""
    col1, col2 = st.columns(2)

    # Users by channel
    channel_users = udf['channel'].value_counts().reset_index()
    channel_users.columns = ['channel', 'users']
    channel_users['users'] *= SCALE_FACTOR
    with col1:
        fig = px.bar(channel_users, x='users', y='channel', orientation='h',
                     title=t('users_by_channel'),
                     color='users', color_continuous_scale='Tealgrn')
        apply_dark_theme(fig)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # CAC by channel
    cac_data = pd.DataFrame([
        {'channel': ch, 'CAC': CHANNEL_CAC[ch] * np.random.uniform(0.9, 1.1)}
        for ch in CHANNELS if CHANNEL_CAC[ch] > 0
    ])
    with col2:
        fig = px.bar(cac_data, x='channel', y='CAC',
                     title=t('cac_by_channel'),
                     color_discrete_sequence=['#f0883e'])
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Channel performance table
    st.markdown(f"### {t('channel_performance')}")
    perf_rows = []
    for ch in CHANNELS:
        ch_users = udf[udf['channel'] == ch]
        ch_trades = tdf[tdf['channel'] == ch]
        n_users = len(ch_users) * SCALE_FACTOR
        n_traders = ch_trades['user_id'].nunique() * SCALE_FACTOR
        vol = ch_trades['volume_usd'].sum() * SCALE_FACTOR
        fees = ch_trades['fee'].sum() * SCALE_FACTOR
        cac = CHANNEL_CAC[ch]
        conv = n_traders / n_users if n_users > 0 else 0
        perf_rows.append({
            'Channel': ch, 'Users': f"{n_users:,}", 'Traders': f"{n_traders:,}",
            'Volume (USD)': f"${vol:,.0f}", 'Fee Revenue': f"${fees:,.0f}",
            'CAC ($)': f"${cac:.0f}" if cac > 0 else "Free",
            'Conversion': f"{conv:.1%}",
        })
    st.dataframe(pd.DataFrame(perf_rows), use_container_width=True, hide_index=True)


def _show_retention(ret_df):
    """Retention sub-tab."""
    col1, col2 = st.columns(2)

    # Retention curve (average across cohorts)
    avg_retention = ret_df[['d1', 'd7', 'd14', 'd30']].mean()
    curve_df = pd.DataFrame({
        'Day': ['D0', 'D1', 'D7', 'D14', 'D30'],
        'Retention %': [100, avg_retention['d1'] * 100, avg_retention['d7'] * 100,
                        avg_retention['d14'] * 100, avg_retention['d30'] * 100]
    })
    with col1:
        fig = px.line(curve_df, x='Day', y='Retention %', markers=True,
                      title=t('retention_curve'),
                      color_discrete_sequence=['#00d4aa'])
        apply_dark_theme(fig)
        fig.update_layout(yaxis_range=[0, 105])
        st.plotly_chart(fig, use_container_width=True)

    # Cohort heatmap
    heatmap_vals = ret_df[['d1', 'd7', 'd14', 'd30']].values * 100
    with col2:
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_vals,
            x=['D1', 'D7', 'D14', 'D30'],
            y=ret_df['cohort'].values,
            colorscale='YlGn',
            text=np.round(heatmap_vals, 1),
            texttemplate="%{text}%",
            textfont={"size": 11},
        ))
        fig.update_layout(title=t('cohort_heatmap'), yaxis_title='Cohort', xaxis_title='Retention Day')
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Cohort table
    display_df = ret_df.copy()
    display_df['cohort_size'] = display_df['cohort_size'].apply(lambda x: f"{x * SCALE_FACTOR:,}")
    for col in ['d1', 'd7', 'd14', 'd30']:
        display_df[col] = display_df[col].apply(lambda x: f"{x * 100:.1f}%")
    display_df.columns = ['Cohort', 'Size', 'D1', 'D7', 'D14', 'D30']
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def _show_order_quality(ob_df, filters):
    """Order Quality sub-tab - execution metrics."""
    filtered_ob = ob_df[ob_df['coin'].isin(filters['coins'])]

    col1, col2 = st.columns(2)

    # Avg execution time trend
    exec_trend = filtered_ob.groupby('date')['avg_exec_time_ms'].mean().reset_index()
    with col1:
        fig = px.line(exec_trend, x='date', y='avg_exec_time_ms',
                      title=t('exec_time_trend'),
                      color_discrete_sequence=['#00b4d8'])
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Avg spread by coin
    spread_by_coin = filtered_ob.groupby('coin')['avg_spread_bps'].mean().reset_index().sort_values('avg_spread_bps')
    with col2:
        fig = px.bar(spread_by_coin, x='coin', y='avg_spread_bps',
                     title=t('spread_by_coin'),
                     color='avg_spread_bps', color_continuous_scale='RdYlGn_r')
        apply_dark_theme(fig)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Fill rate by coin
    fill_by_coin = filtered_ob.groupby('coin')['fill_rate'].mean().reset_index().sort_values('fill_rate', ascending=False)
    fig = px.bar(fill_by_coin, x='coin', y='fill_rate',
                 title=t('fill_rate'),
                 color_discrete_sequence=['#00d4aa'])
    apply_dark_theme(fig)
    fig.update_layout(yaxis_range=[0.94, 1.0], yaxis_tickformat='.1%')
    st.plotly_chart(fig, use_container_width=True)


def _show_real_time_prices():
    """Real-Time Prices sub-tab using CoinGecko API."""
    # Auto-refresh every 30 seconds
    if AUTOREFRESH_AVAILABLE:
        st_autorefresh(interval=30000, limit=None, key="price_refresh")

    prices, is_live = fetch_coingecko_prices()

    badge = '<span class="live-badge">LIVE</span>' if is_live else '<span class="demo-badge">DEMO</span>'
    st.markdown(f"### {t('real_time_prices')} {badge}", unsafe_allow_html=True)

    if not prices:
        st.warning("No price data available.")
        return

    # Build price table
    rows = []
    for coin in prices[:20]:
        symbol = coin.get('symbol', '').upper()
        price = coin.get('current_price', 0)
        ch_1h = coin.get('price_change_percentage_1h_in_currency', 0) or 0
        ch_24h = coin.get('price_change_percentage_24h_in_currency', 0) or 0
        ch_7d = coin.get('price_change_percentage_7d_in_currency', 0) or 0
        mcap = coin.get('market_cap', 0)
        vol = coin.get('total_volume', 0)
        rank = coin.get('market_cap_rank', '-')

        rows.append({
            t('rank'): rank,
            t('coin'): f"{coin.get('name', symbol)} ({symbol})",
            t('price'): f"${price:,.2f}" if price >= 1 else f"${price:,.4f}",
            t('change_1h'): f"{ch_1h:+.2f}%",
            t('change_24h'): f"{ch_24h:+.2f}%",
            t('change_7d'): f"{ch_7d:+.2f}%",
            t('market_cap'): f"${mcap / 1e9:.1f}B" if mcap >= 1e9 else f"${mcap / 1e6:.0f}M",
            t('volume_24h'): f"${vol / 1e9:.2f}B" if vol >= 1e9 else f"${vol / 1e6:.0f}M",
        })

    price_df = pd.DataFrame(rows)
    st.dataframe(price_df, use_container_width=True, hide_index=True)

    # Sparkline charts for top 6 coins
    st.markdown(f"### {t('sparkline')} - Top 6")
    spark_cols = st.columns(6)
    for i, coin in enumerate(prices[:6]):
        sparkline_data = coin.get('sparkline_in_7d', {}).get('price', [])
        if sparkline_data:
            with spark_cols[i]:
                symbol = coin.get('symbol', '').upper()
                ch_7d = coin.get('price_change_percentage_7d_in_currency', 0) or 0
                color = '#00d4aa' if ch_7d >= 0 else '#f85149'
                fig = go.Figure(go.Scatter(
                    y=sparkline_data, mode='lines',
                    line=dict(color=color, width=2),
                    fill='tozeroy', fillcolor=f"rgba({','.join(str(int(color.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))},0.1)"
                ))
                fig.update_layout(
                    title=dict(text=f"{symbol} ({ch_7d:+.1f}%)", font=dict(size=12)),
                    height=150, margin=dict(l=5, r=5, t=30, b=5),
                    xaxis=dict(visible=False), yaxis=dict(visible=False),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: NEWS & SENTIMENT
# Crypto news, VADER sentiment, LDA topic modeling
# CEX relevance: market intelligence, actionable insights
# ══════════════════════════════════════════════════════════════════════════════

def show_news_sentiment(filters):
    """Render News & Sentiment tab."""

    # Fetch news
    news_items, is_live_news = fetch_crypto_news(st.session_state.cryptopanic_token)
    sentiment_df = analyze_sentiment(news_items)

    badge = '<span class="live-badge">LIVE</span>' if is_live_news else '<span class="demo-badge">DEMO</span>'

    # ── News Table ──
    st.markdown(f"### {t('latest_news')} {badge}", unsafe_allow_html=True)

    if not sentiment_df.empty:
        display_news = sentiment_df[['title', 'source', 'published_at', 'sentiment_label', 'compound']].head(30).copy()
        display_news.columns = ['Title', 'Source', 'Published', 'Sentiment', 'Score']
        st.dataframe(display_news, use_container_width=True, hide_index=True)
    else:
        st.info("No news data available.")
        return

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Sentiment Gauges by Coin ──
    st.markdown(f"### {t('sentiment_gauges')}")

    # Explode coins column and aggregate
    sent_exploded = sentiment_df.explode('coins')
    coin_sentiment = sent_exploded.groupby('coins')['compound'].mean().reset_index()
    coin_sentiment = coin_sentiment[coin_sentiment['coins'].isin(COINS)]

    # Display gauges in 2 rows of 5
    gauge_coins = coin_sentiment.sort_values('coins')
    rows = [gauge_coins.iloc[:5], gauge_coins.iloc[5:10]] if len(gauge_coins) > 5 else [gauge_coins]

    for row_data in rows:
        cols = st.columns(min(5, len(row_data)))
        for idx, (_, row) in enumerate(row_data.iterrows()):
            with cols[idx]:
                score = row['compound']
                color = '#00d4aa' if score > 0.05 else ('#f85149' if score < -0.05 else '#f0883e')
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={'text': row['coins'], 'font': {'size': 14, 'color': '#e6edf3'}},
                    number={'font': {'size': 18, 'color': color}},
                    gauge=dict(
                        axis=dict(range=[-1, 1], tickcolor='#8b949e'),
                        bar=dict(color=color),
                        bgcolor='#161b22',
                        bordercolor='#30363d',
                        steps=[
                            dict(range=[-1, -0.3], color='rgba(248,81,73,0.2)'),
                            dict(range=[-0.3, 0.3], color='rgba(240,136,62,0.2)'),
                            dict(range=[0.3, 1], color='rgba(0,212,170,0.2)'),
                        ],
                    )
                ))
                fig.update_layout(height=180, margin=dict(l=20, r=20, t=40, b=10),
                                  paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e6edf3'))
                st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Sentiment Charts ──
    col1, col2 = st.columns(2)

    # Daily sentiment trend
    if 'published_at' in sentiment_df.columns:
        sent_copy = sentiment_df.copy()
        sent_copy['date'] = pd.to_datetime(sent_copy['published_at'], errors='coerce').dt.date
        daily_sent = sent_copy.groupby('date')['compound'].mean().reset_index()
        with col1:
            fig = px.line(daily_sent, x='date', y='compound',
                          title=t('sentiment_trend'),
                          color_discrete_sequence=['#00d4aa'])
            fig.add_hline(y=0, line_dash="dash", line_color="#8b949e")
            apply_dark_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

    # Sentiment distribution
    with col2:
        sent_dist = sentiment_df['sentiment_label'].value_counts().reset_index()
        sent_dist.columns = ['Sentiment', 'Count']
        fig = px.pie(sent_dist, values='Count', names='Sentiment',
                     title=t('sentiment_dist'),
                     color='Sentiment',
                     color_discrete_map={'Bullish': '#00d4aa', 'Neutral': '#f0883e', 'Bearish': '#f85149'})
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Sentiment by coin bar chart
    if not coin_sentiment.empty:
        coin_sentiment_sorted = coin_sentiment.sort_values('compound', ascending=True)
        colors = ['#00d4aa' if v > 0.05 else ('#f85149' if v < -0.05 else '#f0883e')
                  for v in coin_sentiment_sorted['compound']]
        fig = px.bar(coin_sentiment_sorted, x='compound', y='coins', orientation='h',
                     title=t('sentiment_by_coin'))
        fig.update_traces(marker_color=colors)
        fig.add_vline(x=0, line_dash="dash", line_color="#8b949e")
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Topic Modeling ──
    st.markdown(f"### {t('topic_modeling')}")

    if not SKLEARN_AVAILABLE:
        st.warning("scikit-learn not installed. Install with: pip install scikit-learn")
        return

    n_topics = st.slider(t('num_topics'), min_value=3, max_value=10, value=5, key="n_topics")

    texts = sentiment_df['title'].tolist()
    topics, doc_topics = run_topic_modeling(tuple(texts), n_topics=n_topics)

    if not topics:
        st.info("Not enough text data for topic modeling (need 10+ documents).")
        return

    # Top words per topic (bar charts in grid)
    st.markdown(f"#### {t('topic_words')}")
    n_cols = min(3, len(topics))
    for row_start in range(0, len(topics), n_cols):
        cols = st.columns(n_cols)
        for j in range(n_cols):
            topic_idx = row_start + j
            if topic_idx >= len(topics):
                break
            topic = topics[topic_idx]
            with cols[j]:
                tdf_topic = pd.DataFrame({'word': topic['words'], 'weight': topic['weights']})
                fig = px.bar(tdf_topic, x='weight', y='word', orientation='h',
                             title=topic['label'],
                             color_discrete_sequence=['#00b4d8'])
                apply_dark_theme(fig)
                fig.update_layout(height=300, yaxis=dict(autorange='reversed'))
                st.plotly_chart(fig, use_container_width=True)

    # Topic distribution
    if doc_topics is not None and len(doc_topics) > 0:
        topic_counts = doc_topics.argmax(axis=1)
        topic_dist = pd.Series(topic_counts).value_counts().sort_index().reset_index()
        topic_dist.columns = ['Topic', 'Documents']
        topic_dist['Topic'] = topic_dist['Topic'].apply(lambda x: f"Topic {x + 1}")

        fig = px.pie(topic_dist, values='Documents', names='Topic',
                     title=t('topic_dist'),
                     color_discrete_sequence=px.colors.qualitative.Set2)
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: BI AGENT
# Conversational BI using DeepSeek LLM
# CEX relevance: "actionable insights", "deep-dive analyses"
# ══════════════════════════════════════════════════════════════════════════════

def show_bi_agent(trades_df, users_df):
    """Render BI Agent tab with chat interface."""
    st.markdown(f"### {t('bi_agent_title')}")
    st.markdown(f"*{t('bi_agent_desc')}*")

    api_key = st.session_state.deepseek_api_key

    if not api_key:
        st.warning(t('no_api_key'))
        st.info("The BI Agent uses DeepSeek API to analyze exchange data and generate insights. "
                "Enter your API key in the sidebar under 'API Configuration'.")
        return

    if not OPENAI_AVAILABLE:
        st.error("OpenAI library not installed. Run: pip install openai")
        return

    # Quick-ask buttons
    st.markdown(f"#### {t('quick_ask')}")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    quick_questions = [
        "What's the top performing coin by volume?",
        "Analyze user retention trends",
        "Compare acquisition channel ROI",
        "What growth recommendations do you have?",
    ]

    quick_q = None
    with qcol1:
        if st.button(quick_questions[0], use_container_width=True):
            quick_q = quick_questions[0]
    with qcol2:
        if st.button(quick_questions[1], use_container_width=True):
            quick_q = quick_questions[1]
    with qcol3:
        if st.button(quick_questions[2], use_container_width=True):
            quick_q = quick_questions[2]
    with qcol4:
        if st.button(quick_questions[3], use_container_width=True):
            quick_q = quick_questions[3]

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Chat history display
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "chart" in msg and msg["chart"] is not None:
                st.plotly_chart(msg["chart"], use_container_width=True)

    # Chat input
    user_input = st.chat_input(t('agent_placeholder'))
    if quick_q:
        user_input = quick_q

    if user_input:
        # Display user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get LLM response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing exchange data..."):
                context = build_data_context(trades_df, users_df)
                response, success = query_deepseek(user_input, context, api_key)

            st.markdown(response)

            # Try to extract and render chart
            chart = try_execute_plotly_code(response)
            if chart:
                st.plotly_chart(chart, use_container_width=True)

            st.session_state.chat_history.append({
                "role": "assistant", "content": response, "chart": chart
            })


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Main application entry point."""
    if not st.session_state.authenticated:
        authenticate()
        return

    # Header
    st.markdown('<div class="main-header">Web3 BI Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">CEX Growth Insights | Data Analytics Platform</div>', unsafe_allow_html=True)

    # Sidebar
    filters = show_sidebar()

    # Load data
    trades_df = load_trades_data(days=30)
    users_df = load_users_data()

    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        f"📊 {t('tab_metrics')}",
        f"📰 {t('tab_sentiment')}",
        f"🤖 {t('tab_agent')}",
    ])

    with tab1:
        show_core_metrics(trades_df, users_df, filters)

    with tab2:
        show_news_sentiment(filters)

    with tab3:
        show_bi_agent(trades_df, users_df)

    # Footer
    st.markdown("---")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        st.caption(f"{t('data_source')}: Demo Data + CoinGecko API")
    with fc2:
        st.caption(f"{t('last_updated')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with fc3:
        st.caption("Built for Data Analyst Interview")


if __name__ == "__main__":
    main()

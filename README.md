# BI Analytics Platform Demo

> 🌐 [中文版本](#中文说明) | English (Default)

A comprehensive Business Intelligence Analytics Platform demo built with **Streamlit**, designed to showcase enterprise-grade BI capabilities for client presentations.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python) ![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit) ![Plotly](https://img.shields.io/badge/Plotly-Interactive-green?logo=plotly) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## ✨ Features

| Module | Description |
|---|---|
| 📈 **Daily** | Hourly traffic, session KPIs, real trend deltas |
| 📊 **Weekly** | Week-over-week comparisons, conversion tracking |
| 📅 **Monthly** | MAU growth, page views, month-over-month trends |
| 💰 **Monetization** | Revenue, MRR, ARPU, product breakdown |
| 👥 **Acquisition** | Channel performance, CPA, organic vs paid share |
| 🔄 **Retention** | Cohort analysis, retention curves, day 1/7/30/90 |
| 🔧 **Custom SQL** | Query editor with syntax validation & mock execution |

**Platform highlights:**
- 🔐 Demo login system (`admin` / `password`)
- 🗄️ Multi data source selector (PostgreSQL, MySQL, BigQuery, SQLite)
- 📊 Plotly interactive charts throughout
- 🔍 Date range, region, platform & device filters
- ⚡ Streamlit caching for fast load times
- 📱 Responsive layout for desktop & mobile

---

## 🚀 Quick Start

### Prerequisites
- Python **3.8+**
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager *(recommended)*

### Install & Run

```bash
# 1. Clone the repo
git clone https://github.com/lenzyh/bi_analytics.git
cd bi_analytics

# 2. Install dependencies
uv sync

# 3. Launch the app
uv run streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) and log in with `admin` / `password`.

### Alternative (pip)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Project Structure

```
bi_analytics/
├── app.py               # Main Streamlit application
├── run_demo.py          # CLI launcher script
├── pyproject.toml       # Project config (uv)
├── requirements.txt     # Dependencies (pip fallback)
├── uv.lock              # Dependency lock file
├── .python-version      # Python version pin
├── .streamlit/
│   └── config.toml      # Streamlit server config
└── README.md
```

---

## 🛠️ Tech Stack

- **[Streamlit](https://streamlit.io/)** — Web app framework
- **[Plotly](https://plotly.com/python/)** — Interactive visualizations
- **[Pandas](https://pandas.pydata.org/)** — Data manipulation
- **[NumPy](https://numpy.org/)** — Numerical computation
- **[Faker](https://faker.readthedocs.io/)** — Realistic mock data

---

## 📊 Demo Data

All data is synthetically generated with a fixed seed (`numpy.random.default_rng(42)`) for **reproducibility**:

- 30 days of daily session data with realistic weekday/weekend patterns
- 90 days of revenue, transactions, and ARPU metrics
- Multi-channel user acquisition with costs and conversion rates
- 6-month cohort retention data (Day 1 / 7 / 30 / 90)
- 24-hour traffic distribution simulating real usage peaks

---

## 🔒 Security

- Only `SELECT` queries permitted in the SQL editor
- Input validation on all query submissions
- Authentication gate before any dashboard access
- Role-based access control (simulated)

---

## 🎨 Customisation

This demo is built to be easily adapted:

- **Branding** — swap colours, fonts, logos in `app.py` CSS block
- **Data sources** — replace mock generators with real DB connectors
- **Metrics** — add custom KPIs per business domain
- **Charts** — extend with Plotly chart types as needed

---

## 📞 Next Steps

1. Custom implementation tailored to your data sources
2. Real database integration (PostgreSQL / BigQuery / Snowflake)
3. SSO / OAuth authentication
4. Cloud deployment (AWS / GCP / Azure)
5. AI/ML predictive analytics layer

---

## 🔑 Demo Credentials

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `password` |

---

---

# 中文说明

> 🌐 [English Version](#bi-analytics-platform-demo) | 中文（说明）

基于 **Streamlit** 构建的商业智能分析平台演示项目，适用于客户演示和 BI 能力展示。

---

## ✨ 功能模块

| 模块 | 说明 |
|---|---|
| 📈 **每日分析** | 小时级流量、会话 KPI、真实环比变化 |
| 📊 **每周分析** | 周同比对比、转化率跟踪 |
| 📅 **每月分析** | MAU 增长、页面浏览量、月同比趋势 |
| 💰 **变现分析** | 营收、MRR、ARPU、产品收入拆解 |
| 👥 **用户获取** | 渠道表现、获客成本、自然/付费占比 |
| 🔄 **用户留存** | 队列分析、留存曲线、第 1/7/30/90 天留存率 |
| 🔧 **自定义 SQL** | SQL 编辑器，支持语法校验与模拟执行 |

**平台亮点：**
- 🔐 演示登录系统（`admin` / `password`）
- 🗄️ 多数据源选择（PostgreSQL、MySQL、BigQuery、SQLite）
- 📊 全页面使用 Plotly 交互图表
- 🔍 日期范围、地区、平台、设备筛选器
- ⚡ Streamlit 缓存加速加载
- 📱 响应式布局，支持桌面与移动端

---

## 🚀 快速开始

### 环境要求
- Python **3.8+**
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) 包管理器（推荐）

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/lenzyh/bi_analytics.git
cd bi_analytics

# 2. 安装依赖
uv sync

# 3. 启动应用
uv run streamlit run app.py
```

打开 [http://localhost:8501](http://localhost:8501)，使用 `admin` / `password` 登录。

### 备选方式（pip）

```bash
python -m venv .venv
# Windows：
.venv\Scripts\activate
# macOS/Linux：
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 项目结构

```
bi_analytics/
├── app.py               # Streamlit 主应用
├── run_demo.py          # 命令行启动脚本
├── pyproject.toml       # 项目配置（uv）
├── requirements.txt     # 依赖列表（pip 备用）
├── uv.lock              # 依赖锁定文件
├── .python-version      # Python 版本指定
├── .streamlit/
│   └── config.toml      # Streamlit 服务器配置
└── README.md
```

---

## 🛠️ 技术栈

- **Streamlit** — Web 应用框架
- **Plotly** — 交互式数据可视化
- **Pandas** — 数据处理
- **NumPy** — 数值计算
- **Faker** — 真实感模拟数据生成

---

## 📊 演示数据说明

所有数据均为合成数据，使用固定随机种子（`numpy.random.default_rng(42)`）生成，确保**结果可复现**：

- 30 天每日会话数据，含工作日/周末真实波动
- 90 天营收、交易量、ARPU 指标
- 多渠道用户获取数据（含成本与转化率）
- 6 个月队列留存数据（第 1/7/30/90 天）
- 24 小时流量分布，模拟真实使用高峰

---

## 🔒 安全说明

- SQL 编辑器仅允许 `SELECT` 查询
- 所有查询提交均进行输入校验
- 仪表盘访问前设有登录验证门控
- 模拟基于角色的权限控制

---

## 🎨 自定义说明

本项目易于按需定制：

- **品牌** — 修改 `app.py` CSS 区块中的颜色、字体、Logo
- **数据源** — 将模拟数据生成器替换为真实数据库连接
- **指标** — 按业务域添加自定义 KPI
- **图表** — 按需扩展 Plotly 图表类型

---

## 🔑 演示登录信息

| 字段 | 值 |
|---|---|
| 用户名 | `admin` |
| 密码 | `password` |
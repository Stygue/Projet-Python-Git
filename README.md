# Crypto Quant Dashboard

Advanced quantitative analysis, backtesting, and AI prediction platform for cryptocurrency assets.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Modules](#modules)
- [API & Data](#api--data)
- [Technologies](#technologies)
- [Authors](#authors)

---

## 🎯 Overview

This project is a comprehensive cryptocurrency analysis platform built with Python and Streamlit. It provides two main analytical modules:

- **Quant A**: Single-asset technical analysis with AI-powered price prediction
- **Quant B**: Multi-asset portfolio management with rebalancing strategies

The application fetches real-time data from the CoinGecko API and offers interactive visualizations, backtesting capabilities, and machine learning forecasts.

---

## ✨ Features

### Quant A: Crypto Analysis
- Real-time price tracking with 24h change indicators
- Multiple timeframe analysis (7 days to Max history)
- Trading strategy backtesting:
  - Buy & Hold
  - SMA Crossover (Momentum)
  - RSI Mean Reversion
- Performance metrics: Total Return, Volatility, Sharpe Ratio, Max Drawdown
- **Advanced AI Forecasting** using Random Forest Regressor:
  - Feature engineering (lags, volatility, momentum)
  - Directional accuracy metrics
  - Visual backtest analysis
  - Feature importance analysis

### Quant B: Portfolio Manager
- Multi-asset portfolio construction (minimum 3 assets)
- Customizable weight allocation with price weighting
- Dynamic rebalancing strategies:
  - Buy & Hold
  - Daily, Weekly, or Monthly rebalancing
- Portfolio metrics: Annualized Return, Volatility, Sharpe Ratio
- Correlation matrix for risk diversification analysis
- Coin quantity tracking to visualize rebalancing impact
- Interactive performance comparison charts

### General Features
- **Auto-refresh**: Data updates every 5 minutes with visual countdown
- **Caching system**: Optimized API calls to respect rate limits
- **Interactive charts**: Zoom, pan, and hover for detailed insights
- **Responsive UI**: Clean, modern interface with dark mode support

---

## 📁 Project Structure

```
project/
│
├── app.py                          # Main application entry point
│
├── data_handling/
│   ├── api_connector.py            # CoinGecko API wrapper
│   └── caching.py                  # Streamlit caching layer
│
├── quant_a/
│   ├── __init__.py
│   ├── ui.py                       # Quant A dashboard UI
│   ├── strategies.py               # Trading strategy implementations
│   ├── metrics.py                  # Performance calculation functions
│   └── prediction.py               # Machine Learning prediction model
│
├── quant_b/
│   ├── frontend_b.py               # Quant B dashboard UI
│   └── portfolio_logic.py          # Portfolio calculation & rebalancing logic
│
└── requirements.txt                # Python dependencies
```



## 💡 Usage

### Home Page
- View real-time market pulse for Bitcoin, Ethereum, and Solana
- Check API connection status
- Read module guides and navigate to analysis tools

### Quant A Workflow
1. Select an asset (Bitcoin, Ethereum, or Solana) from the sidebar
2. Choose a historical timeframe
3. Pick a trading strategy and adjust parameters
4. Analyze the performance chart (dual Y-axis: Price vs Strategy Return)
5. Review performance metrics
6. Click "Run AI Analysis" to generate ML-based forecasts

### Quant B Workflow
1. Select at least 3 assets for your portfolio
2. Choose a historical period (90 days to 2 years)
3. Adjust weight sliders to define target allocation (must sum to 100%)
4. Select a rebalancing frequency
5. Analyze cumulative performance vs individual assets
6. Review the correlation matrix for diversification insights
7. Observe coin quantity evolution to understand rebalancing mechanics

---

## 🔧 Modules

### `api_connector.py`
Handles all HTTP requests to the CoinGecko API.

**Key Functions:**
- `get_historical_data(coin_id, days)`: Fetches OHLC price history
- `get_current_price(coin_id)`: Retrieves current price + 24h change for a single asset
- `get_current_prices_batch(coin_ids)`: Batch request for multiple assets (optimized)

**Error Handling:**
- Rate limit detection (HTTP 429) with automatic retry
- Graceful fallback for missing data

---

### `caching.py`
Implements Streamlit's `@st.cache_data` decorator to minimize API calls.

**Cache TTL:**
- Historical data: 10 minutes
- Current prices: 1 minute

---

### `strategies.py`
Contains backtesting logic for trading strategies.

**Implemented Strategies:**
- **Buy & Hold**: Baseline strategy (no trading)
- **SMA Crossover**: Momentum-based (buy when short SMA > long SMA)
- **RSI Mean Reversion**: Contrarian strategy (buy oversold, sell overbought)

**Key Concept:** All strategies shift signals by 1 day to avoid look-ahead bias.

---

### `metrics.py`
Calculates financial performance indicators.

**Metrics:**
- **Total Return**: (End Price - Start Price) / Start Price
- **Volatility**: Annualized standard deviation of returns
- **Sharpe Ratio**: Risk-adjusted return (assuming 0% risk-free rate)
- **Max Drawdown**: Largest peak-to-trough decline

**Robustness:** Handles division by zero, NaN values, and both price/return inputs.

---

### `prediction.py`
Advanced machine learning forecasting using Random Forest.

**Features Engineered:**
- Lagged returns (1, 2, 3, 5 days)
- Rolling volatility (5-day window)
- Distance to Simple Moving Average (momentum proxy)

**Model Details:**
- Target: Log returns (stationary data)
- Training: TimeSeriesSplit (no look-ahead bias)
- Evaluation: RMSE + Directional Accuracy

**Output:**
- Next-day price prediction
- Confidence score (directional accuracy)
- Feature importance chart
- Actual vs Predicted backtest visualization

---

### `portfolio_logic.py`
Core portfolio management calculations.

**Key Functions:**
- `load_multi_asset_data()`: Synchronizes price data across assets
- `calculate_portfolio_metrics()`: Computes return, volatility, Sharpe, correlation
- `calculate_rebalanced_portfolio_with_quantities()`: Simulates rebalancing with coin tracking

**Rebalancing Logic:**
- Periodically resets portfolio weights to target allocation
- Sells outperformers, buys underperformers
- Tracks exact coin quantities held over time

---

## 🌐 API & Data

**Data Source:** [CoinGecko API](https://www.coingecko.com/en/api) (Free tier)

**Rate Limits:**
- ~50 calls/minute (enforced by the API)
- Application uses caching to stay within limits

**Supported Assets:**
- Bitcoin (BTC)
- Ethereum (ETH)
- Solana (SOL)
- Cardano (ADA)
- Polkadot (DOT)

**Data Points:**
- Historical OHLC prices
- Current spot prices
- 24-hour percentage change

---

## 🛠 Technologies

**Core:**
- Python 3.8+
- Streamlit (UI framework)
- Pandas (data manipulation)
- NumPy (numerical computing)

**Visualization:**
- Plotly (interactive charts)

**Machine Learning:**
- scikit-learn (Random Forest, metrics)

**API:**
- Requests (HTTP client)

**Utilities:**
- streamlit-autorefresh (auto-update)

---

## 👥 Authors

**MEHAH Grégoire** - Developer  
**PAGNIEZ David** - Developer

*Python for Finance Project | 2025*

---

## 📝 License

This project is for educational purposes as part of a university finance course.

---

## 🙏 Acknowledgments

- CoinGecko for providing free cryptocurrency data
- Streamlit community for excellent documentation
- scikit-learn for robust ML tools

---

**💡 Pro Tip:** Use the interactive legend on charts! Click to hide/show elements, double-click to isolate a single trace.
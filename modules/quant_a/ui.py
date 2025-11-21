import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Import data fetching (CoinGecko)
from data_handling.caching import get_cached_historical_data, get_cached_current_price

# Import logic modules
from quant_a.strategies import apply_buy_and_hold, apply_sma_crossover
from quant_a.metrics import get_performance_summary
from quant_a.prediction import PricePredictor

def render_quant_a_dashboard():
    """
    Main function to render the Single Asset Analysis (Quant A) dashboard.
    """
    st.header("🦄 Single Asset Analysis (Quant A)")
    st.markdown("Analyze individual crypto assets, backtest strategies, and predict future prices.")

    # --- 1. Sidebar Controls ---
    st.sidebar.subheader("Asset Selection")
    
    # The specific assets you requested
    asset_options = {
        "Bitcoin": "bitcoin",
        "Ethereum": "ethereum",
        "Solana": "solana"
    }
    
    selected_asset_name = st.sidebar.selectbox("Select Asset", list(asset_options.keys()))
    coin_id = asset_options[selected_asset_name]

        # Timeframe selection
    days_options = {"7 Days": "7", "30 Days": "30", "90 Days": "90", "1 Year": "365", "Max": "max"}
    selected_days_label = st.sidebar.selectbox("Timeframe", list(days_options.keys()), index=1)
    days = days_options[selected_days_label]

    # --- 2. Data Retrieval (CoinGecko API) ---
    with st.spinner(f"Fetching data for {selected_asset_name}..."):
        # This calls your caching.py -> api_connector.py -> CoinGecko
        df = get_cached_historical_data(coin_id, days)
        current_price = get_cached_current_price(coin_id)

    if df is None or df.empty:
        st.error("Error fetching data. Please try again later or check API limits.")
        return

    # Display Current Price
    st.metric(label=f"{selected_asset_name} Price (USD)", value=f"${current_price:,.2f}")

    # --- 3. Strategy Selection & Backtesting ---
    st.subheader("Strategy Backtesting")
    strategy_type = st.radio("Choose Strategy", ["Buy & Hold", "SMA Crossover (Momentum)"], horizontal=True)

    if strategy_type == "Buy & Hold":
        df_processed = apply_buy_and_hold(df)
        strategy_col = 'cum_return_bh'
        st.info("Strategy: Simply buying the asset at the start and holding it.")
        
    elif strategy_type == "SMA Crossover (Momentum)":
        short_w = st.slider("Short Window (Days)", 5, 50, 10)
        long_w = st.slider("Long Window (Days)", 20, 200, 30)
        
        df_processed = apply_sma_crossover(df, short_w, long_w)
        strategy_col = 'cum_return_sma'
        st.info(f"Strategy: Buy when SMA({short_w}) > SMA({long_w}).")

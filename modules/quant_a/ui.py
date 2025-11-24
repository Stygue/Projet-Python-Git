import streamlit as st
import plotly.graph_objects as go
from quant_a.strategies import apply_buy_and_hold, apply_sma_crossover, apply_rsi_strategy
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
    
    strategy_type = st.radio(
        "Choose Strategy", 
        ["Buy & Hold", "SMA Crossover (Momentum)", "RSI Mean Reversion"], 
        horizontal=True
    )

    if strategy_type == "Buy & Hold":
        df_processed = apply_buy_and_hold(df)
        strategy_col = 'cum_return_bh'
        st.info("Strategy: Simply buying the asset at the start and holding it.")
        
    elif strategy_type == "SMA Crossover (Momentum)":
        c1, c2 = st.columns(2)
        short_w = c1.slider("Short Window (Days)", 5, 50, 10)
        long_w = c2.slider("Long Window (Days)", 20, 200, 30)
        
        df_processed = apply_sma_crossover(df, short_w, long_w)
        strategy_col = 'cum_return_sma'
        st.info(f"Strategy: Buy when SMA({short_w}) > SMA({long_w}). Trend Following.")

    elif strategy_type == "RSI Mean Reversion":
        c1, c2, c3 = st.columns(3)
        rsi_window = c1.slider("RSI Window", 5, 30, 14)
        lower_bound = c2.slider("Oversold (< Buy)", 10, 40, 30)
        upper_bound = c3.slider("Overbought (> Sell)", 60, 90, 70)
        
        df_processed = apply_rsi_strategy(df, rsi_window, lower_bound, upper_bound)
        strategy_col = 'cum_return_rsi'
        st.info(f"Strategy: Buy when RSI < {lower_bound}, Sell when RSI > {upper_bound}. Contrarian.")

 # --- 4. Visualization (Main Chart) ---
    fig = go.Figure()

    # Plot Raw Price (normalized to start at 1 for comparison) or pure price?
    # The prompt asks to show raw asset price AND cumulative value of strategy.
    # To make them comparable on the same chart, it's often better to use dual axis or normalize.
    # Let's use Dual Axis: Left = Price, Right = Strategy Performance
    
    # Trace 1: Asset Price
    fig.add_trace(go.Scatter(
        x=df_processed.index, 
        y=df_processed['price'], 
        mode='lines', 
        name=f'{selected_asset_name} Price',
        line=dict(color='blue')
    ))

    # Trace 2: Strategy Performance (Cumulative Return)
    # We scale it to match the price starting point for visual comparison
    start_price = df_processed['price'].iloc[0]
    scaled_strategy = df_processed[strategy_col] * start_price

    fig.add_trace(go.Scatter(
        x=df_processed.index, 
        y=scaled_strategy, 
        mode='lines', 
        name=f'Strategy Value ({strategy_type})',
        line=dict(color='green', dash='dot')
    ))

    fig.update_layout(
        title=f"Price vs Strategy Performance ({selected_days_label})",
        xaxis_title="Date",
        yaxis_title="Value (USD)",
        legend=dict(x=0, y=1),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 5. Performance Metrics ---
    st.subheader("Performance Metrics")
    
    # Calculate metrics based on the strategy returns
    # Note: For Buy&Hold, we use raw returns. For SMA, we use 'strategy_returns'
    metric_col_input = 'returns' if strategy_type == "Buy & Hold" else 'strategy_returns'
    
    metrics = get_performance_summary(df_processed, metric_col_input)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Return", f"{metrics['Total Return']:.2%}")
    c2.metric("Volatility (Ann.)", f"{metrics['Volatility']:.2%}")
    c3.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
    c4.metric("Max Drawdown", f"{metrics['Max Drawdown']:.2%}")

    # --- 6. Bonus: ML Prediction ---
    st.markdown("---")
    st.subheader("🔮 AI Price Prediction (Bonus)")
    
    if st.button("Predict Next Day Price"):
        predictor = PricePredictor(df)
        predicted_price, score = predictor.train_and_predict()
        
        if predicted_price:
            col_pred1, col_pred2 = st.columns(2)
            col_pred1.metric("Predicted Price (Tomorrow)", f"${predicted_price:,.2f}")
            col_pred2.metric("Model Confidence (R²)", f"{score:.2f}")
            
            if score < 0.5:
                st.warning("Warning: Model confidence is low. Market is volatile.")
            else:
                st.success("Model fit is reasonable.")
        else:
            st.warning("Not enough data to make a prediction.")
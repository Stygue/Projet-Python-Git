import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from quant_b.portfolio_logic import (
    load_multi_asset_data,
    calculate_portfolio_metrics,
    calculate_portfolio_performance_series,
    calculate_individual_cumulative_returns,
    calculate_rebalanced_portfolio_with_quantities, # Assure-toi de l'ajouter dans portfolio_logic.py
    SUPPORTED_ASSETS
)

def render_quant_b_dashboard():
    """
    Renders the complete Quant B Portfolio Management Dashboard with Rebalancing logic.
    """
    st.title("💼 Quant B: Multi-Asset Portfolio Manager")
    st.subheader("Simulate, analyze, and visualize multi-asset crypto portfolio performance.")

    # --- 1. USER CONTROLS (SIDEBAR) ---
    with st.sidebar.expander("⚙️ Simulation & Strategy", expanded=True):
        
        selected_assets_names = st.multiselect(
            "Select Assets (minimum 3 required):",
            options=list(SUPPORTED_ASSETS.keys()),
            default=list(SUPPORTED_ASSETS.keys())[:3]
        )
        
        days_to_fetch = st.selectbox(
            "Historical Period:",
            options=["90", "180", "365", "730"],
            index=2 
        )
        
        risk_free_rate = st.number_input(
            "Annual Risk-Free Rate (e.g., 0.02 for 2%)",
            min_value=0.0, max_value=0.1, value=0.02, step=0.005, format="%.4f"
        )

        st.markdown("---")
        st.markdown("#### 🔄 Rebalancing Strategy")
        rebalance_freq = st.selectbox(
            "Rebalancing Frequency:",
            options=["None (Buy & Hold)", "Daily", "Weekly", "Monthly"],
            index=2,
            help="How often the portfolio resets to target weights (Price Weighting strategy)."
        )
        
    # --- 2. VALIDATION ---
    if len(selected_assets_names) < 3:
        st.warning("Please select at least 3 assets for multi-asset portfolio analysis.")
        return

    asset_ids = [SUPPORTED_ASSETS[name] for name in selected_assets_names]

    # --- 3. WEIGHTS ALLOCATION ---
    st.markdown("### ⚖️ Portfolio Allocation (Price Weighting)")
    st.info("💡 **Tip:** Adjust sliders to define your target weights. The strategy will buy/sell assets to maintain these proportions.")
    
    cols = st.columns(len(asset_ids))
    default_weight_value = 100 / len(selected_assets_names)
    weights = []
    
    def set_equal_weights():
        equal_weight = 100 / len(selected_assets_names)
        for name in selected_assets_names:
            st.session_state[f"weight_slider_{name}"] = equal_weight

    for i, name in enumerate(selected_assets_names):
        if f"weight_slider_{name}" not in st.session_state:
            st.session_state[f"weight_slider_{name}"] = default_weight_value
            
        with cols[i]:
            weight = st.slider(
                name, min_value=0.0, max_value=100.0,
                value=st.session_state[f"weight_slider_{name}"],
                step=0.01, key=f"weight_slider_{name}"
            )
            weights.append(weight / 100)
            
    weights_sum = sum(weights) * 100
    if weights_sum < 99.99 or weights_sum > 100.01:
        st.error(f"The sum of weights must equal 100%. Current sum: {weights_sum:.2f}%")
        st.button("Distribute Weights Equally", on_click=set_equal_weights)
        return
        
    # --- 4. DATA LOADING ---
    with st.spinner("Loading and synchronizing data..."):
        price_df = load_multi_asset_data(asset_ids, days_to_fetch)

    if price_df is None or price_df.empty:
        st.error("Could not load data. Check API status.")
        return

    # --- 5. CALCULATIONS (REBALANCING LOGIC) ---
    freq_map = {"None (Buy & Hold)": None, "Daily": "D", "Weekly": "W", "Monthly": "M"}
    freq_code = freq_map[rebalance_freq]

    # Simulation avec suivi des quantités
    portfolio_cumulative, amounts_df = calculate_rebalanced_portfolio_with_quantities(
        price_df, weights, frequency=freq_code
    )

    metrics = calculate_portfolio_metrics(price_df, weights, risk_free_rate)
    if metrics is None:
        st.error("❌ ERROR: Failed to calculate metrics.")
        return

    individual_cumulative = calculate_individual_cumulative_returns(price_df)

    # --- 6. METRICS DISPLAY ---
    st.markdown("---")
    st.markdown("### 📈 Performance Metrics")
    st.caption(f"Strategy: {rebalance_freq}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Annualized Return", f"{metrics['Annual Return (%)']:.2f}%")
    col2.metric("Annual Volatility (Risk)", f"{metrics['Annual Volatility (%)']:.2f}%")
    col3.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
    
    # --- 7. MAIN CHART ---
    st.markdown("### 📊 Cumulative Performance (Asset vs. Portfolio)")
    st.info("💡 **Interactive Graph:** Click legend names to hide/show curves. Double-click to isolate the Portfolio.")
    
    plot_df = individual_cumulative.copy()
    # On normalise la valeur du portfolio à 1.0 au début pour la comparaison
    plot_df['Portfolio'] = portfolio_cumulative / portfolio_cumulative.iloc[0]
    plot_df.index.name = 'Date'
    
    plot_long = plot_df.reset_index().melt(id_vars='Date', var_name='Asset/Portfolio', value_name='Cumulative Value')
    
    fig = px.line(plot_long, x='Date', y='Cumulative Value', color='Asset/Portfolio',
                 title=f"Performance Comparison (Rebalancing: {rebalance_freq})")
    
    fig.update_traces(line=dict(width=4), selector=dict(name='Portfolio'))
    st.plotly_chart(fig, width='stretch') 

    # --- 8. QUANTITY TRACKING CHART ---
    st.markdown("---")
    st.markdown("### 🪙 Evolution of Coin Quantities (Rebalancing Impact)")
    st.write("This chart visualizes how many 'units' of each coin you hold. In a Buy & Hold strategy, these stay flat. With rebalancing, you sell winners and buy losers.")
    
    

    # Normalisation pour voir la variation relative des quantités (Base 100)
    amounts_norm = (amounts_df / amounts_df.iloc[0]) * 100
    
    fig_amounts = px.line(amounts_norm, title="Relative Quantity of Coins Held (Base 100)",
                         labels={"value": "Quantity Index", "variable": "Asset"})
    
    st.plotly_chart(fig_amounts, width='stretch')

    # --- 9. CORRELATION MATRIX ---
    st.markdown("---")
    st.markdown("### 🤝 Correlation Matrix")
    st.markdown(metrics['Correlation Matrix'], unsafe_allow_html=True)
    
    st.caption("The 'Quant B' module simulates price-weighted portfolios with dynamic rebalancing rules.")
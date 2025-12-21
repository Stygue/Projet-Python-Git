import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.quant_b.portfolio_logic import (
    load_multi_asset_data,
    calculate_portfolio_metrics,
    calculate_portfolio_performance_series,
    calculate_individual_cumulative_returns,
    calculate_rebalanced_portfolio, # Nouvelle fonction à importer
    SUPPORTED_ASSETS
)

# --- QUANT B DASHBOARD RENDERING FUNCTION ---
def render_quant_b_dashboard():
    """
    Renders the complete Quant B Portfolio Management Dashboard.
    """
    st.title("💼 Quant B: Multi-Asset Portfolio Manager")
    st.subheader("Simulate, analyze, and visualize multi-asset crypto portfolio performance.")

    # --- 1. USER CONTROLS (SIDEBAR) ---
    with st.sidebar.expander("⚙️ Simulation Parameters", expanded=True):
        
        # Asset Selection (Project requires min. 3 assets)
        selected_assets_names = st.multiselect(
            "Select Assets (minimum 3 required):",
            options=list(SUPPORTED_ASSETS.keys()),
            default=list(SUPPORTED_ASSETS.keys())[:3]
        )
        
        # Historical Period
        days_to_fetch = st.selectbox(
            "Historical Period:",
            options=["90", "180", "365", "730"],
            index=2 
        )
        
        # Risk-Free Rate
        risk_free_rate = st.number_input(
            "Annual Risk-Free Rate (e.g., 0.02 for 2%)",
            min_value=0.0,
            max_value=0.1,
            value=0.02,
            step=0.005,
            format="%.4f"
        )

        st.markdown("---")
        st.markdown("#### 🔄 Rebalancing Strategy")
        
        # Ajout du paramètre de fréquence de rebalancement demandé par le prof
        rebalance_freq = st.selectbox(
            "Rebalancing Frequency:",
            options=["None (Buy & Hold)", "Daily", "Weekly", "Monthly"],
            index=2,
            help="Determine how often the portfolio is re-aligned to target weights."
        )
        
    # --- 2. VALIDATION ---
    if len(selected_assets_names) < 3:
        st.warning("Please select at least 3 assets for multi-asset portfolio analysis.")
        return

    # Map display names to API IDs
    asset_ids = [SUPPORTED_ASSETS[name] for name in selected_assets_names]

    # --- 3. WEIGHTS ALLOCATION ---
    st.markdown("### ⚖️ Portfolio Allocation")
    
    # Setup columns for weight sliders
    cols = st.columns(len(asset_ids))
    default_weight_value = 100 / len(selected_assets_names)
    weights = []
    
    # --- Fonction de Callback pour le bouton 'Equal Weights' ---
    def set_equal_weights():
        """Met à jour st.session_state pour tous les sliders avec un poids égal."""
        equal_weight = 100 / len(selected_assets_names)
        for name in selected_assets_names:
            st.session_state[f"weight_slider_{name}"] = equal_weight

    st.write("Adjust allocation weights (in %) :")
    for i, name in enumerate(selected_assets_names):
        # Initialisation du session_state si non défini
        if f"weight_slider_{name}" not in st.session_state:
            st.session_state[f"weight_slider_{name}"] = default_weight_value
            
        with cols[i]:
            weight = st.slider(
                name,
                min_value=0.0,
                max_value=100.0,
                value=st.session_state[f"weight_slider_{name}"],
                step=0.01,
                key=f"weight_slider_{name}"
            )
            weights.append(weight / 100)
            
    # Check if weights sum to 100%
    weights_sum = sum(weights) * 100
    if weights_sum < 99.99 or weights_sum > 100.01:
        st.error(f"The sum of weights must equal 100%. Current sum: {weights_sum:.2f}%")
        st.button("Distribute Weights Equally", on_click=set_equal_weights)
        return
        
    # --- 4. DATA LOADING AND INITIALIZATION ---
    
    with st.spinner(f"Loading and synchronizing data for {len(asset_ids)} assets..."):
        price_df = load_multi_asset_data(asset_ids, days_to_fetch)

    if price_df is None or price_df.empty:
        st.error("Could not load data. Check API status or the selected time period.")
        return

    # --- 4.1 LOGIQUE DE REBALANCEMENT ---
    # Conversion de la sélection UI en code de fréquence pandas
    freq_map = {"None (Buy & Hold)": None, "Daily": "D", "Weekly": "W", "Monthly": "M"}
    freq_code = freq_map[rebalance_freq]

    # Calcul de la performance cumulative avec ou sans rebalancement
    if freq_code:
        portfolio_cumulative = calculate_rebalanced_portfolio(price_df, weights, freq_code)
    else:
        portfolio_cumulative = calculate_portfolio_performance_series(price_df, weights)

    # Calcul des métriques et des rendements individuels
    metrics = calculate_portfolio_metrics(price_df, weights, risk_free_rate)
    
    if metrics is None:
        st.error("❌ ERROR: Failed to calculate portfolio metrics.")
        return

    individual_cumulative = calculate_individual_cumulative_returns(price_df)

    # --- 5. KEY METRICS DISPLAY ---
    st.markdown("---")
    st.markdown("### 📈 Performance Metrics")
    
    if freq_code:
        st.caption(f"Strategy: Periodic Rebalancing ({rebalance_freq})")
    else:
        st.caption("Strategy: Buy & Hold (No rebalancing)")

    col1, col2, col3 = st.columns(3)
    col1.metric("Annualized Return", f"{metrics['Annual Return (%)']:.2f}%")
    col2.metric("Annual Volatility (Risk)", f"{metrics['Annual Volatility (%)']:.2f}%")
    col3.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
    
    st.markdown("---")
    
    # --- 6. MAIN CHART (ASSET VS. PORTFOLIO) ---
    st.markdown("### 📊 Cumulative Performance (Asset vs. Portfolio)")
    
    plot_df = individual_cumulative.copy()
    plot_df['Portfolio'] = portfolio_cumulative
    plot_df.index.name = 'Date'
    
    plot_long = plot_df.reset_index().melt(
        id_vars='Date', 
        var_name='Asset/Portfolio', 
        value_name='Cumulative Value'
    )
    
    fig = px.line(
        plot_long, 
        x='Date', 
        y='Cumulative Value', 
        color='Asset/Portfolio',
        title=f"Performance Evolution (Rebalancing: {rebalance_freq})"
    )
    
    fig.update_traces(line=dict(width=4), selector=dict(name='Portfolio'))
    st.plotly_chart(fig, width='stretch') 
    
    st.markdown("---")
    
    # --- 7. CORRELATION MATRIX ---
    st.markdown("### 🤝 Correlation Matrix of Daily Returns")
    st.caption("Measures the relationship between asset returns.")
    
    col_corr, col_empty = st.columns([2, 1])
    with col_corr:
        st.markdown(metrics['Correlation Matrix'], unsafe_allow_html=True)
        
    st.markdown("---")
    st.caption("The 'Quant B' module provides dynamic rebalancing simulation and multi-asset risk analysis.")
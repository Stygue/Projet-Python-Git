import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.quant_b.portfolio_logic import (
    load_multi_asset_data,
    calculate_portfolio_metrics,
    calculate_portfolio_performance_series,
    calculate_individual_cumulative_returns,
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
        # Initialisation du session_state si non défini, sinon le slider lit la valeur existante
        if f"weight_slider_{name}" not in st.session_state:
            st.session_state[f"weight_slider_{name}"] = default_weight_value
            
        with cols[i]:
            # Le slider lit/écrit directement dans st.session_state
            weight = st.slider(
                name,
                min_value=0.0,
                max_value=100.0,
                value=st.session_state[f"weight_slider_{name}"],
                step=0.01,
                key=f"weight_slider_{name}"
            )
            weights.append(weight / 100) # Convert to decimal for calculation
            
    # Check if weights sum to 100%
    weights_sum = sum(weights) * 100
    if weights_sum < 99.99 or weights_sum > 100.01:
        st.error(f"The sum of weights must equal 100%. Current sum: {weights_sum:.2f}%")
        
        # Le bouton utilise la fonction de rappel pour mettre à jour les poids
        st.button(
            "Distribute Weights Equally",
            on_click=set_equal_weights # Appel de la fonction de rappel avant le RERUN
        )
        return
        
    # --- 4. DATA LOADING AND INITIALIZATION ---
    
    with st.spinner(f"Loading and synchronizing data for {len(asset_ids)} assets..."):
        price_df = load_multi_asset_data(asset_ids, days_to_fetch)

    if price_df is None or price_df.empty:
        st.error("Could not load data. Check API status or the selected time period.")
        return

    # Calculate Metrics and Performance Series
    metrics = calculate_portfolio_metrics(price_df, weights, risk_free_rate)
    
    # --- GESTION D'ERREUR CRITIQUE (Réintroduite pour résoudre le TypeError) ---
    if metrics is None:
        st.error("❌ ERROR: Failed to calculate portfolio metrics. Data might be insufficient or parameters are invalid.")
        return
    # ----------------------------------------------------------------

    portfolio_cumulative = calculate_portfolio_performance_series(price_df, weights)
    individual_cumulative = calculate_individual_cumulative_returns(price_df)

    # --- 5. KEY METRICS DISPLAY ---
    st.markdown("---")
    st.markdown("### 📈 Performance Metrics")

    col1, col2, col3 = st.columns(3)
    
    # Display Annual Return
    col1.metric(
        "Annualized Return", 
        f"{metrics['Annual Return (%)']:.2f}%", 
        help="Expected annual return based on historical data."
    )
    # Display Annual Volatility
    col2.metric(
        "Annual Volatility (Risk)", 
        f"{metrics['Annual Volatility (%)']:.2f}%", 
        help="Annualized standard deviation of returns (risk)."
    )
    # Display Sharpe Ratio
    col3.metric(
        "Sharpe Ratio", 
        f"{metrics['Sharpe Ratio']:.2f}", 
        help="Risk-adjusted return (higher is better)."
    )
    
    st.markdown("---")
    
    # --- 6. MAIN CHART (ASSET VS. PORTFOLIO) ---
    st.markdown("### 📊 Cumulative Performance (Asset vs. Portfolio)")
    
    # 6.1 Data Preparation
    plot_df = individual_cumulative.copy()
    plot_df['Portfolio'] = portfolio_cumulative
    plot_df.index.name = 'Date'
    
    # Transform DataFrame to long format for Plotly (best practice)
    plot_long = plot_df.reset_index().melt(
        id_vars='Date', 
        var_name='Asset/Portfolio', 
        value_name='Cumulative Value'
    )
    
    # 6.2 Plotting with Plotly
    fig = px.line(
        plot_long, 
        x='Date', 
        y='Cumulative Value', 
        color='Asset/Portfolio',
        title="Performance Evolution (Normalized to 1.0 at Start Date)"
    )
    
    # Highlight the Portfolio line for clear visualization
    fig.update_traces(
        line=dict(width=3), 
        selector=dict(name='Portfolio')
    )
    
    # Correction de dépréciation (width='stretch')
    st.plotly_chart(fig, width='stretch') 
    
    st.markdown("---")
    
    # --- 7. CORRELATION MATRIX ---
    st.markdown("### 🤝 Correlation Matrix of Daily Returns")
    st.caption("Measures the relationship between asset returns (Closer to 1 = strong correlation, closer to 0 = better diversification effect).")
    
    col_corr, col_empty = st.columns([2, 1])
    
    with col_corr:
        # The HTML table was pre-calculated in portfolio_logic.py
        st.markdown(metrics['Correlation Matrix'], unsafe_allow_html=True)
        
    st.markdown("---")
    st.caption("The 'Quant B' module successfully implements the minimum requirements: 3+ assets, portfolio simulation, and display of key metrics (Correlation, Volatility, Returns) and visual comparisons.")
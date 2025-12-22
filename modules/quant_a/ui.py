import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots


# Import data fetching (CoinGecko)
from data_handling.caching import get_cached_historical_data, get_cached_current_price

# Import logic modules
from quant_a.strategies import apply_buy_and_hold, apply_sma_crossover, apply_rsi_strategy 
from quant_a.metrics import get_performance_summary
from quant_a.prediction import AdvancedPricePredictor

def render_quant_a_dashboard():
    """
    Main function to render the Single Asset Analysis (Quant A) dashboard.
    """
    st.header("Single Asset Analysis (Quant A)")
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
        
        # CORRECTION ICI : On récupère les deux valeurs (Prix ET Variation)
        price, change_24h = get_cached_current_price(coin_id)

    if df is None or df.empty:
        st.error("Error fetching data. Please try again later or check API limits.")
        return

    # Display Current Price
    # CORRECTION ICI : On utilise la variable 'price' (qui est un float) et non le tuple
    # Bonus : On ajoute le paramètre 'delta' pour afficher la variation en vert/rouge
    st.metric(
        label=f"{selected_asset_name} Price (USD)", 
        value=f"${price:,.2f}",
        delta=f"{change_24h:.2f}%"
    )

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
    
    # On crée une figure capable d'avoir deux axes Y (gauche et droite)
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Trace 1 : Le PRIX de l'actif (Axe de GAUCHE)
    fig.add_trace(
        go.Scatter(
            x=df_processed.index, 
            y=df_processed['price'], 
            mode='lines', 
            name=f'{selected_asset_name} Price',
            line=dict(color='#1f77b4', width=2) # Bleu
        ),
        secondary_y=False # Axe de gauche
    )

    # Trace 2 : La PERFORMANCE de la stratégie (Axe de DROITE)
    # Note : On utilise directement la colonne de stratégie (ex: 1.15), sans la multiplier par le prix !
    fig.add_trace(
        go.Scatter(
            x=df_processed.index, 
            y=df_processed[strategy_col], 
            mode='lines', 
            name=f'Strategy Cumulative Return',
            line=dict(color='#2ca02c', width=2, dash='dot') # Vert pointillé
        ),
        secondary_y=True # Axe de droite
    )

    # Mise en forme du graphique
    fig.update_layout(
        title=f"Price vs Strategy Analysis ({selected_days_label})",
        xaxis_title="Date",
        height=500,
        hovermode="x unified", # Affiche les infos des deux courbes quand on passe la souris
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Titres des axes Y
    fig.update_yaxes(title_text="Asset Price (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative Return (1.0 = Start)", secondary_y=True, showgrid=False)

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

        # --- 6. Advanced AI Prediction ---
    st.markdown("---")
    st.subheader("🧠 Advanced AI Forecasting (Random Forest)")
    st.caption("Model: Random Forest Regressor | Target: Log-Returns | Features: Lags, Volatility, Momentum")
    
    if st.button("Run AI Analysis"):
        with st.spinner("Training Random Forest model & Engineering features..."):
            # Import local pour être sûr d'avoir la bonne classe
            from quant_a.prediction import AdvancedPricePredictor
            
            predictor = AdvancedPricePredictor(df)
            
            # 1. Analyse et Métriques
            metrics = predictor.train_and_analyze()
            
            if "error" in metrics:
                st.warning(metrics["error"])
            else:
                # 2. Prédiction Future
                pred_price, pred_return, confidence = predictor.predict_next_day()
                
                # --- A. Affichage des Résultats Clés ---
                st.markdown("#### 🔮 Forecast for Tomorrow")
                col_p1, col_p2, col_p3 = st.columns(3)
                
                current_price = df['price'].iloc[-1]
                delta_color = "normal"
                if pred_price > current_price: delta_color = "inverse" # Vert si hausse
                
                col_p1.metric(
                    "Predicted Price", 
                    f"${pred_price:,.2f}", 
                    delta=f"{pred_return:.2%}",
                    delta_color=delta_color
                )
                
                col_p2.metric(
                    "Directional Accuracy", 
                    f"{metrics['directional_accuracy']:.1%}",
                    help="Percentage of time the model correctly predicted the Up/Down movement on test data."
                )
                
                col_p3.metric(
                    "Model RMSE", 
                    f"{metrics['rmse']:.4f}",
                    help="Root Mean Squared Error on Log-Returns."
                )

                st.markdown("---")

                # --- B. Graphique Actual vs Predicted (NOUVEAU) ---
                st.markdown("#### 📉 Backtest Analysis: Actual vs. Predicted")
                st.caption("Visualizing model performance on unseen test data (Last 20% of history).")
                
                plot_data = metrics['plotting_data']
                
                fig_pred = go.Figure()
                
                # Courbe Réelle
                fig_pred.add_trace(go.Scatter(
                    x=plot_data.index, 
                    y=plot_data['Actual'],
                    mode='lines',
                    name='Actual Price',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                # Courbe Prédite
                fig_pred.add_trace(go.Scatter(
                    x=plot_data.index, 
                    y=plot_data['Predicted'],
                    mode='lines',
                    name='Predicted (AI)',
                    line=dict(color='#ff7f0e', width=2, dash='dot')
                ))
                
                fig_pred.update_layout(
                    title="One-Step Ahead Prediction Accuracy",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)",
                    height=400,
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig_pred, use_container_width=True)

                # --- C. Feature Importance ---
                st.markdown("#### 🧐 What drives the market?")
                st.caption("Which features influenced the model's decision the most?")
                
                importances = metrics['feature_importance']
                df_imp = pd.DataFrame(list(importances.items()), columns=['Feature', 'Importance'])
                df_imp = df_imp.sort_values(by='Importance', ascending=True)
                
                fig_imp = go.Figure(go.Bar(
                    x=df_imp['Importance'],
                    y=df_imp['Feature'],
                    orientation='h',
                    marker=dict(color='rgba(50, 171, 96, 0.6)', line=dict(color='rgba(50, 171, 96, 1.0)', width=1))
                ))
                fig_imp.update_layout(
                    height=300, 
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis_title="Relative Importance"
                )
                st.plotly_chart(fig_imp, use_container_width=True)
                
                st.info(
                    "💡 **Analyst Note:** Unlike simple Linear Regression, this Random Forest model trains on **Returns** (Stationary data) "
                    "and uses technical indicators (Volatility, SMA distance). The 'Directional Accuracy' is the most reliable metric for trading."
                )


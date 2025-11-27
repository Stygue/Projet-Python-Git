import streamlit as st
import sys
import os
from streamlit_autorefresh import st_autorefresh
from data_handling.caching import get_cached_current_price

# --- 1. THE PATCH (Essential) ---
# This allows Python to find the 'quant_a' and 'quant_b' folders located inside 'modules'
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(current_dir, 'modules')
if modules_path not in sys.path:
    sys.path.append(modules_path)

# --- 2. IMPORTS ---
try:
    # Import Quant A dashboard (Partner's code)
    from quant_a.ui import render_quant_a_dashboard
    # Import Quant B dashboard (Your new code) 👈 ADDITION
    from quant_b.frontend_b import render_quant_b_dashboard
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.stop()

# --- 3. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Projet Finance",
    page_icon="📈",
    layout="wide"
)

# --- 4. APPLICATION STRUCTURE ---
def main():
    st.sidebar.title("Navigation")

    # Refresh every 5 minutes (300000 milliseconds) as required by project specs
    st_autorefresh(interval=300000, key="datarefresh")

    # Sidebar menu
    page = st.sidebar.radio(
        "Go to:",
        ["Home", "Quant A: Crypto Analysis", "Quant B: Portfolio"]
    )

    st.sidebar.markdown("---")

    # Display the correct page
    if page == "Home":
        render_home()
    elif page == "Quant A: Crypto Analysis":
        # Call the partner's module function
        render_quant_a_dashboard()
    elif page == "Quant B: Portfolio":
        # Call your new module function 👈 MODIFICATION
        render_quant_b_dashboard()

def render_home():
    # --- HERO SECTION (Visual Header) ---
    st.markdown("""
        <style>
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            background: -webkit-linear-gradient(45deg, #007CF0, #00DFD8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
        }
        .card-box {
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            background-color: #f9f9f9;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="hero-title">Crypto Quant Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Advanced quantitative analysis, backtesting, and AI prediction platform.</p>', unsafe_allow_html=True)

    st.divider()

        # --- MARKET OVERVIEW (REAL-TIME DATA + 24H CHANGE) ---
    st.subheader("🌍 Market Pulse (Price & 24h Change)")
    
    # Retrieve price and change for key assets
    btc_price, btc_change = get_cached_current_price("bitcoin")
    eth_price, eth_change = get_cached_current_price("ethereum")
    sol_price, sol_change = get_cached_current_price("solana")

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Bitcoin (BTC)", 
            value=f"${btc_price:,.2f}", 
            delta=f"{btc_change:.2f}%"
        )
    with col2:
        st.metric(
            label="Ethereum (ETH)", 
            value=f"${eth_price:,.2f}", 
            delta=f"{eth_change:.2f}%"
        )
    with col3:
        st.metric(
            label="Solana (SOL)", 
            value=f"${sol_price:,.2f}", 
            delta=f"{sol_change:.2f}%"
        )
    with col4:
        st.metric(label="API Status", value="Online", delta="OK")

    st.markdown("---")

    # --- MODULES NAVIGATION (Interactive Cards) ---
    st.subheader("🚀 Module Access")
    
    c1, c2 = st.columns(2)

    with c1:
        with st.container():
            st.info("### 📊 Quant A: Crypto Analysis")
            st.markdown("""
            **Mission :** Analyze individual asset performance.
            
            * ✅ **Strategies :** Buy & Hold, SMA Crossover, RSI.
            * ✅ **Visualization :** Interactive Dual-Axis Charts.
            * ✅ **Metrics :** Sharpe Ratio, Volatility, Drawdown.
            * ✅ **Bonus :** Machine Learning Price Prediction.
            """)
            st.markdown("👉 *Select 'Quant A' in the left menu.*")

    with c2:
        with st.container():
            # Status is now COMPLETE
            st.success("### 💼 Quant B: Portfolio Manager") 
            st.markdown("""
            **Mission :** Global portfolio management and multi-asset analysis.
            
            * ✅ **Status :** Operational and Integrated.
            * 🎯 **Objective :** Asset allocation (Equal Weight, Custom Weights).
            * 🤝 **Risk :** Correlation Matrix, Volatility, Sharpe Ratio.
            """)
            st.markdown("👉 *Select 'Quant B' in the left menu.*")

    # --- FOOTER ---
    st.markdown("---")
    
    f1, f2 = st.columns([3, 1])
    with f1:
        st.caption("Python for Finance Project | Data: CoinGecko API | Engine: Streamlit & Plotly")
        st.caption("© 2025 - MEHAH Grégoire - PAGNIEZ David")
    with f2:
        st.button("🔄 Refresh Data Now")


# The placeholder function `render_quant_b()` has been removed as requested.

if __name__ == "__main__":
    main()
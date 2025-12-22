import streamlit as st
import sys
import os
from streamlit_autorefresh import st_autorefresh
from streamlit.components.v1 import html

# Custom imports for data handling
# We use caching to avoid spamming the API and to speed up the app
from data_handling.caching import get_cached_current_price, get_cached_current_prices_batch 

# --- 1. SYSTEM PATH SETUP ---
# Streamlit sometimes has trouble finding local modules when running from different folders.
# We explicitly add the 'modules' directory to Python's search path to prevent "ModuleNotFound" errors.
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(current_dir, 'modules')
if modules_path not in sys.path:
    sys.path.append(modules_path)

# --- 2. MODULE IMPORTS ---
# We wrap imports in a try/except block to handle cases where a file might be missing or broken.
try:
    from quant_a.ui import render_quant_a_dashboard
    from quant_b.frontend_b import render_quant_b_dashboard
except ImportError as e:
    st.error(f"Critical Import Error: {e}")
    st.stop()

# --- 3. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Projet Finance - Crypto Quant",
    page_icon="📈",
    layout="wide" # Uses the full width of the screen for better charts
)

# --- 4. MAIN APPLICATION LOGIC ---
def main():
    st.sidebar.title("🧭 Navigation")

    # --- AUTO-REFRESH LOGIC ---
    # Financial dashboards need live data. Streamlit is static by default.
    # We use a timer to force the page to reload every 5 minutes (300 seconds).
    REFRESH_INTERVAL_SEC = 300 
    
    # This Streamlit component handles the background counting
    st_autorefresh(interval=REFRESH_INTERVAL_SEC * 1000, key="datarefresh")

    # Visual Countdown (JavaScript Injection)
    # This is a UI enhancement: it shows a visual timer in the sidebar so the user knows when the update happens.
    timer_html = f"""
    <div style="
        border: 1px solid #444; 
        border-radius: 5px; 
        padding: 10px; 
        text-align: center; 
        background-color: #0e1117; 
        color: #fafafa; 
        font-family: sans-serif;
        margin-bottom: 20px;">
        <span style="font-size: 0.9em; color: #aaa;">Next Update:</span>
        <br>
        <span id="countdown" style="font-size: 1.5em; font-weight: bold;">--:--</span>
    </div>

    <script>
        var timeleft = {REFRESH_INTERVAL_SEC};
        var downloadTimer = setInterval(function(){{
          if(timeleft <= 0){{
            clearInterval(downloadTimer);
            document.getElementById("countdown").innerHTML = "Refreshing...";
            // Force the browser to reload the page
            window.parent.location.reload(); 
          }} else {{
            var minutes = Math.floor(timeleft / 60);
            var seconds = timeleft % 60;
            seconds = seconds < 10 ? '0' + seconds : seconds;
            document.getElementById("countdown").innerHTML = minutes + ":" + seconds;
          }}
          timeleft -= 1;
        }}, 1000);
    </script>
    """
    
    st.sidebar.markdown("### ⏳ Status")
    with st.sidebar:
        html(timer_html, height=85)

    # Navigation Menu
    page = st.sidebar.radio(
        "Go to:",
        ["Home", "Quant A: Crypto Analysis", "Quant B: Portfolio"]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip:** All charts are interactive. You can zoom, pan, and hover for details.")

    # Routing logic
    if page == "Home":
        render_home()
    elif page == "Quant A: Crypto Analysis":
        render_quant_a_dashboard()
    elif page == "Quant B: Portfolio":
        render_quant_b_dashboard()

def render_home():
    """
    Renders the landing page with a market overview and instructions.
    """
    # --- HERO SECTION (CSS Styling) ---
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
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="hero-title">Crypto Quant Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Advanced quantitative analysis, backtesting, and AI prediction platform.</p>', unsafe_allow_html=True)

    st.divider()

    # --- MARKET PULSE ---
    # Quick look at the top 3 assets to give immediate value to the user.
    st.subheader("🌍 Market Pulse (Price & 24h Change)")
    
    HOME_ASSETS = ["bitcoin", "ethereum", "solana"]
    # Fetching data in batch is more efficient than 3 separate calls
    prices_data = get_cached_current_prices_batch(HOME_ASSETS) 

    # Unpacking data safely
    btc_price, btc_change = prices_data.get("bitcoin", (0.0, 0.0))
    eth_price, eth_change = prices_data.get("ethereum", (0.0, 0.0))
    sol_price, sol_change = prices_data.get("solana", (0.0, 0.0))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Bitcoin (BTC)", value=f"${btc_price:,.2f}", delta=f"{btc_change:.2f}%")
    with col2:
        st.metric(label="Ethereum (ETH)", value=f"${eth_price:,.2f}", delta=f"{eth_change:.2f}%")
    with col3:
        st.metric(label="Solana (SOL)", value=f"${sol_price:,.2f}", delta=f"{sol_change:.2f}%")
    with col4:
        st.metric(label="API Status", value="Online", delta="OK")

    st.markdown("---")

    # --- MODULE GUIDES ---
    st.subheader("🚀 Module Guides & Access")
    
    c1, c2 = st.columns(2)

    with c1:
        with st.container():
            st.info("### 📊 Quant A: Crypto Analysis")
            st.markdown("""
            **Focus:** Technical analysis and Price Prediction for a single asset.
            
            **User Guide:**
            1. **Select Asset & Timeframe:** Choose a crypto and adjust the date slider to compare short-term vs. long-term trends.
            2. **Technical Indicators:** Overlay **SMA** (Trend) or **RSI** (Momentum) to identify potential entry points.
            3. **Strategy Backtesting:** Look at the 'Cumulative Return' chart to see if a strategy (e.g., SMA Crossover) beats the 'Buy & Hold' benchmark.
            4. **Risk Metrics:** Check the data table for **Volatility** and **Max Drawdown** to understand the risk before investing.
            5. **AI Prediction:** Consult the 'ML Prediction' section. **Tip:** Look at the 'Confidence Score'—only trust the prediction if the confidence is high (> 60%).
            """)
            st.markdown("👉 *Select 'Quant A' in the left menu.*")

    with c2:
        with st.container():
            st.success("### 💼 Quant B: Portfolio Manager") 
            st.markdown("""
            **Focus:** Portfolio simulation and Risk Optimization (Diversification).
            
            **User Guide:**
            1. **Portfolio Construction:** Select at least 3 assets to combine.
            2. **Price Weighting:** Use sliders to define your target allocation (e.g., 50% BTC, 25% ETH, 25% SOL).
            3. **Rebalancing Strategy:** Choose a frequency (Daily, Weekly, Monthly). The system simulates selling winners to buy losers to maintain your weights.
            4. **Quantity Tracking:** Observe the 'Coin Quantities' chart to see how your token holdings change over time.
            5. **Risk Analysis:** Check the Correlation Matrix to ensure your assets are not moving identically.
            """)
            st.markdown("👉 *Select 'Quant B' in the left menu.*")

    # --- FOOTER ---
    st.markdown("---")
    
    f1, f2 = st.columns([3, 1])
    with f1:
        st.caption("Python for Finance Project | Data: CoinGecko API | Engine: Streamlit & Plotly")
        st.caption("© 2025 - MEHAH Grégoire - PAGNIEZ David")
    with f2:
        # Manual Refresh Button
        # Useful if the user wants to force an update immediately without waiting for the timer.
        if st.button("🔄 Refresh Data Now"):
            # 1. Clear the cache to force new API calls
            st.cache_data.clear()
            # 2. Rerun the script from top to bottom
            st.rerun()

if __name__ == "__main__":
    main()

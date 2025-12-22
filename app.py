import streamlit as st
import sys
import os
from streamlit_autorefresh import st_autorefresh
# AJOUT : Importation de get_cached_current_prices_batch
from data_handling.caching import get_cached_current_price, get_cached_current_prices_batch 
from streamlit.components.v1 import html

# --- 1. THE PATCH (Essential) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(current_dir, 'modules')
if modules_path not in sys.path:
    sys.path.append(modules_path)

# --- 2. IMPORTS ---
try:
    from quant_a.ui import render_quant_a_dashboard
    from quant_b.frontend_b import render_quant_b_dashboard
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.stop()

# --- 3. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Projet Finance - Crypto Quant",
    page_icon="📈",
    layout="wide"
)

# --- 4. APPLICATION STRUCTURE ---
def main():
    st.sidebar.title("🧭 Navigation")

    # --- GESTION DU REFRESH & CHRONO ---
    # Durée en secondes (5 minutes = 300)
    REFRESH_INTERVAL_SEC = 300 
    
    # 1. Le mécanisme de refresh automatique (invisible mais actif)
    st_autorefresh(interval=REFRESH_INTERVAL_SEC * 1000, key="datarefresh")

        # 2. Le Chronomètre Visuel (JavaScript injecté)
    # NOTE : Les doubles accolades {{ }} sont nécessaires pour le JS dans une f-string Python
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
        <span style="font-size: 0.9em; color: #aaa;">Prochain update :</span>
        <br>
        <span id="countdown" style="font-size: 1.5em; font-weight: bold;">--:--</span>
    </div>

    <script>
        var timeleft = {REFRESH_INTERVAL_SEC};
        var downloadTimer = setInterval(function(){{
          if(timeleft <= 0){{
            clearInterval(downloadTimer);
            document.getElementById("countdown").innerHTML = "Refreshing...";
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

    
    # On l'affiche tout en haut de la sidebar
    st.sidebar.markdown("### ⏳ Status")
    with st.sidebar:
        html(timer_html, height=85)
    page = st.sidebar.radio(
        "Go to:",
        ["Home", "Quant A: Crypto Analysis", "Quant B: Portfolio"]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip:** All charts are interactive. You can zoom, pan, and hover for details.")

    if page == "Home":
        render_home()
    elif page == "Quant A: Crypto Analysis":
        render_quant_a_dashboard()
    elif page == "Quant B: Portfolio":
        render_quant_b_dashboard()

def render_home():
    # --- HERO SECTION ---
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

    # --- MARKET OVERVIEW ---
    st.subheader("🌍 Market Pulse (Price & 24h Change)")
    
    HOME_ASSETS = ["bitcoin", "ethereum", "solana"]
    prices_data = get_cached_current_prices_batch(HOME_ASSETS) 

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

    # --- MODULES NAVIGATION ---
    st.subheader("🚀 Module Guides & Access")
    
    c1, c2 = st.columns(2)

    with c1:
        with st.container():
            st.info("### 📊 Quant A: Crypto Analysis")
            st.markdown("""
            **Focus :** Analyse technique et prédictive d'un actif unique.
            
            **Guide d'utilisation :**
            1. **Select Asset :** Choisissez une crypto-monnaie dans la barre latérale.
            2. **Indicators :** Superposez SMA, RSI ou Bollinger pour analyser les tendances.
            3. **Interactive Legend :** Cliquez sur les éléments de la légende du graphique pour masquer/afficher les indicateurs.
            4. **AI Prediction :** Consultez la section 'ML Prediction' pour voir la tendance estimée à 7 jours via régression linéaire.
            """)
            st.markdown("👉 *Select 'Quant A' in the left menu.*")

    with c2:
        with st.container():
            st.success("### 💼 Quant B: Portfolio Manager") 
            st.markdown("""
            **Focus :** Simulation de gestion de portefeuille et optimisation du risque.
            
            **Guide d'utilisation :**
            1. **Portfolio Construction :** Sélectionnez au moins 3 actifs à combiner.
            2. **Price Weighting :** Utilisez les curseurs pour définir vos poids cibles (ex: 50% BTC, 25% ETH, 25% SOL).
            3. **Rebalancing Strategy :** Choisissez une fréquence (Daily, Weekly, Monthly). Le système simulera la vente des actifs gagnants pour racheter les perdants afin de maintenir vos poids.
            4. **Quantity Tracking :** Observez le graphique 'Coin Quantities' pour voir l'ajustement dynamique du nombre de jetons détenus suite au rebalancement.
            5. **Risk Analysis :** Consultez la matrice de corrélation pour vérifier la diversification de votre panier.
            
            **💡 Interactive Tip :** Double-cliquez sur 'Portfolio' dans la légende du graphique de performance pour isoler la courbe globale.
            """)
            st.markdown("👉 *Select 'Quant B' in the left menu.*")

    # --- FOOTER ---
    st.markdown("---")
    
    f1, f2 = st.columns([3, 1])
    with f1:
        st.caption("Python for Finance Project | Data: CoinGecko API | Engine: Streamlit & Plotly")
        st.caption("© 2025 - MEHAH Grégoire - PAGNIEZ David")
    with f2:
        # On stocke le résultat du clic dans une variable
        if st.button("🔄 Refresh Data Now"):
            # 1. On vide TOUT le cache de données
            st.cache_data.clear()
            # 2. On force le rechargement immédiat de la page
            st.rerun()

if __name__ == "__main__":
    main()
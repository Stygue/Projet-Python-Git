import streamlit as st
import sys
import os
from streamlit_autorefresh import st_autorefresh
from data_handling.caching import get_cached_current_price

# --- 1. LE PATCH (Indispensable) ---
# Cela permet à Python de trouver le dossier 'quant_a' qui est caché dans 'modules'
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(current_dir, 'modules')
if modules_path not in sys.path:
    sys.path.append(modules_path)

# --- 2. IMPORTATIONS ---
try:
    # On importe ton dashboard Quant A
    from quant_a.ui import render_quant_a_dashboard
except ImportError as e:
    st.error(f"Erreur d'importation : {e}")
    st.stop()

# --- 3. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Projet Finance",
    page_icon="📈",
    layout="wide"
)

# --- 4. STRUCTURE DE L'APPLICATION ---
def main():
    st.sidebar.title("Navigation")

    # Refresh every 5 minutes (300000 milliseconds)
    st_autorefresh(interval=300000, key="datarefresh")

    # Menu de gauche
    page = st.sidebar.radio(
        "Aller vers :",
        ["Accueil", "Quant A: Crypto Analysis", "Quant B: Portfolio"]
    )

    st.sidebar.markdown("---")

    # Affichage de la bonne page
    if page == "Accueil":
        render_home()
    elif page == "Quant A: Crypto Analysis":
        render_quant_a_dashboard()
    elif page == "Quant B: Portfolio":
        render_quant_b()

def render_home():
    # --- HERO SECTION (En-tête visuel) ---
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
    st.markdown('<p class="hero-subtitle">Plateforme avancée d\'analyse quantitative, de backtesting et de prédiction IA.</p>', unsafe_allow_html=True)

    st.divider()

       # --- MARKET OVERVIEW (VRAIES DONNÉES + VARIATION) ---
    st.subheader("🌍 Market Pulse (Prix & Variation 24h)")
    
    # On récupère MAINTENANT deux valeurs : le prix ET la variation
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
        st.metric(label="Status API", value="Online", delta="OK")

    st.markdown("---")

    # --- MODULES NAVIGATION (Cartes interactives) ---
    st.subheader("🚀 Accès aux Modules")
    
    c1, c2 = st.columns(2)

    with c1:
        with st.container():
            st.info("### 📊 Quant A: Crypto Analysis")
            st.markdown("""
            **Mission :** Analyser la performance d'actifs individuels.
            
            *   ✅ **Stratégies :** Buy & Hold, SMA Crossover, RSI.
            *   ✅ **Visualisation :** Graphiques interactifs Double Axe.
            *   ✅ **Métriques :** Sharpe Ratio, Volatilité, Drawdown.
            *   ✅ **Bonus :** Prédiction de prix par Machine Learning.
            """)
            st.markdown("👉 *Sélectionnez 'Quant A' dans le menu à gauche.*")

    with c2:
        with st.container():
            st.warning("### 💼 Quant B: Portfolio Manager")
            st.markdown("""
            **Mission :** Gestion de portefeuille global.
            
            *   🚧 **Statut :** En cours de développement.
            *   🎯 **Objectif :** Optimisation de l'allocation d'actifs (Markowitz).
            *   📉 **Risque :** Analyse de la VaR (Value at Risk).
            """)
            st.markdown("👉 *Sélectionnez 'Quant B' dans le menu à gauche.*")

    # --- FOOTER ---
    st.markdown("---")
    
    f1, f2 = st.columns([3, 1])
    with f1:
        st.caption("Projet Python pour la Finance | Données : CoinGecko API | Moteur : Streamlit & Plotly")
        st.caption("© 2025 - MEHAH Grégoire - PAGNIEZ David")
    with f2:
        st.button("🔄 Rafraîchir les données")


def render_quant_b():
    st.header("💼 Module Portfolio")
    st.info("🚧 Ce module est en cours de construction.")

if __name__ == "__main__":
    main()

import streamlit as st
import sys
import os

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
    st.title("📈 Dashboard Financier")
    st.markdown("""
    Bienvenue sur l'application de gestion d'actifs.
    
    👈 **Utilise le menu à gauche** pour accéder aux modules.
    """)

def render_quant_b():
    st.header("💼 Module Portfolio")
    st.info("🚧 Ce module est en cours de construction.")

if __name__ == "__main__":
    main()

import streamlit as st
from modules.quant_b.frontend_b import display_quant_b_module
# from modules.quant_a.frontend_a import display_quant_a_module # Sera ajouté par ton coéquipier

# ----------------------------------------------------
# Configuration de la Page
# ----------------------------------------------------
st.set_page_config(
    page_title="Quant Finance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏛️ Quantitative Portfolio Analysis Dashboard")
st.markdown("---")

# ----------------------------------------------------
# Navigation et Affichage des Modules
# ----------------------------------------------------

# Utilisation des onglets pour séparer les modules (permet une meilleure intégration)
tab_portfolio, tab_single_asset = st.tabs(["📊 Portfolio Analysis (Quant B)", "📈 Single Asset Analysis (Quant A)"])

# Affichage du Module Quant B (Ton module)
with tab_portfolio:
    display_quant_b_module()

# Emplacement réservé pour le Module Quant A (sera complété par ton coéquipier)
with tab_single_asset:
    st.header("Module Quant A - En construction")
    st.info("This section is reserved for the Univariate Single Asset Analysis module.")
    # if 'display_quant_a_module' in locals():
    #     display_quant_a_module()

# ----------------------------------------------------
# Pied de page/Informations
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Project Goal:** Build a professional financial dashboard using Python/Streamlit on Linux, collaborating via Git/GitHub[cite: 12, 13]."
)
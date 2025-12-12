"""Application principale Streamlit pour GardeTonOr."""
import streamlit as st
from src.config import STREAMLIT_CONFIG
from src.database import init_database

# Configuration de la page
st.set_page_config(**STREAMLIT_CONFIG)

# Initialiser la base de données au premier lancement
init_database()

# Style CSS personnalisé
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FFD700;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FFD700;
    }
    .alert-warning {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .alert-success {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .alert-info {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header principal
st.markdown('<div class="main-header">💰 GardeTonOr</div>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align: center; font-size: 1.2rem; color: #666;">Optimisez vos contrats avec l\'intelligence artificielle</p>',
    unsafe_allow_html=True,
)

st.divider()

# Navigation dans la sidebar
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Aller à",
    ["🏠 Dashboard", "➕ Ajouter un contrat", "⚖️ Comparer", "📊 Historique"],
    label_visibility="collapsed",
    key="navigation",
)

# Affichage des pages
if page == "🏠 Dashboard":
    from src.pages import dashboard

    dashboard.show()
elif page == "➕ Ajouter un contrat":
    from src.pages import add_contract

    add_contract.show()
elif page == "⚖️ Comparer":
    from src.pages import compare

    compare.show()
elif page == "📊 Historique":
    from src.pages import history

    history.show()

# Footer
st.sidebar.divider()
st.sidebar.markdown("---")
st.sidebar.caption("© 2025 GardeTonOr - Quanteam")
st.sidebar.caption("Propulsé par OpenAI GPT-4")

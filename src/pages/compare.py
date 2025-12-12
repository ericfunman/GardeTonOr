"""Page de comparaison de contrats."""

import streamlit as st

from src.database import get_db

from src.services import OpenAIService, PDFService, ContractService

from src.config import (
    CONTRACT_TYPES,
    DATE_FORMAT,
)

from src.pages.compare_logic import (
    handle_market_analysis,
    handle_competitor_comparison,
    display_competitor_comparison,
    display_market_analysis,
)


def _select_contract(contracts):
    st.markdown("### 📋 Sélectionnez un contrat à comparer")

    # Préremplir si vient du dashboard

    default_index = 0

    contract_ids = [c.id for c in contracts]

    if "compare_contract_id" in st.session_state:
        try:
            default_index = contract_ids.index(st.session_state["compare_contract_id"])

            del st.session_state["compare_contract_id"]

        except ValueError:
            pass

    # Créer un dictionnaire pour l'affichage

    contract_display = {
        c.id: f"{CONTRACT_TYPES.get(c.contract_type)} - {c.provider} (Date anniversaire: {c.anniversary_date.strftime('%d/%m/%Y')})"
        for c in contracts
    }

    selected_contract_id = st.selectbox(
        "Contrat",
        options=contract_ids,
        format_func=lambda x: contract_display.get(x, f"Contrat {x}"),
        index=default_index if contract_ids else 0,
        key="compare_contract_selector",
    )

    return selected_contract_id


def _display_contract_details(selected_contract):
    if selected_contract:
        # Afficher les détails du contrat

        contract_data = selected_contract.contract_data

        with st.expander("📄 Détails du contrat", expanded=False):
            st.json(contract_data)

        st.divider()


def _handle_comparison_type(contract_service, contract_id):
    st.markdown("### 🔍 Type de comparaison")

    comparison_type = st.radio(
        "Choisissez le type de comparaison",
        ["📊 Analyse de marché", "🆚 Comparer avec un devis concurrent"],
        label_visibility="collapsed",
    )

    # Analyse de marché

    if comparison_type == "📊 Analyse de marché":
        handle_market_analysis(contract_service, contract_id)

    # Comparaison avec concurrent

    else:
        handle_competitor_comparison(contract_service, contract_id)


def _display_history(contract_service, contract_id):
    st.divider()

    st.markdown("### 📜 Historique des comparaisons")

    comparisons = contract_service.get_contract_comparisons(contract_id)

    if comparisons:
        for i, comp in enumerate(comparisons):
            with st.expander(
                f"{'📊' if comp.comparison_type == 'market_analysis' else '🆚'} "
                f"{comp.created_at.strftime(f'{DATE_FORMAT} %H:%M')} - {comp.analysis_summary[:50]}...",
                expanded=(i == 0),
            ):
                if comp.comparison_type == "market_analysis":
                    display_market_analysis(comp)

                else:
                    display_competitor_comparison(comp)

    else:
        st.info("Aucune comparaison effectuée pour ce contrat")


def show():
    """Affiche la page de comparaison."""

    st.title("⚖️ Comparer un contrat")

    st.markdown("Analysez vos contrats pour trouver de meilleures offres")

    with get_db() as db:
        openai_service = OpenAIService()

        pdf_service = PDFService()

        contract_service = ContractService(db, openai_service, pdf_service)

        contracts = contract_service.get_all_contracts()

        if not contracts:
            st.warning("⚠️ Aucun contrat enregistré. Ajoutez d'abord un contrat !")

            if st.button("➕ Ajouter un contrat"):
                st.session_state["page"] = "add"

                st.rerun()

            return

        selected_contract_id = _select_contract(contracts)

        if selected_contract_id:
            # Récupérer l'objet frais depuis la session actuelle

            selected_contract = contract_service.get_contract_by_id(selected_contract_id)

            _display_contract_details(selected_contract)

            if selected_contract:
                _handle_comparison_type(contract_service, selected_contract.id)

                _display_history(contract_service, selected_contract.id)


if __name__ == "__main__":
    show()

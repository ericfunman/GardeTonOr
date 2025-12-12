"""Page Dashboard - Vue d'ensemble des contrats."""
import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px

from src.database import get_db
from src.services import OpenAIService, PDFService, ContractService
from src.config import CONTRACT_TYPES, NOTIFICATION_DAYS_BEFORE


def show():
    """Affiche le dashboard principal."""
    st.title("🏠 Dashboard")
    st.markdown("Vue d'ensemble de vos contrats et alertes")

    with get_db() as db:
        openai_service = OpenAIService()
        pdf_service = PDFService()
        contract_service = ContractService(db, openai_service, pdf_service)

        # Récupérer tous les contrats
        contracts = contract_service.get_all_contracts()
        contracts_needing_attention = contract_service.get_contracts_needing_attention()

        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(label="📄 Total Contrats", value=len(contracts))

        with col2:
            st.metric(
                label="⚠️ Alertes",
                value=len(contracts_needing_attention),
                delta=f"{len(contracts_needing_attention)} à vérifier"
                if contracts_needing_attention
                else None,
            )

        with col3:
            telephone_count = sum(1 for c in contracts if c.contract_type == "telephone")
            st.metric(label="📱 Téléphone", value=telephone_count)

        with col4:
            assurance_count = sum(1 for c in contracts if c.contract_type == "assurance_pno")
            st.metric(label="🏠 Assurance PNO", value=assurance_count)

        st.divider()

        # Alertes dates anniversaires
        if contracts_needing_attention:
            st.markdown("### ⚠️ Contrats nécessitant attention")
            st.markdown(
                f'<div class="alert-warning">'
                f"<strong>{len(contracts_needing_attention)} contrat(s)</strong> "
                f"arrive(nt) à échéance dans les {NOTIFICATION_DAYS_BEFORE} prochains jours"
                f"</div>",
                unsafe_allow_html=True,
            )

            for contract in contracts_needing_attention:
                days_until = (contract.anniversary_date - datetime.now()).days

                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    st.markdown(f"**{contract.provider}**")
                    st.caption(
                        f"{CONTRACT_TYPES.get(contract.contract_type, contract.contract_type)}"
                    )

                with col2:
                    st.markdown(
                        f"📅 Date anniversaire: **{contract.anniversary_date.strftime('%d/%m/%Y')}**"
                    )

                    if days_until <= 7:
                        st.markdown(f"🔴 Dans **{days_until} jour(s)**")
                    elif days_until <= 30:
                        st.markdown(f"🟡 Dans **{days_until} jour(s)**")
                    else:
                        st.markdown(f"🟢 Dans **{days_until} jour(s)**")

                with col3:
                    if st.button("🔍 Comparer", key=f"compare_{contract.id}"):
                        st.session_state["compare_contract_id"] = contract.id
                        st.rerun()

                st.divider()
        else:
            st.success("✅ Aucun contrat ne nécessite d'attention immédiate")

        st.divider()

        # Liste de tous les contrats
        col_header, col_btn = st.columns([3, 1])
        with col_header:
            st.markdown("### 📋 Tous vos contrats")
        with col_btn:
            if st.button("➕ Ajouter un contrat", key="add_contract_top"):
                st.session_state["navigation"] = "➕ Ajouter un contrat"
                st.rerun()

        if not contracts:
            st.info("Aucun contrat enregistré. Commencez par ajouter un contrat !")
        else:
            # Tableau des contrats
            contracts_data = []
            for contract in contracts:
                # Calculer le coût mensuel/annuel selon le type
                cost = "N/A"
                if contract.contract_type == "telephone":
                    cost = f"{contract.contract_data.get('prix_mensuel', 0):.2f} €/mois"
                elif contract.contract_type == "assurance_pno":
                    if contract.contract_data.get("prime_mensuelle"):
                        cost = f"{contract.contract_data.get('prime_mensuelle', 0):.2f} €/mois"
                    else:
                        cost = f"{contract.contract_data.get('prime_annuelle', 0):.2f} €/an"
                elif contract.contract_type in ["electricite", "gaz"]:
                    if contract.contract_data.get("estimation_facture_annuelle"):
                        cost_annual = contract.contract_data.get("estimation_facture_annuelle", 0)
                        cost = f"{cost_annual:.2f} €/an ({cost_annual / 12:.2f} €/mois)"
                    elif contract.contract_data.get("prix_abonnement_mensuel"):
                        cost = (
                            f"{contract.contract_data.get('prix_abonnement_mensuel', 0):.2f} €/mois"
                        )

                contracts_data.append(
                    {
                        "ID": contract.id,
                        "Type": CONTRACT_TYPES.get(contract.contract_type, contract.contract_type),
                        "Fournisseur": contract.provider,
                        "Coût": cost,
                        "Date anniversaire": contract.anniversary_date.strftime("%d/%m/%Y"),
                        "Statut": "✅ Validé" if contract.validated else "⏳ En attente",
                    }
                )

            df = pd.DataFrame(contracts_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Graphique d'évolution si historique de comparaisons
            st.markdown("### 📈 Évolution des économies potentielles")

            all_comparisons = contract_service.get_all_comparisons()

            if all_comparisons:
                comparison_data = []
                for comp in all_comparisons:
                    if (
                        comp.comparison_result
                        and "economie_potentielle_annuelle" in comp.comparison_result
                    ):
                        comparison_data.append(
                            {
                                "Date": comp.created_at,
                                "Contrat": comp.contract.provider,
                                "Économie potentielle (€/an)": comp.comparison_result.get(
                                    "economie_potentielle_annuelle", 0
                                ),
                            }
                        )

                if comparison_data:
                    df_comp = pd.DataFrame(comparison_data)
                    fig = px.line(
                        df_comp,
                        x="Date",
                        y="Économie potentielle (€/an)",
                        color="Contrat",
                        title="Évolution des économies potentielles par contrat",
                        markers=True,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(
                        "Effectuez des comparaisons pour voir l'évolution des économies potentielles"
                    )
            else:
                st.info("Aucune comparaison effectuée pour le moment")


if __name__ == "__main__":
    show()

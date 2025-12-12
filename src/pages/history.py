"""Page d'historique des analyses."""
import streamlit as st
import pandas as pd
import plotly.express as px

from src.database import get_db
from src.services import OpenAIService, PDFService, ContractService
from src.config import CONTRACT_TYPES, LABEL_ECONOMY_YEAR, LABEL_TOTAL_ECONOMY_YEAR


def show():
    """Affiche la page d'historique."""
    st.title("📊 Historique des analyses")
    st.markdown("Consultez toutes vos comparaisons et analyses passées")

    with get_db() as db:
        openai_service = OpenAIService()
        pdf_service = PDFService()
        contract_service = ContractService(db, openai_service, pdf_service)

        comparisons = contract_service.get_all_comparisons()

        if not comparisons:
            st.info("Aucune analyse effectuée pour le moment")
            if st.button("⚖️ Comparer un contrat"):
                st.session_state["page"] = "compare"
                st.rerun()
            return

        # Statistiques globales
        st.markdown("### 📈 Statistiques")

        col1, col2, col3, col4 = st.columns(4)

        total_comparisons = len(comparisons)
        market_analyses = sum(1 for c in comparisons if c.comparison_type == "market_analysis")
        competitor_comparisons = sum(
            1 for c in comparisons if c.comparison_type == "competitor_quote"
        )

        # Calculer économies totales potentielles
        total_savings = 0
        for comp in comparisons:
            if comp.comparison_result:
                # Gestion de la structure imbriquée "analyse"
                market_analysis = comp.comparison_result.get("analyse", {})
                if not isinstance(market_analysis, dict):
                    market_analysis = {}

                savings = (
                    comp.comparison_result.get("economie_potentielle_annuelle", 0)
                    or (comp.comparison_result.get("economie_potentielle_mensuelle", 0) * 12)
                    or market_analysis.get("economie_potentielle_annuelle", 0)
                    or (market_analysis.get("economie_potentielle_mensuelle", 0) * 12)
                    or comp.comparison_result.get("comparaison_prix", {}).get(
                        "economie_potentielle", 0
                    )
                )
                if savings > 0:
                    total_savings += savings

        with col1:
            st.metric("Total analyses", total_comparisons)

        with col2:
            st.metric("📊 Analyses marché", market_analyses)

        with col3:
            st.metric("🆚 Comparaisons", competitor_comparisons)

        with col4:
            st.metric("💰 Économies potentielles", f"{total_savings:.0f} €/an")

        st.divider()

        # Filtres
        st.markdown("### 🔍 Filtres")

        col1, col2 = st.columns(2)

        with col1:
            filter_type = st.selectbox(
                "Type d'analyse", ["Toutes", "Analyses de marché", "Comparaisons concurrent"]
            )

        with col2:
            contracts = contract_service.get_all_contracts()
            contract_options = ["Tous"] + [
                f"{c.provider} ({CONTRACT_TYPES.get(c.contract_type)})" for c in contracts
            ]
            filter_contract = st.selectbox("Contrat", contract_options)

        # Appliquer les filtres
        filtered_comparisons = comparisons

        if filter_type == "Analyses de marché":
            filtered_comparisons = [
                c for c in filtered_comparisons if c.comparison_type == "market_analysis"
            ]
        elif filter_type == "Comparaisons concurrent":
            filtered_comparisons = [
                c for c in filtered_comparisons if c.comparison_type == "competitor_quote"
            ]

        if filter_contract != "Tous":
            selected_contract_name = filter_contract.split(" (")[0]
            filtered_comparisons = [
                c for c in filtered_comparisons if c.contract.provider == selected_contract_name
            ]

        st.divider()

        # Liste des analyses
        st.markdown(f"### 📋 Analyses ({len(filtered_comparisons)})")

        if not filtered_comparisons:
            st.info("Aucune analyse ne correspond aux filtres sélectionnés")
            return

        # Tableau récapitulatif
        analysis_data = []
        for comp in filtered_comparisons:
            # Extraire les infos principales
            type_label = "📊 Marché" if comp.comparison_type == "market_analysis" else "🆚 Concurrent"

            economie = 0
            if comp.comparison_result:
                # Gestion de la structure imbriquée "analyse"
                market_analysis = comp.comparison_result.get("analyse", {})
                if not isinstance(market_analysis, dict):
                    market_analysis = {}

                economie = (
                    comp.comparison_result.get("economie_potentielle_annuelle", 0)
                    or (comp.comparison_result.get("economie_potentielle_mensuelle", 0) * 12)
                    or market_analysis.get("economie_potentielle_annuelle", 0)
                    or (market_analysis.get("economie_potentielle_mensuelle", 0) * 12)
                    or comp.comparison_result.get("comparaison_prix", {}).get(
                        "economie_potentielle", 0
                    )
                )

            recommandation = ""
            if comp.comparison_result:
                market_analysis = comp.comparison_result.get("analyse", {})
                if not isinstance(market_analysis, dict):
                    market_analysis = {}

                recommandation = (
                    comp.comparison_result.get("recommandation")
                    or market_analysis.get("recommandation", "")
                )[:50]

            analysis_data.append(
                {
                    "ID": comp.id,
                    "Date": comp.created_at.strftime("%d/%m/%Y %H:%M"),
                    "Type": type_label,
                    "Contrat": f"{comp.contract.provider}",
                    LABEL_ECONOMY_YEAR: f"{economie:.2f}",
                    "Recommandation": recommandation,
                }
            )

        df = pd.DataFrame(analysis_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # Graphique d'évolution
        st.markdown("### 📈 Évolution des économies potentielles")

        chart_data = []
        for comp in filtered_comparisons:
            if comp.comparison_result:
                # Gestion de la structure imbriquée "analyse"
                market_analysis = comp.comparison_result.get("analyse", {})
                if not isinstance(market_analysis, dict):
                    market_analysis = {}

                economie = (
                    comp.comparison_result.get("economie_potentielle_annuelle", 0)
                    or (comp.comparison_result.get("economie_potentielle_mensuelle", 0) * 12)
                    or market_analysis.get("economie_potentielle_annuelle", 0)
                    or (market_analysis.get("economie_potentielle_mensuelle", 0) * 12)
                    or comp.comparison_result.get("comparaison_prix", {}).get(
                        "economie_potentielle", 0
                    )
                )

                chart_data.append(
                    {
                        "Date": comp.created_at,
                        "Contrat": comp.contract.provider,
                        LABEL_ECONOMY_YEAR: economie,
                        "Taille": abs(economie) + 5,  # Taille minimale pour visibilité
                        "Type": "Marché"
                        if comp.comparison_type == "market_analysis"
                        else "Concurrent",
                    }
                )

        if chart_data:
            df_chart = pd.DataFrame(chart_data)

            fig = px.scatter(
                df_chart,
                x="Date",
                y=LABEL_ECONOMY_YEAR,
                color="Contrat",
                symbol="Type",
                title="Économies potentielles par analyse",
                size="Taille",
                size_max=20,
                hover_data=["Type", LABEL_ECONOMY_YEAR],
            )

            fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Seuil")

            st.plotly_chart(fig, use_container_width=True)

        # Graphique par contrat
        st.markdown("### 📊 Économies par contrat")

        savings_by_contract = {}
        for comp in filtered_comparisons:
            contract_name = comp.contract.provider
            if contract_name not in savings_by_contract:
                savings_by_contract[contract_name] = 0

            if comp.comparison_result:
                economie = (
                    comp.comparison_result.get("economie_potentielle_annuelle", 0)
                    or (comp.comparison_result.get("economie_potentielle_mensuelle", 0) * 12)
                    or comp.comparison_result.get("comparaison_prix", {}).get(
                        "economie_potentielle", 0
                    )
                )
                savings_by_contract[contract_name] += economie

        if savings_by_contract:
            df_savings = pd.DataFrame(
                [
                    {"Contrat": k, LABEL_TOTAL_ECONOMY_YEAR: v}
                    for k, v in savings_by_contract.items()
                ]
            )

            fig2 = px.bar(
                df_savings,
                x="Contrat",
                y=LABEL_TOTAL_ECONOMY_YEAR,
                title="Économies potentielles cumulées par contrat",
                color=LABEL_TOTAL_ECONOMY_YEAR,
                color_continuous_scale="RdYlGn",
            )

            st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # Détails des analyses
        st.markdown("### 🔍 Détails des analyses")

        for comp in filtered_comparisons[:10]:  # Limiter aux 10 dernières
            type_icon = "📊" if comp.comparison_type == "market_analysis" else "🆚"

            with st.expander(
                f"{type_icon} {comp.created_at.strftime('%d/%m/%Y %H:%M')} - "
                f"{comp.contract.provider} - {comp.analysis_summary[:50]}..."
            ):
                # Import dynamique pour éviter circular import
                from src.pages.compare import display_market_analysis, display_competitor_comparison

                if comp.comparison_type == "market_analysis":
                    display_market_analysis(comp)
                else:
                    display_competitor_comparison(comp)


if __name__ == "__main__":
    show()

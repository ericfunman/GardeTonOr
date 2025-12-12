"""Page de comparaison de contrats."""
import streamlit as st
import pandas as pd

from src.database import get_db
from src.services import OpenAIService, PDFService, ContractService
from src.config import (
    CONTRACT_TYPES,
    DATE_FORMAT,
    LABEL_ECONOMY,
    LABEL_SURCOST,
)


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

        # Sélection du contrat
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
        )

        if selected_contract_id:
            # Récupérer l'objet frais depuis la session actuelle
            selected_contract = contract_service.get_contract_by_id(selected_contract_id)

            if selected_contract:
                # Afficher les détails du contrat
                contract_data = selected_contract.contract_data
                contract_id = selected_contract.id

                with st.expander("📄 Détails du contrat", expanded=False):
                    st.json(contract_data)

                st.divider()

            # Type de comparaison
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

            # Historique des comparaisons pour ce contrat
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


def display_market_analysis(comparison):
    """Affiche les résultats d'une analyse de marché."""
    full_result = comparison.comparison_result

    # Support for new structure with "analyse" and "meilleure_offre"
    result = full_result.get("analyse", full_result)
    best_offer_data = full_result.get("meilleure_offre")

    # Recommandation principale
    recommandation = result.get("recommandation", "")
    niveau = result.get("niveau_competitivite", "")

    if "garder" in recommandation.lower():
        st.markdown(
            f'<div class="alert-success">'
            f"<h4>✅ Recommandation : {recommandation}</h4>"
            f"<p>Niveau de compétitivité : <strong>{niveau}</strong></p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="alert-warning">'
            f"<h4>⚠️ Recommandation : {recommandation}</h4>"
            f"<p>Niveau de compétitivité : <strong>{niveau}</strong></p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Justification
    st.markdown("#### 📝 Justification")
    st.write(result.get("justification", ""))

    # Métriques financières
    st.markdown("#### 💰 Analyse financière")

    col1, col2, col3 = st.columns(3)

    tarif_actuel = (
        result.get("tarif_actuel")
        or result.get("prime_actuelle_annuelle")
        or result.get("cout_annuel_actuel")
        or 0
    )
    estimation = result.get("estimation_marche", {})
    economie_mensuelle = result.get("economie_potentielle_mensuelle", 0)
    economie_annuelle = result.get("economie_potentielle_annuelle", 0)

    with col1:
        st.metric("Tarif actuel", f"{tarif_actuel:.2f} €")

    with col2:
        tarif_moyen = (
            estimation.get("tarif_moyen")
            or estimation.get("prime_moyenne")
            or estimation.get("cout_moyen")
            or 0
        )
        delta = tarif_actuel - tarif_moyen if tarif_moyen else 0
        st.metric(
            "Tarif moyen marché",
            f"{tarif_moyen:.2f} €",
            delta=f"{delta:.2f} €" if delta else None,
            delta_color="inverse",
        )

    with col3:
        if economie_annuelle:
            st.metric(
                "Économie potentielle/an",
                f"{economie_annuelle:.2f} €",
                delta=LABEL_ECONOMY if economie_annuelle > 0 else LABEL_SURCOST,
            )
        elif economie_mensuelle:
            st.metric(
                "Économie potentielle/mois",
                f"{economie_mensuelle:.2f} €",
                delta=LABEL_ECONOMY if economie_mensuelle > 0 else LABEL_SURCOST,
            )

    # Offres similaires
    if "offres_similaires" in result and result["offres_similaires"]:
        st.markdown("#### 🏪 Offres similaires sur le marché")

        for offre in result["offres_similaires"]:
            with st.container():
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**{offre.get('fournisseur') or offre.get('assureur')}**")
                    st.caption(offre.get("forfait") or offre.get("offre") or "")

                    if offre.get("avantages"):
                        st.markdown("✅ " + ", ".join(offre["avantages"][:3]))
                    if offre.get("inconvenients"):
                        st.markdown("❌ " + ", ".join(offre["inconvenients"][:2]))

                with col2:
                    if offre.get("prix_mensuel"):
                        prix = offre.get("prix_mensuel")
                        unite = "/mois"
                    elif offre.get("cout_annuel_estime"):
                        prix = offre.get("cout_annuel_estime")
                        unite = "/an"
                    elif offre.get("prime_annuelle"):
                        prix = offre.get("prime_annuelle")
                        unite = "/an"
                    else:
                        prix = 0
                        unite = ""

                    st.metric("Prix", f"{prix:.2f} €{unite}")

                st.divider()

    # Tableau comparatif
    if best_offer_data:
        st.markdown("#### 🆚 Tableau comparatif")

        current_data = comparison.contract.contract_data

        # Helper to flatten/extract key values for comparison
        def get_val(data, *keys):
            res = data
            for k in keys:
                if isinstance(res, dict):
                    res = res.get(k)
                else:
                    return None
            return res

        # Build comparison rows based on contract type
        rows = []
        c_type = comparison.contract.contract_type

        if c_type == "electricite":
            rows = [
                (
                    "Fournisseur",
                    get_val(current_data, "fournisseur"),
                    get_val(best_offer_data, "fournisseur"),
                ),
                (
                    "Abonnement (€/mois)",
                    get_val(current_data, "electricite", "tarifs", "abonnement_mensuel_ttc")
                    or get_val(current_data, "prix_abonnement_mensuel"),
                    get_val(best_offer_data, "electricite", "tarifs", "abonnement_mensuel_ttc")
                    or get_val(best_offer_data, "prix_abonnement_mensuel"),
                ),
                (
                    "Prix kWh (€)",
                    get_val(current_data, "electricite", "tarifs", "prix_kwh_ttc")
                    or get_val(current_data, "prix_kwh", "base"),
                    get_val(best_offer_data, "electricite", "tarifs", "prix_kwh_ttc")
                    or get_val(best_offer_data, "prix_kwh", "base"),
                ),
                (
                    "Coût annuel estimé (€)",
                    get_val(current_data, "electricite", "budget_annuel_estime_ttc")
                    or get_val(current_data, "estimation_facture_annuelle"),
                    get_val(best_offer_data, "electricite", "budget_annuel_estime_ttc")
                    or get_val(best_offer_data, "estimation_facture_annuelle"),
                ),
            ]
        elif c_type == "gaz":
            rows = [
                (
                    "Fournisseur",
                    get_val(current_data, "fournisseur"),
                    get_val(best_offer_data, "fournisseur"),
                ),
                (
                    "Abonnement (€/mois)",
                    get_val(current_data, "gaz", "tarifs", "abonnement_mensuel_ttc")
                    or get_val(current_data, "prix_abonnement_mensuel"),
                    get_val(best_offer_data, "gaz", "tarifs", "abonnement_mensuel_ttc")
                    or get_val(best_offer_data, "prix_abonnement_mensuel"),
                ),
                (
                    "Prix kWh (€)",
                    get_val(current_data, "gaz", "tarifs", "prix_kwh_ttc")
                    or get_val(current_data, "prix_kwh"),
                    get_val(best_offer_data, "gaz", "tarifs", "prix_kwh_ttc")
                    or get_val(best_offer_data, "prix_kwh"),
                ),
                (
                    "Coût annuel estimé (€)",
                    get_val(current_data, "gaz", "budget_annuel_estime_ttc")
                    or get_val(current_data, "estimation_facture_annuelle"),
                    get_val(best_offer_data, "gaz", "budget_annuel_estime_ttc")
                    or get_val(best_offer_data, "estimation_facture_annuelle"),
                ),
            ]
        elif c_type == "telephone":
            rows = [
                (
                    "Fournisseur",
                    get_val(current_data, "fournisseur"),
                    get_val(best_offer_data, "fournisseur"),
                ),
                (
                    "Forfait",
                    get_val(current_data, "forfait_nom"),
                    get_val(best_offer_data, "forfait_nom"),
                ),
                (
                    "Data (Go)",
                    get_val(current_data, "data_go"),
                    get_val(best_offer_data, "data_go"),
                ),
                (
                    "Prix mensuel (€)",
                    get_val(current_data, "prix_mensuel"),
                    get_val(best_offer_data, "prix_mensuel"),
                ),
            ]
        elif c_type == "assurance_pno":
            rows = [
                (
                    "Assureur",
                    get_val(current_data, "assureur"),
                    get_val(best_offer_data, "assureur"),
                ),
                (
                    "Prime annuelle (€)",
                    get_val(current_data, "prime_annuelle"),
                    get_val(best_offer_data, "prime_annuelle"),
                ),
                (
                    "Franchise (€)",
                    get_val(current_data, "franchise"),
                    get_val(best_offer_data, "franchise"),
                ),
            ]
        elif c_type == "assurance_habitation":
            rows = [
                (
                    "Assureur",
                    get_val(current_data, "assureur"),
                    get_val(best_offer_data, "assureur"),
                ),
                (
                    "Prime annuelle (€)",
                    get_val(current_data, "tarifs", "prime_annuelle_ttc"),
                    get_val(best_offer_data, "tarifs", "prime_annuelle_ttc"),
                ),
                (
                    "Franchise (€)",
                    get_val(current_data, "franchises", "franchise_generale"),
                    get_val(best_offer_data, "franchises", "franchise_generale"),
                ),
                (
                    "Garanties",
                    len(get_val(current_data, "garanties_incluses") or []),
                    len(get_val(best_offer_data, "garanties_incluses") or []),
                ),
            ]

        if rows:
            df_compare = pd.DataFrame(
                rows, columns=["Caractéristique", "Mon Contrat", "Meilleure Offre Marché"]
            )
            # Convertir en string pour éviter les erreurs PyArrow avec les types mixtes
            df_compare = df_compare.astype(str)
            st.dataframe(df_compare, use_container_width=True, hide_index=True)

        with st.expander("Voir les détails complets (JSON)", expanded=False):
            st.json(best_offer_data)

    # Réponse complète
    with st.expander("📄 Réponse complète de l'IA"):
        st.json(full_result)


def display_competitor_comparison(comparison):
    """Affiche les résultats d'une comparaison avec concurrent."""
    result = comparison.comparison_result

    # Recommandation principale
    recommandation = result.get("recommandation", "")

    if "garder" in recommandation.lower() or "actuel" in recommandation.lower():
        st.markdown(
            f'<div class="alert-success">'
            f"<h4>✅ Recommandation : {recommandation}</h4>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="alert-info">' f"<h4>💡 Recommandation : {recommandation}</h4>" f"</div>",
            unsafe_allow_html=True,
        )

    # Justification
    st.markdown("#### 📝 Justification")
    st.write(result.get("justification", ""))

    # Comparaison des prix
    st.markdown("#### 💰 Comparaison des prix")

    comp_prix = result.get("comparaison_prix", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Contrat actuel", f"{comp_prix.get('prix_actuel', 0):.2f} €")

    with col2:
        st.metric("Offre concurrente", f"{comp_prix.get('prix_concurrent', 0):.2f} €")

    with col3:
        economie = comp_prix.get("economie_potentielle", 0)
        st.metric(
            "Économie potentielle",
            f"{abs(economie):.2f} €",
            delta=LABEL_ECONOMY if economie > 0 else LABEL_SURCOST,
        )

    # Comparaison des services
    st.markdown("#### 🔍 Comparaison des services")

    comp_services = result.get("comparaison_services", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**✅ Avantages contrat actuel**")
        for avantage in comp_services.get("avantages_contrat_actuel", []):
            st.markdown(f"- {avantage}")

    with col2:
        st.markdown("**✅ Avantages offre concurrente**")
        for avantage in comp_services.get("avantages_concurrent", []):
            st.markdown(f"- {avantage}")

    # Services identiques
    if comp_services.get("services_identiques"):
        st.markdown("**🟰 Services identiques**")
        st.write(", ".join(comp_services["services_identiques"]))

    # Points de vigilance
    if result.get("points_vigilance"):
        st.markdown("#### ⚠️ Points de vigilance")
        for point in result["points_vigilance"]:
            st.warning(point)

    # Scores globaux
    st.markdown("#### 📊 Scores globaux")

    scores = result.get("score_global", {})

    col1, col2 = st.columns(2)

    with col1:
        score_actuel = scores.get("contrat_actuel", 0)
        st.metric("Contrat actuel", f"{score_actuel}/10")
        st.progress(score_actuel / 10)

    with col2:
        score_concurrent = scores.get("offre_concurrente", 0)
        st.metric("Offre concurrente", f"{score_concurrent}/10")
        st.progress(score_concurrent / 10)

    # Données du concurrent
    with st.expander("📄 Données extraites du devis concurrent"):
        st.json(comparison.competitor_data)

    # Réponse complète
    with st.expander("📄 Analyse complète de l'IA"):
        st.json(result)


def handle_market_analysis(contract_service, contract_id):
    """Gère l'analyse de marché."""
    st.markdown("#### 📊 Analyse de marché")
    st.info(
        "L'IA va analyser votre contrat et le comparer avec les offres "
        "actuelles disponibles sur le marché français."
    )

    if st.button("🚀 Lancer l'analyse", type="primary", use_container_width=True):
        with st.spinner("Analyse en cours... (cela peut prendre 30 secondes)"):
            try:
                comparison = contract_service.compare_with_market(contract_id)

                st.success("✅ Analyse terminée !")

                # Afficher les résultats
                display_market_analysis(comparison)

            except Exception as e:
                st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
                st.exception(e)


def handle_competitor_comparison(contract_service, contract_id):
    """Gère la comparaison avec un concurrent."""
    st.markdown("#### 🆚 Comparer avec un devis concurrent")
    st.info(
        "Uploadez un devis concurrent au format PDF. "
        "L'IA va extraire les données et comparer les deux offres."
    )

    competitor_file = st.file_uploader(
        "Choisissez le PDF du devis concurrent", type=["pdf"], key="competitor_upload"
    )

    if competitor_file is not None:
        st.success(f"✅ Fichier chargé : {competitor_file.name}")

        if st.button("🚀 Comparer les offres", type="primary", use_container_width=True):
            with st.spinner("Comparaison en cours... (cela peut prendre 45 secondes)"):
                try:
                    competitor_bytes = competitor_file.read()

                    comparison = contract_service.compare_with_competitor(
                        contract_id=contract_id,
                        competitor_pdf_bytes=competitor_bytes,
                        competitor_filename=competitor_file.name,
                    )

                    st.success("✅ Comparaison terminée !")

                    # Afficher les résultats
                    display_competitor_comparison(comparison)

                except Exception as e:
                    st.error(f"❌ Erreur lors de la comparaison : {str(e)}")
                    st.exception(e)


if __name__ == "__main__":
    show()

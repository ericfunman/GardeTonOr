
import streamlit as st
import pandas as pd
from src.config import DATE_FORMAT, LABEL_ECONOMY, LABEL_SURCOST

def _display_recommendation(result):
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

def _display_financial_metrics(result):
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

def _display_similar_offers(result):
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

def _get_val(data, *keys):
    res = data
    for k in keys:
        if isinstance(res, dict):
            res = res.get(k)
        else:
            return None
    return res

def _build_comparison_rows(c_type, current_data, best_offer_data):
    rows = []
    if c_type == "electricite":
        rows = [
            (
                "Fournisseur",
                _get_val(current_data, "fournisseur"),
                _get_val(best_offer_data, "fournisseur"),
            ),
            (
                "Abonnement (€/mois)",
                _get_val(current_data, "electricite", "tarifs", "abonnement_mensuel_ttc")
                or _get_val(current_data, "prix_abonnement_mensuel"),
                _get_val(best_offer_data, "electricite", "tarifs", "abonnement_mensuel_ttc")
                or _get_val(best_offer_data, "prix_abonnement_mensuel"),
            ),
            (
                "Prix kWh (€)",
                _get_val(current_data, "electricite", "tarifs", "prix_kwh_ttc")
                or _get_val(current_data, "prix_kwh", "base"),
                _get_val(best_offer_data, "electricite", "tarifs", "prix_kwh_ttc")
                or _get_val(best_offer_data, "prix_kwh", "base"),
            ),
            (
                "Coût annuel estimé (€)",
                _get_val(current_data, "electricite", "budget_annuel_estime_ttc")
                or _get_val(current_data, "estimation_facture_annuelle"),
                _get_val(best_offer_data, "electricite", "budget_annuel_estime_ttc")
                or _get_val(best_offer_data, "estimation_facture_annuelle"),
            ),
        ]
    elif c_type == "gaz":
        rows = [
            (
                "Fournisseur",
                _get_val(current_data, "fournisseur"),
                _get_val(best_offer_data, "fournisseur"),
            ),
            (
                "Abonnement (€/mois)",
                _get_val(current_data, "gaz", "tarifs", "abonnement_mensuel_ttc")
                or _get_val(current_data, "prix_abonnement_mensuel"),
                _get_val(best_offer_data, "gaz", "tarifs", "abonnement_mensuel_ttc")
                or _get_val(best_offer_data, "prix_abonnement_mensuel"),
            ),
            (
                "Prix kWh (€)",
                _get_val(current_data, "gaz", "tarifs", "prix_kwh_ttc")
                or _get_val(current_data, "prix_kwh"),
                _get_val(best_offer_data, "gaz", "tarifs", "prix_kwh_ttc")
                or _get_val(best_offer_data, "prix_kwh"),
            ),
            (
                "Coût annuel estimé (€)",
                _get_val(current_data, "gaz", "budget_annuel_estime_ttc")
                or _get_val(current_data, "estimation_facture_annuelle"),
                _get_val(best_offer_data, "gaz", "budget_annuel_estime_ttc")
                or _get_val(best_offer_data, "estimation_facture_annuelle"),
            ),
        ]
    elif c_type == "telephone":
        rows = [
            (
                "Fournisseur",
                _get_val(current_data, "fournisseur"),
                _get_val(best_offer_data, "fournisseur"),
            ),
            (
                "Forfait",
                _get_val(current_data, "forfait_nom"),
                _get_val(best_offer_data, "forfait_nom"),
            ),
            (
                "Data (Go)",
                _get_val(current_data, "data_go"),
                _get_val(best_offer_data, "data_go"),
            ),
            (
                "Prix mensuel (€)",
                _get_val(current_data, "prix_mensuel"),
                _get_val(best_offer_data, "prix_mensuel"),
            ),
        ]
    elif c_type == "assurance_pno":
        rows = [
            (
                "Assureur",
                _get_val(current_data, "assureur"),
                _get_val(best_offer_data, "assureur"),
            ),
            (
                "Prime annuelle (€)",
                _get_val(current_data, "prime_annuelle"),
                _get_val(best_offer_data, "prime_annuelle"),
            ),
            (
                "Franchise (€)",
                _get_val(current_data, "franchise"),
                _get_val(best_offer_data, "franchise"),
            ),
        ]
    elif c_type == "assurance_habitation":
        rows = [
            (
                "Assureur",
                _get_val(current_data, "assureur"),
                _get_val(best_offer_data, "assureur"),
            ),
            (
                "Prime annuelle (€)",
                _get_val(current_data, "tarifs", "prime_annuelle_ttc"),
                _get_val(best_offer_data, "tarifs", "prime_annuelle_ttc"),
            ),
            (
                "Franchise (€)",
                _get_val(current_data, "franchises", "franchise_generale"),
                _get_val(best_offer_data, "franchises", "franchise_generale"),
            ),
            (
                "Garanties",
                len(_get_val(current_data, "garanties_incluses") or []),
                len(_get_val(best_offer_data, "garanties_incluses") or []),
            ),
        ]
    return rows

def _display_comparison_table(comparison, best_offer_data):
    if best_offer_data:
        st.markdown("#### 🆚 Tableau comparatif")

        current_data = comparison.contract.contract_data
        c_type = comparison.contract.contract_type
        rows = _build_comparison_rows(c_type, current_data, best_offer_data)

        if rows:
            df_compare = pd.DataFrame(
                rows, columns=["Caractéristique", "Mon Contrat", "Meilleure Offre Marché"]
            )
            # Convertir en string pour éviter les erreurs PyArrow avec les types mixtes
            df_compare = df_compare.astype(str)
            st.dataframe(df_compare, use_container_width=True, hide_index=True)

        with st.expander("Voir les détails complets (JSON)", expanded=False):
            st.json(best_offer_data)

def display_market_analysis(comparison):
    """Affiche les résultats d'une analyse de marché."""
    full_result = comparison.comparison_result

    # Support for new structure with "analyse" and "meilleure_offre"
    result = full_result.get("analyse", full_result)
    best_offer_data = full_result.get("meilleure_offre")

    _display_recommendation(result)

    # Justification
    st.markdown("#### 📝 Justification")
    st.write(result.get("justification", ""))

    _display_financial_metrics(result)
    _display_similar_offers(result)
    _display_comparison_table(comparison, best_offer_data)

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
            f'<div class="alert-info"><h4>💡 Recommandation : {recommandation}</h4></div>',
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

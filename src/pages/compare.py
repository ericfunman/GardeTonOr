"""Page de comparaison de contrats."""
import streamlit as st
import json

from src.database import get_db
from src.services import OpenAIService, PDFService, ContractService
from src.config import CONTRACT_TYPES


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
        if "compare_contract_id" in st.session_state:
            try:
                default_index = [c.id for c in contracts].index(st.session_state["compare_contract_id"])
                del st.session_state["compare_contract_id"]
            except ValueError:
                pass
        
        selected_contract = st.selectbox(
            "Contrat",
            options=contracts,
            format_func=lambda x: f"{CONTRACT_TYPES.get(x.contract_type)} - {x.provider} (Date anniversaire: {x.anniversary_date.strftime('%d/%m/%Y')})",
            index=default_index
        )
        
        if selected_contract:
            # Afficher les détails du contrat
            with st.expander("📄 Détails du contrat", expanded=False):
                st.json(selected_contract.contract_data)
            
            st.divider()
            
            # Type de comparaison
            st.markdown("### 🔍 Type de comparaison")
            
            comparison_type = st.radio(
                "Choisissez le type de comparaison",
                ["📊 Analyse de marché", "🆚 Comparer avec un devis concurrent"],
                label_visibility="collapsed"
            )
            
            # Analyse de marché
            if comparison_type == "📊 Analyse de marché":
                st.markdown("#### 📊 Analyse de marché")
                st.info(
                    "L'IA va analyser votre contrat et le comparer avec les offres "
                    "actuelles disponibles sur le marché français."
                )
                
                if st.button("🚀 Lancer l'analyse", type="primary", use_container_width=True):
                    with st.spinner("Analyse en cours... (cela peut prendre 30 secondes)"):
                        try:
                            comparison = contract_service.compare_with_market(selected_contract.id)
                            
                            st.success("✅ Analyse terminée !")
                            
                            # Afficher les résultats
                            display_market_analysis(comparison)
                        
                        except Exception as e:
                            st.error(f"❌ Erreur lors de l'analyse : {str(e)}")
                            st.exception(e)
            
            # Comparaison avec concurrent
            else:
                st.markdown("#### 🆚 Comparer avec un devis concurrent")
                st.info(
                    "Uploadez un devis concurrent au format PDF. "
                    "L'IA va extraire les données et comparer les deux offres."
                )
                
                competitor_file = st.file_uploader(
                    "Choisissez le PDF du devis concurrent",
                    type=["pdf"],
                    key="competitor_upload"
                )
                
                if competitor_file is not None:
                    st.success(f"✅ Fichier chargé : {competitor_file.name}")
                    
                    if st.button("🚀 Comparer les offres", type="primary", use_container_width=True):
                        with st.spinner("Comparaison en cours... (cela peut prendre 45 secondes)"):
                            try:
                                competitor_bytes = competitor_file.read()
                                
                                comparison = contract_service.compare_with_competitor(
                                    contract_id=selected_contract.id,
                                    competitor_pdf_bytes=competitor_bytes,
                                    competitor_filename=competitor_file.name
                                )
                                
                                st.success("✅ Comparaison terminée !")
                                
                                # Afficher les résultats
                                display_competitor_comparison(comparison)
                            
                            except Exception as e:
                                st.error(f"❌ Erreur lors de la comparaison : {str(e)}")
                                st.exception(e)
            
            # Historique des comparaisons pour ce contrat
            st.divider()
            st.markdown("### 📜 Historique des comparaisons")
            
            comparisons = contract_service.get_contract_comparisons(selected_contract.id)
            
            if comparisons:
                for i, comp in enumerate(comparisons):
                    with st.expander(
                        f"{'📊' if comp.comparison_type == 'market_analysis' else '🆚'} "
                        f"{comp.created_at.strftime('%d/%m/%Y %H:%M')} - {comp.analysis_summary[:50]}...",
                        expanded=(i == 0)
                    ):
                        if comp.comparison_type == "market_analysis":
                            display_market_analysis(comp)
                        else:
                            display_competitor_comparison(comp)
            else:
                st.info("Aucune comparaison effectuée pour ce contrat")


def display_market_analysis(comparison):
    """Affiche les résultats d'une analyse de marché."""
    result = comparison.comparison_result
    
    # Recommandation principale
    recommandation = result.get("recommandation", "")
    niveau = result.get("niveau_competitivite", "")
    
    if "garder" in recommandation.lower():
        st.markdown(
            f'<div class="alert-success">'
            f'<h4>✅ Recommandation : {recommandation}</h4>'
            f'<p>Niveau de compétitivité : <strong>{niveau}</strong></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="alert-warning">'
            f'<h4>⚠️ Recommandation : {recommandation}</h4>'
            f'<p>Niveau de compétitivité : <strong>{niveau}</strong></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Justification
    st.markdown("#### 📝 Justification")
    st.write(result.get("justification", ""))
    
    # Métriques financières
    st.markdown("#### 💰 Analyse financière")
    
    col1, col2, col3 = st.columns(3)
    
    tarif_actuel = result.get("tarif_actuel") or result.get("prime_actuelle_annuelle", 0)
    estimation = result.get("estimation_marche", {})
    economie_mensuelle = result.get("economie_potentielle_mensuelle", 0)
    economie_annuelle = result.get("economie_potentielle_annuelle", 0)
    
    with col1:
        st.metric("Tarif actuel", f"{tarif_actuel:.2f} €")
    
    with col2:
        tarif_moyen = estimation.get("tarif_moyen") or estimation.get("prime_moyenne", 0)
        delta = tarif_actuel - tarif_moyen if tarif_moyen else 0
        st.metric(
            "Tarif moyen marché",
            f"{tarif_moyen:.2f} €",
            delta=f"{delta:.2f} €" if delta else None,
            delta_color="inverse"
        )
    
    with col3:
        if economie_annuelle:
            st.metric(
                "Économie potentielle/an",
                f"{economie_annuelle:.2f} €",
                delta="Économie" if economie_annuelle > 0 else "Surcoût"
            )
        elif economie_mensuelle:
            st.metric(
                "Économie potentielle/mois",
                f"{economie_mensuelle:.2f} €",
                delta="Économie" if economie_mensuelle > 0 else "Surcoût"
            )
    
    # Offres similaires
    if "offres_similaires" in result and result["offres_similaires"]:
        st.markdown("#### 🏪 Offres similaires sur le marché")
        
        for offre in result["offres_similaires"]:
            with st.container():
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**{offre.get('fournisseur') or offre.get('assureur')}**")
                    st.caption(offre.get("forfait", ""))
                    
                    if offre.get("avantages"):
                        st.markdown("✅ " + ", ".join(offre["avantages"][:3]))
                    if offre.get("inconvenients"):
                        st.markdown("❌ " + ", ".join(offre["inconvenients"][:2]))
                
                with col2:
                    prix = offre.get("prix_mensuel") or offre.get("prime_annuelle", 0)
                    unite = "/mois" if offre.get("prix_mensuel") else "/an"
                    st.metric("Prix", f"{prix:.2f} €{unite}")
                
                st.divider()
    
    # Réponse complète
    with st.expander("📄 Réponse complète de l'IA"):
        st.json(result)


def display_competitor_comparison(comparison):
    """Affiche les résultats d'une comparaison avec concurrent."""
    result = comparison.comparison_result
    
    # Recommandation principale
    recommandation = result.get("recommandation", "")
    
    if "garder" in recommandation.lower() or "actuel" in recommandation.lower():
        st.markdown(
            f'<div class="alert-success">'
            f'<h4>✅ Recommandation : {recommandation}</h4>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="alert-info">'
            f'<h4>💡 Recommandation : {recommandation}</h4>'
            f'</div>',
            unsafe_allow_html=True
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
            delta="Économie" if economie > 0 else "Surcoût"
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


if __name__ == "__main__":
    show()

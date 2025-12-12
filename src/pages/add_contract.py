"""Page d'ajout de contrat."""
import streamlit as st
from datetime import datetime

from src.database import get_db
from src.services import OpenAIService, PDFService, ContractService
from src.config import CONTRACT_TYPES
from src.pages.add_contract_forms import (
    render_dual_energy_form,
    render_telephone_form,
    render_insurance_pno_form,
    render_insurance_habitation_form,
    render_electricity_form,
    render_gas_form,
)


def handle_extraction(uploaded_file, contract_type):
    """Gère l'extraction des données du fichier uploadé."""
    with get_db() as db:
        openai_service = OpenAIService()
        pdf_service = PDFService()
        contract_service = ContractService(db, openai_service, pdf_service)

        # Lire le contenu du PDF
        # Si le fichier a déjà été lu, on doit remettre le curseur au début
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        pdf_bytes = uploaded_file.read()

        # Extraire les données
        extracted_data, _ = contract_service.extract_and_create_contract(
            pdf_bytes=pdf_bytes,
            filename=uploaded_file.name,
            contract_type=contract_type,
        )

        return extracted_data, pdf_bytes


def show():
    """Affiche la page d'ajout de contrat."""
    st.title("➕ Ajouter un contrat")
    st.markdown("Importez un PDF de contrat pour extraction automatique des données")

    # Étape 1 : Upload du fichier et sélection du type
    st.markdown("### 📄 Étape 1 : Importer le document")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choisissez un fichier PDF", type=["pdf"], help="Le contrat au format PDF"
        )

    with col2:
        contract_type = st.selectbox(
            "Type de contrat",
            options=list(CONTRACT_TYPES.keys()),
            format_func=lambda x: CONTRACT_TYPES[x],
        )

    if uploaded_file is not None:
        st.success(f"✅ Fichier chargé : {uploaded_file.name}")

        # Bouton d'extraction
        if st.button("🔍 Extraire les données", type="primary", use_container_width=True):
            with st.spinner("Extraction en cours... (cela peut prendre quelques secondes)"):
                try:
                    extracted_data, pdf_bytes = handle_extraction(uploaded_file, contract_type)

                    # Stocker dans session state pour validation
                    st.session_state["extracted_data"] = extracted_data
                    st.session_state["pdf_bytes"] = pdf_bytes
                    st.session_state["filename"] = uploaded_file.name
                    st.session_state["contract_type"] = contract_type
                    st.session_state["extraction_done"] = True

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur lors de l'extraction : {str(e)}")
                    st.exception(e)

    # Étape 2 : Validation des données extraites
    if st.session_state.get("extraction_done"):
        st.divider()
        st.markdown("### ✅ Étape 2 : Valider les données extraites")

        extracted_data = st.session_state["extracted_data"]
        contract_type = st.session_state["contract_type"]

        # DEBUG: Afficher les données brutes pour comprendre le problème
        with st.expander("🔍 Voir les données brutes (Debug)", expanded=False):
            st.json(extracted_data)

        # Logique de détection automatique
        if contract_type == "auto":
            has_elec = extracted_data.get("electricite") is not None and (
                extracted_data.get("electricite", {}).get("pdl")
                or extracted_data.get("electricite", {}).get("matricule_compteur")
            )
            has_gaz = extracted_data.get("gaz") is not None and (
                extracted_data.get("gaz", {}).get("pce")
                or extracted_data.get("gaz", {}).get("matricule_compteur")
            )

            if has_elec and has_gaz:
                st.success("✨ Deux contrats détectés : Électricité et Gaz")
                contract_type = "electricite_gaz"
            elif has_elec:
                st.success("✨ Contrat d'électricité détecté")
                contract_type = "electricite"
            elif has_gaz:
                st.success("✨ Contrat de gaz détecté")
                contract_type = "gaz"
            else:
                st.warning(
                    "⚠️ Impossible de déterminer le type précis. Affichage par défaut (Électricité)."
                )
                contract_type = "electricite"

        st.info("Vérifiez et modifiez si nécessaire les données extraites par l'IA")

        # Formulaire de validation selon le type de contrat
        with st.form("validate_contract"):
            if contract_type == "electricite_gaz":
                data_elec, data_gaz = render_dual_energy_form(extracted_data)

            elif contract_type == "telephone":
                validated_data = render_telephone_form(extracted_data)

            elif contract_type == "assurance_pno":
                validated_data = render_insurance_pno_form(extracted_data)

            elif contract_type == "assurance_habitation":
                validated_data = render_insurance_habitation_form(extracted_data)

            elif contract_type == "electricite":
                validated_data = render_electricity_form(extracted_data)

            elif contract_type == "gaz":
                validated_data = render_gas_form(extracted_data)

            is_simulation = st.checkbox(
                "Ceci est une simulation / devis concurrent (ne pas afficher dans mes contrats principaux)",
                value=False,
            )

            # Boutons de soumission
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button(
                    "✅ Valider et enregistrer", type="primary", use_container_width=True
                )
            with col2:
                cancel = st.form_submit_button("❌ Annuler", use_container_width=True)

            if submit:
                try:
                    with get_db() as db:
                        openai_service = OpenAIService()
                        pdf_service = PDFService()
                        contract_service = ContractService(db, openai_service, pdf_service)

                        if contract_type == "electricite_gaz":
                            # Création du contrat Électricité
                            contract_e = contract_service.create_contract(
                                contract_type="electricite",
                                provider=data_elec["provider"],
                                start_date=data_elec["date_debut"],
                                anniversary_date=data_elec["date_anniv"],
                                contract_data={
                                    "fournisseur": data_elec["provider"],
                                    "pdl": data_elec["pdl"],
                                    "puissance_souscrite_kva": data_elec["puissance"],
                                    "prix_abonnement_mensuel": data_elec["prix_abo"],
                                    "prix_kwh": {"base": data_elec["prix_kwh"]},
                                    "estimation_conso_annuelle_kwh": data_elec["conso_annuelle"],
                                    "estimation_facture_annuelle": (data_elec["prix_abo"] * 12)
                                    + (data_elec["prix_kwh"] * data_elec["conso_annuelle"]),
                                },
                                pdf_bytes=st.session_state["pdf_bytes"],
                                filename=st.session_state["filename"],
                                is_simulation=is_simulation,
                            )

                            # Création du contrat Gaz
                            contract_g = contract_service.create_contract(
                                contract_type="gaz",
                                provider=data_gaz["provider"],
                                start_date=data_gaz["date_debut"],
                                anniversary_date=data_gaz["date_anniv"],
                                contract_data={
                                    "fournisseur": data_gaz["provider"],
                                    "pce": data_gaz["pce"],
                                    "zone_tarifaire": data_gaz["zone"],
                                    "prix_abonnement_mensuel": data_gaz["prix_abo"],
                                    "prix_kwh": data_gaz["prix_kwh"],
                                    "estimation_conso_annuelle_kwh": data_gaz["conso_annuelle"],
                                    "estimation_facture_annuelle": (data_gaz["prix_abo"] * 12)
                                    + (data_gaz["prix_kwh"] * data_gaz["conso_annuelle"]),
                                },
                                pdf_bytes=st.session_state["pdf_bytes"],
                                filename=st.session_state["filename"],
                                is_simulation=is_simulation,
                            )
                            st.success(
                                f"✅ 2 Contrats enregistrés avec succès ! (IDs: {contract_e.id}, {contract_g.id})"
                            )

                        else:
                            # Créer le contrat unique
                            # Si le type était "auto" mais résolu en un seul type, on utilise le type résolu
                            final_type = (
                                contract_type
                                if contract_type != "auto"
                                else st.session_state["contract_type"]
                            )

                            contract = contract_service.create_contract(
                                contract_type=final_type,
                                provider=validated_data.get("fournisseur")
                                or validated_data.get("assureur"),
                                start_date=datetime.strptime(
                                    validated_data.get("date_debut")
                                    or validated_data.get("date_effet"),
                                    "%Y-%m-%d",
                                ),
                                anniversary_date=datetime.strptime(
                                    validated_data["date_anniversaire"], "%Y-%m-%d"
                                ),
                                contract_data=validated_data,
                                pdf_bytes=st.session_state["pdf_bytes"],
                                filename=st.session_state["filename"],
                                is_simulation=is_simulation,
                            )

                            st.success(f"✅ Contrat enregistré avec succès ! (ID: {contract.id})")

                        # Nettoyer la session
                        for key in [
                            "extracted_data",
                            "pdf_bytes",
                            "filename",
                            "contract_type",
                            "extraction_done",
                        ]:
                            if key in st.session_state:
                                del st.session_state[key]

                        st.balloons()

                        # Rediriger vers le dashboard après 2 secondes
                        st.info("Redirection vers le dashboard...")
                        import time

                        time.sleep(2)
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur lors de l'enregistrement : {str(e)}")
                    st.exception(e)

            if cancel:
                # Nettoyer la session
                for key in [
                    "extracted_data",
                    "pdf_bytes",
                    "filename",
                    "contract_type",
                    "extraction_done",
                ]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()


if __name__ == "__main__":
    show()

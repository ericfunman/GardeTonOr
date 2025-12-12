"""Page d'ajout de contrat."""
import streamlit as st
from datetime import datetime

from src.database import get_db
from src.services import OpenAIService, PDFService, ContractService
from src.config import CONTRACT_TYPES


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
                    with get_db() as db:
                        openai_service = OpenAIService()
                        pdf_service = PDFService()
                        contract_service = ContractService(db, openai_service, pdf_service)

                        # Lire le contenu du PDF
                        pdf_bytes = uploaded_file.read()

                        # Extraire les données
                        extracted_data, pdf_text = contract_service.extract_and_create_contract(
                            pdf_bytes=pdf_bytes,
                            filename=uploaded_file.name,
                            contract_type=contract_type,
                        )

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
                tab_elec, tab_gaz = st.tabs(["⚡ Électricité", "🔥 Gaz"])

                # --- ELECTRICITE ---
                with tab_elec:
                    st.subheader("Contrat Électricité")
                    col1_e, col2_e = st.columns(2)
                    with col1_e:
                        provider_e = st.text_input(
                            "Fournisseur (Elec)",
                            value=extracted_data.get("fournisseur", ""),
                            key="prov_e",
                        )
                        pdl = st.text_input(
                            "PDL (Point de Livraison)",
                            value=extracted_data.get("electricite", {}).get("pdl", ""),
                            key="pdl_dual",
                        )
                        puissance = st.number_input(
                            "Puissance (kVA)",
                            value=float(
                                extracted_data.get("electricite", {}).get(
                                    "puissance_souscrite_kva", 0
                                )
                                or 0
                            ),
                            min_value=0.0,
                            key="puis_dual",
                        )
                        prix_abo_e = st.number_input(
                            "Abonnement mensuel (€)",
                            value=float(
                                extracted_data.get("electricite", {})
                                .get("tarifs", {})
                                .get("abonnement_mensuel_ttc", 0)
                                or 0
                            ),
                            min_value=0.0,
                            step=0.01,
                            key="abo_e_dual",
                        )

                    with col2_e:
                        date_debut_e = st.date_input(
                            "Date de début (Elec)",
                            value=datetime.now(),  # TODO: Parse date
                            key="date_deb_e_dual",
                        )
                        date_anniv_e = st.date_input(
                            "Date anniversaire (Elec)",
                            value=datetime.now(),  # TODO: Parse date
                            key="date_ann_e_dual",
                        )
                        prix_kwh_e = st.number_input(
                            "Prix kWh (€)",
                            value=float(
                                extracted_data.get("electricite", {})
                                .get("tarifs", {})
                                .get("prix_kwh_ttc", 0)
                                or 0
                            ),
                            min_value=0.0,
                            step=0.0001,
                            format="%.4f",
                            key="kwh_e_dual",
                        )
                        conso_annuelle_e = st.number_input(
                            "Conso annuelle estimée (kWh)",
                            value=float(
                                extracted_data.get("electricite", {}).get(
                                    "consommation_estimee_annuelle_kwh", 0
                                )
                                or 0
                            ),
                            min_value=0.0,
                            key="conso_e_dual",
                        )

                # --- GAZ ---
                with tab_gaz:
                    st.subheader("Contrat Gaz")
                    col1_g, col2_g = st.columns(2)
                    with col1_g:
                        provider_g = st.text_input(
                            "Fournisseur (Gaz)",
                            value=extracted_data.get("fournisseur", ""),
                            key="prov_g",
                        )
                        pce = st.text_input(
                            "PCE (Point Comptage)",
                            value=extracted_data.get("gaz", {}).get("pce", ""),
                            key="pce_dual",
                        )
                        zone_gaz = st.text_input(
                            "Zone tarifaire",
                            value=str(extracted_data.get("gaz", {}).get("zone_tarifaire", "")),
                            key="zone_g_dual",
                        )
                        prix_abo_g = st.number_input(
                            "Abonnement mensuel (€)",
                            value=float(
                                extracted_data.get("gaz", {})
                                .get("tarifs", {})
                                .get("abonnement_mensuel_ttc", 0)
                                or 0
                            ),
                            min_value=0.0,
                            step=0.01,
                            key="abo_g_dual",
                        )

                    with col2_g:
                        date_debut_g = st.date_input(
                            "Date de début (Gaz)",
                            value=datetime.now(),  # TODO: Parse date
                            key="date_deb_g_dual",
                        )
                        date_anniv_g = st.date_input(
                            "Date anniversaire (Gaz)",
                            value=datetime.now(),  # TODO: Parse date
                            key="date_ann_g_dual",
                        )
                        prix_kwh_g = st.number_input(
                            "Prix kWh (€)",
                            value=float(
                                extracted_data.get("gaz", {})
                                .get("tarifs", {})
                                .get("prix_kwh_ttc", 0)
                                or 0
                            ),
                            min_value=0.0,
                            step=0.0001,
                            format="%.4f",
                            key="kwh_g_dual",
                        )
                        conso_annuelle_g = st.number_input(
                            "Conso annuelle estimée (kWh)",
                            value=float(
                                extracted_data.get("gaz", {}).get(
                                    "consommation_estimee_annuelle_kwh", 0
                                )
                                or 0
                            ),
                            min_value=0.0,
                            key="conso_g_dual",
                        )

            if contract_type == "telephone":
                col1, col2 = st.columns(2)

                with col1:
                    provider = st.text_input(
                        "Fournisseur", value=extracted_data.get("fournisseur", "")
                    )
                    forfait_nom = st.text_input(
                        "Nom du forfait", value=extracted_data.get("forfait_nom", "")
                    )
                    data_go = st.number_input(
                        "Data (Go)", value=float(extracted_data.get("data_go", 0)), min_value=0.0
                    )
                    prix_mensuel = st.number_input(
                        "Prix mensuel (€)",
                        value=float(extracted_data.get("prix_mensuel", 0)),
                        min_value=0.0,
                        step=0.01,
                    )

                with col2:
                    minutes = st.text_input(
                        "Minutes", value=str(extracted_data.get("minutes", "illimité"))
                    )
                    sms = st.text_input("SMS", value=str(extracted_data.get("sms", "illimité")))
                    engagement_mois = st.number_input(
                        "Engagement (mois)",
                        value=int(extracted_data.get("engagement_mois", 0)),
                        min_value=0,
                    )

                    date_debut = st.date_input(
                        "Date de début",
                        value=datetime.strptime(
                            extracted_data.get("date_debut", datetime.now().strftime("%Y-%m-%d")),
                            "%Y-%m-%d",
                        ),
                    )
                    date_anniversaire = st.date_input(
                        "Date anniversaire",
                        value=datetime.strptime(
                            extracted_data.get(
                                "date_anniversaire", datetime.now().strftime("%Y-%m-%d")
                            ),
                            "%Y-%m-%d",
                        ),
                    )

                options = st.text_area(
                    "Options incluses", value="\n".join(extracted_data.get("options", []))
                )
                conditions = st.text_area(
                    "Conditions particulières",
                    value=extracted_data.get("conditions_particulieres", ""),
                )

                # Préparer les données validées
                validated_data = {
                    "fournisseur": provider,
                    "forfait_nom": forfait_nom,
                    "data_go": data_go,
                    "minutes": minutes,
                    "sms": sms,
                    "prix_mensuel": prix_mensuel,
                    "engagement_mois": engagement_mois,
                    "date_debut": date_debut.strftime("%Y-%m-%d"),
                    "date_anniversaire": date_anniversaire.strftime("%Y-%m-%d"),
                    "options": options.split("\n") if options else [],
                    "conditions_particulieres": conditions,
                }

            elif contract_type == "assurance_pno":
                col1, col2 = st.columns(2)

                with col1:
                    provider = st.text_input("Assureur", value=extracted_data.get("assureur", ""))
                    numero_contrat = st.text_input(
                        "Numéro de contrat", value=extracted_data.get("numero_contrat", "")
                    )

                    st.markdown("**Bien assuré**")
                    bien = extracted_data.get("bien_assure", {})
                    adresse = st.text_input("Adresse", value=bien.get("adresse", ""))
                    type_bien = st.text_input("Type de bien", value=bien.get("type", ""))
                    surface_m2 = st.number_input(
                        "Surface (m²)", value=float(bien.get("surface_m2", 0)), min_value=0.0
                    )
                    nombre_pieces = st.number_input(
                        "Nombre de pièces", value=int(bien.get("nombre_pieces", 0)), min_value=0
                    )

                with col2:
                    prime_annuelle = st.number_input(
                        "Prime annuelle (€)",
                        value=float(extracted_data.get("prime_annuelle", 0)),
                        min_value=0.0,
                        step=0.01,
                    )
                    prime_mensuelle = st.number_input(
                        "Prime mensuelle (€)",
                        value=float(extracted_data.get("prime_mensuelle", 0)),
                        min_value=0.0,
                        step=0.01,
                    )
                    franchise = st.number_input(
                        "Franchise (€)",
                        value=float(extracted_data.get("franchise", 0)),
                        min_value=0.0,
                        step=0.01,
                    )

                    date_effet = st.date_input(
                        "Date d'effet",
                        value=datetime.strptime(
                            extracted_data.get("date_effet", datetime.now().strftime("%Y-%m-%d")),
                            "%Y-%m-%d",
                        ),
                    )
                    date_anniversaire = st.date_input(
                        "Date anniversaire",
                        value=datetime.strptime(
                            extracted_data.get(
                                "date_anniversaire", datetime.now().strftime("%Y-%m-%d")
                            ),
                            "%Y-%m-%d",
                        ),
                    )

                st.markdown("**Garanties**")
                garanties = extracted_data.get("garanties", {})
                col1, col2 = st.columns(2)
                with col1:
                    incendie = st.number_input(
                        "Incendie (€)", value=float(garanties.get("incendie", 0)), min_value=0.0
                    )
                    degats_eaux = st.number_input(
                        "Dégâts des eaux (€)",
                        value=float(garanties.get("degats_des_eaux", 0)),
                        min_value=0.0,
                    )
                with col2:
                    vol = st.number_input(
                        "Vol (€)", value=float(garanties.get("vol", 0)), min_value=0.0
                    )
                    rc = st.number_input(
                        "Responsabilité civile (€)",
                        value=float(garanties.get("responsabilite_civile", 0)),
                        min_value=0.0,
                    )

                conditions = st.text_area(
                    "Conditions particulières",
                    value=extracted_data.get("conditions_particulieres", ""),
                )

                # Préparer les données validées
                validated_data = {
                    "assureur": provider,
                    "numero_contrat": numero_contrat,
                    "bien_assure": {
                        "adresse": adresse,
                        "type": type_bien,
                        "surface_m2": surface_m2,
                        "nombre_pieces": nombre_pieces,
                    },
                    "garanties": {
                        "incendie": incendie,
                        "degats_des_eaux": degats_eaux,
                        "vol": vol,
                        "responsabilite_civile": rc,
                    },
                    "franchise": franchise,
                    "prime_annuelle": prime_annuelle,
                    "prime_mensuelle": prime_mensuelle,
                    "date_effet": date_effet.strftime("%Y-%m-%d"),
                    "date_anniversaire": date_anniversaire.strftime("%Y-%m-%d"),
                    "conditions_particulieres": conditions,
                }

            elif contract_type == "assurance_habitation":
                col1, col2 = st.columns(2)

                with col1:
                    provider = st.text_input("Assureur", value=extracted_data.get("assureur", ""))
                    numero_contrat = st.text_input(
                        "Numéro de contrat", value=extracted_data.get("numero_contrat", "")
                    )

                    st.markdown("**Bien assuré**")
                    bien = extracted_data.get("bien_assure", {})
                    adresse = st.text_input("Adresse", value=bien.get("adresse", ""))
                    type_bien = st.text_input("Type de logement", value=bien.get("type_logement", ""))
                    surface_m2 = st.number_input(
                        "Surface (m²)", value=float(bien.get("surface_m2", 0) or 0), min_value=0.0
                    )
                    nombre_pieces = st.number_input(
                        "Nombre de pièces", value=int(bien.get("nombre_pieces", 0) or 0), min_value=0
                    )

                    st.markdown("**Équipements spécifiques**")
                    col_eq1, col_eq2 = st.columns(2)
                    with col_eq1:
                        cheminee = st.checkbox("Cheminée", value=bien.get("cheminee", False))
                        piscine = st.checkbox("Piscine", value=bien.get("piscine", False))
                    with col_eq2:
                        veranda = st.checkbox("Véranda", value=bien.get("veranda", False))
                        dependances = st.checkbox("Dépendances", value=bien.get("dependances", False))

                with col2:
                    tarifs = extracted_data.get("tarifs", {})
                    prime_annuelle = st.number_input(
                        "Prime annuelle (€)",
                        value=float(tarifs.get("prime_annuelle_ttc", 0) or 0),
                        min_value=0.0,
                        step=0.01,
                    )
                    prime_mensuelle = st.number_input(
                        "Prime mensuelle (€)",
                        value=float(tarifs.get("prime_mensuelle_ttc", 0) or 0),
                        min_value=0.0,
                        step=0.01,
                    )

                    franchises = extracted_data.get("franchises", {})
                    franchise = st.number_input(
                        "Franchise générale (€)",
                        value=float(franchises.get("franchise_generale", 0) or 0),
                        min_value=0.0,
                        step=0.01,
                    )

                    dates = extracted_data.get("dates", {})

                    # Helper pour parser les dates
                    def parse_date(date_str):
                        if not date_str:
                            return datetime.now()
                        for fmt in ["%d/%m/%Y", "%Y-%m-%d"]:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except ValueError:
                                continue
                        return datetime.now()

                    date_effet_val = parse_date(dates.get("date_debut", ""))
                    date_anniv_val = parse_date(dates.get("date_anniversaire", ""))

                    date_effet = st.date_input("Date d'effet", value=date_effet_val)
                    date_anniversaire = st.date_input("Date anniversaire", value=date_anniv_val)

                st.markdown("**Garanties incluses**")
                garanties_list = extracted_data.get("garanties_incluses", [])
                garanties_text = st.text_area("Liste des garanties", value=", ".join(garanties_list) if isinstance(garanties_list, list) else str(garanties_list))

                # Préparer les données validées
                validated_data = {
                    "assureur": provider,
                    "numero_contrat": numero_contrat,
                    "bien_assure": {
                        "adresse": adresse,
                        "type_logement": type_bien,
                        "surface_m2": surface_m2,
                        "nombre_pieces": nombre_pieces,
                        "cheminee": cheminee,
                        "piscine": piscine,
                        "veranda": veranda,
                        "dependances": dependances
                    },
                    "garanties_incluses": [g.strip() for g in garanties_text.split(",")] if garanties_text else [],
                    "tarifs": {
                        "prime_annuelle_ttc": prime_annuelle,
                        "prime_mensuelle_ttc": prime_mensuelle
                    },
                    "franchises": {
                        "franchise_generale": franchise
                    },
                    "dates": {
                        "date_debut": date_effet.strftime("%d/%m/%Y"),
                        "date_anniversaire": date_anniversaire.strftime("%d/%m/%Y")
                    }
                }

            elif contract_type == "electricite":
                elec_data = extracted_data.get("electricite", {})
                dates_data = extracted_data.get("dates", {})
                tarifs_data = elec_data.get("tarifs", {})
                adresses_data = extracted_data.get("adresses", {})

                col1, col2 = st.columns(2)

                with col1:
                    provider = st.text_input(
                        "Fournisseur", value=extracted_data.get("fournisseur", "")
                    )
                    numero_contrat = st.text_input(
                        "Numéro de contrat", value=extracted_data.get("numero_contrat", "")
                    )
                    type_offre = st.text_input(
                        "Type d'offre", value=elec_data.get("option_tarifaire", "")
                    )
                    puissance_kva = st.number_input(
                        "Puissance souscrite (kVA)",
                        value=float(elec_data.get("puissance_souscrite_kva") or 0),
                        min_value=0.0,
                    )
                    option_tarifaire = st.text_input(
                        "Option tarifaire", value=elec_data.get("option_tarifaire", "Base")
                    )
                    pdl = st.text_input("Numéro PDL", value=elec_data.get("pdl", ""))

                with col2:
                    prix_abo = st.number_input(
                        "Abonnement mensuel (€)",
                        value=float(tarifs_data.get("abonnement_mensuel_ttc") or 0),
                        min_value=0.0,
                        step=0.01,
                    )

                    prix_kwh_base = st.number_input(
                        "Prix kWh TTC (€)",
                        value=float(tarifs_data.get("prix_kwh_ttc") or 0),
                        min_value=0.0,
                        step=0.001,
                        format="%.4f",
                    )

                    conso_annuelle = st.number_input(
                        "Consommation annuelle (kWh)",
                        value=float(elec_data.get("consommation_estimee_annuelle_kwh") or 0),
                        min_value=0.0,
                    )

                    date_debut_str = dates_data.get("date_debut")
                    if not date_debut_str:
                        date_debut_val = datetime.now()
                    else:
                        try:
                            date_debut_val = datetime.strptime(date_debut_str, "%d/%m/%Y")
                        except ValueError:
                            date_debut_val = datetime.now()

                    date_debut = st.date_input(
                        "Date de début",
                        value=date_debut_val,
                    )

                    date_anniv_str = dates_data.get("date_anniversaire")
                    if not date_anniv_str:
                        date_anniv_val = datetime.now()
                    else:
                        try:
                            date_anniv_val = datetime.strptime(date_anniv_str, "%d/%m/%Y")
                        except ValueError:
                            date_anniv_val = datetime.now()

                    date_anniversaire = st.date_input(
                        "Date anniversaire",
                        value=date_anniv_val,
                    )

                adresse = st.text_input(
                    "Adresse de fourniture", value=adresses_data.get("site_de_consommation", "")
                )
                conditions = st.text_area(
                    "Conditions de résiliation",
                    value=extracted_data.get("conditions_resiliation", ""),
                )

                validated_data = {
                    "fournisseur": provider,
                    "numero_contrat": numero_contrat,
                    "type_offre": type_offre,
                    "puissance_souscrite_kva": puissance_kva,
                    "option_tarifaire": option_tarifaire,
                    "prix_abonnement_mensuel": prix_abo,
                    "prix_kwh": {"base": prix_kwh_base},
                    "adresse_fourniture": adresse,
                    "pdl": pdl,
                    "date_debut": date_debut.strftime("%Y-%m-%d"),
                    "date_anniversaire": date_anniversaire.strftime("%Y-%m-%d"),
                    "estimation_conso_annuelle_kwh": conso_annuelle,
                    "estimation_facture_annuelle": (prix_abo * 12)
                    + (prix_kwh_base * conso_annuelle),
                    "conditions_resiliation": conditions,
                }

            elif contract_type == "gaz":
                gaz_data = extracted_data.get("gaz", {})
                dates_data = extracted_data.get("dates", {})
                tarifs_data = gaz_data.get("tarifs", {})
                adresses_data = extracted_data.get("adresses", {})

                col1, col2 = st.columns(2)

                with col1:
                    provider = st.text_input(
                        "Fournisseur", value=extracted_data.get("fournisseur", "")
                    )
                    numero_contrat = st.text_input(
                        "Numéro de contrat", value=extracted_data.get("numero_contrat", "")
                    )
                    type_offre = st.text_input(
                        "Type d'offre", value=gaz_data.get("option_tarifaire", "")
                    )
                    classe_conso = st.text_input(
                        "Classe de consommation",
                        value=gaz_data.get("option_tarifaire", "Base"),
                    )
                    pce = st.text_input("Numéro PCE", value=gaz_data.get("pce", ""))

                with col2:
                    prix_abo = st.number_input(
                        "Abonnement mensuel (€)",
                        value=float(tarifs_data.get("abonnement_mensuel_ttc") or 0),
                        min_value=0.0,
                        step=0.01,
                    )
                    prix_kwh = st.number_input(
                        "Prix kWh (€)",
                        value=float(tarifs_data.get("prix_kwh_ttc") or 0),
                        min_value=0.0,
                        step=0.001,
                        format="%.4f",
                    )

                    conso_annuelle = st.number_input(
                        "Consommation annuelle (kWh)",
                        value=float(gaz_data.get("consommation_estimee_annuelle_kwh") or 0),
                        min_value=0.0,
                    )

                    date_debut_str = dates_data.get("date_debut")
                    if not date_debut_str:
                        date_debut_val = datetime.now()
                    else:
                        try:
                            date_debut_val = datetime.strptime(date_debut_str, "%d/%m/%Y")
                        except ValueError:
                            date_debut_val = datetime.now()

                    date_debut = st.date_input(
                        "Date de début",
                        value=date_debut_val,
                    )

                    date_anniv_str = dates_data.get("date_anniversaire")
                    if not date_anniv_str:
                        date_anniv_val = datetime.now()
                    else:
                        try:
                            date_anniv_val = datetime.strptime(date_anniv_str, "%d/%m/%Y")
                        except ValueError:
                            date_anniv_val = datetime.now()

                    date_anniversaire = st.date_input(
                        "Date anniversaire",
                        value=date_anniv_val,
                    )

                adresse = st.text_input(
                    "Adresse de fourniture", value=adresses_data.get("site_de_consommation", "")
                )
                conditions = st.text_area(
                    "Conditions de résiliation",
                    value=extracted_data.get("conditions_resiliation", ""),
                )

                validated_data = {
                    "fournisseur": provider,
                    "numero_contrat": numero_contrat,
                    "type_offre": type_offre,
                    "classe_consommation": classe_conso,
                    "prix_abonnement_mensuel": prix_abo,
                    "prix_kwh": prix_kwh,
                    "adresse_fourniture": adresse,
                    "pce": pce,
                    "date_debut": date_debut.strftime("%Y-%m-%d"),
                    "date_anniversaire": date_anniversaire.strftime("%Y-%m-%d"),
                    "estimation_conso_annuelle_kwh": conso_annuelle,
                    "estimation_facture_annuelle": (prix_abo * 12) + (prix_kwh * conso_annuelle),
                    "conditions_resiliation": conditions,
                }

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
                                provider=provider_e,
                                start_date=date_debut_e,
                                anniversary_date=date_anniv_e,
                                contract_data={
                                    "fournisseur": provider_e,
                                    "pdl": pdl,
                                    "puissance_souscrite_kva": puissance,
                                    "prix_abonnement_mensuel": prix_abo_e,
                                    "prix_kwh": {"base": prix_kwh_e},
                                    "estimation_conso_annuelle_kwh": conso_annuelle_e,
                                    "estimation_facture_annuelle": (prix_abo_e * 12)
                                    + (prix_kwh_e * conso_annuelle_e),
                                },
                                pdf_bytes=st.session_state["pdf_bytes"],
                                filename=st.session_state["filename"],
                            )

                            # Création du contrat Gaz
                            contract_g = contract_service.create_contract(
                                contract_type="gaz",
                                provider=provider_g,
                                start_date=date_debut_g,
                                anniversary_date=date_anniv_g,
                                contract_data={
                                    "fournisseur": provider_g,
                                    "pce": pce,
                                    "zone_tarifaire": zone_gaz,
                                    "prix_abonnement_mensuel": prix_abo_g,
                                    "prix_kwh": prix_kwh_g,
                                    "estimation_conso_annuelle_kwh": conso_annuelle_g,
                                    "estimation_facture_annuelle": (prix_abo_g * 12)
                                    + (prix_kwh_g * conso_annuelle_g),
                                },
                                pdf_bytes=st.session_state["pdf_bytes"],
                                filename=st.session_state["filename"],
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
                                provider=provider,
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

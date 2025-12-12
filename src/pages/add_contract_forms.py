"""Form rendering functions for add_contract page."""
import streamlit as st
from datetime import datetime
from src.config import (
    DATE_FORMAT,
    LABEL_MONTHLY_SUB,
    LABEL_PRICE_KWH,
    LABEL_START_DATE,
    LABEL_ANNIVERSARY_DATE,
    LABEL_CONTRACT_NUMBER,
)


def parse_date(date_str):
    """Helper to parse dates with multiple formats."""
    if not date_str:
        return datetime.now()
    for fmt in [DATE_FORMAT, "%Y-%m-%d"]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return datetime.now()


def render_dual_energy_form(extracted_data):
    """Renders the form for dual energy contracts (Electricity + Gas)."""
    tab_elec, tab_gaz = st.tabs(["⚡ Électricité", "🔥 Gaz"])
    
    data_elec = {}
    data_gaz = {}

    # --- ELECTRICITE ---
    with tab_elec:
        st.subheader("Contrat Électricité")
        col1_e, col2_e = st.columns(2)
        with col1_e:
            data_elec["provider"] = st.text_input(
                "Fournisseur (Elec)",
                value=extracted_data.get("fournisseur", ""),
                key="prov_e",
            )
            data_elec["pdl"] = st.text_input(
                "PDL (Point de Livraison)",
                value=extracted_data.get("electricite", {}).get("pdl", ""),
                key="pdl_dual",
            )
            data_elec["puissance"] = st.number_input(
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
            data_elec["prix_abo"] = st.number_input(
                LABEL_MONTHLY_SUB,
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
            data_elec["date_debut"] = st.date_input(
                "Date de début (Elec)",
                value=datetime.now(),  # TODO: Parse date properly if available
                key="date_deb_e_dual",
            )
            data_elec["date_anniv"] = st.date_input(
                "Date anniversaire (Elec)",
                value=datetime.now(),
                key="date_ann_e_dual",
            )
            data_elec["prix_kwh"] = st.number_input(
                LABEL_PRICE_KWH,
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
            data_elec["conso_annuelle"] = st.number_input(
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
            data_gaz["provider"] = st.text_input(
                "Fournisseur (Gaz)",
                value=extracted_data.get("fournisseur", ""),
                key="prov_g",
            )
            data_gaz["pce"] = st.text_input(
                "PCE (Point Comptage)",
                value=extracted_data.get("gaz", {}).get("pce", ""),
                key="pce_dual",
            )
            data_gaz["zone"] = st.text_input(
                "Zone tarifaire",
                value=str(extracted_data.get("gaz", {}).get("zone_tarifaire", "")),
                key="zone_g_dual",
            )
            data_gaz["prix_abo"] = st.number_input(
                LABEL_MONTHLY_SUB,
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
            data_gaz["date_debut"] = st.date_input(
                "Date de début (Gaz)",
                value=datetime.now(),
                key="date_deb_g_dual",
            )
            data_gaz["date_anniv"] = st.date_input(
                "Date anniversaire (Gaz)",
                value=datetime.now(),
                key="date_ann_g_dual",
            )
            data_gaz["prix_kwh"] = st.number_input(
                LABEL_PRICE_KWH,
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
            data_gaz["conso_annuelle"] = st.number_input(
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
            
    return data_elec, data_gaz


def render_telephone_form(extracted_data):
    """Renders the form for telephone contracts."""
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
            LABEL_START_DATE,
            value=parse_date(extracted_data.get("date_debut")),
        )
        date_anniversaire = st.date_input(
            LABEL_ANNIVERSARY_DATE,
            value=parse_date(extracted_data.get("date_anniversaire")),
        )

    options = st.text_area(
        "Options incluses", value="\n".join(extracted_data.get("options", []))
    )
    conditions = st.text_area(
        "Conditions particulières",
        value=extracted_data.get("conditions_particulieres", ""),
    )

    return {
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


def render_insurance_pno_form(extracted_data):
    """Renders the form for PNO insurance contracts."""
    col1, col2 = st.columns(2)

    with col1:
        provider = st.text_input("Assureur", value=extracted_data.get("assureur", ""))
        numero_contrat = st.text_input(
            LABEL_CONTRACT_NUMBER, value=extracted_data.get("numero_contrat", "")
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
            value=parse_date(extracted_data.get("date_effet")),
        )
        date_anniversaire = st.date_input(
            LABEL_ANNIVERSARY_DATE,
            value=parse_date(extracted_data.get("date_anniversaire")),
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

    return {
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


def render_insurance_habitation_form(extracted_data):
    """Renders the form for habitation insurance contracts."""
    col1, col2 = st.columns(2)

    with col1:
        provider = st.text_input("Assureur", value=extracted_data.get("assureur", ""))
        numero_contrat = st.text_input(
            LABEL_CONTRACT_NUMBER, value=extracted_data.get("numero_contrat", "")
        )

        st.markdown("**Bien assuré**")
        bien = extracted_data.get("bien_assure", {})
        adresse = st.text_input("Adresse", value=bien.get("adresse", ""))
        type_bien = st.text_input(
            "Type de logement", value=bien.get("type_logement", "")
        )
        surface_m2 = st.number_input(
            "Surface (m²)", value=float(bien.get("surface_m2", 0) or 0), min_value=0.0
        )
        nombre_pieces = st.number_input(
            "Nombre de pièces",
            value=int(bien.get("nombre_pieces", 0) or 0),
            min_value=0,
        )

        st.markdown("**Équipements spécifiques**")
        col_eq1, col_eq2 = st.columns(2)
        with col_eq1:
            cheminee = st.checkbox("Cheminée", value=bien.get("cheminee", False))
            piscine = st.checkbox("Piscine", value=bien.get("piscine", False))
        with col_eq2:
            veranda = st.checkbox("Véranda", value=bien.get("veranda", False))
            dependances = st.checkbox(
                "Dépendances", value=bien.get("dependances", False)
            )

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
        date_effet = st.date_input("Date d'effet", value=parse_date(dates.get("date_debut")))
        date_anniversaire = st.date_input(LABEL_ANNIVERSARY_DATE, value=parse_date(dates.get("date_anniversaire")))

    st.markdown("**Garanties incluses**")
    garanties_list = extracted_data.get("garanties_incluses", [])
    garanties_text = st.text_area(
        "Liste des garanties",
        value=", ".join(garanties_list)
        if isinstance(garanties_list, list)
        else str(garanties_list),
    )

    return {
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
            "dependances": dependances,
        },
        "garanties_incluses": [g.strip() for g in garanties_text.split(",")]
        if garanties_text
        else [],
        "tarifs": {
            "prime_annuelle_ttc": prime_annuelle,
            "prime_mensuelle_ttc": prime_mensuelle,
        },
        "franchises": {"franchise_generale": franchise},
        "dates": {
            "date_debut": date_effet.strftime(DATE_FORMAT),
            "date_anniversaire": date_anniversaire.strftime(DATE_FORMAT),
        },
    }


def render_electricity_form(extracted_data):
    """Renders the form for electricity contracts."""
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
            LABEL_MONTHLY_SUB,
            value=float(tarifs_data.get("abonnement_mensuel_ttc") or 0),
            min_value=0.0,
            step=0.01,
        )

        prix_kwh_base = st.number_input(
            LABEL_PRICE_KWH,
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

        date_debut = st.date_input(
            LABEL_START_DATE,
            value=parse_date(dates_data.get("date_debut")),
        )

        date_anniversaire = st.date_input(
            LABEL_ANNIVERSARY_DATE,
            value=parse_date(dates_data.get("date_anniversaire")),
        )

    adresse = st.text_input(
        "Adresse de fourniture", value=adresses_data.get("site_de_consommation", "")
    )
    conditions = st.text_area(
        "Conditions de résiliation",
        value=extracted_data.get("conditions_resiliation", ""),
    )

    return {
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


def render_gas_form(extracted_data):
    """Renders the form for gas contracts."""
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
            LABEL_MONTHLY_SUB,
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

        date_debut = st.date_input(
            LABEL_START_DATE,
            value=parse_date(dates_data.get("date_debut")),
        )

        date_anniversaire = st.date_input(
            LABEL_ANNIVERSARY_DATE,
            value=parse_date(dates_data.get("date_anniversaire")),
        )

    adresse = st.text_input(
        "Adresse de fourniture", value=adresses_data.get("site_de_consommation", "")
    )
    conditions = st.text_area(
        "Conditions de résiliation",
        value=extracted_data.get("conditions_resiliation", ""),
    )

    return {
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

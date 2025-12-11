"""
Page pour importer le contrat TotalEnergies
"""
import streamlit as st
from datetime import datetime
from database.database import SessionLocal
from database.models import Contract

st.set_page_config(page_title="Import TotalEnergies", page_icon="⚡", layout="wide")

st.title("⚡ Import Contrat TotalEnergies")

# Données extraites par ChatGPT
totalenergies_data = {
    "fournisseur": "TotalEnergies Électricité et Gaz France",
    "type_contrat": "Offre Heures Eco - Electricité & Gaz",
    "client": {
        "noms": ["LAPINA ERIC", "ZHI NANXI"],
        "telephone": "0668317946",
        "email": "lapinae@gmail.com",
        "date_naissance": "24/06/1983",
        "reference_client": "116836462",
    },
    "adresses": {
        "site_de_consommation": "18B ALLEE VALERE LEFEVBRE - 93340 LE RAINCY",
        "adresse_facturation": "18B ALLEE VALERE LEFEBVRE - 93340 LE RAINCY",
        "facture_par_email": "lapinae@gmail.com",
    },
    "electricite": {
        "pdl": "22477713358214",
        "puissance_souscrite_kva": 9,
        "option_tarifaire": "Base",
        "matricule_compteur": "027",
        "date_debut_previsionnelle": "06/12/2025",
        "tarifs": {
            "abonnement_mensuel_ttc_9kVA": 20.21,
            "prix_kwh_ht": 0.1327,
            "prix_kwh_ttc": 0.1952,
        },
        "promotion": {"remise_kwh_ht_percent": 20, "duree_mois": 12},
        "consommation_estimee_annuelle_kwh": 8637,
        "budget_annuel_estime_ttc": 1639,
    },
    "gaz": {
        "pce": "22477858076069",
        "option_tarifaire": "T2",
        "zone_tarifaire": 2,
        "matricule_compteur": "003",
        "date_debut_previsionnelle": "06/12/2025",
        "tarifs": {"abonnement_mensuel_ttc": 27.57, "prix_kwh_ht": 0.0683, "prix_kwh_ttc": 0.1005},
        "promotion": {"remise_kwh_ht_percent": 10, "duree_mois": 12},
        "consommation_estimee_annuelle_kwh": 23593,
        "budget_annuel_estime_ttc": 2464,
    },
    "paiements": {
        "mensualite_electricite_ttc": 145,
        "mensualite_gaz_ttc": 210,
        "date_prelevement": "07",
        "mode": "Prélèvement automatique",
        "date_envoi_echeancier": "21/12/2025",
    },
    "dates": {"signature_contrat": "05/12/2025", "retractation_limite": "19/12/2025"},
    "service_client": {
        "tel_souscription": "3099",
        "tel_service_client": "0970 80 69 69",
        "contact_courrier": "TotalEnergies - Service Clientèle - TSA 21519 - 75901 Paris cedex 15",
    },
}

# Affichage des informations avec texte plus petit
st.markdown(
    "<style>.small-text {font-size: 0.75rem; margin: 0; padding: 2px 0;}</style>",
    unsafe_allow_html=True,
)

st.markdown("### 👤 Informations Client")
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        f"<p class='small-text'><b>Titulaires:</b> {', '.join(totalenergies_data['client']['noms'])}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Référence:</b> {totalenergies_data['client']['reference_client']}</p>",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"<p class='small-text'><b>Téléphone:</b> {totalenergies_data['client']['telephone']}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Email:</b> {totalenergies_data['client']['email']}</p>",
        unsafe_allow_html=True,
    )

st.markdown("### 📍 Adresse")
st.markdown(
    f"<p class='small-text'><b>Site de consommation:</b> {totalenergies_data['adresses']['site_de_consommation']}</p>",
    unsafe_allow_html=True,
)

# Électricité
st.markdown("### ⚡ Contrat Électricité")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"<p class='small-text'><b>PDL:</b> {totalenergies_data['electricite']['pdl']}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Puissance:</b> {totalenergies_data['electricite']['puissance_souscrite_kva']} kVA</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Option:</b> {totalenergies_data['electricite']['option_tarifaire']}</p>",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"<p class='small-text'><b>Abonnement:</b> {totalenergies_data['electricite']['tarifs']['abonnement_mensuel_ttc_9kVA']:.2f} €/mois</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Prix kWh:</b> {totalenergies_data['electricite']['tarifs']['prix_kwh_ttc']:.4f} €</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Promotion:</b> -{totalenergies_data['electricite']['promotion']['remise_kwh_ht_percent']}% / {totalenergies_data['electricite']['promotion']['duree_mois']} mois</p>",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"<p class='small-text'><b>Consommation:</b> {totalenergies_data['electricite']['consommation_estimee_annuelle_kwh']:,} kWh/an</p>".replace(
            ",", " "
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Budget annuel:</b> {totalenergies_data['electricite']['budget_annuel_estime_ttc']} €</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Mensualité:</b> {totalenergies_data['paiements']['mensualite_electricite_ttc']} €</p>",
        unsafe_allow_html=True,
    )

# Gaz
st.markdown("### 🔥 Contrat Gaz")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"<p class='small-text'><b>PCE:</b> {totalenergies_data['gaz']['pce']}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Option:</b> {totalenergies_data['gaz']['option_tarifaire']}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Zone tarifaire:</b> {totalenergies_data['gaz']['zone_tarifaire']}</p>",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"<p class='small-text'><b>Abonnement:</b> {totalenergies_data['gaz']['tarifs']['abonnement_mensuel_ttc']:.2f} €/mois</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Prix kWh:</b> {totalenergies_data['gaz']['tarifs']['prix_kwh_ttc']:.4f} €</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Promotion:</b> -{totalenergies_data['gaz']['promotion']['remise_kwh_ht_percent']}% / {totalenergies_data['gaz']['promotion']['duree_mois']} mois</p>",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"<p class='small-text'><b>Consommation:</b> {totalenergies_data['gaz']['consommation_estimee_annuelle_kwh']:,} kWh/an</p>".replace(
            ",", " "
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Budget annuel:</b> {totalenergies_data['gaz']['budget_annuel_estime_ttc']} €</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p class='small-text'><b>Mensualité:</b> {totalenergies_data['paiements']['mensualite_gaz_ttc']} €</p>",
        unsafe_allow_html=True,
    )

# Total
st.markdown("### 💰 Budget Total")
col1, col2, col3 = st.columns(3)
with col1:
    total_annuel = (
        totalenergies_data["electricite"]["budget_annuel_estime_ttc"]
        + totalenergies_data["gaz"]["budget_annuel_estime_ttc"]
    )
    st.metric("Budget annuel total", f"{total_annuel} € TTC", delta=None)
with col2:
    total_mensuel = (
        totalenergies_data["paiements"]["mensualite_electricite_ttc"]
        + totalenergies_data["paiements"]["mensualite_gaz_ttc"]
    )
    st.metric("Mensualité totale", f"{total_mensuel} € TTC", delta=None)
with col3:
    st.metric("Mode de paiement", totalenergies_data["paiements"]["mode"])

# Dates
st.markdown("### 📅 Dates importantes")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"<p class='small-text'><b>Signature:</b> {totalenergies_data['dates']['signature_contrat']}</p>",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"<p class='small-text'><b>Début:</b> {totalenergies_data['electricite']['date_debut_previsionnelle']}</p>",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"<p class='small-text'><b>⚠️ Rétractation jusqu'au:</b> {totalenergies_data['dates']['retractation_limite']}</p>",
        unsafe_allow_html=True,
    )

# Service client
st.markdown("### 📞 Service Client")
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        f"<p class='small-text'><b>Souscription:</b> {totalenergies_data['service_client']['tel_souscription']}</p>",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"<p class='small-text'><b>Service client:</b> {totalenergies_data['service_client']['tel_service_client']}</p>",
        unsafe_allow_html=True,
    )

# Boutons de sauvegarde
st.markdown("---")
st.markdown("### 💾 Sauvegarder dans la base de données")

col1, col2, col3, col4 = st.columns(4)


def save_contract(contract_type):
    """Sauvegarde un contrat dans la base de données"""
    try:
        if contract_type == "electricite":
            contract_data = {
                "fournisseur": totalenergies_data["fournisseur"],
                "numero_contrat": totalenergies_data["client"]["reference_client"],
                "type_offre": totalenergies_data["type_contrat"],
                "puissance_souscrite_kva": totalenergies_data["electricite"][
                    "puissance_souscrite_kva"
                ],
                "option_tarifaire": totalenergies_data["electricite"]["option_tarifaire"],
                "prix_abonnement_mensuel": totalenergies_data["electricite"]["tarifs"][
                    "abonnement_mensuel_ttc_9kVA"
                ],
                "prix_kwh": {"base": totalenergies_data["electricite"]["tarifs"]["prix_kwh_ttc"]},
                "adresse_fourniture": totalenergies_data["adresses"]["site_de_consommation"],
                "pdl": totalenergies_data["electricite"]["pdl"],
                "date_debut": totalenergies_data["electricite"]["date_debut_previsionnelle"],
                "date_anniversaire": totalenergies_data["dates"]["signature_contrat"],
                "estimation_conso_annuelle_kwh": totalenergies_data["electricite"][
                    "consommation_estimee_annuelle_kwh"
                ],
                "estimation_facture_annuelle": totalenergies_data["electricite"][
                    "budget_annuel_estime_ttc"
                ],
                "conditions_resiliation": f"Limite de rétractation: {totalenergies_data['dates']['retractation_limite']}",
                "client": totalenergies_data["client"],
                "promotion": totalenergies_data["electricite"]["promotion"],
                "paiement": totalenergies_data["paiements"],
                "service_client": totalenergies_data["service_client"],
            }
        else:  # gaz
            contract_data = {
                "fournisseur": totalenergies_data["fournisseur"],
                "numero_contrat": totalenergies_data["client"]["reference_client"],
                "type_offre": totalenergies_data["type_contrat"],
                "classe_consommation": totalenergies_data["gaz"]["option_tarifaire"],
                "zone_tarifaire": totalenergies_data["gaz"]["zone_tarifaire"],
                "prix_abonnement_mensuel": totalenergies_data["gaz"]["tarifs"][
                    "abonnement_mensuel_ttc"
                ],
                "prix_kwh": totalenergies_data["gaz"]["tarifs"]["prix_kwh_ttc"],
                "adresse_fourniture": totalenergies_data["adresses"]["site_de_consommation"],
                "pce": totalenergies_data["gaz"]["pce"],
                "date_debut": totalenergies_data["gaz"]["date_debut_previsionnelle"],
                "date_anniversaire": totalenergies_data["dates"]["signature_contrat"],
                "estimation_conso_annuelle_kwh": totalenergies_data["gaz"][
                    "consommation_estimee_annuelle_kwh"
                ],
                "estimation_facture_annuelle": totalenergies_data["gaz"][
                    "budget_annuel_estime_ttc"
                ],
                "conditions_resiliation": f"Limite de rétractation: {totalenergies_data['dates']['retractation_limite']}",
                "client": totalenergies_data["client"],
                "promotion": totalenergies_data["gaz"]["promotion"],
                "paiement": totalenergies_data["paiements"],
                "service_client": totalenergies_data["service_client"],
            }

        anniversary_date = datetime.strptime(
            totalenergies_data["dates"]["signature_contrat"], "%d/%m/%Y"
        )
        start_date = datetime.strptime(
            totalenergies_data[contract_type]["date_debut_previsionnelle"], "%d/%m/%Y"
        )

        db = SessionLocal()
        contract = Contract(
            provider=totalenergies_data["fournisseur"],
            contract_type=contract_type,
            contract_data=contract_data,
            start_date=start_date,
            anniversary_date=anniversary_date,
            validated=True,
        )

        db.add(contract)
        db.commit()
        db.refresh(contract)
        db.close()

        return True, contract.id

    except Exception as e:
        return False, str(e)


with col1:
    if st.button("💾 Sauvegarder Électricité", use_container_width=True):
        success, result = save_contract("electricite")
        if success:
            st.success(f"✅ Contrat électricité sauvegardé (ID: {result})")
        else:
            st.error(f"❌ Erreur: {result}")

with col2:
    if st.button("💾 Sauvegarder Gaz", use_container_width=True):
        success, result = save_contract("gaz")
        if success:
            st.success(f"✅ Contrat gaz sauvegardé (ID: {result})")
        else:
            st.error(f"❌ Erreur: {result}")

with col3:
    if st.button("💾 Sauvegarder les deux", use_container_width=True):
        success1, result1 = save_contract("electricite")
        success2, result2 = save_contract("gaz")
        if success1 and success2:
            st.success(f"✅ Contrats sauvegardés (IDs: {result1}, {result2})")
        else:
            if not success1:
                st.error(f"❌ Erreur électricité: {result1}")
            if not success2:
                st.error(f"❌ Erreur gaz: {result2}")

with col4:
    if st.button("🏠 Retour Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

# Afficher le JSON brut
with st.expander("📋 Voir le JSON brut"):
    st.json(totalenergies_data)

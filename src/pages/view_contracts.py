"""Page de visualisation détaillée des contrats."""
import streamlit as st
from src.database import get_db
from src.services import ContractService, OpenAIService, PDFService
from src.config import CONTRACT_TYPES


def show():
    """Affiche la page de visualisation des contrats."""
    st.title("👀 Visualisation des contrats")
    st.markdown("Consultez les détails de vos contrats enregistrés.")

    with get_db() as db:
        openai_service = OpenAIService()
        pdf_service = PDFService()
        contract_service = ContractService(db, openai_service, pdf_service)

        contracts = contract_service.get_all_contracts()

        if not contracts:
            st.info("Aucun contrat enregistré.")
            return

        # Sélection du contrat
        contract_options = {
            c.id: f"{CONTRACT_TYPES.get(c.contract_type, c.contract_type)} - {c.provider} ({c.anniversary_date.strftime('%d/%m/%Y')})"
            for c in contracts
        }

        # Gestion de la pré-sélection depuis le dashboard
        default_index = 0
        contract_ids = list(contract_options.keys())

        if "view_contract_id" in st.session_state:
            try:
                default_index = contract_ids.index(st.session_state["view_contract_id"])
                # On ne supprime pas forcément la variable pour garder la sélection si on rafraîchit
                # del st.session_state["view_contract_id"]
            except ValueError:
                pass

        selected_id = st.selectbox(
            "Choisir un contrat à visualiser",
            options=contract_ids,
            format_func=lambda x: contract_options[x],
            index=default_index,
        )

        if selected_id:
            contract = contract_service.get_contract_by_id(selected_id)
            if not contract:
                st.error("Contrat introuvable.")
                return

            st.divider()

            # En-tête du contrat
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader(f"{contract.provider}")
                st.caption(
                    f"Type: {CONTRACT_TYPES.get(contract.contract_type, contract.contract_type)}"
                )
            with col2:
                st.metric("Date anniversaire", contract.anniversary_date.strftime("%d/%m/%Y"))

            # Affichage spécifique selon le type
            data = contract.contract_data

            if contract.contract_type == "assurance_habitation":
                display_assurance_habitation(data)
            elif contract.contract_type == "assurance_pno":
                display_assurance_pno(data)
            elif contract.contract_type == "telephone":
                display_telephone(data)
            elif contract.contract_type in ["electricite", "gaz"]:
                display_energy(data, contract.contract_type)
            else:
                st.json(data)

            # Données brutes (toujours utile pour vérifier)
            with st.expander("Voir les données brutes (JSON)"):
                st.json(data)


def display_assurance_habitation(data):
    """Affichage détaillé pour Assurance Habitation."""
    st.markdown("### 🏠 Bien Assuré")
    bien = data.get("bien_assure", {})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Adresse:** {bien.get('adresse', 'N/A')}")
        st.markdown(f"**Type:** {bien.get('type_logement', 'N/A')}")
        st.markdown(f"**Statut:** {bien.get('statut_occupant', 'N/A')}")
        st.markdown(f"**Résidence:** {bien.get('residence', 'N/A')}")

    with col2:
        st.markdown(f"**Surface:** {bien.get('surface_m2', 0)} m²")
        st.markdown(f"**Pièces:** {bien.get('nombre_pieces', 0)}")

        # Equipements
        equipements = []
        if bien.get("cheminee"):
            equipements.append("🔥 Cheminée")
        if bien.get("piscine"):
            equipements.append("🏊 Piscine")
        if bien.get("veranda"):
            equipements.append("☀️ Véranda")
        if bien.get("dependances"):
            equipements.append("🏚️ Dépendances")
        if bien.get("systeme_securite"):
            equipements.append("🚨 Alarme")

        if equipements:
            st.markdown("**Équipements:** " + ", ".join(equipements))
        else:
            st.markdown("**Équipements:** Aucun détecté")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🛡️ Garanties & Capitaux")
        st.markdown(
            f"**Capital Mobilier:** {data.get('capitaux', {}).get('capital_mobilier', 0):,.2f} €"
        )
        st.markdown(
            f"**Objets de valeur:** {data.get('capitaux', {}).get('objets_valeur', 0):,.2f} €"
        )

        garanties = data.get("garanties_incluses", [])
        if garanties:
            st.markdown("**Garanties incluses:**")
            for g in garanties:
                st.markdown(f"- {g}")

    with col2:
        st.markdown("### 💰 Tarifs & Franchises")
        tarifs = data.get("tarifs", {})
        st.metric("Prime Annuelle", f"{tarifs.get('prime_annuelle_ttc', 0):.2f} €")
        if tarifs.get("prime_mensuelle_ttc"):
            st.markdown(f"*(soit {tarifs.get('prime_mensuelle_ttc'):.2f} €/mois)*")

        franchises = data.get("franchises", {})
        st.markdown(f"**Franchise générale:** {franchises.get('franchise_generale', 0):.2f} €")


def display_assurance_pno(data):
    st.markdown("### 🏠 Bien Assuré")
    bien = data.get("bien_assure", {})
    st.markdown(f"**Adresse:** {bien.get('adresse', 'N/A')}")
    st.markdown(
        f"**Type:** {bien.get('type', 'N/A')} - {bien.get('surface_m2', 0)} m² - {bien.get('nombre_pieces', 0)} pièces"
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🛡️ Garanties")
        garanties = data.get("garanties", {})
        for k, v in garanties.items():
            if isinstance(v, (int, float)) and v > 0:
                st.markdown(f"**{k.replace('_', ' ').capitalize()}:** {v:,.2f} €")
            elif isinstance(v, list):
                st.markdown(f"**{k.replace('_', ' ').capitalize()}:** {', '.join(v)}")

    with col2:
        st.markdown("### 💰 Tarifs")
        st.metric("Prime Annuelle", f"{data.get('prime_annuelle', 0):.2f} €")
        st.markdown(f"**Franchise:** {data.get('franchise', 0):.2f} €")


def display_telephone(data):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Forfait:** {data.get('forfait_nom', 'N/A')}")
        st.markdown(f"**Data:** {data.get('data_go', 0)} Go")
        st.markdown(f"**Appels:** {data.get('minutes', 'N/A')}")
    with col2:
        st.metric("Prix Mensuel", f"{data.get('prix_mensuel', 0):.2f} €")
        st.markdown(f"**Engagement:** {data.get('engagement_mois', 0)} mois")


def display_energy(data, type_energy):
    # Tenter de récupérer les données structurées (nouveau format)
    energy_data = data.get(type_energy, {})

    # Si vide, vérifier si c'est l'ancien format (plat)
    if not energy_data and not data.get("electricite") and not data.get("gaz"):
        # C'est probablement un ancien format où les clés sont à la racine
        energy_data = data
        is_legacy = True
    else:
        is_legacy = False

    col1, col2 = st.columns(2)
    with col1:
        # PDL / PCE
        pdl_key = "pdl" if type_energy == "electricite" else "pce"
        pdl_val = energy_data.get(pdl_key)

        # Fallback legacy
        if not pdl_val and is_legacy:
            pdl_val = data.get(pdl_key)

        st.markdown(f"**Point de livraison:** {pdl_val or 'N/A'}")

        if type_energy == "electricite":
            puissance = energy_data.get("puissance_souscrite_kva")
            st.markdown(f"**Puissance:** {puissance if puissance is not None else 'N/A'} kVA")

        conso = energy_data.get("consommation_estimee_annuelle_kwh")
        if not conso and is_legacy:
            conso = data.get("estimation_conso_annuelle_kwh")

        if conso:
            st.markdown(f"**Conso estimée:** {conso} kWh/an")

    with col2:
        # Tarifs
        tarifs = energy_data.get("tarifs", {})

        # Abonnement
        abo = tarifs.get("abonnement_mensuel_ttc")
        if abo is None:
            # Essayer format plat ou legacy
            abo = energy_data.get("abonnement_mensuel_ttc") or data.get("prix_abonnement_mensuel")

        st.metric("Abonnement Mensuel", f"{abo:.2f} €" if abo is not None else "N/A")

        # Prix kWh
        kwh = tarifs.get("prix_kwh_ttc")
        if kwh is None:
            # Essayer format plat
            kwh = energy_data.get("prix_kwh_ttc")

        # Legacy format: prix_kwh peut être un dict ou un float
        if kwh is None and is_legacy:
            legacy_kwh = data.get("prix_kwh")
            if isinstance(legacy_kwh, dict):
                kwh = legacy_kwh.get("base") or legacy_kwh.get("heures_pleines")
            else:
                kwh = legacy_kwh

        st.markdown(f"**Prix kWh:** {kwh:.4f} €" if kwh is not None else "**Prix kWh:** N/A")


if __name__ == "__main__":
    show()

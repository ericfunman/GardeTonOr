"""
Script pour importer le contrat TotalEnergies dans la base de données
"""
import sys

sys.path.insert(0, "src")

from datetime import datetime
from database.database import SessionLocal
from database.models import Contract
import json

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


def create_contract(data, contract_type):
    """Crée un contrat dans la base de données"""

    if contract_type == "electricite":
        contract_data = {
            "fournisseur": data["fournisseur"],
            "numero_contrat": data["client"]["reference_client"],
            "type_offre": data["type_contrat"],
            "puissance_souscrite_kva": data["electricite"]["puissance_souscrite_kva"],
            "option_tarifaire": data["electricite"]["option_tarifaire"],
            "prix_abonnement_mensuel": data["electricite"]["tarifs"]["abonnement_mensuel_ttc_9kVA"],
            "prix_kwh": {"base": data["electricite"]["tarifs"]["prix_kwh_ttc"]},
            "adresse_fourniture": data["adresses"]["site_de_consommation"],
            "pdl": data["electricite"]["pdl"],
            "date_debut": data["electricite"]["date_debut_previsionnelle"],
            "date_anniversaire": data["dates"]["signature_contrat"],
            "estimation_conso_annuelle_kwh": data["electricite"][
                "consommation_estimee_annuelle_kwh"
            ],
            "estimation_facture_annuelle": data["electricite"]["budget_annuel_estime_ttc"],
            "conditions_resiliation": f"Limite de rétractation: {data['dates']['retractation_limite']}",
            "client": data["client"],
            "promotion": data["electricite"]["promotion"],
            "paiement": data["paiements"],
            "service_client": data["service_client"],
        }
        anniversary_date = datetime.strptime(data["dates"]["signature_contrat"], "%d/%m/%Y")

    else:  # gaz
        contract_data = {
            "fournisseur": data["fournisseur"],
            "numero_contrat": data["client"]["reference_client"],
            "type_offre": data["type_contrat"],
            "classe_consommation": data["gaz"]["option_tarifaire"],
            "zone_tarifaire": data["gaz"]["zone_tarifaire"],
            "prix_abonnement_mensuel": data["gaz"]["tarifs"]["abonnement_mensuel_ttc"],
            "prix_kwh": data["gaz"]["tarifs"]["prix_kwh_ttc"],
            "adresse_fourniture": data["adresses"]["site_de_consommation"],
            "pce": data["gaz"]["pce"],
            "date_debut": data["gaz"]["date_debut_previsionnelle"],
            "date_anniversaire": data["dates"]["signature_contrat"],
            "estimation_conso_annuelle_kwh": data["gaz"]["consommation_estimee_annuelle_kwh"],
            "estimation_facture_annuelle": data["gaz"]["budget_annuel_estime_ttc"],
            "conditions_resiliation": f"Limite de rétractation: {data['dates']['retractation_limite']}",
            "client": data["client"],
            "promotion": data["gaz"]["promotion"],
            "paiement": data["paiements"],
            "service_client": data["service_client"],
        }
        anniversary_date = datetime.strptime(data["dates"]["signature_contrat"], "%d/%m/%Y")

    db = SessionLocal()
    try:
        contract = Contract(
            provider=data["fournisseur"],
            contract_type=contract_type,
            contract_data=contract_data,
            anniversary_date=anniversary_date,
            validated=True,
        )

        db.add(contract)
        db.commit()
        db.refresh(contract)

        print(f"✅ Contrat {contract_type} créé avec succès (ID: {contract.id})")
        return contract

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors de la création du contrat: {e}")
        return None
    finally:
        db.close()


def display_contract_info(data):
    """Affiche les informations du contrat de manière jolie"""

    print("\n" + "=" * 80)
    print("📄 CONTRAT TOTALENERGIES - ÉLECTRICITÉ & GAZ")
    print("=" * 80)

    print("\n👤 CLIENT")
    print("-" * 80)
    print(f"  Titulaires      : {', '.join(data['client']['noms'])}")
    print(f"  Référence       : {data['client']['reference_client']}")
    print(f"  Téléphone       : {data['client']['telephone']}")
    print(f"  Email           : {data['client']['email']}")

    print("\n📍 ADRESSES")
    print("-" * 80)
    print(f"  Consommation    : {data['adresses']['site_de_consommation']}")
    print(f"  Facturation     : {data['adresses']['adresse_facturation']}")

    print("\n⚡ ÉLECTRICITÉ")
    print("-" * 80)
    print(f"  Type d'offre    : {data['type_contrat']}")
    print(f"  PDL             : {data['electricite']['pdl']}")
    print(f"  Puissance       : {data['electricite']['puissance_souscrite_kva']} kVA")
    print(f"  Option          : {data['electricite']['option_tarifaire']}")
    print(
        f"  Abonnement      : {data['electricite']['tarifs']['abonnement_mensuel_ttc_9kVA']:.2f} €/mois TTC"
    )
    print(f"  Prix kWh        : {data['electricite']['tarifs']['prix_kwh_ttc']:.4f} € TTC")
    print(
        f"  Promotion       : -{data['electricite']['promotion']['remise_kwh_ht_percent']}% pendant {data['electricite']['promotion']['duree_mois']} mois"
    )
    print(
        f"  Conso estimée   : {data['electricite']['consommation_estimee_annuelle_kwh']:,} kWh/an".replace(
            ",", " "
        )
    )
    print(f"  💰 Budget annuel : {data['electricite']['budget_annuel_estime_ttc']} € TTC")
    print(f"  💳 Mensualité    : {data['paiements']['mensualite_electricite_ttc']} € TTC")

    print("\n🔥 GAZ")
    print("-" * 80)
    print(f"  Type d'offre    : {data['type_contrat']}")
    print(f"  PCE             : {data['gaz']['pce']}")
    print(f"  Option          : {data['gaz']['option_tarifaire']}")
    print(f"  Zone tarifaire  : {data['gaz']['zone_tarifaire']}")
    print(f"  Abonnement      : {data['gaz']['tarifs']['abonnement_mensuel_ttc']:.2f} €/mois TTC")
    print(f"  Prix kWh        : {data['gaz']['tarifs']['prix_kwh_ttc']:.4f} € TTC")
    print(
        f"  Promotion       : -{data['gaz']['promotion']['remise_kwh_ht_percent']}% pendant {data['gaz']['promotion']['duree_mois']} mois"
    )
    print(
        f"  Conso estimée   : {data['gaz']['consommation_estimee_annuelle_kwh']:,} kWh/an".replace(
            ",", " "
        )
    )
    print(f"  💰 Budget annuel : {data['gaz']['budget_annuel_estime_ttc']} € TTC")
    print(f"  💳 Mensualité    : {data['paiements']['mensualite_gaz_ttc']} € TTC")

    print("\n💳 PAIEMENT")
    print("-" * 80)
    print(f"  Mode            : {data['paiements']['mode']}")
    print(f"  Date prélèvement: Le {data['paiements']['date_prelevement']} de chaque mois")
    print(
        f"  💰 TOTAL        : {data['paiements']['mensualite_electricite_ttc'] + data['paiements']['mensualite_gaz_ttc']} €/mois"
    )

    print("\n📅 DATES")
    print("-" * 80)
    print(f"  Signature       : {data['dates']['signature_contrat']}")
    print(f"  Début           : {data['electricite']['date_debut_previsionnelle']}")
    print(f"  Rétractation    : Jusqu'au {data['dates']['retractation_limite']}")

    print("\n📞 SERVICE CLIENT")
    print("-" * 80)
    print(f"  Souscription    : {data['service_client']['tel_souscription']}")
    print(f"  Service client  : {data['service_client']['tel_service_client']}")
    print(f"  Courrier        : {data['service_client']['contact_courrier']}")

    print("\n" + "=" * 80)
    print(
        f"💰 BUDGET TOTAL ANNUEL : {data['electricite']['budget_annuel_estime_ttc'] + data['gaz']['budget_annuel_estime_ttc']} € TTC"
    )
    print(
        f"💳 MENSUALITÉ TOTALE   : {data['paiements']['mensualite_electricite_ttc'] + data['paiements']['mensualite_gaz_ttc']} € TTC"
    )
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Afficher les informations
    display_contract_info(totalenergies_data)

    # Demander confirmation
    print("\n❓ Voulez-vous sauvegarder ces contrats dans la base de données ?")
    print("   1. Électricité seulement")
    print("   2. Gaz seulement")
    print("   3. Les deux")
    print("   4. Annuler")

    choice = input("\nVotre choix (1-4): ").strip()

    if choice == "1":
        create_contract(totalenergies_data, "electricite")
    elif choice == "2":
        create_contract(totalenergies_data, "gaz")
    elif choice == "3":
        create_contract(totalenergies_data, "electricite")
        create_contract(totalenergies_data, "gaz")
    else:
        print("\n❌ Annulé")

from datetime import datetime
from src.database.database import get_db
from src.database.models import Contract


def insert_contract():
    contract_data = {
        "type_contrat": "assurance_habitation",
        "assureur": "Direct Assurance",
        "numero_contrat": "MANUEL",
        "client": {
            "noms": ["Eric Lapina"],
            "email": "",
            "telephone": "",
            "date_naissance": "",
            "reference_client": "",
        },
        "bien_assure": {
            "adresse": "18 B allée Valere Lefebvre 93340 le Raincy",
            "type_logement": "Maison",
            "statut_occupant": "Propriétaire",
            "residence": "Principale",
            "surface_m2": 215,
            "nombre_pieces": 7,
            "dependances": True,
            "veranda": False,
            "cheminee": False,
            "piscine": True,
            "systeme_securite": True,
        },
        "garanties_incluses": [
            "Formule Confort",
            "Dommages électriques",
            "Rééquipement à neuf",
            "Piscine",
        ],
        "capitaux": {"capital_mobilier": 90300, "objets_valeur": 9030},
        "franchises": {"franchise_generale": 0, "franchise_cat_nat": 0},
        "tarifs": {"prime_annuelle_ttc": 923.22, "prime_mensuelle_ttc": 0.0, "frais_dossier": 0.0},
        "dates": {
            "signature_contrat": "01/07/2015",
            "date_debut": "01/07/2015",
            "date_anniversaire": "01/07/2026",
            "retractation_limite": "",
        },
    }

    # Parse dates for the main columns
    start_date = datetime.strptime("01/07/2015", "%d/%m/%Y")
    anniversary_date = datetime.strptime("01/07/2026", "%d/%m/%Y")

    contract = Contract(
        contract_type="assurance_habitation",
        provider="Direct Assurance",
        start_date=start_date,
        anniversary_date=anniversary_date,
        contract_data=contract_data,
        original_filename="Import Manuel",
        validated=1,
    )

    with get_db() as db:
        db.add(contract)
        # Commit is handled by the context manager, but explicit commit is fine too if needed,
        # though get_db does it on exit.
        # However, to get the ID, we might need to flush or commit.
        # get_db commits on exit.
        pass

    print("Contrat ajouté avec succès !")


if __name__ == "__main__":
    insert_contract()

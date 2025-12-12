from datetime import datetime
from src.database.database import get_db
from src.database.models import Contract


def insert_phone_contract():
    # Cleanup previous attempt
    with get_db() as db:
        old_contract = db.query(Contract).filter(Contract.provider == "Sosh").first()
        if old_contract:
            db.delete(old_contract)
            print("Ancien contrat Sosh supprimé.")

    contract_data = {
        "type_contrat": "telephone",
        "fournisseur": "B&You",
        "numero_contrat": "0668317946",
        "client": {
            "noms": ["Eric"],
            "telephone": "06 68 31 79 46",
            "email": "",
            "date_naissance": "",
            "reference_client": "",
        },
        "forfait_nom": "Forfait B&You 200 Go 5G",
        "data_go": 200,
        "minutes": "illimité",
        "sms": "illimité",
        "prix_mensuel": 9.99,
        "engagement_mois": 0,
        "date_debut": "01/03/2019",
        "date_anniversaire": "01/03/2026",
        "options": [
            "25 Go Europe/DOM/USA/Canada/Suisse",
            "Appels illimités vers mobiles USA/Canada/Suisse",
            "5G inclus",
        ],
        "conditions_particulieres": "Appels illimités depuis France vers France/DOM. SMS illimités.",
    }

    # Parse dates
    start_date = datetime.strptime("01/03/2019", "%d/%m/%Y")
    anniversary_date = datetime.strptime("01/03/2026", "%d/%m/%Y")

    contract = Contract(
        contract_type="telephone",
        provider="B&You",
        start_date=start_date,
        anniversary_date=anniversary_date,
        contract_data=contract_data,
        original_filename="Import Manuel Téléphone",
        validated=1,
    )

    with get_db() as db:
        db.add(contract)
        pass

    print(f"Contrat téléphone ajouté avec succès !")


if __name__ == "__main__":
    insert_phone_contract()

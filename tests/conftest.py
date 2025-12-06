"""Configuration des fixtures pytest."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.database.models import Base, Contract, Comparison, ExtractionLog


@pytest.fixture
def db_engine():
    """Crée un engine de base de données en mémoire pour les tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    """Crée une session de base de données pour les tests."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_contract_data_telephone():
    """Données d'exemple pour un contrat téléphone."""
    return {
        "fournisseur": "Free Mobile",
        "forfait_nom": "Forfait 5G 210Go",
        "data_go": 210,
        "minutes": "illimité",
        "sms": "illimité",
        "prix_mensuel": 19.99,
        "engagement_mois": 12,
        "date_debut": "2024-01-15",
        "date_anniversaire": "2025-01-15",
        "options": ["5G", "Appels internationaux"],
        "conditions_particulieres": "Résiliation possible après 12 mois"
    }


@pytest.fixture
def sample_contract_data_pno():
    """Données d'exemple pour un contrat assurance PNO."""
    return {
        "assureur": "AXA",
        "numero_contrat": "PNO123456",
        "bien_assure": {
            "adresse": "10 rue de la Paix, 75001 Paris",
            "type": "Appartement",
            "surface_m2": 65,
            "nombre_pieces": 3
        },
        "garanties": {
            "incendie": 200000,
            "degats_des_eaux": 50000,
            "vol": 30000,
            "responsabilite_civile": 1000000
        },
        "franchise": 150,
        "prime_annuelle": 350,
        "prime_mensuelle": 29.17,
        "date_effet": "2024-03-01",
        "date_anniversaire": "2025-03-01",
        "conditions_particulieres": "Franchise réduite si travaux de sécurité"
    }


@pytest.fixture
def sample_contract_telephone(db_session, sample_contract_data_telephone):
    """Crée un contrat téléphone d'exemple en base."""
    contract = Contract(
        contract_type="telephone",
        provider="Free Mobile",
        start_date=datetime(2024, 1, 15),
        anniversary_date=datetime(2025, 1, 15),
        contract_data=sample_contract_data_telephone,
        original_filename="contrat_free.pdf",
        validated=1
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract


@pytest.fixture
def sample_contract_pno(db_session, sample_contract_data_pno):
    """Crée un contrat assurance PNO d'exemple en base."""
    contract = Contract(
        contract_type="assurance_pno",
        provider="AXA",
        start_date=datetime(2024, 3, 1),
        anniversary_date=datetime(2025, 3, 1),
        contract_data=sample_contract_data_pno,
        original_filename="contrat_axa.pdf",
        validated=1
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract


@pytest.fixture
def sample_pdf_text_telephone():
    """Texte d'exemple extrait d'un PDF de contrat téléphone."""
    return """
    CONTRAT DE TELEPHONIE MOBILE
    
    Free Mobile
    Forfait 5G 210Go
    
    Souscripteur: Jean Dupont
    Date de souscription: 15/01/2024
    
    Caractéristiques du forfait:
    - 210 Go de data en France métropolitaine
    - Appels illimités vers fixes et mobiles
    - SMS/MMS illimités
    - 5G incluse
    
    Tarif: 19.99€/mois
    Engagement: 12 mois
    Date d'échéance annuelle: 15/01/2025
    
    Options incluses:
    - Réseau 5G
    - Appels internationaux vers 100 destinations
    
    Conditions de résiliation:
    Résiliation possible sans frais après 12 mois d'engagement.
    """


@pytest.fixture
def mock_openai_response_extraction():
    """Mock de réponse OpenAI pour extraction de données."""
    return {
        "data": {
            "fournisseur": "Free Mobile",
            "forfait_nom": "Forfait 5G 210Go",
            "data_go": 210,
            "minutes": "illimité",
            "sms": "illimité",
            "prix_mensuel": 19.99,
            "engagement_mois": 12,
            "date_debut": "2024-01-15",
            "date_anniversaire": "2025-01-15",
            "options": ["5G", "Appels internationaux"],
            "conditions_particulieres": "Résiliation possible après 12 mois"
        },
        "prompt": "test prompt",
        "raw_response": '{"fournisseur": "Free Mobile"}'
    }


@pytest.fixture
def mock_openai_response_market():
    """Mock de réponse OpenAI pour comparaison de marché."""
    return {
        "analysis": {
            "tarif_actuel": 19.99,
            "estimation_marche": {
                "tarif_min": 9.99,
                "tarif_moyen": 15.99,
                "tarif_max": 29.99
            },
            "economie_potentielle_mensuelle": 4.00,
            "economie_potentielle_annuelle": 48.00,
            "offres_similaires": [
                {
                    "fournisseur": "B&You",
                    "forfait": "Forfait 200Go",
                    "prix_mensuel": 15.99,
                    "avantages": ["Prix compétitif", "Sans engagement"],
                    "inconvenients": ["Moins de data"]
                }
            ],
            "recommandation": "changer",
            "justification": "Des offres moins chères existent sur le marché",
            "niveau_competitivite": "moyen"
        },
        "prompt": "test prompt",
        "raw_response": '{"recommandation": "changer"}'
    }


@pytest.fixture
def mock_openai_response_competitor():
    """Mock de réponse OpenAI pour comparaison avec concurrent."""
    return {
        "analysis": {
            "comparaison_prix": {
                "prix_actuel": 19.99,
                "prix_concurrent": 15.99,
                "difference_mensuelle": 4.00,
                "difference_annuelle": 48.00,
                "economie_potentielle": 48.00
            },
            "comparaison_services": {
                "avantages_contrat_actuel": ["5G incluse", "Plus de data"],
                "avantages_concurrent": ["Prix plus bas", "Sans engagement"],
                "services_identiques": ["Appels illimités"],
                "differences_majeures": ["10Go de différence"]
            },
            "analyse_qualitative": {
                "qualite_actuelle": 8,
                "qualite_concurrent": 7,
                "rapport_qualite_prix_actuel": 7,
                "rapport_qualite_prix_concurrent": 9
            },
            "points_vigilance": ["Vérifier la couverture réseau"],
            "recommandation": "changer pour concurrent",
            "justification": "Meilleur rapport qualité-prix",
            "score_global": {
                "contrat_actuel": 7.5,
                "offre_concurrente": 8.0
            }
        },
        "prompt": "test prompt",
        "raw_response": '{"recommandation": "changer"}'
    }

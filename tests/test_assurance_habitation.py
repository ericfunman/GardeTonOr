import pytest
from unittest.mock import MagicMock
import json
from src.services.openai_service import OpenAIService


class TestAssuranceHabitation:
    @pytest.fixture
    def openai_service(self):
        # Create service with dummy key
        service = OpenAIService(api_key="fake-key")
        # Replace client with MagicMock to avoid real API calls
        service.client = MagicMock()
        return service

    def test_extract_assurance_habitation(self, openai_service):
        # Mock response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "type_contrat": "assurance_habitation",
            "assureur": "Maif",
            "numero_contrat": "123456789",
            "bien_assure": {
                "adresse": "10 Rue de la Paix, 75000 Paris",
                "type_logement": "Maison",
                "statut_occupant": "Propriétaire",
                "residence": "Principale",
                "surface_m2": 120,
                "nombre_pieces": 5,
                "dependances": True,
                "veranda": False,
                "cheminee": True,
                "piscine": True,
                "systeme_securite": True
            },
            "garanties_incluses": ["Incendie", "Dégâts des eaux", "Vol"],
            "capitaux": {
                "capital_mobilier": 50000,
                "objets_valeur": 5000
            },
            "franchises": {
                "franchise_generale": 150,
                "franchise_cat_nat": 380
            },
            "tarifs": {
                "prime_annuelle_ttc": 450.50,
                "prime_mensuelle_ttc": 37.54,
                "frais_dossier": 0
            },
            "dates": {
                "date_debut": "01/01/2024",
                "date_anniversaire": "01/01/2025"
            }
        })

        # Setup mock client
        openai_service.client.chat.completions.create.return_value = mock_response

        # Test extraction
        pdf_text = "Contrat habitation Maif..."
        result = openai_service.extract_contract_data(pdf_text, "assurance_habitation")

        data = result["data"]
        assert data["type_contrat"] == "assurance_habitation"
        assert data["assureur"] == "Maif"
        assert data["bien_assure"]["cheminee"] is True
        assert data["bien_assure"]["piscine"] is True
        assert data["tarifs"]["prime_annuelle_ttc"] == 450.50

    def test_compare_assurance_habitation(self, openai_service):
        # Mock response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "analyse": {
                "prime_actuelle_annuelle": 450.50,
                "estimation_marche": {
                    "prime_min": 350,
                    "prime_moyenne": 420,
                    "prime_max": 600
                },
                "economie_potentielle_annuelle": 30.50,
                "ratio_qualite_prix": 8,
                "offres_similaires": [],
                "points_attention": ["Vérifier la garantie piscine"],
                "recommandation": "garder",
                "justification": "Bon prix pour les garanties incluses",
                "niveau_competitivite": "bon"
            },
            "meilleure_offre": {}
        })

        openai_service.client.chat.completions.create.return_value = mock_response

        contract_data = {
            "type_contrat": "assurance_habitation",
            "assureur": "Maif",
            "tarifs": {"prime_annuelle_ttc": 450.50}
        }

        result = openai_service.compare_with_market(contract_data, "assurance_habitation")

        assert result["analysis"]["analyse"]["prime_actuelle_annuelle"] == 450.50
        assert "Vérifier la garantie piscine" in result["analysis"]["analyse"]["points_attention"]

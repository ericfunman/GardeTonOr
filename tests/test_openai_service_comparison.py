"""Tests pour les fonctionnalités de comparaison du service OpenAI."""
import pytest
from unittest.mock import Mock, patch
import json
from src.services.openai_service import OpenAIService


class TestOpenAIServiceComparison:
    """Tests pour les méthodes de comparaison."""

    @pytest.fixture
    def mock_openai_client(self):
        with patch("src.services.openai_service.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            yield mock_client

    def test_compare_with_market_telephone(self, mock_openai_client):
        """Test de comparaison marché pour un forfait mobile."""
        service = OpenAIService(api_key="test")
        contract_data = {
            "fournisseur": "Orange",
            "prix_mensuel": 50.0,
            "data_go": 10
        }

        expected_analysis = {
            "recommandation": "Changer",
            "justification": "Trop cher pour 10Go",
            "comparaison_prix": {
                "prix_actuel": 50.0,
                "prix_concurrent": 15.0,
                "economie_potentielle": 35.0
            }
        }

        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = json.dumps(expected_analysis)
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_response

        result = service.compare_with_market(contract_data, "telephone")

        assert result["analysis"] == expected_analysis
        assert "telephone" in result["prompt"]
        assert "Orange" in result["prompt"]

    def test_compare_with_market_electricite(self, mock_openai_client):
        """Test de comparaison marché pour l'électricité."""
        service = OpenAIService(api_key="test")
        contract_data = {
            "fournisseur": "EDF",
            "prix_kwh": 0.25,
            "puissance_souscrite_kva": 6
        }

        expected_analysis = {
            "recommandation": "Garder",
            "justification": "Prix compétitif",
            "comparaison_prix": {
                "prix_actuel": 0.25,
                "prix_concurrent": 0.24,
                "economie_potentielle": 0.01
            }
        }

        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = json.dumps(expected_analysis)
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_response

        result = service.compare_with_market(contract_data, "electricite")

        assert result["analysis"] == expected_analysis
        assert "electricite" in result["prompt"]

    def test_compare_with_competitor(self, mock_openai_client):
        """Test de comparaison avec un concurrent."""
        service = OpenAIService(api_key="test")
        contract_data = {"prix": 100}
        competitor_data = {"prix": 80}

        expected_analysis = {
            "recommandation": "Changer pour le concurrent",
            "economie": 20
        }

        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = json.dumps(expected_analysis)
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_response

        result = service.compare_with_competitor(contract_data, competitor_data, "telephone")

        assert result["analysis"] == expected_analysis
        assert "concurrent" in result["prompt"]

    def test_compare_error_handling(self, mock_openai_client):
        """Test de gestion d'erreur lors de la comparaison."""
        service = OpenAIService(api_key="test")
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="Erreur lors de la comparaison"):
            service.compare_with_market({}, "telephone")

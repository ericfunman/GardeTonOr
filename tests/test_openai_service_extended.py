"""Tests étendus pour le service OpenAI."""
import pytest
from unittest.mock import Mock, patch
import json

from src.services.openai_service import OpenAIService

class TestOpenAIServiceExtended:
    """Tests supplémentaires pour couvrir tous les types de contrats."""

    @pytest.fixture
    def mock_openai_client(self):
        with patch("src.services.openai_service.OpenAI") as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            yield mock_client

    def test_build_extraction_prompt_electricite(self):
        """Test de la construction du prompt pour l'électricité."""
        service = OpenAIService(api_key="test")
        prompt = service._build_extraction_prompt("electricite", "Texte du contrat...")
        assert "Analyse ce contrat de type 'electricite'" in prompt
        assert "puissance_souscrite_kva" in prompt
        assert "Texte du contrat..." in prompt

    def test_build_extraction_prompt_gaz(self):
        """Test de la construction du prompt pour le gaz."""
        service = OpenAIService(api_key="test")
        prompt = service._build_extraction_prompt("gaz", "Texte du contrat...")
        assert "Analyse ce contrat de type 'gaz'" in prompt
        assert "pce" in prompt
        assert "Texte du contrat..." in prompt

    def test_extract_contract_data_electricite(self, mock_openai_client):
        """Test d'extraction pour l'électricité."""
        service = OpenAIService(api_key="test")
        
        expected_data = {
            "fournisseur": "EDF",
            "prix_kwh": {"base": 0.20},
            "prix_abonnement_mensuel": 15.0
        }
        
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = json.dumps(expected_data)
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_response

        result = service.extract_contract_data("PDF content", "electricite")
        
        assert result["data"] == expected_data
        # Check user message content
        assert "electricite" in mock_openai_client.chat.completions.create.call_args[1]["messages"][1]["content"]

    def test_extract_contract_data_gaz(self, mock_openai_client):
        """Test d'extraction pour le gaz."""
        service = OpenAIService(api_key="test")
        
        expected_data = {
            "fournisseur": "Engie",
            "prix_kwh": 0.08,
            "prix_abonnement_mensuel": 20.0
        }
        
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = json.dumps(expected_data)
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_response

        result = service.extract_contract_data("PDF content", "gaz")
        
        assert result["data"] == expected_data
        # Check user message content
        assert "gaz" in mock_openai_client.chat.completions.create.call_args[1]["messages"][1]["content"]

    def test_extract_contract_data_json_error(self, mock_openai_client):
        """Test de gestion d'erreur JSON malformé."""
        service = OpenAIService(api_key="test")
        
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "Not a JSON string"
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_response

        with pytest.raises(Exception, match="Erreur lors de l'extraction des données"):
            service.extract_contract_data("PDF content", "telephone")

    def test_extract_contract_data_api_error(self, mock_openai_client):
        """Test de gestion d'erreur API."""
        service = OpenAIService(api_key="test")
        
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="Erreur lors de l'extraction des données"):
            service.extract_contract_data("PDF content", "telephone")

    def test_build_market_comparison_prompt_electricite(self):
        """Test de la construction du prompt de comparaison pour l'électricité."""
        service = OpenAIService(api_key="test")
        contract_data = {"fournisseur": "EDF", "prix_kwh": 0.20}
        prompt = service._build_market_comparison_prompt("electricite", contract_data)
        assert "Analyse ce contrat d'électricité" in prompt
        assert "cout_annuel_actuel" in prompt
        assert "EDF" in prompt

    def test_build_market_comparison_prompt_gaz(self):
        """Test de la construction du prompt de comparaison pour le gaz."""
        service = OpenAIService(api_key="test")
        contract_data = {"fournisseur": "Engie", "prix_kwh": 0.08}
        prompt = service._build_market_comparison_prompt("gaz", contract_data)
        assert "Analyse ce contrat de gaz naturel" in prompt
        assert "cout_annuel_actuel" in prompt
        assert "Engie" in prompt

"""Tests pour le service OpenAI."""
import pytest
from unittest.mock import Mock, patch
import json

from src.services.openai_service import OpenAIService


class TestOpenAIService:
    """Tests pour le service OpenAI."""

    @patch("src.services.openai_service.OpenAI")
    def test_initialization(self, mock_openai):
        """Test de l'initialisation du service."""
        service = OpenAIService(api_key="test_key")
        assert service.api_key == "test_key"
        mock_openai.assert_called_once_with(api_key="test_key")

    def test_initialization_without_key(self):
        """Test d'initialisation sans clé API."""
        # Patching the imported variable in the module where it is used
        with patch("src.services.openai_service.OPENAI_API_KEY", ""):
            with pytest.raises(ValueError) as excinfo:
                OpenAIService()
            assert "Clé API OpenAI non configurée" in str(excinfo.value)

    @patch("src.services.openai_service.OpenAI")
    def test_extract_contract_data_telephone(
        self, mock_openai_class, sample_pdf_text_telephone, mock_openai_response_extraction
    ):
        """Test d'extraction de données d'un contrat téléphone."""
        # Mock de la réponse OpenAI
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = json.dumps(mock_openai_response_extraction["data"])
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        # Test
        service = OpenAIService(api_key="test_key")
        result = service.extract_contract_data(sample_pdf_text_telephone, "telephone")

        assert "data" in result
        assert result["data"]["fournisseur"] == "Free Mobile"
        assert result["data"]["prix_mensuel"] == 19.99
        assert "prompt" in result
        assert "raw_response" in result

        # Vérifier que l'API a été appelée
        mock_client.chat.completions.create.assert_called_once()

    @patch("src.services.openai_service.OpenAI")
    def test_compare_with_market(
        self, mock_openai_class, sample_contract_data_telephone, mock_openai_response_market
    ):
        """Test de comparaison avec le marché."""
        # Mock de la réponse OpenAI
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = json.dumps(mock_openai_response_market["analysis"])
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        # Test
        service = OpenAIService(api_key="test_key")
        result = service.compare_with_market(sample_contract_data_telephone, "telephone")

        assert "analysis" in result
        assert result["analysis"]["recommandation"] == "changer"
        assert result["analysis"]["economie_potentielle_annuelle"] == 48.00
        mock_client.chat.completions.create.assert_called_once()

    @patch("src.services.openai_service.OpenAI")
    def test_compare_with_competitor(
        self, mock_openai_class, sample_contract_data_telephone, mock_openai_response_competitor
    ):
        """Test de comparaison avec un concurrent."""
        # Mock de la réponse OpenAI
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = json.dumps(mock_openai_response_competitor["analysis"])
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        # Test
        service = OpenAIService(api_key="test_key")
        competitor_data = {**sample_contract_data_telephone, "prix_mensuel": 15.99}

        result = service.compare_with_competitor(
            sample_contract_data_telephone, competitor_data, "telephone"
        )

        assert "analysis" in result
        assert result["analysis"]["recommandation"] == "changer pour concurrent"
        assert result["analysis"]["comparaison_prix"]["economie_potentielle"] == 48.00
        mock_client.chat.completions.create.assert_called_once()

    def test_build_extraction_prompt_telephone(self):
        """Test de construction du prompt d'extraction pour téléphone."""
        service = OpenAIService(api_key="test_key")
        prompt = service._build_extraction_prompt("telephone", "test text")

        assert "telephone" in prompt
        assert "schéma json attendu" in prompt.lower()
        assert "test text" in prompt

    def test_build_extraction_prompt_pno(self):
        """Test de construction du prompt d'extraction pour assurance PNO."""
        service = OpenAIService(api_key="test_key")
        prompt = service._build_extraction_prompt("assurance_pno", "test text")

        assert "assurance_pno" in prompt
        assert "schéma json attendu" in prompt.lower()

    def test_build_extraction_prompt_invalid_type(self):
        """Test de construction de prompt avec type invalide."""
        service = OpenAIService(api_key="test_key")

        with pytest.raises(ValueError) as excinfo:
            service._build_extraction_prompt("invalid_type", "test")

        assert "Type de contrat non supporté" in str(excinfo.value)

    @patch("src.services.openai_service.OpenAI")
    def test_extract_contract_data_error_handling(self, mock_openai_class):
        """Test de gestion d'erreur lors de l'extraction."""
        # Mock qui lève une exception
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        service = OpenAIService(api_key="test_key")

        with pytest.raises(Exception) as excinfo:
            service.extract_contract_data("test text", "telephone")

        assert "Erreur lors de l'extraction" in str(excinfo.value)

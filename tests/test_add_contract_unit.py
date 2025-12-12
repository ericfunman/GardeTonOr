import pytest
from unittest.mock import MagicMock, patch
from src.pages.add_contract import handle_extraction
from io import BytesIO

class TestAddContractUnit:
    @patch("src.pages.add_contract.get_db")
    @patch("src.pages.add_contract.OpenAIService")
    @patch("src.pages.add_contract.PDFService")
    @patch("src.pages.add_contract.ContractService")
    def test_handle_extraction(self, mock_contract_service_cls, mock_pdf_service_cls, mock_openai_service_cls, mock_get_db):
        """Test the handle_extraction function."""
        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        
        mock_contract_service = mock_contract_service_cls.return_value
        mock_contract_service.extract_and_create_contract.return_value = ({"fournisseur": "Test"}, "text")
        
        # Create fake file
        fake_file = BytesIO(b"fake pdf content")
        fake_file.name = "test.pdf"
        
        # Call function
        extracted_data, pdf_bytes = handle_extraction(fake_file, "electricite")
        
        # Assertions
        assert extracted_data == {"fournisseur": "Test"}
        assert pdf_bytes == b"fake pdf content"
        
        mock_contract_service.extract_and_create_contract.assert_called_once()
        args, kwargs = mock_contract_service.extract_and_create_contract.call_args
        assert kwargs["filename"] == "test.pdf"
        assert kwargs["contract_type"] == "electricite"

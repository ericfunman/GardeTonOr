import unittest
from unittest.mock import MagicMock, patch
import streamlit as st
from src.pages import add_contract
from datetime import datetime

class TestAddContractCoverage(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_openai_service = MagicMock()
        self.mock_contract_service = MagicMock()

    @patch("src.pages.add_contract.get_db")
    @patch("src.pages.add_contract.OpenAIService")
    @patch("src.pages.add_contract.PDFService")
    @patch("src.pages.add_contract.ContractService")
    @patch("src.pages.add_contract.st")
    def test_auto_detection_gaz(self, mock_st, mock_contract_service_cls, mock_pdf_cls, mock_openai_cls, mock_get_db):
        # Setup session state
        mock_st.session_state = {
            "extracted_data": {
                "gaz": {"pce": "12345"}
            },
            "contract_type": "auto",
            "extraction_done": True,
            "pdf_bytes": b"pdf",
            "filename": "test.pdf"
        }
        
        # Mock columns
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        
        # Execute
        add_contract.show()
        
        # Verify
        mock_st.success.assert_any_call("✨ Contrat de gaz détecté")

    @patch("src.pages.add_contract.get_db")
    @patch("src.pages.add_contract.OpenAIService")
    @patch("src.pages.add_contract.PDFService")
    @patch("src.pages.add_contract.ContractService")
    @patch("src.pages.add_contract.st")
    def test_auto_detection_fallback(self, mock_st, mock_contract_service_cls, mock_pdf_cls, mock_openai_cls, mock_get_db):
        # Setup session state
        mock_st.session_state = {
            "extracted_data": {},
            "contract_type": "auto",
            "extraction_done": True,
            "pdf_bytes": b"pdf",
            "filename": "test.pdf"
        }
        
        # Mock columns
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        
        # Execute
        add_contract.show()
        
        # Verify
        mock_st.warning.assert_called_with("⚠️ Impossible de déterminer le type précis. Affichage par défaut (Électricité).")

    @patch("src.pages.add_contract.render_dual_energy_form")
    @patch("src.pages.add_contract.get_db")
    @patch("src.pages.add_contract.OpenAIService")
    @patch("src.pages.add_contract.PDFService")
    @patch("src.pages.add_contract.ContractService")
    @patch("src.pages.add_contract.st")
    def test_submit_dual_energy(self, mock_st, mock_contract_service_cls, mock_pdf_cls, mock_openai_cls, mock_get_db, mock_render_dual):
        # Setup session state
        mock_st.session_state = {
            "extracted_data": {
                "electricite": {"pdl": "123"},
                "gaz": {"pce": "456"}
            },
            "contract_type": "auto",
            "extraction_done": True,
            "pdf_bytes": b"pdf",
            "filename": "test.pdf"
        }
        
        # Mock form submission
        mock_st.form_submit_button.side_effect = [True, False] # Submit, Cancel
        
        # Mock render form
        mock_render_dual.return_value = (
            {
                "provider": "EDF",
                "date_debut": datetime(2023, 1, 1),
                "date_anniv": datetime(2024, 1, 1),
                "pdl": "123",
                "puissance": 6,
                "prix_abo": 10,
                "prix_kwh": 0.15,
                "conso_annuelle": 1000
            },
            {
                "provider": "EDF",
                "date_debut": datetime(2023, 1, 1),
                "date_anniv": datetime(2024, 1, 1),
                "pce": "456",
                "zone": "1",
                "prix_abo": 10,
                "prix_kwh": 0.08,
                "conso_annuelle": 5000
            }
        )
        
        # Mock columns
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        
        # Mock contract service
        mock_service = mock_contract_service_cls.return_value
        mock_service.create_contract.side_effect = [MagicMock(id=1), MagicMock(id=2)]
        
        # Execute
        add_contract.show()
        
        # Verify
        self.assertEqual(mock_service.create_contract.call_count, 2)
        mock_st.success.assert_called_with("✅ 2 Contrats enregistrés avec succès ! (IDs: 1, 2)")

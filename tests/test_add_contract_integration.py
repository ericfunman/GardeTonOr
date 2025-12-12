import unittest
from unittest.mock import MagicMock, patch
from src.pages import add_contract


class TestAddContractIntegration(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_openai_service = MagicMock()
        self.mock_pdf_service = MagicMock()
        self.mock_contract_service = MagicMock()

        # Setup session state
        pass

    @patch("src.pages.add_contract.get_db")
    @patch("src.pages.add_contract.OpenAIService")
    @patch("src.pages.add_contract.PDFService")
    @patch("src.pages.add_contract.ContractService")
    def test_handle_extraction(
        self, mock_contract_service_cls, mock_pdf_cls, mock_openai_cls, mock_get_db
    ):
        # Setup mocks
        mock_contract_service = mock_contract_service_cls.return_value
        mock_contract_service.extract_and_create_contract.return_value = (
            {"some": "data"},
            "pdf_bytes",
        )

        mock_file = MagicMock()
        mock_file.name = "test.pdf"
        mock_file.read.return_value = b"pdf_content"

        # Execute
        data, pdf_bytes = add_contract.handle_extraction(mock_file, "electricite")

        # Verify
        mock_contract_service.extract_and_create_contract.assert_called_once()
        self.assertEqual(data, {"some": "data"})
        self.assertEqual(pdf_bytes, b"pdf_content")

    @patch("src.pages.add_contract.st")
    @patch("src.pages.add_contract.handle_extraction")
    def test_show_extraction_flow(self, mock_handle_extraction, mock_st):
        # Setup mocks for UI elements
        mock_st.file_uploader.return_value = MagicMock(name="uploaded_file")
        mock_st.selectbox.return_value = "electricite"
        mock_st.button.return_value = True  # Click extraction button
        mock_st.form_submit_button.return_value = False  # Don't submit the form
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        # Mock session_state as a dict
        mock_st.session_state = {}

        mock_handle_extraction.return_value = ({"extracted": "data"}, b"pdf_bytes")

        # Execute
        add_contract.show()

        # Verify extraction was called
        mock_handle_extraction.assert_called_once()

        # Check for errors
        if mock_st.error.called:
            print(f"st.error called with: {mock_st.error.call_args}")

        # Verify session state was updated
        self.assertIn("extracted_data", mock_st.session_state)
        self.assertEqual(mock_st.session_state["extracted_data"], {"extracted": "data"})
        self.assertEqual(mock_st.session_state["extraction_done"], True)
        self.assertTrue(mock_st.rerun.called)

    @patch("src.pages.add_contract.st")
    def test_show_auto_detection_electricite(self, mock_st):
        # Setup session state for "auto" detection
        mock_st.session_state = {
            "extraction_done": True,
            "contract_type": "auto",
            "extracted_data": {"electricite": {"pdl": "123"}, "gaz": None},
            "filename": "test.pdf",
            "pdf_bytes": b"bytes",
        }
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        # Execute
        add_contract.show()

        # Verify that it detected electricity
        mock_st.success.assert_any_call("✨ Contrat d'électricité détecté")

    @patch("src.pages.add_contract.st")
    @patch("src.pages.add_contract.render_electricity_form")
    def test_show_render_electricity(self, mock_render, mock_st):
        # Setup session state for rendering
        mock_st.session_state = {
            "extraction_done": True,
            "contract_type": "electricite",
            "extracted_data": {"some": "data"},
            "filename": "test.pdf",
            "pdf_bytes": b"bytes",
        }
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        # Execute
        add_contract.show()

        # Verify render function was called
        mock_render.assert_called_once()

    @patch("src.pages.add_contract.st")
    @patch("src.pages.add_contract.render_gas_form")
    def test_show_render_gas(self, mock_render, mock_st):
        mock_st.session_state = {
            "extraction_done": True,
            "contract_type": "gaz",
            "extracted_data": {"some": "data"},
            "filename": "test.pdf",
            "pdf_bytes": b"bytes",
        }
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        add_contract.show()
        mock_render.assert_called_once()

    @patch("src.pages.add_contract.st")
    @patch("src.pages.add_contract.render_dual_energy_form")
    def test_show_render_dual(self, mock_render, mock_st):
        mock_st.session_state = {
            "extraction_done": True,
            "contract_type": "electricite_gaz",
            "extracted_data": {"some": "data"},
            "filename": "test.pdf",
            "pdf_bytes": b"bytes",
        }
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        # Mock return value for unpacking
        mock_render.return_value = ({"elec": "data"}, {"gaz": "data"})

        add_contract.show()
        mock_render.assert_called_once()

    @patch("src.pages.add_contract.st")
    @patch("src.pages.add_contract.render_telephone_form")
    def test_show_render_telephone(self, mock_render, mock_st):
        mock_st.session_state = {
            "extraction_done": True,
            "contract_type": "telephone",
            "extracted_data": {"some": "data"},
            "filename": "test.pdf",
            "pdf_bytes": b"bytes",
        }
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        add_contract.show()
        mock_render.assert_called_once()

    @patch("src.pages.add_contract.st")
    @patch("src.pages.add_contract.render_insurance_habitation_form")
    def test_show_render_habitation(self, mock_render, mock_st):
        mock_st.session_state = {
            "extraction_done": True,
            "contract_type": "assurance_habitation",
            "extracted_data": {"some": "data"},
            "filename": "test.pdf",
            "pdf_bytes": b"bytes",
        }
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        add_contract.show()
        mock_render.assert_called_once()

    @patch("src.pages.add_contract.st")
    @patch("src.pages.add_contract.render_insurance_pno_form")
    def test_show_render_pno(self, mock_render, mock_st):
        mock_st.session_state = {
            "extraction_done": True,
            "contract_type": "assurance_pno",
            "extracted_data": {"some": "data"},
            "filename": "test.pdf",
            "pdf_bytes": b"bytes",
        }
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        add_contract.show()
        mock_render.assert_called_once()

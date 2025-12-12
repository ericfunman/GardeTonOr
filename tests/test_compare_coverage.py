import unittest
from unittest.mock import MagicMock, patch
from src.pages import compare


class TestCompareCoverage(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_openai_service = MagicMock()
        self.mock_contract_service = MagicMock()

    @patch("src.pages.compare.get_db")
    @patch("src.pages.compare.OpenAIService")
    @patch("src.pages.compare.PDFService")
    @patch("src.pages.compare.ContractService")
    @patch("src.pages.compare.st")
    def test_show_no_contracts_add_button(
        self, mock_st, mock_contract_service_cls, mock_pdf_cls, mock_openai_cls, mock_get_db
    ):
        # Setup mocks
        mock_contract_service = mock_contract_service_cls.return_value
        mock_contract_service.get_all_contracts.return_value = []

        # Mock button click
        mock_st.button.return_value = True

        # Setup session state
        mock_st.session_state = {}

        # Execute
        compare.show()

        # Verify
        mock_st.warning.assert_called_with(
            "⚠️ Aucun contrat enregistré. Ajoutez d'abord un contrat !"
        )
        self.assertEqual(mock_st.session_state["page"], "add")
        mock_st.rerun.assert_called()

    @patch("src.pages.compare.get_db")
    @patch("src.pages.compare.OpenAIService")
    @patch("src.pages.compare.PDFService")
    @patch("src.pages.compare.ContractService")
    @patch("src.pages.compare.st")
    def test_show_preselect_contract_error(
        self, mock_st, mock_contract_service_cls, mock_pdf_cls, mock_openai_cls, mock_get_db
    ):
        # Setup mocks
        mock_contract_service = mock_contract_service_cls.return_value

        contract = MagicMock()
        contract.id = 1
        contract.contract_type = "telephone"
        contract.provider = "Orange"
        mock_contract_service.get_all_contracts.return_value = [contract]

        # Setup session state with invalid ID
        mock_st.session_state = {"compare_contract_id": 999}

        # Execute
        compare.show()

        # Verify
        # Should not crash, just ignore the invalid ID
        # The selectbox should be called (with default index 0 probably, or whatever logic handles it)
        mock_st.selectbox.assert_called()

    @patch("src.pages.compare.st")
    def test_display_market_analysis_price_types(self, mock_st):
        # Test with cout_annuel_estime (e.g. electricity)
        comparison_elec = MagicMock()
        comparison_elec.comparison_result = {
            "analyse": {
                "offres_concurrentes": [
                    {
                        "fournisseur": "EDF",
                        "cout_annuel_estime": 1200,
                        "avantages": ["Vert"],
                        "inconvenients": ["Cher"],
                    }
                ]
            },
            "meilleure_offre": {},
        }

        # Mock columns
        def columns_side_effect(num_columns):
            return [MagicMock() for _ in range(num_columns)]

        mock_st.columns.side_effect = columns_side_effect

        compare.display_market_analysis(comparison_elec)

        # Verify metric called with /an
        mock_st.metric.assert_called()

        # Test with prime_annuelle (e.g. insurance)
        comparison_ins = MagicMock()
        comparison_ins.comparison_result = {
            "analyse": {
                "offres_concurrentes": [
                    {
                        "assureur": "AXA",
                        "prime_annuelle": 500,
                        "avantages": ["Rapide"],
                        "inconvenients": ["Franchise"],
                    }
                ]
            },
            "meilleure_offre": {},
        }

        compare.display_market_analysis(comparison_ins)
        mock_st.metric.assert_called()

        # Test with no price
        comparison_none = MagicMock()
        comparison_none.comparison_result = {
            "analyse": {
                "offres_concurrentes": [
                    {"fournisseur": "Unknown", "avantages": [], "inconvenients": []}
                ]
            },
            "meilleure_offre": {},
        }

        compare.display_market_analysis(comparison_none)
        mock_st.metric.assert_called()

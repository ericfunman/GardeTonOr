import unittest
from unittest.mock import MagicMock, patch
import streamlit as st
from src.pages import compare

class TestCompareIntegration(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_openai_service = MagicMock()
        self.mock_contract_service = MagicMock()
        
        # Setup session state
        pass

    @patch("src.pages.compare.get_db")
    @patch("src.pages.compare.OpenAIService")
    @patch("src.pages.compare.PDFService")
    @patch("src.pages.compare.ContractService")
    @patch("src.pages.compare.st")
    def test_display_comparison_table_telephone(self, mock_st, mock_contract_service_cls, mock_pdf_cls, mock_openai_cls, mock_get_db):
        # Setup mocks
        mock_contract_service = mock_contract_service_cls.return_value
        
        # Mock contract
        contract = MagicMock()
        contract.id = 1
        contract.contract_type = "telephone"
        contract.provider = "Orange"
        contract.contract_data = {
            "fournisseur": "Orange",
            "forfait_nom": "Forfait 50Go",
            "data_go": 50,
            "prix_mensuel": 20
        }
        mock_contract_service.get_all_contracts.return_value = [contract]
        
        # Mock comparison
        comparison = MagicMock()
        comparison.contract = contract
        comparison.best_competitor_data = {
            "fournisseur": "Free",
            "forfait_nom": "Forfait 100Go",
            "data_go": 100,
            "prix_mensuel": 15
        }
        comparison.comparison_result = {
            "recommandation": "Changer pour Free",
            "justification": "Moins cher et plus de data",
            "comparaison_prix": {
                "prix_actuel": 20.0,
                "prix_concurrent": 15.0,
                "economie_annuelle": 60.0
            }
        }
        mock_contract_service.get_contract_comparisons.return_value = [comparison]
        
        # Mock UI
        mock_st.selectbox.return_value = 1
        
        def columns_side_effect(num_columns):
            return [MagicMock() for _ in range(num_columns)]
            
        mock_st.columns.side_effect = columns_side_effect
        
        # Execute
        compare.show()
        
        # Verify
        # Check if dataframe was displayed (it's used for the table)
        # Note: The code might use st.table or st.dataframe or st.columns
        # Looking at the code, it constructs 'rows' list and then creates a DataFrame
        # df = pd.DataFrame(rows, columns=["Caractéristique", "Mon Contrat", "Meilleure Offre"])
        # st.table(df)
        mock_st.metric.assert_called()

    @patch("src.pages.compare.get_db")
    @patch("src.pages.compare.OpenAIService")
    @patch("src.pages.compare.PDFService")
    @patch("src.pages.compare.ContractService")
    @patch("src.pages.compare.st")
    def test_display_comparison_table_pno(self, mock_st, mock_contract_service_cls, mock_pdf_cls, mock_openai_cls, mock_get_db):
        mock_contract_service = mock_contract_service_cls.return_value
        
        contract = MagicMock()
        contract.id = 1
        contract.contract_type = "assurance_pno"
        contract.provider = "AXA"
        contract.contract_data = {
            "assureur": "AXA",
            "prime_annuelle": 200,
            "franchise": 150
        }
        mock_contract_service.get_all_contracts.return_value = [contract]
        
        comparison = MagicMock()
        comparison.contract = contract
        comparison.best_competitor_data = {
            "assureur": "Allianz",
            "prime_annuelle": 150,
            "franchise": 100
        }
        comparison.comparison_result = {
            "recommandation": "Changer pour Allianz",
            "justification": "Moins cher",
            "comparaison_prix": {
                "prix_actuel": 200.0,
                "prix_concurrent": 150.0,
                "economie_annuelle": 50.0
            }
        }
        mock_contract_service.get_contract_comparisons.return_value = [comparison]
        
        mock_st.selectbox.return_value = 1
        
        def columns_side_effect(num_columns):
            return [MagicMock() for _ in range(num_columns)]
            
        mock_st.columns.side_effect = columns_side_effect
        
        compare.show()
        
        mock_st.metric.assert_called()

    @patch("src.pages.compare.get_db")
    @patch("src.pages.compare.OpenAIService")
    @patch("src.pages.compare.PDFService")
    @patch("src.pages.compare.ContractService")
    @patch("src.pages.compare.st")
    def test_display_comparison_table_habitation(self, mock_st, mock_contract_service_cls, mock_pdf_cls, mock_openai_cls, mock_get_db):
        mock_contract_service = mock_contract_service_cls.return_value
        
        contract = MagicMock()
        contract.id = 1
        contract.contract_type = "assurance_habitation"
        contract.provider = "AXA"
        contract.contract_data = {
            "assureur": "AXA",
            "prime_annuelle": 300,
            "franchise": 200
        }
        mock_contract_service.get_all_contracts.return_value = [contract]
        
        comparison = MagicMock()
        comparison.contract = contract
        comparison.best_competitor_data = {
            "assureur": "Allianz",
            "prime_annuelle": 250,
            "franchise": 150
        }
        comparison.comparison_result = {
            "recommandation": "Changer pour Allianz",
            "justification": "Moins cher",
            "comparaison_prix": {
                "prix_actuel": 300.0,
                "prix_concurrent": 250.0,
                "economie_annuelle": 50.0
            }
        }
        mock_contract_service.get_contract_comparisons.return_value = [comparison]
        
        mock_st.selectbox.return_value = 1
        
        def columns_side_effect(num_columns):
            return [MagicMock() for _ in range(num_columns)]
            
        mock_st.columns.side_effect = columns_side_effect
        
        compare.show()
        
        mock_st.metric.assert_called()
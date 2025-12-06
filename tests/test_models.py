"""Tests pour les modèles de base de données."""
import pytest
from datetime import datetime

from src.database.models import Contract, Comparison, ExtractionLog


class TestContractModel:
    """Tests pour le modèle Contract."""

    def test_create_contract(self, db_session, sample_contract_data_telephone):
        """Test de création d'un contrat."""
        contract = Contract(
            contract_type="telephone",
            provider="Free Mobile",
            start_date=datetime(2024, 1, 15),
            anniversary_date=datetime(2025, 1, 15),
            contract_data=sample_contract_data_telephone,
            original_filename="test.pdf",
            validated=1
        )
        
        db_session.add(contract)
        db_session.commit()
        db_session.refresh(contract)
        
        assert contract.id is not None
        assert contract.provider == "Free Mobile"
        assert contract.contract_type == "telephone"
        assert contract.validated == 1
        assert contract.contract_data["prix_mensuel"] == 19.99

    def test_contract_relationships(self, db_session, sample_contract_telephone):
        """Test des relations du contrat."""
        # Créer une comparaison liée au contrat
        comparison = Comparison(
            contract_id=sample_contract_telephone.id,
            comparison_type="market_analysis",
            gpt_prompt="test",
            gpt_response="test response",
            comparison_result={"test": "data"}
        )
        
        db_session.add(comparison)
        db_session.commit()
        
        # Vérifier la relation
        assert len(sample_contract_telephone.comparisons) == 1
        assert sample_contract_telephone.comparisons[0].comparison_type == "market_analysis"

    def test_contract_repr(self, sample_contract_telephone):
        """Test de la représentation string du contrat."""
        repr_str = repr(sample_contract_telephone)
        assert "Contract" in repr_str
        assert "Free Mobile" in repr_str


class TestComparisonModel:
    """Tests pour le modèle Comparison."""

    def test_create_comparison(self, db_session, sample_contract_telephone):
        """Test de création d'une comparaison."""
        comparison = Comparison(
            contract_id=sample_contract_telephone.id,
            comparison_type="market_analysis",
            gpt_prompt="Test prompt",
            gpt_response="Test response",
            analysis_summary="Test summary",
            comparison_result={"economie": 50}
        )
        
        db_session.add(comparison)
        db_session.commit()
        db_session.refresh(comparison)
        
        assert comparison.id is not None
        assert comparison.contract_id == sample_contract_telephone.id
        assert comparison.comparison_type == "market_analysis"
        assert comparison.comparison_result["economie"] == 50

    def test_comparison_with_competitor_data(self, db_session, sample_contract_telephone):
        """Test d'une comparaison avec devis concurrent."""
        comparison = Comparison(
            contract_id=sample_contract_telephone.id,
            comparison_type="competitor_quote",
            competitor_filename="concurrent.pdf",
            competitor_data={"prix": 15.99},
            gpt_prompt="Compare",
            gpt_response="Result",
            comparison_result={"economie": 48}
        )
        
        db_session.add(comparison)
        db_session.commit()
        
        assert comparison.competitor_filename == "concurrent.pdf"
        assert comparison.competitor_data["prix"] == 15.99


class TestExtractionLogModel:
    """Tests pour le modèle ExtractionLog."""

    def test_create_extraction_log(self, db_session):
        """Test de création d'un log d'extraction."""
        log = ExtractionLog(
            filename="test.pdf",
            contract_type="telephone",
            gpt_prompt="Extract data",
            gpt_response="Extracted",
            extracted_data={"provider": "Test"},
            success=1
        )
        
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        
        assert log.id is not None
        assert log.filename == "test.pdf"
        assert log.success == 1
        assert log.extracted_data["provider"] == "Test"

    def test_extraction_log_with_error(self, db_session):
        """Test d'un log d'extraction avec erreur."""
        log = ExtractionLog(
            filename="bad.pdf",
            contract_type="telephone",
            gpt_prompt="Extract",
            gpt_response="Error",
            extracted_data={},
            success=0,
            error_message="PDF format invalide"
        )
        
        db_session.add(log)
        db_session.commit()
        
        assert log.success == 0
        assert log.error_message == "PDF format invalide"

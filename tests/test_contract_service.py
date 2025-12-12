"""Tests pour le service de gestion des contrats."""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from src.services.contract_service import ContractService
from src.database.models import Contract


class TestContractService:
    """Tests pour le service de contrats."""

    def test_get_all_contracts(self, db_session, sample_contract_telephone, sample_contract_pno):
        """Test de récupération de tous les contrats."""
        mock_openai = Mock()
        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)
        contracts = service.get_all_contracts()

        assert len(contracts) == 2
        assert any(c.provider == "Free Mobile" for c in contracts)
        assert any(c.provider == "AXA" for c in contracts)

    def test_get_contract_by_id(self, db_session, sample_contract_telephone):
        """Test de récupération d'un contrat par ID."""
        mock_openai = Mock()
        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)
        contract = service.get_contract_by_id(sample_contract_telephone.id)

        assert contract is not None
        assert contract.provider == "Free Mobile"

    def test_get_contract_by_invalid_id(self, db_session):
        """Test de récupération avec un ID invalide."""
        mock_openai = Mock()
        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)
        contract = service.get_contract_by_id(9999)

        assert contract is None

    def test_get_contracts_needing_attention(self, db_session):
        """Test de récupération des contrats nécessitant attention."""
        # Créer un contrat avec date anniversaire proche
        near_date = datetime.now() + timedelta(days=30)
        contract = Contract(
            contract_type="telephone",
            provider="Test Provider",
            start_date=datetime.now(),
            anniversary_date=near_date,
            contract_data={"test": "data"},
            validated=1,
        )
        db_session.add(contract)
        db_session.commit()

        mock_openai = Mock()
        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)
        contracts = service.get_contracts_needing_attention()

        assert len(contracts) >= 1
        assert any(c.provider == "Test Provider" for c in contracts)

    def test_create_contract(self, db_session):
        """Test de création d'un contrat."""
        mock_openai = Mock()
        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)

        contract_data = {"fournisseur": "Orange", "prix_mensuel": 25.99}

        contract = service.create_contract(
            contract_type="telephone",
            provider="Orange",
            start_date=datetime(2024, 1, 1),
            anniversary_date=datetime(2025, 1, 1),
            contract_data=contract_data,
            pdf_bytes=b"fake pdf content",
            filename="orange.pdf",
        )

        assert contract.id is not None
        assert contract.provider == "Orange"
        assert contract.validated == 1
        assert contract.contract_data["prix_mensuel"] == 25.99

    def test_extract_and_create_contract(self, db_session, mock_openai_response_extraction):
        """Test d'extraction et préparation de création de contrat."""
        mock_openai = Mock()
        mock_openai.extract_contract_data.return_value = mock_openai_response_extraction

        mock_pdf = Mock()
        mock_pdf.validate_pdf.return_value = True
        mock_pdf.extract_text_from_pdf.return_value = "test pdf text"

        service = ContractService(db_session, mock_openai, mock_pdf)

        extracted_data, pdf_text = service.extract_and_create_contract(
            pdf_bytes=b"fake pdf", filename="test.pdf", contract_type="telephone"
        )

        assert extracted_data["fournisseur"] == "Free Mobile"
        assert pdf_text == "test pdf text"
        mock_pdf.validate_pdf.assert_called_once()
        mock_pdf.extract_text_from_pdf.assert_called_once()
        mock_openai.extract_contract_data.assert_called_once()

    def test_extract_and_create_contract_invalid_pdf(self, db_session):
        """Test d'extraction avec un PDF invalide."""
        mock_openai = Mock()

        mock_pdf = Mock()
        mock_pdf.validate_pdf.return_value = False

        service = ContractService(db_session, mock_openai, mock_pdf)

        with pytest.raises(ValueError) as excinfo:
            service.extract_and_create_contract(
                pdf_bytes=b"invalid", filename="bad.pdf", contract_type="telephone"
            )

        assert "PDF valide" in str(excinfo.value)

    def test_compare_with_market(
        self, db_session, sample_contract_telephone, mock_openai_response_market
    ):
        """Test de comparaison avec le marché."""
        mock_openai = Mock()
        mock_openai.compare_with_market.return_value = mock_openai_response_market

        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)
        comparison = service.compare_with_market(sample_contract_telephone.id)

        assert comparison.id is not None
        assert comparison.contract_id == sample_contract_telephone.id
        assert comparison.comparison_type == "market_analysis"
        assert comparison.comparison_result["recommandation"] == "changer"
        mock_openai.compare_with_market.assert_called_once()

    def test_compare_with_market_invalid_contract(self, db_session):
        """Test de comparaison avec un contrat inexistant."""
        mock_openai = Mock()
        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)

        with pytest.raises(ValueError) as excinfo:
            service.compare_with_market(9999)

        assert "non trouvé" in str(excinfo.value)

    def test_compare_with_competitor(
        self,
        db_session,
        sample_contract_telephone,
        mock_openai_response_extraction,
        mock_openai_response_competitor,
    ):
        """Test de comparaison avec un concurrent."""
        mock_openai = Mock()
        mock_openai.extract_contract_data.return_value = mock_openai_response_extraction
        mock_openai.compare_with_competitor.return_value = mock_openai_response_competitor

        mock_pdf = Mock()
        mock_pdf.extract_text_from_pdf.return_value = "competitor text"

        service = ContractService(db_session, mock_openai, mock_pdf)

        comparison = service.compare_with_competitor(
            contract_id=sample_contract_telephone.id,
            competitor_pdf_bytes=b"competitor pdf",
            competitor_filename="competitor.pdf",
        )

        assert comparison.id is not None
        assert comparison.comparison_type == "competitor_quote"
        assert comparison.competitor_filename == "competitor.pdf"
        assert comparison.competitor_data is not None
        mock_pdf.extract_text_from_pdf.assert_called_once()
        mock_openai.extract_contract_data.assert_called_once()
        mock_openai.compare_with_competitor.assert_called_once()

    def test_get_contract_comparisons(
        self, db_session, sample_contract_telephone, mock_openai_response_market
    ):
        """Test de récupération des comparaisons d'un contrat."""
        mock_openai = Mock()
        mock_openai.compare_with_market.return_value = mock_openai_response_market
        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)

        # Créer une comparaison
        service.compare_with_market(sample_contract_telephone.id)

        # Récupérer les comparaisons
        comparisons = service.get_contract_comparisons(sample_contract_telephone.id)

        assert len(comparisons) == 1
        assert comparisons[0].contract_id == sample_contract_telephone.id

    def test_delete_contract(self, db_session, sample_contract_telephone):
        """Test de suppression d'un contrat."""
        mock_openai = Mock()
        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)

        contract_id = sample_contract_telephone.id
        result = service.delete_contract(contract_id)

        assert result is True

        # Vérifier que le contrat n'existe plus
        deleted_contract = service.get_contract_by_id(contract_id)
        assert deleted_contract is None

    def test_delete_nonexistent_contract(self, db_session):
        """Test de suppression d'un contrat inexistant."""
        mock_openai = Mock()
        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)
        result = service.delete_contract(9999)

        assert result is False

    def test_update_contract(self, db_session, sample_contract_telephone):
        """Test de mise à jour d'un contrat."""
        mock_openai = Mock()
        mock_pdf = Mock()

        service = ContractService(db_session, mock_openai, mock_pdf)

        updates = {"provider": "Free Mobile Updated", "validated": 0}

        updated_contract = service.update_contract(sample_contract_telephone.id, updates)

        assert updated_contract is not None
        assert updated_contract.provider == "Free Mobile Updated"
        assert updated_contract.validated == 0

    def test_get_all_simulations(self, db_session):
        """Test de récupération des simulations."""
        mock_openai = Mock()
        mock_pdf = Mock()
        service = ContractService(db_session, mock_openai, mock_pdf)

        # Créer un contrat réel
        service.create_contract(
            contract_type="telephone",
            provider="Real",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={},
            pdf_bytes=b"pdf",
            filename="real.pdf",
            is_simulation=False,
        )

        # Créer une simulation
        service.create_contract(
            contract_type="telephone",
            provider="Simu",
            start_date=datetime.now(),
            anniversary_date=datetime.now(),
            contract_data={},
            pdf_bytes=b"pdf",
            filename="simu.pdf",
            is_simulation=True,
        )

        contracts = service.get_all_contracts()
        simulations = service.get_all_simulations()

        # Note: get_all_contracts might return existing sample contracts from fixtures if not isolated properly,
        # but db_session should be clean or we check for existence.
        # Actually, db_session is function scoped, so it might have data from other tests if not rolled back?
        # No, pytest fixtures usually handle this.
        # But wait, sample_contract_telephone fixture adds to session?
        # This test doesn't use those fixtures, so it should be empty initially.

        assert any(c.provider == "Real" for c in contracts)
        assert not any(c.provider == "Simu" for c in contracts)

        assert any(c.provider == "Simu" for c in simulations)
        assert not any(c.provider == "Real" for c in simulations)

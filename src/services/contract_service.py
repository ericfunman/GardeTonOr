"""Service métier pour la gestion des contrats."""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from src.database.models import Contract, Comparison, ExtractionLog
from src.services.openai_service import OpenAIService
from src.services.pdf_service import PDFService
from src.config import NOTIFICATION_DAYS_BEFORE


class ContractService:
    """Service pour la logique métier des contrats."""

    def __init__(self, db: Session, openai_service: OpenAIService, pdf_service: PDFService):
        """
        Initialise le service de contrats.

        Args:
            db: Session de base de données
            openai_service: Service OpenAI
            pdf_service: Service PDF
        """
        self.db = db
        self.openai_service = openai_service
        self.pdf_service = pdf_service

    def extract_and_create_contract(
        self, pdf_bytes: bytes, filename: str, contract_type: str
    ) -> Tuple[Dict[str, Any], str]:
        """
        Extrait les données d'un PDF et prépare les données pour création de contrat.

        Args:
            pdf_bytes: Contenu du PDF
            filename: Nom du fichier
            contract_type: Type de contrat

        Returns:
            Tuple (données extraites, texte du PDF pour affichage)

        Raises:
            Exception: Si l'extraction échoue
        """
        # Valider le PDF
        if not self.pdf_service.validate_pdf(pdf_bytes):
            raise ValueError("Le fichier n'est pas un PDF valide")

        # Extraire le texte
        pdf_text = self.pdf_service.extract_text_from_pdf(pdf_bytes)

        # Extraire les données structurées avec OpenAI
        extraction_result = self.openai_service.extract_contract_data(pdf_text, contract_type)

        # Logger l'extraction
        extraction_log = ExtractionLog(
            filename=filename,
            contract_type=contract_type,
            gpt_prompt=extraction_result["prompt"],
            gpt_response=extraction_result["raw_response"],
            extracted_data=extraction_result["data"],
            success=1,
        )
        self.db.add(extraction_log)
        self.db.commit()

        return extraction_result["data"], pdf_text

    def create_contract(
        self,
        contract_type: str,
        provider: str,
        start_date: datetime,
        anniversary_date: datetime,
        contract_data: Dict[str, Any],
        pdf_bytes: bytes,
        filename: str,
        end_date: Optional[datetime] = None,
    ) -> Contract:
        """
        Crée un nouveau contrat dans la base de données.

        Args:
            contract_type: Type de contrat
            provider: Fournisseur
            start_date: Date de début
            anniversary_date: Date anniversaire
            contract_data: Données structurées du contrat
            pdf_bytes: Contenu du PDF
            filename: Nom du fichier
            end_date: Date de fin (optionnel)

        Returns:
            Contrat créé
        """
        contract = Contract(
            contract_type=contract_type,
            provider=provider,
            start_date=start_date,
            end_date=end_date,
            anniversary_date=anniversary_date,
            contract_data=contract_data,
            pdf_content=pdf_bytes,
            original_filename=filename,
            validated=1,  # Validé après confirmation utilisateur
        )

        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)

        return contract

    def get_all_contracts(self) -> List[Contract]:
        """Récupère tous les contrats."""
        return self.db.query(Contract).order_by(Contract.anniversary_date).all()

    def get_contract_by_id(self, contract_id: int) -> Optional[Contract]:
        """Récupère un contrat par son ID."""
        return self.db.query(Contract).filter(Contract.id == contract_id).first()

    def get_contracts_needing_attention(self) -> List[Contract]:
        """
        Récupère les contrats dont la date anniversaire approche.

        Returns:
            Liste des contrats nécessitant attention
        """
        threshold_date = datetime.now() + timedelta(days=NOTIFICATION_DAYS_BEFORE)

        return (
            self.db.query(Contract)
            .filter(
                Contract.anniversary_date <= threshold_date,
                Contract.anniversary_date >= datetime.now(),
            )
            .order_by(Contract.anniversary_date)
            .all()
        )

    def compare_with_market(self, contract_id: int) -> Comparison:
        """
        Compare un contrat avec le marché actuel.

        Args:
            contract_id: ID du contrat à comparer

        Returns:
            Objet Comparison créé

        Raises:
            ValueError: Si le contrat n'existe pas
        """
        contract = self.get_contract_by_id(contract_id)
        if not contract:
            raise ValueError(f"Contrat {contract_id} non trouvé")

        # Effectuer la comparaison via OpenAI
        comparison_result = self.openai_service.compare_with_market(
            contract.contract_data, contract.contract_type
        )

        # Créer l'objet Comparison
        # Gérer la structure imbriquée "analyse" pour les analyses de marché
        analysis_data = comparison_result["analysis"]
        recommandation = analysis_data.get("recommandation", "")

        if "analyse" in analysis_data and isinstance(analysis_data["analyse"], dict):
            recommandation = analysis_data["analyse"].get("recommandation", recommandation)

        comparison = Comparison(
            contract_id=contract_id,
            comparison_type="market_analysis",
            gpt_prompt=comparison_result["prompt"],
            gpt_response=comparison_result["raw_response"],
            comparison_result=comparison_result["analysis"],
            analysis_summary=recommandation,
        )

        self.db.add(comparison)
        self.db.commit()
        self.db.refresh(comparison)

        return comparison

    def compare_with_competitor(
        self, contract_id: int, competitor_pdf_bytes: bytes, competitor_filename: str
    ) -> Comparison:
        """
        Compare un contrat avec un devis concurrent.

        Args:
            contract_id: ID du contrat à comparer
            competitor_pdf_bytes: Contenu du PDF concurrent
            competitor_filename: Nom du fichier concurrent

        Returns:
            Objet Comparison créé

        Raises:
            ValueError: Si le contrat n'existe pas ou si l'extraction échoue
        """
        contract = self.get_contract_by_id(contract_id)
        if not contract:
            raise ValueError(f"Contrat {contract_id} non trouvé")

        # Extraire les données du PDF concurrent
        competitor_text = self.pdf_service.extract_text_from_pdf(competitor_pdf_bytes)
        competitor_extraction = self.openai_service.extract_contract_data(
            competitor_text, contract.contract_type
        )

        # Comparer les deux contrats
        comparison_result = self.openai_service.compare_with_competitor(
            contract.contract_data, competitor_extraction["data"], contract.contract_type
        )

        # Créer l'objet Comparison
        comparison = Comparison(
            contract_id=contract_id,
            comparison_type="competitor_quote",
            competitor_filename=competitor_filename,
            competitor_pdf=competitor_pdf_bytes,
            competitor_data=competitor_extraction["data"],
            gpt_prompt=comparison_result["prompt"],
            gpt_response=comparison_result["raw_response"],
            comparison_result=comparison_result["analysis"],
            analysis_summary=comparison_result["analysis"].get("recommandation", ""),
        )

        self.db.add(comparison)
        self.db.commit()
        self.db.refresh(comparison)

        return comparison

    def get_contract_comparisons(self, contract_id: int) -> List[Comparison]:
        """Récupère toutes les comparaisons d'un contrat."""
        return (
            self.db.query(Comparison)
            .filter(Comparison.contract_id == contract_id)
            .order_by(Comparison.created_at.desc())
            .all()
        )

    def get_all_comparisons(self) -> List[Comparison]:
        """Récupère toutes les comparaisons."""
        return self.db.query(Comparison).order_by(Comparison.created_at.desc()).all()

    def delete_contract(self, contract_id: int) -> bool:
        """
        Supprime un contrat.

        Args:
            contract_id: ID du contrat à supprimer

        Returns:
            True si suppression réussie, False sinon
        """
        contract = self.get_contract_by_id(contract_id)
        if not contract:
            return False

        self.db.delete(contract)
        self.db.commit()
        return True

    def update_contract(self, contract_id: int, updates: Dict[str, Any]) -> Optional[Contract]:
        """
        Met à jour un contrat.

        Args:
            contract_id: ID du contrat
            updates: Dictionnaire des champs à mettre à jour

        Returns:
            Contrat mis à jour ou None
        """
        contract = self.get_contract_by_id(contract_id)
        if not contract:
            return None

        for key, value in updates.items():
            if hasattr(contract, key):
                setattr(contract, key, value)

        contract.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(contract)

        return contract

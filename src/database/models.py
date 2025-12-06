"""Modèles de base de données pour GardeTonOr."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    LargeBinary,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Contract(Base):
    """Modèle pour les contrats."""

    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_type = Column(String(50), nullable=False, index=True)  # telephone, assurance_pno
    provider = Column(String(200), nullable=False)  # Fournisseur
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    anniversary_date = Column(DateTime, nullable=False, index=True)
    
    # Données structurées spécifiques au type de contrat (JSON)
    contract_data = Column(JSON, nullable=False)
    
    # Document original
    original_filename = Column(String(500))
    pdf_content = Column(LargeBinary, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    validated = Column(Integer, default=0)  # 0 = non validé, 1 = validé
    
    # Relations
    comparisons = relationship("Comparison", back_populates="contract", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contract(id={self.id}, type={self.contract_type}, provider={self.provider})>"


class Comparison(Base):
    """Modèle pour les comparaisons de contrats."""

    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    
    # Type de comparaison
    comparison_type = Column(String(50), nullable=False)  # market_analysis, competitor_quote
    
    # Pour les comparaisons avec devis concurrent
    competitor_filename = Column(String(500), nullable=True)
    competitor_pdf = Column(LargeBinary, nullable=True)
    competitor_data = Column(JSON, nullable=True)
    
    # Résultats de la comparaison
    gpt_prompt = Column(Text, nullable=False)
    gpt_response = Column(Text, nullable=False)
    analysis_summary = Column(Text, nullable=True)
    
    # Résultat structuré (JSON)
    comparison_result = Column(JSON, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    contract = relationship("Contract", back_populates="comparisons")
    
    def __repr__(self):
        return f"<Comparison(id={self.id}, contract_id={self.contract_id}, type={self.comparison_type})>"


class ExtractionLog(Base):
    """Modèle pour logger les extractions de données par GPT."""

    __tablename__ = "extraction_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    contract_type = Column(String(50), nullable=False)
    
    # Prompt et réponse GPT
    gpt_prompt = Column(Text, nullable=False)
    gpt_response = Column(Text, nullable=False)
    
    # Données extraites (JSON)
    extracted_data = Column(JSON, nullable=False)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Integer, default=1)  # 1 = succès, 0 = échec
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ExtractionLog(id={self.id}, filename={self.filename}, success={self.success})>"

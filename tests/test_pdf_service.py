"""Tests pour le service PDF."""
import pytest
import io
from PyPDF2 import PdfWriter

from src.services.pdf_service import PDFService


class TestPDFService:
    """Tests pour le service PDF."""

    def test_validate_valid_pdf(self):
        """Test de validation d'un PDF valide."""
        # Créer un PDF minimal valide
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=200, height=200)
        
        pdf_bytes = io.BytesIO()
        pdf_writer.write(pdf_bytes)
        pdf_content = pdf_bytes.getvalue()
        
        service = PDFService()
        assert service.validate_pdf(pdf_content) is True

    def test_validate_invalid_pdf(self):
        """Test de validation d'un fichier invalide."""
        service = PDFService()
        invalid_content = b"This is not a PDF"
        
        assert service.validate_pdf(invalid_content) is False

    def test_extract_text_invalid_pdf(self):
        """Test d'extraction de texte d'un PDF invalide."""
        service = PDFService()
        invalid_content = b"Not a PDF"
        
        with pytest.raises(Exception) as excinfo:
            service.extract_text_from_pdf(invalid_content)
        
        assert "Erreur lors de l'extraction" in str(excinfo.value)

    def test_extract_text_empty_pdf(self):
        """Test d'extraction d'un PDF vide."""
        # Créer un PDF vide
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=200, height=200)
        
        pdf_bytes = io.BytesIO()
        pdf_writer.write(pdf_bytes)
        pdf_content = pdf_bytes.getvalue()
        
        service = PDFService()
        
        with pytest.raises(Exception) as excinfo:
            service.extract_text_from_pdf(pdf_content)
        
        assert "ne contient pas de texte" in str(excinfo.value)

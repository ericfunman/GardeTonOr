"""Service d'extraction de texte depuis les fichiers PDF."""
import io
from typing import Optional
import pdfplumber


class PDFService:
    """Service pour extraire le texte des fichiers PDF."""

    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """
        Extrait le texte d'un fichier PDF.

        Args:
            pdf_bytes: Contenu du PDF en bytes

        Returns:
            Texte extrait du PDF

        Raises:
            Exception: Si l'extraction échoue
        """
        try:
            text_content = []
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            full_text = "\n\n".join(text_content)
            
            if not full_text.strip():
                raise ValueError("Le PDF ne contient pas de texte extractible")
            
            return full_text
        
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction du PDF: {str(e)}")

    @staticmethod
    def validate_pdf(pdf_bytes: bytes) -> bool:
        """
        Vérifie si le fichier est un PDF valide.

        Args:
            pdf_bytes: Contenu du fichier en bytes

        Returns:
            True si le fichier est un PDF valide
        """
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                # Vérifie qu'il y a au moins une page
                return len(pdf.pages) > 0
        except Exception:
            return False

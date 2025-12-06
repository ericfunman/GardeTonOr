"""Test d'extraction du PDF TotalEnergies"""
import sys
sys.path.insert(0, 'src')

from services.pdf_service import PDFService
from services.openai_service import OpenAIService
from config import OPENAI_API_KEY

# Extraire le texte
pdf_service = PDFService()
pdf_path = "Contrats/TotalEnergies.pdf"

print("="*80)
print("EXTRACTION DU TEXTE DU PDF")
print("="*80)

text = pdf_service.extract_text_from_pdf(pdf_path)
print(f"\nTexte extrait: {len(text)} caractères\n")
print(text[:1500])
print("\n[...]\n")

# Analyser avec ChatGPT
print("\n" + "="*80)
print("ANALYSE AVEC CHATGPT")
print("="*80 + "\n")

openai_service = OpenAIService(OPENAI_API_KEY)
result = openai_service.extract_contract_data(text, "electricite")

print("\nRésultat:")
print(result)

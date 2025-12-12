import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Force reload .env to override any dummy keys in environment
load_dotenv(override=True)

from src.services.pdf_service import PDFService
from src.services.openai_service import OpenAIService


def test_extraction():
    # Path to the PDF
    pdf_path = Path(
        r"c:\Users\lapin\OneDrive\Documents\Developpement\GardeTonOr\Contrats\TotalEnergies.pdf"
    )

    if not pdf_path.exists():
        print(f"Error: File not found at {pdf_path}")
        return

    print(f"Reading file: {pdf_path}")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # 1. Extract Text
    print("\n--- 1. Extracting Text with PDFService ---")
    try:
        pdf_service = PDFService()
        pdf_text = pdf_service.extract_text_from_pdf(pdf_bytes)
        print(f"Success! Extracted {len(pdf_text)} characters.")
        print("First 500 chars preview:")
        print("-" * 50)
        print(pdf_text[:500])
        print("-" * 50)
    except Exception as e:
        print(f"Error extracting text: {e}")
        return

    # 2. Call OpenAI
    print("\n--- 2. Calling OpenAI Service (Type: electricite) ---")
    try:
        openai_service = OpenAIService()
        # Using 'electricite' as default for TotalEnergies
        result = openai_service.extract_contract_data(pdf_text, "electricite")

        print("\n--- Extraction Result ---")
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))

        # Check for empty fields
        data = result["data"]
        empty_fields = []

        # Check some key fields
        if not data.get("electricite", {}).get("pdl"):
            empty_fields.append("electricite.pdl")
        if not data.get("electricite", {}).get("tarifs", {}).get("prix_kwh_ttc"):
            empty_fields.append("electricite.tarifs.prix_kwh_ttc")

        if empty_fields:
            print(f"\nWARNING: Some fields are empty: {empty_fields}")
        else:
            print("\nSUCCESS: Key fields seem populated.")

    except Exception as e:
        print(f"Error calling OpenAI: {e}")


if __name__ == "__main__":
    test_extraction()

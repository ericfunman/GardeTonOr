"""
Script pour extraire les données du PDF TotalEnergies via ChatGPT
"""
import pdfplumber
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

def extract_pdf_with_chatgpt(pdf_path):
    """Extrait le texte du PDF et l'envoie à ChatGPT pour analyse"""
    
    # Extraire le texte du PDF
    print(f"Extraction du texte de {pdf_path}...")
    text_content = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Nombre de pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages, 1):
            print(f"Traitement page {i}...")
            page_text = page.extract_text()
            if page_text:
                text_content += f"\n\n--- Page {i} ---\n\n{page_text}"
    
    if not text_content.strip():
        print("Erreur: Impossible d'extraire le texte du PDF")
        return None
    
    print(f"\nTexte extrait ({len(text_content)} caractères)")
    print("\n" + "="*80)
    print(text_content[:500] + "...")
    print("="*80 + "\n")
    
    # Envoyer à ChatGPT pour analyse
    print("Envoi à ChatGPT pour analyse...")
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = """Analyse ce contrat d'électricité et extrais TOUTES les données importantes.

Réponds UNIQUEMENT avec un JSON valide contenant ces champs:
{
    "fournisseur": "nom du fournisseur",
    "numero_contrat": "numéro de contrat",
    "type_offre": "type d'offre (ex: Offre Verte, Fixe, etc)",
    "puissance_souscrite_kva": 6,
    "option_tarifaire": "Base ou HP/HC",
    "prix_abonnement_mensuel": 12.34,
    "prix_kwh": {
        "base": 0.1234,
        "heures_pleines": 0.1234,
        "heures_creuses": 0.1234
    },
    "adresse_fourniture": "adresse complète",
    "pdl": "numéro PDL (14 chiffres)",
    "pce": "si c'est du gaz",
    "date_debut": "YYYY-MM-DD",
    "date_anniversaire": "YYYY-MM-DD",
    "estimation_conso_annuelle_kwh": 5000,
    "estimation_facture_annuelle": 1234.56,
    "conditions_resiliation": "texte des conditions"
}

IMPORTANT: 
- Extrais TOUTES les informations disponibles
- Mets null pour les champs non trouvés
- Vérifie bien les prix et la puissance
- Le PDL fait 14 chiffres

Contrat à analyser:

"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse de contrats d'énergie. Tu extrais les données de manière précise et structurée."},
                {"role": "user", "content": prompt + text_content}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        print("\nRéponse de ChatGPT:")
        print("="*80)
        print(result)
        print("="*80)
        
        # Essayer de parser le JSON
        try:
            # Nettoyer la réponse si elle contient du markdown
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            data = json.loads(result)
            print("\n✅ JSON valide extrait avec succès!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
            
        except json.JSONDecodeError as e:
            print(f"\n⚠️ Erreur de parsing JSON: {e}")
            print("Réponse brute:", result)
            return None
            
    except Exception as e:
        print(f"\n❌ Erreur lors de l'appel à ChatGPT: {e}")
        return None

if __name__ == "__main__":
    pdf_path = "Contrats/TotalEnergies.pdf"
    data = extract_pdf_with_chatgpt(pdf_path)
    
    if data:
        # Sauvegarder dans un fichier JSON
        output_file = "totalenergies_extracted.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Données sauvegardées dans {output_file}")

"""Service OpenAI amélioré pour extraction avec fichiers PDF."""
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from pathlib import Path

from src.config import OPENAI_API_KEY, OPENAI_MODEL


class OpenAIService:
    """Service pour interagir avec l'API OpenAI avec support fichiers."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le service OpenAI.

        Args:
            api_key: Clé API OpenAI (utilise la config par défaut si None)
        """
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("Clé API OpenAI non configurée")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = OPENAI_MODEL

    def extract_contract_data_from_file(self, pdf_bytes: bytes, contract_type: str, filename: str = "contrat.pdf") -> Dict[str, Any]:
        """
        Extrait les données structurées d'un contrat directement depuis le fichier PDF.
        Utilise l'API File Upload de OpenAI pour une meilleure analyse.

        Args:
            pdf_bytes: Contenu binaire du PDF
            contract_type: Type de contrat (telephone, assurance_pno, electricite, gaz)
            filename: Nom du fichier

        Returns:
            Dictionnaire contenant les données extraites

        Raises:
            Exception: Si l'extraction échoue
        """
        try:
            # Upload du fichier vers OpenAI
            file_response = self.client.files.create(
                file=(filename, pdf_bytes),
                purpose='assistants'
            )
            
            file_id = file_response.id
            
            # Créer le schéma JSON attendu selon le type de contrat
            schema = self._get_contract_schema(contract_type)
            
            # Construire l'instruction d'analyse
            instruction = f"""Analyse ce contrat de type '{contract_type}' et renvoie un JSON normalisé.

IMPORTANT : Respecte EXACTEMENT ce schéma JSON :
{json.dumps(schema, indent=2, ensure_ascii=False)}

Instructions :
1. Extrais TOUTES les informations disponibles dans le document
2. Pour les champs non trouvés, mets null (pas de string vide)
3. Respecte les types de données (nombres, strings, dates au format DD/MM/YYYY)
4. Pour les montants, utilise des nombres décimaux (pas de string)
5. Sois précis et exhaustif

Retourne UNIQUEMENT le JSON, sans texte supplémentaire."""

            # Interroger ChatGPT avec le fichier
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en analyse de contrats. Tu extrais les données de manière précise et structurée en JSON."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": instruction},
                            {
                                "type": "file",
                                "file_id": file_id
                            }
                        ]
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            
            # Nettoyer et parser le JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            extracted_data = json.loads(result)
            
            # Nettoyer le fichier temporaire
            try:
                self.client.files.delete(file_id)
            except:
                pass  # Ignore les erreurs de suppression
            
            return {
                "data": extracted_data,
                "file_id": file_id,
                "raw_response": result
            }
        
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction des données: {str(e)}")

    def extract_contract_data(self, pdf_text: str, contract_type: str) -> Dict[str, Any]:
        """
        Extrait les données structurées d'un contrat à partir du texte PDF.
        Version fallback utilisant le texte brut.

        Args:
            pdf_text: Texte extrait du PDF
            contract_type: Type de contrat

        Returns:
            Dictionnaire contenant les données extraites
        """
        schema = self._get_contract_schema(contract_type)
        prompt = self._build_extraction_prompt(contract_type, pdf_text, schema)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un assistant expert en analyse de contrats. "
                        "Tu dois extraire les informations clés d'un contrat et les retourner "
                        "au format JSON structuré. Sois précis et exhaustif."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            
            # Nettoyer le JSON si nécessaire
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            extracted_data = json.loads(result)
            
            return {
                "data": extracted_data,
                "prompt": prompt,
                "raw_response": result
            }
        
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction des données: {str(e)}")

    def _get_contract_schema(self, contract_type: str) -> Dict[str, Any]:
        """Retourne le schéma JSON générique selon le type de contrat."""
        
        # Schéma de base commun à tous les contrats
        base_schema = {
            "type_contrat": contract_type,
            "fournisseur": "",
            "numero_contrat": "",
            "client": {
                "noms": [],
                "email": "",
                "telephone": "",
                "date_naissance": "",
                "reference_client": ""
            },
            "dates": {
                "signature_contrat": "",
                "date_debut": "",
                "date_anniversaire": "",
                "retractation_limite": ""
            },
            "paiements": {
                "mode": "",
                "date_prelevement": ""
            },
            "service_client": {
                "tel_souscription": "",
                "tel_service_client": "",
                "contact_courrier": ""
            }
        }
        
        if contract_type == "electricite":
            base_schema.update({
                "adresses": {
                    "site_de_consommation": "",
                    "adresse_facturation": ""
                },
                "electricite": {
                    "pdl": "",
                    "puissance_souscrite_kva": None,
                    "option_tarifaire": "",
                    "matricule_compteur": "",
                    "date_debut_previsionnelle": "",
                    "tarifs": {
                        "abonnement_mensuel_ttc": None,
                        "prix_kwh_ht": None,
                        "prix_kwh_ttc": None
                    },
                    "promotion": {
                        "remise_kwh_ht_percent": None,
                        "duree_mois": None
                    },
                    "consommation_estimee_annuelle_kwh": None,
                    "budget_annuel_estime_ttc": None
                },
                "paiements": {
                    "mensualite_electricite_ttc": None,
                    "mode": "",
                    "date_prelevement": ""
                }
            })
        
        elif contract_type == "gaz":
            base_schema.update({
                "adresses": {
                    "site_de_consommation": "",
                    "adresse_facturation": ""
                },
                "gaz": {
                    "pce": "",
                    "option_tarifaire": "",
                    "zone_tarifaire": None,
                    "matricule_compteur": "",
                    "date_debut_previsionnelle": "",
                    "tarifs": {
                        "abonnement_mensuel_ttc": None,
                        "prix_kwh_ht": None,
                        "prix_kwh_ttc": None
                    },
                    "promotion": {
                        "remise_kwh_ht_percent": None,
                        "duree_mois": None
                    },
                    "consommation_estimee_annuelle_kwh": None,
                    "budget_annuel_estime_ttc": None
                },
                "paiements": {
                    "mensualite_gaz_ttc": None,
                    "mode": "",
                    "date_prelevement": ""
                }
            })
        
        elif contract_type == "telephone":
            base_schema.update({
                "telephone": {
                    "operateur": "",
                    "numero": "",
                    "forfait": "",
                    "data_go": None,
                    "appels_illimites": False,
                    "sms_illimites": False,
                    "prix_mensuel": None,
                    "engagement_mois": None,
                    "options": []
                }
            })
        
        elif contract_type == "assurance_pno":
            base_schema.update({
                "assurance": {
                    "assureur": "",
                    "numero_police": "",
                    "type_bien": "",
                    "adresse_bien": "",
                    "surface_m2": None,
                    "garanties": [],
                    "franchise": None,
                    "capital_mobilier": None,
                    "prime_annuelle": None,
                    "prime_mensuelle": None
                }
            })
        
        return base_schema

    def _build_extraction_prompt(self, contract_type: str, pdf_text: str, schema: Dict[str, Any]) -> str:
        """Construit le prompt d'extraction avec le schéma."""
        
        return f"""Analyse ce contrat de type '{contract_type}' et extrais toutes les informations pertinentes.

SCHÉMA JSON ATTENDU :
{json.dumps(schema, indent=2, ensure_ascii=False)}

RÈGLES :
1. Extrais TOUTES les informations du document
2. Pour les champs non trouvés, mets null
3. Dates au format DD/MM/YYYY
4. Montants en nombres décimaux
5. Réponds UNIQUEMENT avec du JSON valide

CONTENU DU CONTRAT :
{pdf_text}

JSON de réponse :"""

    def compare_with_market(self, contract_data: Dict[str, Any], contract_type: str) -> Dict[str, Any]:
        """Compare un contrat avec les offres actuelles du marché."""
        
        prompt = self._build_market_comparison_prompt(contract_type, contract_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en comparaison de contrats et d'offres du marché. "
                        "Tu analyses les offres disponibles et fournis des recommandations précises."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            comparison_data = json.loads(result)
            
            return {
                "data": comparison_data,
                "prompt": prompt,
                "raw_response": result
            }
        
        except Exception as e:
            raise Exception(f"Erreur lors de la comparaison: {str(e)}")

    def _build_market_comparison_prompt(self, contract_type: str, contract_data: Dict[str, Any]) -> str:
        """Construit le prompt de comparaison de marché."""
        
        if contract_type == "electricite":
            return f"""Compare ce contrat d'électricité avec le marché actuel (décembre 2025).

CONTRAT ACTUEL :
{json.dumps(contract_data, indent=2, ensure_ascii=False)}

Analyse et retourne un JSON avec :
{{
  "cout_annuel_actuel": <nombre>,
  "estimation_marche": {{
    "prix_min_kwh": <nombre>,
    "prix_moyen_kwh": <nombre>,
    "prix_max_kwh": <nombre>
  }},
  "offres_similaires": [
    {{
      "fournisseur": "",
      "nom_offre": "",
      "prix_kwh_ttc": <nombre>,
      "abonnement_mensuel": <nombre>,
      "cout_annuel_estime": <nombre>,
      "economie_potentielle": <nombre>,
      "avantages": [],
      "inconvenients": []
    }}
  ],
  "recommandation": {{
    "changer": <boolean>,
    "meilleure_offre": "",
    "economies_annuelles": <nombre>,
    "raison": ""
  }}
}}"""
        
        elif contract_type == "gaz":
            return f"""Compare ce contrat de gaz avec le marché actuel (décembre 2025).

CONTRAT ACTUEL :
{json.dumps(contract_data, indent=2, ensure_ascii=False)}

Analyse et retourne un JSON avec le même format que pour l'électricité."""
        
        elif contract_type == "telephone":
            return f"""Compare ce forfait téléphone avec le marché actuel (décembre 2025).

CONTRAT ACTUEL :
{json.dumps(contract_data, indent=2, ensure_ascii=False)}

Analyse et retourne un JSON structuré avec offres similaires et recommandations."""
        
        elif contract_type == "assurance_pno":
            return f"""Compare cette assurance PNO avec le marché actuel (décembre 2025).

CONTRAT ACTUEL :
{json.dumps(contract_data, indent=2, ensure_ascii=False)}

Analyse et retourne un JSON structuré avec offres similaires et recommandations."""
        
        return f"Compare ce contrat : {json.dumps(contract_data, indent=2, ensure_ascii=False)}"

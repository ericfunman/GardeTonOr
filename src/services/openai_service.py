"""Service OpenAI pour extraction et comparaison de contrats."""
import json
from typing import Dict, Any, Optional
from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL


class OpenAIService:
    """Service pour interagir avec l'API OpenAI."""

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

    def extract_contract_data(self, pdf_text: str, contract_type: str) -> Dict[str, Any]:
        """
        Extrait les données structurées d'un contrat à partir du texte PDF.

        Args:
            pdf_text: Texte extrait du PDF
            contract_type: Type de contrat (telephone, assurance_pno)

        Returns:
            Dictionnaire contenant les données extraites

        Raises:
            Exception: Si l'extraction échoue
        """
        prompt = self._build_extraction_prompt(contract_type, pdf_text)
        
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
                temperature=0.1,  # Basse température pour plus de précision
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            extracted_data = json.loads(result)
            
            return {
                "data": extracted_data,
                "prompt": prompt,
                "raw_response": result
            }
        
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction des données: {str(e)}")

    def compare_with_market(self, contract_data: Dict[str, Any], contract_type: str) -> Dict[str, Any]:
        """
        Compare un contrat avec les offres actuelles du marché.

        Args:
            contract_data: Données du contrat à comparer
            contract_type: Type de contrat

        Returns:
            Dictionnaire contenant l'analyse de comparaison

        Raises:
            Exception: Si la comparaison échoue
        """
        prompt = self._build_market_comparison_prompt(contract_type, contract_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en comparaison de contrats et d'offres commerciales. "
                        "Tu connais le marché français et ses tarifs actuels. "
                        "Fournis une analyse objective et des recommandations concrètes au format JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            comparison_result = json.loads(result)
            
            return {
                "analysis": comparison_result,
                "prompt": prompt,
                "raw_response": result
            }
        
        except Exception as e:
            raise Exception(f"Erreur lors de la comparaison de marché: {str(e)}")

    def compare_with_competitor(
        self,
        current_contract: Dict[str, Any],
        competitor_data: Dict[str, Any],
        contract_type: str
    ) -> Dict[str, Any]:
        """
        Compare un contrat actuel avec une offre concurrente.

        Args:
            current_contract: Données du contrat actuel
            competitor_data: Données du devis concurrent
            contract_type: Type de contrat

        Returns:
            Dictionnaire contenant l'analyse comparative

        Raises:
            Exception: Si la comparaison échoue
        """
        prompt = self._build_competitor_comparison_prompt(
            contract_type,
            current_contract,
            competitor_data
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en comparaison de contrats. "
                        "Analyse objectivement les deux offres et fournis une recommandation "
                        "claire au format JSON avec les avantages et inconvénients de chaque offre."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            comparison_result = json.loads(result)
            
            return {
                "analysis": comparison_result,
                "prompt": prompt,
                "raw_response": result
            }
        
        except Exception as e:
            raise Exception(f"Erreur lors de la comparaison avec concurrent: {str(e)}")

    def _build_extraction_prompt(self, contract_type: str, pdf_text: str) -> str:
        """Construit le prompt pour l'extraction de données."""
        
        if contract_type == "telephone":
            return f"""Analyse ce contrat de téléphonie mobile et extrais les informations suivantes au format JSON:

{{
    "fournisseur": "nom du fournisseur",
    "forfait_nom": "nom du forfait",
    "data_go": nombre de Go de data (nombre),
    "minutes": "nombre de minutes ou 'illimité'",
    "sms": "nombre de SMS ou 'illimité'",
    "prix_mensuel": prix mensuel en euros (nombre),
    "engagement_mois": durée d'engagement en mois (nombre, 0 si sans engagement),
    "date_debut": "date de début au format YYYY-MM-DD",
    "date_fin": "date de fin au format YYYY-MM-DD si applicable",
    "date_anniversaire": "date anniversaire au format YYYY-MM-DD",
    "options": ["liste des options incluses"],
    "conditions_particulieres": "conditions particulières importantes",
    "resiliation": "conditions de résiliation"
}}

Texte du contrat:
{pdf_text}

Réponds uniquement avec le JSON, sans texte additionnel."""

        elif contract_type == "assurance_pno":
            return f"""Analyse ce contrat d'assurance Propriétaire Non Occupant (PNO) et extrais les informations suivantes au format JSON:

{{
    "assureur": "nom de l'assureur",
    "numero_contrat": "numéro de contrat",
    "bien_assure": {{
        "adresse": "adresse complète du bien",
        "type": "type de bien (appartement, maison, etc.)",
        "surface_m2": surface en m² (nombre),
        "nombre_pieces": nombre de pièces (nombre)
    }},
    "garanties": {{
        "incendie": montant garanti (nombre),
        "degats_des_eaux": montant garanti (nombre),
        "vol": montant garanti (nombre),
        "responsabilite_civile": montant garanti (nombre),
        "autres": ["liste des autres garanties"]
    }},
    "franchise": montant de la franchise en euros (nombre),
    "prime_annuelle": prime annuelle en euros (nombre),
    "prime_mensuelle": prime mensuelle en euros (nombre) si applicable,
    "date_effet": "date d'effet au format YYYY-MM-DD",
    "date_echeance": "date d'échéance au format YYYY-MM-DD",
    "date_anniversaire": "date anniversaire au format YYYY-MM-DD",
    "mode_paiement": "mode de paiement (mensuel, annuel, etc.)",
    "conditions_particulieres": "conditions particulières importantes",
    "resiliation": "conditions et délais de résiliation"
}}

Texte du contrat:
{pdf_text}

Réponds uniquement avec le JSON, sans texte additionnel."""

        else:
            raise ValueError(f"Type de contrat non supporté: {contract_type}")

    def _build_market_comparison_prompt(
        self,
        contract_type: str,
        contract_data: Dict[str, Any]
    ) -> str:
        """Construit le prompt pour la comparaison de marché."""
        
        contract_json = json.dumps(contract_data, indent=2, ensure_ascii=False)
        
        if contract_type == "telephone":
            return f"""Analyse ce contrat de téléphonie mobile et compare-le avec les offres actuelles du marché français en décembre 2025.

Contrat actuel:
{contract_json}

Fournis une analyse au format JSON avec:
{{
    "tarif_actuel": prix mensuel actuel (nombre),
    "estimation_marche": {{
        "tarif_min": tarif minimum trouvable sur le marché pour des conditions similaires (nombre),
        "tarif_moyen": tarif moyen du marché (nombre),
        "tarif_max": tarif maximum (nombre)
    }},
    "economie_potentielle_mensuelle": économie mensuelle possible en euros (nombre, peut être négative),
    "economie_potentielle_annuelle": économie annuelle possible en euros (nombre),
    "offres_similaires": [
        {{
            "fournisseur": "nom",
            "forfait": "nom du forfait",
            "prix_mensuel": prix (nombre),
            "avantages": ["liste des avantages"],
            "inconvenients": ["liste des inconvénients"]
        }}
    ],
    "recommandation": "recommendation claire (garder/changer)",
    "justification": "explication détaillée de la recommandation",
    "niveau_competitivite": "excellent/bon/moyen/faible"
}}

Base-toi sur les offres réelles des opérateurs français (Orange, SFR, Bouygues, Free, Sosh, Red, B&You, etc.)."""

        elif contract_type == "assurance_pno":
            return f"""Analyse ce contrat d'assurance PNO et compare-le avec les offres actuelles du marché français en décembre 2025.

Contrat actuel:
{contract_json}

Fournis une analyse au format JSON avec:
{{
    "prime_actuelle_annuelle": prime annuelle actuelle (nombre),
    "estimation_marche": {{
        "prime_min": prime minimum trouvable pour des conditions similaires (nombre),
        "prime_moyenne": prime moyenne du marché (nombre),
        "prime_max": prime maximum (nombre)
    }},
    "economie_potentielle_annuelle": économie annuelle possible en euros (nombre, peut être négative),
    "ratio_qualite_prix": évaluation du rapport qualité/prix (nombre entre 0 et 10),
    "offres_similaires": [
        {{
            "assureur": "nom",
            "prime_annuelle": prix (nombre),
            "franchise": montant franchise (nombre),
            "garanties_principales": ["liste des garanties"],
            "avantages": ["liste des avantages"],
            "inconvenients": ["liste des inconvénients"]
        }}
    ],
    "points_attention": ["points importants à vérifier"],
    "recommandation": "recommendation claire (garder/changer)",
    "justification": "explication détaillée",
    "niveau_competitivite": "excellent/bon/moyen/faible"
}}

Base-toi sur les offres réelles des assureurs français (Allianz, AXA, Generali, MAIF, MACIF, Groupama, etc.)."""

        else:
            raise ValueError(f"Type de contrat non supporté: {contract_type}")

    def _build_competitor_comparison_prompt(
        self,
        contract_type: str,
        current_contract: Dict[str, Any],
        competitor_data: Dict[str, Any]
    ) -> str:
        """Construit le prompt pour la comparaison avec un concurrent."""
        
        current_json = json.dumps(current_contract, indent=2, ensure_ascii=False)
        competitor_json = json.dumps(competitor_data, indent=2, ensure_ascii=False)
        
        return f"""Compare ces deux contrats de type {contract_type} et fournis une analyse détaillée.

CONTRAT ACTUEL:
{current_json}

OFFRE CONCURRENTE:
{competitor_json}

Fournis une analyse comparative au format JSON avec:
{{
    "comparaison_prix": {{
        "prix_actuel": prix actuel (nombre),
        "prix_concurrent": prix concurrent (nombre),
        "difference_mensuelle": différence mensuelle en euros (nombre, positif = concurrent plus cher),
        "difference_annuelle": différence annuelle en euros (nombre),
        "economie_potentielle": économie si changement (nombre)
    }},
    "comparaison_services": {{
        "avantages_contrat_actuel": ["liste des avantages de l'offre actuelle"],
        "avantages_concurrent": ["liste des avantages de l'offre concurrente"],
        "services_identiques": ["liste des services identiques"],
        "differences_majeures": ["liste des différences importantes"]
    }},
    "analyse_qualitative": {{
        "qualite_actuelle": note sur 10 (nombre),
        "qualite_concurrent": note sur 10 (nombre),
        "rapport_qualite_prix_actuel": note sur 10 (nombre),
        "rapport_qualite_prix_concurrent": note sur 10 (nombre)
    }},
    "points_vigilance": ["points importants à considérer avant de changer"],
    "recommandation": "recommendation claire (garder contrat actuel/changer pour concurrent)",
    "justification": "explication détaillée et argumentée de la recommandation",
    "score_global": {{
        "contrat_actuel": note globale sur 10 (nombre),
        "offre_concurrente": note globale sur 10 (nombre)
    }}
}}

Sois objectif et prends en compte tous les aspects (prix, qualité, services, conditions)."""

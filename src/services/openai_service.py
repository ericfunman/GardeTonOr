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
        Utilise un schéma JSON générique normalisé.

        Args:
            pdf_text: Texte extrait du PDF
            contract_type: Type de contrat (telephone, assurance_pno, electricite, gaz)

        Returns:
            Dictionnaire contenant les données extraites

        Raises:
            Exception: Si l'extraction échoue
        """
        # Obtenir le schéma générique
        schema = self._get_contract_schema(contract_type)
        prompt = self._build_extraction_prompt(contract_type, pdf_text, schema)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en analyse de contrats. "
                        "Tu extrais les données de manière précise et structurée en JSON. "
                        "Respecte EXACTEMENT le schéma fourni."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Basse température pour plus de précision
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
                "raw_response": result,
                "schema": schema
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

    def _get_contract_schema(self, contract_type: str) -> Dict[str, Any]:
        """Retourne le schéma JSON générique normalisé selon le type de contrat."""
        
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
        
        return base_schema

    def _build_extraction_prompt(self, contract_type: str, pdf_text: str, schema: Dict[str, Any] = None) -> str:
        """Construit le prompt pour l'extraction de données avec schéma générique."""
        
        if schema is None:
            schema = self._get_contract_schema(contract_type)
        
        base_instructions = f"""Analyse ce contrat de type '{contract_type}' et extrais TOUTES les informations disponibles.

SCHÉMA JSON ATTENDU (respecte-le EXACTEMENT) :
{json.dumps(schema, indent=2, ensure_ascii=False)}

RÈGLES IMPORTANTES :
1. Extrais TOUTES les informations trouvées dans le document
2. Pour les champs non trouvés, mets null (pas de string vide)
3. Respecte les types de données (nombres pour les montants, pas de string)
4. Dates au format DD/MM/YYYY
5. Pour les listes (noms, garanties, etc.), utilise des arrays
6. Sois précis sur les montants (avec décimales)
7. Réponds UNIQUEMENT avec du JSON valide, sans texte avant ou après

CONTENU DU CONTRAT :
{pdf_text}

JSON de réponse :"""
        
        return base_instructions

    def _build_extraction_prompt_legacy(self, contract_type: str, pdf_text: str) -> str:
        """Version legacy du prompt (pour compatibilité)."""
        
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

        elif contract_type == "electricite":
            return f"""Analyse ce contrat d'électricité et extrais les informations suivantes au format JSON:

{{
    "fournisseur": "nom du fournisseur",
    "numero_contrat": "numéro de contrat ou référence client",
    "type_offre": "nom de l'offre (ex: Offre Online, Tarif Bleu, etc.)",
    "puissance_souscrite_kva": puissance souscrite en kVA (nombre),
    "option_tarifaire": "option tarifaire (Base, Heures Pleines/Heures Creuses, Tempo, etc.)",
    "prix_abonnement_mensuel": prix de l'abonnement mensuel en euros (nombre),
    "prix_kwh": {{
        "base": prix du kWh en base en euros (nombre) si applicable,
        "heures_pleines": prix du kWh heures pleines en euros (nombre) si applicable,
        "heures_creuses": prix du kWh heures creuses en euros (nombre) si applicable
    }},
    "adresse_fourniture": "adresse du point de livraison",
    "pdl": "numéro de Point De Livraison (14 chiffres)",
    "date_debut": "date de début du contrat au format YYYY-MM-DD",
    "date_fin": "date de fin si contrat à durée déterminée au format YYYY-MM-DD",
    "date_anniversaire": "date anniversaire au format YYYY-MM-DD",
    "duree_engagement": "durée d'engagement en mois (0 si sans engagement)",
    "mode_paiement": "mode de paiement (prélèvement, virement, etc.)",
    "estimation_conso_annuelle_kwh": estimation de consommation annuelle en kWh (nombre),
    "estimation_facture_annuelle": estimation de la facture annuelle en euros (nombre),
    "options": ["liste des options incluses"],
    "conditions_resiliation": "conditions de résiliation"
}}

Texte du contrat:
{pdf_text}

Réponds uniquement avec le JSON, sans texte additionnel."""

        elif contract_type == "gaz":
            return f"""Analyse ce contrat de gaz naturel et extrais les informations suivantes au format JSON:

{{
    "fournisseur": "nom du fournisseur",
    "numero_contrat": "numéro de contrat ou référence client",
    "type_offre": "nom de l'offre",
    "classe_consommation": "classe de consommation (Base, B0, B1, B2i, etc.)",
    "prix_abonnement_mensuel": prix de l'abonnement mensuel en euros (nombre),
    "prix_kwh": prix du kWh de gaz en euros (nombre),
    "adresse_fourniture": "adresse du point de livraison",
    "pce": "numéro de Point de Comptage et d'Estimation (14 chiffres)",
    "date_debut": "date de début du contrat au format YYYY-MM-DD",
    "date_fin": "date de fin si contrat à durée déterminée au format YYYY-MM-DD",
    "date_anniversaire": "date anniversaire au format YYYY-MM-DD",
    "duree_engagement": "durée d'engagement en mois (0 si sans engagement)",
    "mode_paiement": "mode de paiement (prélèvement, virement, etc.)",
    "estimation_conso_annuelle_kwh": estimation de consommation annuelle en kWh (nombre),
    "estimation_facture_annuelle": estimation de la facture annuelle en euros (nombre),
    "options": ["liste des options incluses"],
    "conditions_resiliation": "conditions de résiliation"
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
        schema = self._get_contract_schema(contract_type)
        schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
        
        if contract_type == "telephone":
            return f"""Analyse ce contrat de téléphonie mobile et compare-le avec les offres actuelles du marché français en décembre 2025.

Contrat actuel:
{contract_json}

SCHÉMA DE DONNÉES POUR L'OFFRE (à respecter pour 'meilleure_offre'):
{schema_json}

Fournis une analyse au format JSON avec:
{{
    "analyse": {{
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
    }},
    "meilleure_offre": (Remplis ce champ avec les données de la meilleure offre trouvée sur le marché, en respectant EXACTEMENT le schéma fourni ci-dessus. Remplis le maximum de champs possibles avec les données de l'offre, mets null si inconnu.)
}}

Base-toi sur les offres réelles des opérateurs français (Orange, SFR, Bouygues, Free, Sosh, Red, B&You, etc.)."""

        elif contract_type == "assurance_pno":
            return f"""Analyse ce contrat d'assurance PNO et compare-le avec les offres actuelles du marché français en décembre 2025.

Contrat actuel:
{contract_json}

SCHÉMA DE DONNÉES POUR L'OFFRE (à respecter pour 'meilleure_offre'):
{schema_json}

Fournis une analyse au format JSON avec:
{{
    "analyse": {{
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
    }},
    "meilleure_offre": (Remplis ce champ avec les données de la meilleure offre trouvée sur le marché, en respectant EXACTEMENT le schéma fourni ci-dessus. Remplis le maximum de champs possibles avec les données de l'offre, mets null si inconnu.)
}}

Base-toi sur les offres réelles des assureurs français (Allianz, AXA, Generali, MAIF, MACIF, Groupama, etc.)."""

        elif contract_type == "electricite":
            return f"""Analyse ce contrat d'électricité et compare-le avec les offres actuelles du marché français en décembre 2025.

Contrat actuel:
{contract_json}

SCHÉMA DE DONNÉES POUR L'OFFRE (à respecter pour 'meilleure_offre'):
{schema_json}

Fournis une analyse au format JSON avec:
{{
    "analyse": {{
        "cout_annuel_actuel": coût annuel estimé actuel (nombre),
        "estimation_marche": {{
            "cout_min": coût annuel minimum trouvable pour une consommation similaire (nombre),
            "cout_moyen": coût annuel moyen du marché (nombre),
            "cout_max": coût annuel maximum (nombre)
        }},
        "economie_potentielle_annuelle": économie annuelle possible en euros (nombre, peut être négative),
        "prix_kwh_marche": {{
            "min": prix du kWh minimum sur le marché (nombre),
            "moyen": prix du kWh moyen (nombre),
            "max": prix du kWh maximum (nombre)
        }},
        "offres_similaires": [
            {{
                "fournisseur": "nom",
                "offre": "nom de l'offre",
                "abonnement_mensuel": prix abonnement (nombre),
                "prix_kwh": prix du kWh (nombre),
                "cout_annuel_estime": coût annuel estimé (nombre),
                "avantages": ["liste des avantages"],
                "inconvenients": ["liste des inconvénients"]
            }}
        ],
        "points_attention": ["points importants à vérifier"],
        "recommandation": "recommendation claire (garder/changer)",
        "justification": "explication détaillée",
        "niveau_competitivite": "excellent/bon/moyen/faible"
    }},
    "meilleure_offre": (Remplis ce champ avec les données de la meilleure offre trouvée sur le marché, en respectant EXACTEMENT le schéma fourni ci-dessus. Remplis le maximum de champs possibles avec les données de l'offre, mets null si inconnu.)
}}

Base-toi sur les offres réelles des fournisseurs français (EDF, Engie, TotalEnergies, Ekwateur, OHM Énergie, etc.)."""

        elif contract_type == "gaz":
            return f"""Analyse ce contrat de gaz naturel et compare-le avec les offres actuelles du marché français en décembre 2025.

Contrat actuel:
{contract_json}

SCHÉMA DE DONNÉES POUR L'OFFRE (à respecter pour 'meilleure_offre'):
{schema_json}

Fournis une analyse au format JSON avec:
{{
    "analyse": {{
        "cout_annuel_actuel": coût annuel estimé actuel (nombre),
        "estimation_marche": {{
            "cout_min": coût annuel minimum trouvable pour une consommation similaire (nombre),
            "cout_moyen": coût annuel moyen du marché (nombre),
            "cout_max": coût annuel maximum (nombre)
        }},
        "economie_potentielle_annuelle": économie annuelle possible en euros (nombre, peut être négative),
        "prix_kwh_marche": {{
            "min": prix du kWh minimum sur le marché (nombre),
            "moyen": prix du kWh moyen (nombre),
            "max": prix du kWh maximum (nombre)
        }},
        "offres_similaires": [
            {{
                "fournisseur": "nom",
                "offre": "nom de l'offre",
                "abonnement_mensuel": prix abonnement (nombre),
                "prix_kwh": prix du kWh (nombre),
                "cout_annuel_estime": coût annuel estimé (nombre),
                "avantages": ["liste des avantages"],
                "inconvenients": ["liste des inconvénients"]
            }}
        ],
        "points_attention": ["points importants à vérifier"],
        "recommandation": "recommendation claire (garder/changer)",
        "justification": "explication détaillée",
        "niveau_competitivite": "excellent/bon/moyen/faible"
    }},
    "meilleure_offre": (Remplis ce champ avec les données de la meilleure offre trouvée sur le marché, en respectant EXACTEMENT le schéma fourni ci-dessus. Remplis le maximum de champs possibles avec les données de l'offre, mets null si inconnu.)
}}

Base-toi sur les offres réelles des fournisseurs français (Engie, TotalEnergies, EDF, Eni, Ekwateur, etc.)."""

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

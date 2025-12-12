import requests
import argparse
import os
import sys
import json

# Configuration
SONAR_HOST = "https://sonarcloud.io"
PROJECT_KEY = "ericfunman_GardeTonOr"
ORGANIZATION = "ericfunman"

def get_quality_gate_status(token):
    """Récupère le statut du Quality Gate."""
    url = f"{SONAR_HOST}/api/qualitygates/project_status"
    params = {"projectKey": PROJECT_KEY}
    auth = (token, "")  # Basic Auth avec le token comme username
    
    try:
        response = requests.get(url, params=params, auth=auth)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération du Quality Gate : {e}")
        if response.status_code == 401:
            print("⚠️ Non autorisé. Vérifiez votre token SonarCloud.")
        return None

def get_measures(token):
    """Récupère les métriques principales."""
    url = f"{SONAR_HOST}/api/measures/component"
    metric_keys = [
        "bugs",
        "vulnerabilities",
        "security_hotspots",
        "code_smells",
        "coverage",
        "duplicated_lines_density",
        "ncloc" # Lines of code
    ]
    params = {
        "component": PROJECT_KEY,
        "metricKeys": ",".join(metric_keys)
    }
    auth = (token, "")
    
    try:
        response = requests.get(url, params=params, auth=auth)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération des mesures : {e}")
        return None

def get_issues(token):
    """Récupère les problèmes (issues) du projet."""
    url = f"{SONAR_HOST}/api/issues/search"
    params = {
        "componentKeys": PROJECT_KEY,
        "resolved": "false",
        "ps": 50,  # Page size
        "types": "CODE_SMELL,BUG,VULNERABILITY"
    }
    auth = (token, "")
    
    try:
        response = requests.get(url, params=params, auth=auth)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération des issues : {e}")
        return None

def print_status(qg_data, measures_data, issues_data=None):
    """Affiche les résultats formatés."""
    print("\n🔍 --- Rapport SonarCloud ---")
    print(f"Projet : {PROJECT_KEY}")
    print(f"URL : {SONAR_HOST}/dashboard?id={PROJECT_KEY}")
    print("-" * 30)

    # Quality Gate
    if qg_data:
        status = qg_data.get("projectStatus", {}).get("status", "UNKNOWN")
        icon = "✅" if status == "OK" else "❌"
        print(f"Statut Quality Gate : {icon} {status}")
        
        # Conditions échouées
        conditions = qg_data.get("projectStatus", {}).get("conditions", [])
        failed_conditions = [c for c in conditions if c["status"] != "OK"]
        if failed_conditions:
            print("\n⚠️ Conditions non respectées :")
            for c in failed_conditions:
                print(f"  - {c['metricKey']} : {c['actualValue']} (Seuil : {c['errorThreshold']})")

    print("-" * 30)

    # Mesures
    if measures_data:
        measures = {m["metric"]: m["value"] for m in measures_data.get("component", {}).get("measures", [])}
        
        print("📊 Métriques :")
        print(f"  🐞 Bugs : {measures.get('bugs', 'N/A')}")
        print(f"  🔓 Vulnérabilités : {measures.get('vulnerabilities', 'N/A')}")
        print(f"  🔥 Security Hotspots : {measures.get('security_hotspots', 'N/A')}")
        print(f"  💩 Code Smells : {measures.get('code_smells', 'N/A')}")
        print(f"  📉 Couverture : {measures.get('coverage', 'N/A')}%")
        print(f"  👯 Duplications : {measures.get('duplicated_lines_density', 'N/A')}%")
        print(f"  📝 Lignes de code : {measures.get('ncloc', 'N/A')}")

    # Issues
    if issues_data and issues_data.get("issues"):
        print("-" * 30)
        print(f"📋 Liste des problèmes ({len(issues_data['issues'])} affichés) :")
        for issue in issues_data["issues"]:
            severity = issue.get("severity", "INFO")
            message = issue.get("message", "")
            component = issue.get("component", "").replace(f"{PROJECT_KEY}:", "")
            line = issue.get("line", "?")
            print(f"  [{severity}] {component}:{line} - {message}")

def main():
    parser = argparse.ArgumentParser(description="Vérifier le statut SonarCloud du projet.")
    parser.add_argument("--token", help="Token SonarCloud (ou via variable d'env SONAR_TOKEN)")
    args = parser.parse_args()

    token = args.token or os.environ.get("SONAR_TOKEN")
    
    if not token:
        print("❌ Erreur : Token SonarCloud manquant.")
        print("Utilisation : python check_sonar.py --token VOTRE_TOKEN")
        print("Ou définissez la variable d'environnement SONAR_TOKEN")
        sys.exit(1)

    print("Connexion à SonarCloud...")
    qg_status = get_quality_gate_status(token)
    measures = get_measures(token)
    issues = get_issues(token)
    
    print_status(qg_status, measures, issues)

if __name__ == "__main__":
    main()

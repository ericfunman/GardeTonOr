"""
Script pour tester la récupération du solde OpenAI API
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("=" * 80)
print("TEST RÉCUPÉRATION SOLDE OPENAI API")
print("=" * 80)
print(f"\nClé API: {OPENAI_API_KEY[:20]}...{OPENAI_API_KEY[-10:]}")
print(f"Longueur: {len(OPENAI_API_KEY)} caractères\n")

# Test 1: Credit Grants (endpoint non documenté mais fonctionnel)
print("\n" + "=" * 80)
print("TEST 1: /dashboard/billing/credit_grants")
print("=" * 80)
try:
    response = requests.get(
        "https://api.openai.com/dashboard/billing/credit_grants",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        timeout=10,
    )

    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"\nRéponse brute:")
    print(response.text)

    if response.status_code == 200:
        data = response.json()
        print(f"\nJSON parsé:")
        print(json.dumps(data, indent=2))

        if "total_available" in data:
            print(f"\n✅ Crédit disponible: {data['total_available']} $")
            print(f"✅ Crédit utilisé: {data.get('total_used', 'N/A')} $")
            print(f"✅ Crédit total: {data.get('total_granted', 'N/A')} $")
    else:
        print(f"\n❌ Erreur HTTP {response.status_code}")
        print(f"Message: {response.text}")

except Exception as e:
    print(f"\n❌ Exception: {type(e).__name__}")
    print(f"Message: {str(e)}")

# Test 2: Usage endpoint
print("\n\n" + "=" * 80)
print("TEST 2: /v1/usage")
print("=" * 80)
try:
    response = requests.get(
        "https://api.openai.com/v1/usage",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        timeout=10,
    )

    print(f"Status Code: {response.status_code}")
    print(f"\nRéponse brute:")
    print(response.text[:500])

    if response.status_code == 200:
        data = response.json()
        print(f"\nJSON parsé (premiers éléments):")
        print(json.dumps(data, indent=2)[:500])
    else:
        print(f"\n❌ Erreur HTTP {response.status_code}")

except Exception as e:
    print(f"\n❌ Exception: {type(e).__name__}")
    print(f"Message: {str(e)}")

# Test 3: Subscription endpoint
print("\n\n" + "=" * 80)
print("TEST 3: /v1/dashboard/billing/subscription")
print("=" * 80)
try:
    response = requests.get(
        "https://api.openai.com/v1/dashboard/billing/subscription",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        timeout=10,
    )

    print(f"Status Code: {response.status_code}")
    print(f"\nRéponse brute:")
    print(response.text)

    if response.status_code == 200:
        data = response.json()
        print(f"\nJSON parsé:")
        print(json.dumps(data, indent=2))
    else:
        print(f"\n❌ Erreur HTTP {response.status_code}")

except Exception as e:
    print(f"\n❌ Exception: {type(e).__name__}")
    print(f"Message: {str(e)}")

# Test 4: Models endpoint (pour vérifier que la clé fonctionne)
print("\n\n" + "=" * 80)
print("TEST 4: /v1/models (vérification clé API)")
print("=" * 80)
try:
    response = requests.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        timeout=10,
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Clé API valide - {len(data.get('data', []))} modèles disponibles")
    else:
        print(f"❌ Erreur HTTP {response.status_code}")
        print(f"Message: {response.text}")

except Exception as e:
    print(f"\n❌ Exception: {type(e).__name__}")
    print(f"Message: {str(e)}")

print("\n" + "=" * 80)
print("FIN DES TESTS")
print("=" * 80)

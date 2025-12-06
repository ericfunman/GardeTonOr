# GardeTonOr 💰

Application de gestion et comparaison intelligente de contrats (assurances, téléphonie, énergie) utilisant l'IA pour optimiser vos dépenses.

## 🎯 Fonctionnalités

- **Importation automatique** : Upload de PDF et extraction des données via GPT-4
- **Gestion des contrats** : Téléphone, Assurance PNO (extensible)
- **Comparaison intelligente** : 
  - Analyse de marché via GPT-4
  - Comparaison avec devis concurrent
- **Dashboard** : Vue d'ensemble avec alertes dates anniversaires (J-40)
- **Historique** : Toutes les analyses et comparaisons sauvegardées
- **Graphiques** : Évolution des tarifs dans le temps

## 🛠️ Stack Technique

- **Frontend** : Streamlit
- **Backend** : Python
- **Base de données** : SQLite + SQLAlchemy ORM
- **IA** : OpenAI GPT-4o
- **Tests** : pytest (couverture 80%+)
- **CI/CD** : GitHub Actions

## 📦 Installation

### Prérequis
- Python 3.10+
- Clé API OpenAI

### Étapes

1. **Cloner le repository**
```bash
git clone <repository-url>
cd GardeTonOr
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
copy .env.example .env
# Éditer .env et ajouter votre OPENAI_API_KEY
```

5. **Initialiser la base de données**
```bash
python -m src.database.init_db
```

## 🚀 Lancement

```bash
streamlit run src/app.py
```

L'application sera accessible sur `http://localhost:8501`

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture
pytest --cov=src --cov-report=html

# Tests spécifiques
pytest tests/test_openai_service.py -v
```

## 📁 Structure du projet

```
GardeTonOr/
├── src/
│   ├── app.py                 # Application Streamlit principale
│   ├── config.py              # Configuration
│   ├── database/
│   │   ├── models.py          # Modèles SQLAlchemy
│   │   ├── database.py        # Connexion DB
│   │   └── init_db.py         # Initialisation
│   ├── services/
│   │   ├── openai_service.py  # Service OpenAI
│   │   ├── pdf_service.py     # Extraction PDF
│   │   └── contract_service.py # Logique métier
│   └── pages/
│       ├── dashboard.py       # Page d'accueil
│       ├── add_contract.py    # Ajout contrat
│       ├── compare.py         # Comparaisons
│       └── history.py         # Historique
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_openai_service.py
│   └── test_contract_service.py
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions
├── requirements.txt
├── .env.example
└── README.md
```

## 🔄 CI/CD

Les GitHub Actions exécutent automatiquement :
- Linting (flake8, black)
- Type checking (mypy)
- Tests unitaires
- Vérification couverture (80%+)

## 📝 Utilisation

1. **Ajouter un contrat** : Uploader un PDF, valider les données extraites
2. **Dashboard** : Voir tous vos contrats et alertes
3. **Comparer** : 
   - Demander une analyse de marché
   - Uploader un devis concurrent
4. **Historique** : Consulter toutes les analyses passées

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

## 📄 Licence

MIT

## 👤 Auteur

Eric LAPINA - Quanteam

# Guide de contribution

Merci de votre intérêt pour contribuer à GardeTonOr !

## Processus de développement

1. **Fork et clone** le repository
2. **Créer une branche** pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. **Développer** en suivant les standards du projet
4. **Tester** votre code (`pytest`)
5. **Commiter** vos changements (`git commit -m 'Ajout fonctionnalité X'`)
6. **Pousser** vers votre fork (`git push origin feature/ma-fonctionnalite`)
7. **Créer une Pull Request**

## Standards de code

### Style
- Suivre **PEP 8**
- Utiliser **Black** pour le formatage (ligne max 100 caractères)
- Passer **flake8** sans erreurs
- Ajouter des **docstrings** pour toutes les fonctions/classes

### Tests
- Couverture minimale de **80%**
- Tests unitaires pour toute nouvelle fonctionnalité
- Utiliser des **mocks** pour les appels API externes

### Commits
- Messages en français ou anglais
- Format: `Type: Description courte`
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

### Pull Requests
- Titre explicite
- Description détaillée des changements
- Lier les issues concernées
- Attendre la review avant merge

## Structure du code

```
src/
├── database/       # Modèles et gestion BDD
├── services/       # Logique métier
├── pages/          # Pages Streamlit
├── config.py       # Configuration
└── app.py          # Point d'entrée
```

## Tests locaux

```bash
# Installer les dépendances
pip install -r requirements.txt

# Linting
flake8 src tests
black --check src tests

# Tests
pytest --cov=src

# Lancer l'application
streamlit run src/app.py
```

## Questions ?

Ouvrez une **issue** pour toute question ou suggestion.

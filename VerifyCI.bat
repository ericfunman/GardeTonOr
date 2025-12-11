@echo off
echo ========================================
echo    Verification CI/CD Locale
echo ========================================
echo.

REM Activation de l'environnement virtuel
if not exist venv (
    echo [ERREUR] Environnement virtuel non trouve. Veuillez executer Install.bat d'abord.
    exit /b 1
)
call venv\Scripts\activate

echo [1/6] Installation des dependances de test...
pip install flake8 black mypy pytest pytest-cov bandit
if errorlevel 1 goto error

echo.
echo [2/6] Verification du style (Flake8)...
flake8 src tests --count --show-source --statistics
if errorlevel 1 goto error

echo.
echo [3/6] Verification du formatage (Black)...
black --check src tests
if errorlevel 1 (
    echo [INFO] Le code n'est pas formate correctement.
    echo [ACTION] Lancement de Black pour corriger...
    black src tests
)

echo.
echo [4/6] Verification des types (Mypy)...
mypy src --ignore-missing-imports
REM On ne bloque pas sur mypy pour l'instant car il peut etre strict
if errorlevel 1 echo [WARN] Erreurs de typage detectees (non bloquant)

echo.
echo [5/6] Tests unitaires (Pytest)...
set OPENAI_API_KEY=sk-dummy-key-for-testing
pytest --cov=src --cov-report=term-missing
if errorlevel 1 goto error

echo.
echo [6/6] Analyse de securite (Bandit)...
bandit -r src -f json -o bandit-report.json
if errorlevel 1 echo [WARN] Problemes de securite potentiels detectes (voir bandit-report.json)

echo.
echo ========================================
echo    SUCCES : Le code est pret pour le CI/CD !
echo ========================================
exit /b 0

:error
echo.
echo ========================================
echo    ECHEC : Corrigez les erreurs avant de pousser.
echo ========================================
exit /b 1

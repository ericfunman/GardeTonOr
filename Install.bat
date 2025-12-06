@echo off
REM Script d'installation de GardeTonOr
REM Auteur: Eric LAPINA - Quanteam
REM Date: 06/12/2025

echo.
echo ========================================
echo    GardeTonOr - Installation
echo ========================================
echo.

REM Se déplacer dans le répertoire du projet
cd /d "%~dp0"

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Python depuis https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Version Python detectee:
python --version
echo.

REM Créer l'environnement virtuel
if exist "venv" (
    echo [INFO] Environnement virtuel deja existant
) else (
    echo [INFO] Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Echec de la creation de l'environnement virtuel
        pause
        exit /b 1
    )
    echo [OK] Environnement virtuel cree
)
echo.

REM Installer les dépendances
echo [INFO] Installation des dependances (peut prendre quelques minutes)...
echo.
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip
"%~dp0venv\Scripts\python.exe" -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERREUR] Echec de l'installation des dependances
    pause
    exit /b 1
)

echo.
echo [OK] Dependances installees avec succes
echo.

REM Créer le fichier .env s'il n'existe pas
if not exist ".env" (
    echo [INFO] Creation du fichier .env...
    copy .env.example .env
    echo.
    echo ========================================
    echo  IMPORTANT: Configuration requise
    echo ========================================
    echo.
    echo Le fichier .env a ete cree.
    echo Vous devez maintenant l'editer et ajouter:
    echo   - Votre cle API OpenAI
    echo.
    echo Fichier: %~dp0.env
    echo.
    pause
)

REM Initialiser la base de données
echo [INFO] Initialisation de la base de donnees...
"%~dp0venv\Scripts\python.exe" -m src.database.init_db

if errorlevel 1 (
    echo [ERREUR] Echec de l'initialisation de la base de donnees
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Installation terminee avec succes!
echo ========================================
echo.
echo Pour lancer l'application, executez:
echo   StartGardeTonOr.bat
echo.
echo Ou utilisez la commande:
echo   venv\Scripts\python.exe -m streamlit run src/app.py
echo.
pause

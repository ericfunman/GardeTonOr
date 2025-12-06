@echo off
REM Script de lancement de l'application GardeTonOr
REM Auteur: Eric LAPINA - Quanteam
REM Date: 06/12/2025

echo.
echo ========================================
echo    GardeTonOr - Lancement
echo ========================================
echo.

REM Se déplacer dans le répertoire du projet
cd /d "%~dp0"

REM Vérifier si l'environnement virtuel existe
if not exist "venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouve!
    echo Veuillez executer: python -m venv venv
    pause
    exit /b 1
)

REM Vérifier si le fichier .env existe
if not exist ".env" (
    echo [AVERTISSEMENT] Fichier .env non trouve!
    echo Copie de .env.example vers .env...
    copy .env.example .env
    echo.
    echo IMPORTANT: Editez le fichier .env et ajoutez votre cle API OpenAI
    pause
)

REM Vérifier si la base de données existe
if not exist "gardetonor.db" (
    echo [INFO] Initialisation de la base de donnees...
    "%~dp0venv\Scripts\python.exe" -m src.database.init_db
    if errorlevel 1 (
        echo [ERREUR] Echec de l'initialisation de la base de donnees
        pause
        exit /b 1
    )
    echo [OK] Base de donnees initialisee avec succes
    echo.
)

REM Lancer l'application Streamlit
echo [INFO] Lancement de l'application GardeTonOr...
echo.
echo L'application va s'ouvrir dans votre navigateur par defaut.
echo Pour arreter l'application, appuyez sur Ctrl+C dans cette fenetre.
echo.

"%~dp0venv\Scripts\python.exe" -m streamlit run src/app.py

REM Si erreur
if errorlevel 1 (
    echo.
    echo [ERREUR] Echec du lancement de l'application
    echo.
    echo Verifiez que toutes les dependances sont installees:
    echo   venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

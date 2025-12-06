"""Configuration de l'application GardeTonOr."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gardetonor.db")

# Application
APP_NAME = os.getenv("APP_NAME", "GardeTonOr")
NOTIFICATION_DAYS_BEFORE = int(os.getenv("NOTIFICATION_DAYS_BEFORE", "40"))

# Types de contrats supportés
CONTRACT_TYPES = {
    "telephone": "Téléphone",
    "assurance_pno": "Assurance PNO",
    "electricite": "Électricité",
    "gaz": "Gaz",
}

# Configuration Streamlit
STREAMLIT_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "💰",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

"""Script d'initialisation de la base de données."""
from src.database.database import init_database

if __name__ == "__main__":
    print("Initialisation de la base de données...")
    init_database()
    print("✅ Base de données initialisée avec succès !")

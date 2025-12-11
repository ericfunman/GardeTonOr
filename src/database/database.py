"""Gestion de la connexion à la base de données."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from src.config import DATABASE_URL
from src.database.models import Base

# Création de l'engine SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Nécessaire pour SQLite
    echo=False,  # Mettre à True pour debug SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database() -> None:
    """Initialise la base de données en créant toutes les tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager pour obtenir une session de base de données.

    Usage:
        with get_db() as db:
            contracts = db.query(Contract).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Retourne une session de base de données.
    À utiliser dans les contextes où un context manager n'est pas pratique.
    N'oubliez pas de fermer la session après utilisation !
    """
    return SessionLocal()

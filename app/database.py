# database.py - Gestiona las conexiones a MongoDB y MySQL.
# MongoDB se usa como staging (datos crudos).
# MySQL se usa como data warehouse (datos limpios).
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import MONGO_URI, MONGO_DB, MYSQL_URL

# ── MongoDB ──────────────────────────────────────────────
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
coleccion_raw = mongo_db["shows_raw"]

# ── MySQL / SQLAlchemy ───────────────────────────────────
engine = create_engine(MYSQL_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    """Generador de sesiones para inyección de dependencias en FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# personajes_sql.py - Define la tabla shows_master en MySQL usando SQLAlchemy ORM.
# La PK id_show es el mismo ID de la API (no autoincremental),
# lo que permite cruzar registros con MongoDB por el mismo identificador.
from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from app.database import Base

class Show(Base):
    __tablename__ = "shows_master"

    id_show          = Column(Integer, primary_key=True, autoincrement=False, comment="ID original de TVmaze")
    nombre           = Column(String(255), nullable=False)
    tipo             = Column(String(100), nullable=True)
    idioma           = Column(String(100), nullable=True)
    estado           = Column(String(100), nullable=True)
    duracion_min     = Column(Integer, nullable=True)
    fecha_estreno    = Column(Date, nullable=True)
    calificacion     = Column(Float, nullable=True)
    genero_principal = Column(String(100), nullable=True)
    red_television   = Column(String(255), nullable=True)
    en_emision       = Column(Boolean, nullable=True, comment="True si estado es Running")

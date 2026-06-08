from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from app.database import Base

class Show(Base):
    __tablename__ = "shows_master"

    id_show        = Column(Integer, primary_key=True, autoincrement=False)
    nombre         = Column(String(255), nullable=False)
    tipo           = Column(String(100), nullable=True)
    idioma         = Column(String(100), nullable=True)
    estado         = Column(String(100), nullable=True)
    duracion_min   = Column(Integer, nullable=True)
    fecha_estreno  = Column(Date, nullable=True)
    calificacion   = Column(Float, nullable=True)
    genero_principal = Column(String(100), nullable=True)
    red_television = Column(String(255), nullable=True)

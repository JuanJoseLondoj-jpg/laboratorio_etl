# main.py - Punto de entrada de la aplicación FastAPI.
# Crea las tablas en MySQL si no existen y registra los routers.
from fastapi import FastAPI
from app.database import Base, engine
from app.models.personajes_sql import Show
from app.controllers import etl_controller, analitica_controller

# Crear tablas si no existen (resiliencia)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Laboratorio ETL - TVmaze",
    description="Pipeline ETL completo con FastAPI, MongoDB y MySQL usando la TVmaze API",
    version="1.0.0",
    contact={
        "name": "Equipo 3 - Bases de Datos para Ciencia de Datos"
    }
)

# Registrar routers
app.include_router(etl_controller.router, prefix="/api/v1/etl", tags=["ETL"])
app.include_router(analitica_controller.router, prefix="/api/v1", tags=["Analitica"])

@app.get("/")
def root():
    return {"mensaje": "API ETL TVmaze funcionando", "status": 200}

from fastapi import FastAPI
from app.database import Base, engine
from app.controllers import etl_controller, analitica_controller

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Laboratorio ETL - TVmaze",
    description="Pipeline ETL con FastAPI, MongoDB y MySQL",
    version="1.0.0"
)

# Registrar rutas
app.include_router(etl_controller.router, prefix="/api/v1/etl", tags=["ETL"])
app.include_router(analitica_controller.router, prefix="/api/v1", tags=["Analitica"])

@app.get("/")
def root():
    return {"mensaje": "API ETL TVmaze funcionando", "status": 200}

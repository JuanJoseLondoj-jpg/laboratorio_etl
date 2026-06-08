# etl_controller.py - Maneja las rutas del pipeline ETL.
# Recibe las peticiones HTTP, valida con schemas Pydantic y llama al service.
from fastapi import APIRouter, HTTPException
from app.views.schemas import ExtraccionRequest, ExtraccionResponse, TransformacionResponse, ResetResponse
from app.services import etl_service

router = APIRouter()

# ── Endpoint A: Extracción ───────────────────────────────

@router.post("/extraer", response_model=ExtraccionResponse, status_code=201)
def extraer(request: ExtraccionRequest):
    """Extrae shows de TVmaze y los guarda en MongoDB."""
    try:
        registros = etl_service.extraer_shows(request.cantidad)
        return ExtraccionResponse(
            mensaje="Datos extraídos exitosamente",
            registros_guardados=registros,
            fuente="TVmaze API",
            status=201
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Endpoint B: Transformación ───────────────────────────

@router.post("/transformar", response_model=TransformacionResponse, status_code=200)
def transformar():
    """Lee de MongoDB, transforma con Pandas y carga en MySQL."""
    try:
        registros = etl_service.transformar_y_cargar()
        return TransformacionResponse(
            mensaje="Pipeline finalizado",
            registros_procesados=registros,
            tabla_destino="shows_master",
            status=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Endpoint C: Reset ────────────────────────────────────

@router.delete("/reset", response_model=ResetResponse, status_code=200)
def reset():
    """Elimina todos los documentos de MongoDB y hace TRUNCATE en MySQL."""
    try:
        resultado = etl_service.reset_pipeline()
        return ResetResponse(
            mensaje="Sistema reseteado correctamente",
            mongo_docs_eliminados=resultado["mongo"],
            mysql_rows_eliminadas=resultado["mysql"],
            status=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

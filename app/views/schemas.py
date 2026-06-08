# schemas.py - Esquemas Pydantic para validar los JSON de entrada y salida.
# Cada endpoint tiene su propio schema de respuesta.
from pydantic import BaseModel, Field
from typing import Optional

# ── Entrada ──────────────────────────────────────────────

class ExtraccionRequest(BaseModel):
    cantidad: int = Field(..., gt=0, description="Cantidad de shows a extraer, debe ser mayor a 0")

# ── Salida ETL ───────────────────────────────────────────

class ExtraccionResponse(BaseModel):
    mensaje: str
    registros_guardados: int
    fuente: str
    status: int

class TransformacionResponse(BaseModel):
    mensaje: str
    registros_procesados: int
    tabla_destino: str
    status: int

class ResetResponse(BaseModel):
    mensaje: str
    mongo_docs_eliminados: int
    mysql_rows_eliminadas: int
    status: int

# ── Salida Analítica ─────────────────────────────────────

class ColumnaResponse(BaseModel):
    columna: str
    tipo: str
    datos: dict

class PerfilDualResponse(BaseModel):
    id: int
    vista_mongo: Optional[dict] = None
    vista_sql: Optional[dict] = None
    warning: Optional[str] = None

# analitica_service.py - Lógica de los endpoints analíticos.
# Le corresponde a: Laura

import pandas as pd
from fastapi import HTTPException
from sqlalchemy import text
from app.database import SessionLocal, engine, coleccion_raw

# ── Endpoint D: Análisis por Columna ─────────────────────────────────

def analizar_columna(nombre: str) -> dict:
    pass

# ── Endpoint E: Perfil Dual Mongo + SQL ──────────────────────────────

def perfil_dual(id: int) -> dict:
    pass
# analitica_service.py - Lógica de los endpoints analíticos.
# Le corresponde a: Laura

import pandas as pd
from fastapi import HTTPException
from sqlalchemy import text
from app.database import SessionLocal, engine, coleccion_raw

# ── Endpoint D: Análisis por Columna ─────────────────────────────────

def analizar_columna(nombre: str) -> dict:
    # Cargar tabla completa
    df = pd.read_sql("SELECT * FROM shows_master", engine)

    # Verificar que la columna existe
    if nombre not in df.columns:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"La columna '{nombre}' no existe",
                "columnas_validas": list(df.columns)
            }
        )

    columna = df[nombre]
    nulos = int(columna.isna().sum())

    # Numérica
    if pd.api.types.is_numeric_dtype(columna):
        return {
            "columna": nombre,
            "tipo": "numerica",
            "min": float(columna.min()),
            "max": float(columna.max()),
            "promedio": round(float(columna.mean()), 2),
            "mediana": float(columna.median()),
            "desviacion_std": round(float(columna.std()), 2),
            "nulos": nulos
        }

# ── Endpoint E: Perfil Dual Mongo + SQL ──────────────────────────────

def perfil_dual(id: int) -> dict:
    pass
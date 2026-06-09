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

    # Convertir columnas que parecen fechas
    for col in df.columns:
        if "fecha" in col.lower() or "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Verificar que la columna existe, si no retornar 400 con columnas válidas
    if nombre not in df.columns:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"La columna '{nombre}' no existe en shows_master",
                "columnas_validas": list(df.columns),
                "sugerencia": "Usa uno de los nombres de columna listados arriba"
            }
        )

    columna = df[nombre]
    nulos = int(columna.isna().sum())

    # Booleana
    if columna.dtype == bool or set(columna.dropna().unique()).issubset({True, False, 0, 1}):
        return {
            "columna": nombre,
            "tipo": "booleana",
            "true": int(columna.sum()),
            "false": int((columna == False).sum()),
            "nulos": nulos
        }

    # Numérica
    elif pd.api.types.is_numeric_dtype(columna):
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

    # Fecha
    elif pd.api.types.is_datetime64_any_dtype(columna):
        return {
            "columna": nombre,
            "tipo": "fecha",
            "min": str(columna.min().date()),
            "max": str(columna.max().date()),
            "rango_dias": (columna.max() - columna.min()).days,
            "nulos": nulos
        }

    # Categórica (texto)
    else:
        distribucion = columna.value_counts().to_dict()
        distribucion = {str(k): int(v) for k, v in distribucion.items()}
        return {
            "columna": nombre,
            "tipo": "categorica",
            "valores_unicos": int(columna.nunique()),
            "distribucion": distribucion,
            "valor_mas_comun": str(columna.mode()[0]),
            "nulos": nulos
        }

# ── Endpoint E: Perfil Dual Mongo + SQL ──────────────────────────────

def perfil_dual(id: int) -> dict:
    # 1. Consultar MongoDB por _id
    doc_mongo = coleccion_raw.find_one({"_id": id})

    # 2. Consultar MySQL por id_show
    db = SessionLocal()
    try:
        resultado = db.execute(
            text("SELECT * FROM shows_master WHERE id_show = :id"), {"id": id}
        ).fetchone()
        doc_sql = dict(resultado._mapping) if resultado else None
    finally:
        db.close()

    # Convertir fechas a string para que JSON las pueda serializar
    # MySQL retorna objetos date/datetime que JSON no entiende directamente
    # hasattr(v, 'isoformat') detecta si el valor es una fecha y lo convierte a string
    if doc_sql:
        doc_sql = {k: str(v) if hasattr(v, 'isoformat') else v
                   for k, v in doc_sql.items()}

    # 3. Manejar los 3 casos
    # Caso 3: no existe en ninguna → el controller devuelve 404
    if doc_mongo is None and doc_sql is None:
        return None

    # Caso 2a: solo en Mongo
    if doc_mongo is not None and doc_sql is None:
        return {
            "id": id,
            "vista_mongo": doc_mongo,
            "vista_sql": None,
            "warning": "Registro existe en Mongo pero no en MySQL. Posiblemente no se ha ejecutado /transformar o el registro falló en la transformación."
        }

    # Caso 2b: solo en MySQL
    if doc_mongo is None and doc_sql is not None:
        return {
            "id": id,
            "vista_mongo": None,
            "vista_sql": doc_sql,
            "warning": "Registro existe en MySQL pero no en Mongo. Inconsistencia en el pipeline."
        }

    # Caso 1: existe en ambas
    return {
        "id": id,
        "vista_mongo": doc_mongo,
        "vista_sql": doc_sql
    }
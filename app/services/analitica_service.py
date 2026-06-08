# analitica_service.py - Lógica de los endpoints analíticos.
# Le corresponde a: Laura
# Endpoint D: GET /api/v1/analitica/columna/{nombre}
# Endpoint E: GET /api/v1/perfil/{id}

import pandas as pd
from sqlalchemy import text
from app.database import SessionLocal, engine, coleccion_raw

# ── Endpoint D: Análisis por Columna ─────────────────────────────────

def analizar_columna(nombre: str) -> dict:
    """
    Analiza una columna de la tabla shows_master en MySQL.
    Detecta el tipo dinámicamente con df.dtypes (NO hardcodeado).
    Tipos soportados:
      - categorica: texto con valores repetidos → distribución, valor más común
      - numerica:   números → min, max, promedio, mediana, desviacion_std
      - fecha:      fechas → min, max, rango_dias
      - booleana:   true/false → conteo de cada uno
    Si la columna no existe → retorna 400 con lista de columnas válidas.
    """
    # TODO Laura:
    # 1. Cargar shows_master en un DataFrame con pd.read_sql
    # 2. Verificar que 'nombre' está en df.columns → si no, retornar error 400
    # 3. Detectar tipo con df[nombre].dtype
    # 4. Según el tipo retornar las estadísticas correspondientes
    pass


# ── Endpoint E: Perfil Dual Mongo + SQL ──────────────────────────────

def perfil_dual(id: int) -> dict:
    """
    Retorna el mismo registro visto desde MongoDB y MySQL.
    Sirve para auditar que el pipeline cargó bien los datos.
    Tres casos posibles:
      1. Existe en ambas bases → retorna vista_mongo y vista_sql
      2. Existe solo en una   → retorna la que existe, la otra como null + warning
      3. No existe en ninguna → retorna 404
    La PK está alineada: _id en Mongo == id_show en MySQL (mismo número).
    """
    # TODO Laura:
    # 1. Consultar MongoDB: coleccion_raw.find_one({"_id": id})
    # 2. Consultar MySQL: SELECT * FROM shows_master WHERE id_show = id
    # 3. Manejar los 3 casos con if/else
    pass
# analitica_controller.py - Maneja las rutas de analítica.
# Le corresponde a: Laura
# Endpoint D: GET /api/v1/analitica/columna/{nombre}
# Endpoint E: GET /api/v1/perfil/{id}
# El controller recibe la petición HTTP, valida y llama al service.
# Toda la lógica dura está en analitica_service.py (no aquí).

from fastapi import APIRouter, HTTPException
from app.services import analitica_service

router = APIRouter()

# ── Endpoint D: Análisis por Columna ─────────────────────────────────
# Ruta: GET /api/v1/analitica/columna/{nombre}
# Ejemplo: GET /api/v1/analitica/columna/idioma
# El {nombre} es dinámico — puede ser cualquier columna de shows_master.
# El service detecta automáticamente si es categórica, numérica, fecha o booleana.

@router.get("/analitica/columna/{nombre}")
def analizar_columna(nombre: str):
    """
    Retorna estadísticas de una columna según su tipo detectado dinámicamente.
    - Categórica: distribución de valores y valor más común.
    - Numérica: min, max, promedio, mediana, desviación estándar.
    - Fecha: min, max, rango en días.
    - Booleana: conteo de true y false.
    Retorna 400 si la columna no existe en shows_master.
    """
    try:
        resultado = analitica_service.analizar_columna(nombre)
        if resultado is None:
            raise HTTPException(status_code=400, detail="Columna no encontrada")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Endpoint E: Perfil Dual ───────────────────────────────────────────
# Ruta: GET /api/v1/perfil/{id}
# Ejemplo: GET /api/v1/perfil/1
# Consulta el mismo ID en MongoDB (_id) y MySQL (id_show).
# Demuestra que la PK está alineada entre ambas bases.
# Maneja 3 casos: ambas bases, solo una, ninguna.

@router.get("/perfil/{id}")
def perfil_dual(id: int):
    """
    Retorna el mismo registro visto desde MongoDB y MySQL.
    Caso 1 - Existe en ambas: retorna vista_mongo y vista_sql.
    Caso 2 - Existe solo en una: retorna la existente + warning.
    Caso 3 - No existe en ninguna: retorna 404.
    """
    try:
        resultado = analitica_service.perfil_dual(id)
        if resultado is None:
            raise HTTPException(status_code=404, detail="Registro no encontrado en ninguna base de datos")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
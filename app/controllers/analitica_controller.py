# analitica_controller.py - Maneja las rutas de analítica.
# Endpoint D: análisis estadístico por columna con detección dinámica de tipo.
# Endpoint E: perfil dual que cruza un registro entre MongoDB y MySQL.
from fastapi import APIRouter, HTTPException
from app.services import analitica_service

router = APIRouter()

# ── Endpoint D: Análisis por Columna ─────────────────────

@router.get("/analitica/columna/{nombre}")
def analizar_columna(nombre: str):
    """Retorna estadísticas de una columna según su tipo detectado dinámicamente."""
    try:
        resultado = analitica_service.analizar_columna(nombre)
        if resultado is None:
            raise HTTPException(status_code=400, detail="Columna no encontrada")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Endpoint E: Perfil Dual ──────────────────────────────

@router.get("/perfil/{id}")
def perfil_dual(id: int):
    """Retorna el mismo registro visto desde MongoDB y MySQL."""
    try:
        resultado = analitica_service.perfil_dual(id)
        if resultado is None:
            raise HTTPException(status_code=404, detail="Registro no encontrado en ninguna base de datos")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

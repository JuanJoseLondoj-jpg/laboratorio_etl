from fastapi import APIRouter, HTTPException
from app.services import analitica_service

router = APIRouter()

# ── Endpoint D: Análisis por Columna ─────────────────────

@router.get("/analitica/columna/{nombre}")
def analizar_columna(nombre: str):
    resultado = analitica_service.analizar_columna(nombre)
    if resultado is None:
        raise HTTPException(status_code=400, detail="Columna no encontrada")
    return resultado

# ── Endpoint E: Perfil Dual ──────────────────────────────

@router.get("/perfil/{id}")
def perfil_dual(id: int):
    resultado = analitica_service.perfil_dual(id)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado en ninguna base de datos")
    return resultado

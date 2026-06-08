# etl_service.py - Lógica del pipeline ETL.
# Extracción: llama TVmaze API, maneja paginación y guarda en MongoDB con upsert.
# La PK natural (_id) es el ID original de la API para alinear con MySQL.
import requests
from app.database import coleccion_raw
from app.config import API_BASE_URL

FUENTE = "TVmaze API"

# ── Extracción ───────────────────────────────────────────

def extraer_shows(cantidad: int) -> int:
    """Extrae shows de TVmaze y los guarda en MongoDB con idempotencia."""
    registros_guardados = 0
    pagina = 0

    while registros_guardados < cantidad:
        response = requests.get(f"{API_BASE_URL}/shows", params={"page": pagina})

        # Si no hay más páginas, detenemos
        if response.status_code == 404:
            break

        response.raise_for_status()
        shows = response.json()

        if not shows:
            break

        for show in shows:
            if registros_guardados >= cantidad:
                break

            # PK natural: usamos el id original de la API
            show["_id"] = show["id"]

            # Idempotencia: upsert por _id
            coleccion_raw.update_one(
                {"_id": show["_id"]},
                {"$set": show},
                upsert=True
            )
            registros_guardados += 1

        pagina += 1

    return registros_guardados

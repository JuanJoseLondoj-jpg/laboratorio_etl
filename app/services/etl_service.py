import requests
from app.database import coleccion_raw

API_URL = "https://api.tvmaze.com/shows"
FUENTE = "TVmaze API"

# ── Extracción ───────────────────────────────────────────

def extraer_shows(cantidad: int) -> int:
    registros_guardados = 0
    pagina = 0

    while registros_guardados < cantidad:
        response = requests.get(API_URL, params={"page": pagina})

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

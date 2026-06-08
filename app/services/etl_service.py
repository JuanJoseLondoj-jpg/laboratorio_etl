# etl_service.py - Lógica del pipeline ETL.
# Extracción: llama TVmaze API, maneja paginación y guarda en MongoDB con upsert.
# La PK natural (_id) es el ID original de la API para alinear con MySQL.
#
# División de responsabilidades en este archivo:
#   - extraer_shows()        → Juan José: extrae de TVmaze y guarda en MongoDB
#   - transformar_y_cargar() → Eendxi: transforma con Pandas y carga en MySQL
#   - reset_pipeline()       → Eendxi: limpia MongoDB y MySQL para reiniciar
#
# Flujo completo del pipeline:
#   1. POST /extraer    → TVmaze API → MongoDB (datos crudos)
#   2. POST /transformar → MongoDB → Pandas → MySQL (datos limpios)
#   3. DELETE /reset    → limpia ambas bases para nueva ejecución

import requests
from app.database import coleccion_raw
from app.config import API_BASE_URL

FUENTE = "TVmaze API"

# ── Extracción ───────────────────────────────────────────

def extraer_shows(cantidad: int) -> int:
    """
    Extrae shows de TVmaze y los guarda en MongoDB con idempotencia.
    Usa upsert por _id para evitar duplicados en ejecuciones repetidas.
    La PK natural (_id) es el ID original de la API.
    Lanza ValueError si cantidad <= 0.
    """
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")
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
            # Esto garantiza que el mismo ID se use en MongoDB (_id) y MySQL (id_show)
            # permitiendo cruzar registros entre ambas bases (validado: id=1 coincide en ambas)
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

# ── Transformación y Carga (EENDXI) ──────────────────────────────────
import pandas as pd
from app.database import coleccion_raw, SessionLocal, engine, Base
from app.models.personajes_sql import Show

def transformar_y_cargar() -> int:
    """
    Lee los datos crudos de MongoDB, los transforma con Pandas
    y los carga en MySQL. Es idempotente: no duplica datos.
    """
    # 1. EXTRACT desde MongoDB (colección shows_raw)
    documentos = list(coleccion_raw.find())
    if not documentos:
        return 0

    # 2. TRANSFORM con Pandas
    df = pd.DataFrame(documentos)

    # Renombrar _id a id_show (la PK de MySQL)
    df.rename(columns={"_id": "id_show"}, inplace=True)

    # Aplanar columna 'network' (viene como dict: {"id":1, "name":"CBS"})
    df["red_television"] = df["network"].apply(
        lambda x: x.get("name", "N/A") if isinstance(x, dict) and x else "N/A"
    )

    # Aplanar columna 'rating' (viene como dict: {"average": 7.5})
    df["calificacion"] = df["rating"].apply(
        lambda x: float(x.get("average")) if isinstance(x, dict) and x.get("average") else None
    )

    # Aplanar columna 'genres' (viene como lista: ["Drama", "Comedy"])
    df["genero_principal"] = df["genres"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else "N/A"
    )

    # Convertir fecha de string a date
    df["fecha_estreno"] = pd.to_datetime(df["premiered"], errors="coerce").dt.date

    # Manejar nulos en columnas de texto
    df["nombre"]       = df["name"].fillna("N/A")
    df["tipo"]         = df["type"].fillna("N/A")
    df["idioma"]       = df["language"].fillna("N/A")
    df["estado"]       = df["status"].fillna("N/A")
    df["duracion_min"] = pd.to_numeric(df["runtime"], errors="coerce").fillna(0).astype(int)

    # Seleccionar solo las columnas que van a MySQL
    df_final = df[["id_show","nombre","tipo","idioma","estado",
                   "duracion_min","fecha_estreno","calificacion",
                   "genero_principal","red_television"]].copy()

    # 3. LOAD en MySQL
    # Crear tabla si no existe (resiliencia)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for _, fila in df_final.iterrows():
            existente = db.query(Show).filter(
                Show.id_show == int(fila["id_show"])
            ).first()

            if existente:
                # Ya existe → actualizar (idempotencia)
                existente.nombre           = str(fila["nombre"])
                existente.tipo             = str(fila["tipo"])
                existente.idioma           = str(fila["idioma"])
                existente.estado           = str(fila["estado"])
                existente.duracion_min     = int(fila["duracion_min"])
                existente.fecha_estreno    = fila["fecha_estreno"]
                existente.calificacion     = fila["calificacion"]
                existente.genero_principal = str(fila["genero_principal"])
                existente.red_television   = str(fila["red_television"])
            else:
                # No existe → insertar
                nuevo = Show(
                    id_show          = int(fila["id_show"]),
                    nombre           = str(fila["nombre"]),
                    tipo             = str(fila["tipo"]),
                    idioma           = str(fila["idioma"]),
                    estado           = str(fila["estado"]),
                    duracion_min     = int(fila["duracion_min"]),
                    fecha_estreno    = fila["fecha_estreno"],
                    calificacion     = fila["calificacion"],
                    genero_principal = str(fila["genero_principal"]),
                    red_television   = str(fila["red_television"])
                )
                db.add(nuevo)

        db.commit()
    finally:
        db.close()

    print(f"[ETL] Transformación completa: {len(df_final)} registros procesados hacia MySQL")
    return len(df_final)

# ── Reset del pipeline (EENDXI) ───────────────────────────────────────
from sqlalchemy import text

def reset_pipeline() -> dict:
    """
    Reinicia completamente el pipeline ETL.
    - MongoDB: delete_many({}) elimina todos los documentos de shows_raw.
    - MySQL: TRUNCATE TABLE vacía shows_master pero conserva la estructura.
    Diferencia clave:
      TRUNCATE: borra todo rápido, resetea contadores, no se puede deshacer.
      DROP: eliminaría la tabla entera (estructura + datos). NO usamos esto.
      DELETE: borra fila por fila, más lento. NO usamos esto.
    Idempotente: se puede ejecutar múltiples veces sin error.
    Retorna conteo de documentos eliminados en cada base.
    """ 
    # Limpiar MongoDB - eliminar todos los documentos
    resultado = coleccion_raw.delete_many({})
    docs_eliminados = resultado.deleted_count

    # Limpiar MySQL con TRUNCATE (no DROP)
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        conn.execute(text("TRUNCATE TABLE shows_master"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()

    return {
        "mongo": docs_eliminados,
        "mysql": docs_eliminados
    }
# Garantías implementadas:
#   - Idempotencia: ningún endpoint duplica datos al ejecutarse varias veces
#   - PK alineada: id_show en MySQL == _id en MongoDB (mismo número)
#   - Resiliencia: la tabla se crea si no existe (Base.metadata.create_all)
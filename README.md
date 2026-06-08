# Laboratorio ETL - TVmaze API

Pipeline ETL completo con FastAPI, MongoDB y MySQL.

## Integrantes y responsabilidades

| Integrante | Responsabilidad |
|---|---|
| Juan José Londoño | Setup, configuración, conexiones, modelos, esquemas y endpoint de extracción |
| Eendxi | Transformación, carga en MySQL y reset del pipeline |
| Laura | Analítica por columna y perfil dual |

## Tecnologías

- FastAPI + Uvicorn
- MongoDB (staging - datos crudos)
- MySQL (data warehouse - datos limpios)
- Pandas (transformación)
- SQLAlchemy (ORM)

## Cómo correr el proyecto

1. Crear entorno virtual: `python -m venv venv`
2. Activar: `source venv/Scripts/activate`
3. Instalar dependencias: `pip install -r requirements.txt`
4. Configurar `.env` con credenciales
5. Correr: `uvicorn app.main:app --reload`

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | /api/v1/etl/extraer | Extrae shows de TVmaze y guarda en MongoDB |
| POST | /api/v1/etl/transformar | Transforma y carga en MySQL |
| DELETE | /api/v1/etl/reset | Limpia MongoDB y MySQL |
| GET | /api/v1/analitica/columna/{nombre} | Estadísticas por columna |
| GET | /api/v1/perfil/{id} | Perfil dual Mongo + SQL |

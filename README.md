# Laboratorio ETL - TVmaze API

Pipeline ETL completo con FastAPI, MongoDB y MySQL usando la TVmaze API.
Materia: Bases de Datos para Ciencia de Datos — Universidad de Antioquia.

## Integrantes y responsabilidades

| Integrante | Responsabilidad | Endpoints |
|---|---|---|
| Juan José Londoño | Setup, configuración, conexiones a MongoDB y MySQL, modelos SQLAlchemy, esquemas Pydantic y endpoint de extracción | POST /extraer |
| Eendxi | Transformación de datos con Pandas, carga en MySQL con idempotencia y reset del pipeline | POST /transformar, DELETE /reset |
| Laura | Analítica por columna con detección dinámica de tipos y perfil dual Mongo+SQL | GET /analitica/columna/{nombre}, GET /perfil/{id} |

## Arquitectura del Pipeline
TVmaze API → MongoDB (staging/datos crudos) → Pandas (transformación) → MySQL (data warehouse)
## Tecnologías

| Tecnología | Uso |
|---|---|
| FastAPI + Uvicorn | Framework web y servidor |
| MongoDB + PyMongo | Staging: almacena JSON crudos de la API |
| MySQL + SQLAlchemy | Data Warehouse: almacena datos limpios y estructurados |
| Pandas | Transformación: aplanamiento de JSON y limpieza de datos |
| Pydantic | Validación de esquemas de entrada y salida |
| python-dotenv | Gestión de variables de entorno |

## Estructura del Proyecto
laboratorio_etl/
├── .env                          # Credenciales (NO incluido en el repo)
├── .gitignore
├── requirements.txt
└── app/
├── main.py                   # Punto de entrada FastAPI
├── config.py                 # Variables de entorno
├── database.py               # Conexiones MongoDB y MySQL
├── controllers/
│   ├── etl_controller.py     # Rutas ETL
│   └── analitica_controller.py # Rutas Analítica
├── models/
│   └── personajes_sql.py     # Modelo tabla shows_master
├── services/
│   ├── etl_service.py        # Lógica ETL (extracción, transformación, reset)
│   └── analitica_service.py  # Lógica analítica
└── views/
└── schemas.py            # Esquemas Pydantic

## Configuración del entorno (.env)

Crear archivo `.env` en la raíz con estas variables:
MONGO_URI=mongodb://localhost:27017
MONGO_DB=laboratorio_etl
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_DB=laboratorio_etl
API_BASE_URL=https://api.tvmaze.com

## Cómo correr el proyecto

```bash
# 1. Clonar el repositorio
git clone https://github.com/JuanJoseLondoj-jpg/laboratorio_etl.git
cd laboratorio_etl

# 2. Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate        # Windows
source venv/bin/activate       # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env con tus credenciales

# 5. Iniciar MongoDB (debe estar corriendo antes de uvicorn)

# 6. Correr el servidor
uvicorn app.main:app --reload
```

## Endpoints

| Método | Ruta | Descripción | HTTP |
|---|---|---|---|
| POST | /api/v1/etl/extraer | Extrae shows de TVmaze y guarda en MongoDB | 201 |
| POST | /api/v1/etl/transformar | Transforma con Pandas y carga en MySQL | 200 |
| DELETE | /api/v1/etl/reset | Limpia MongoDB (delete_many) y MySQL (TRUNCATE) | 200 |
| GET | /api/v1/analitica/columna/{nombre} | Estadísticas por columna con detección dinámica de tipo | 200 |
| GET | /api/v1/perfil/{id} | Perfil dual: mismo registro visto desde Mongo y MySQL | 200 |

## Tabla MySQL — shows_master

| Columna | Tipo | Descripción |
|---|---|---|
| id_show | INT (PK) | ID original de TVmaze, alineado con _id de MongoDB |
| nombre | VARCHAR | Nombre del show |
| tipo | VARCHAR | Tipo (Scripted, Reality, etc.) |
| idioma | VARCHAR | Idioma original |
| estado | VARCHAR | Estado actual (Running, Ended, etc.) |
| duracion_min | INT | Duración en minutos |
| fecha_estreno | DATE | Fecha de estreno |
| calificacion | FLOAT | Calificación promedio |
| genero_principal | VARCHAR | Primer género de la lista |
| red_television | VARCHAR | Red/canal de televisión |

## Decisiones de diseño

- **Idempotencia en extracción:** Se usa `upsert` en MongoDB — si el documento ya existe se actualiza, nunca se duplica.
- **Idempotencia en transformación:** Antes de insertar en MySQL se verifica si el `id_show` ya existe. Si existe, se actualiza; si no, se inserta.
- **PK alineada:** El `id_show` en MySQL es exactamente el mismo que el `_id` en MongoDB, permitiendo cruzar registros entre ambas bases.
- **TRUNCATE vs DROP en reset:** TRUNCATE vacía la tabla conservando su estructura. DROP la eliminaría completamente.
- **Patrón MVC + Services:** Separación clara entre controladores (rutas HTTP), servicios (lógica de negocio) y modelos (estructura de datos).

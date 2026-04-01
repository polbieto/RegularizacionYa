# Regularización Ya — Asistente Virtual

Chatbot de orientación sobre la **Regularización Extraordinaria** en España, impulsado por el movimiento [Regularización Ya](https://regularizacionya.com).

> ⚠️ La información proporcionada por este asistente es **estrictamente orientativa** y no tiene valor legal. El texto definitivo será el publicado en el BOE.

## ¿Qué hace?

Responde dudas sobre el proceso de regularización extraordinaria a partir de un manual compilado con fuentes del movimiento Regularización Ya y el Círculo de Migraciones. El usuario introduce su email, inicia una conversación y puede preguntar sobre requisitos, plazos, documentación, vías de acceso, etc.

## Stack técnico

| Capa | Tecnología |
|------|------------|
| Interfaz conversacional | [Chainlit](https://chainlit.io) |
| Orquestación del agente | LangChain + LangGraph |
| LLM | LiteLLM (configurable) |
| Embeddings | Google Generative AI |
| Base de datos | PostgreSQL + pgvector |
| ORM | SQLAlchemy |
| Migraciones | yoyo-migrations |
| Contenedorización | Docker / Docker Compose |

## Requisitos previos

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Docker y Docker Compose (para la base de datos)
- Claves de API configuradas en `.env` (ver `.env` de ejemplo)

## Instalación

```bash
# Instalar dependencias
poetry install

# Levantar la base de datos con pgvector
docker compose up -d db

# Aplicar migraciones
yoyo apply --database "$DATABASE_URL" --batch ./migrations
```

## Ejecución

```bash
# Desarrollo local
chainlit run chatregularizacion/app.py -w
```

O con Docker Compose completo:

```bash
docker compose up
```

## Estructura del proyecto

```
chatregularizacion/
├── app.py                  # Punto de entrada (Chainlit)
├── config.py               # Variables de configuración
├── domain/                 # Entidades y puertos del dominio
├── application/            # Casos de uso
├── infrastructure/
│   ├── agent/              # Factoría del agente y proveedor LLM
│   └── repository/         # Repositorio y ORM (pgvector)
└── utils/                  # Validadores y utilidades
data/                       # Manual y fuentes de conocimiento
migrations/                 # Migraciones SQL
scripts/                    # Scripts de ingesta de documentos
tests/                      # Tests unitarios e integración
```

## Tests

```bash
poetry run pytest
```

## Autor

**Pol Bieto** — [stask.bieto@gmail.com](mailto:stask.bieto@gmail.com)

# Internal Assistant

Internal platform for document/ticket assistance. Current release: **gateway + ML analyze API** as two independently deployable services.

```
internal-assistant-project/
├── laravel/     # HTTP gateway, auth-ready app, Redis cache
├── ml-api/      # FastAPI analytics service
└── README.md
```

## Architecture

| Service | Role | Default URL |
|---------|------|-------------|
| `laravel` | Web UI + API gateway | http://127.0.0.1:8080 |
| `ml-api` | CSV analyze / future retrieval & LLM | http://127.0.0.1:8000 |
| Postgres | Application database | host `5433` |
| Redis | Cache / sessions / queues | host `6380` |

Services join a shared Docker network `internal-assistant-net` so Laravel reaches `http://ml-api:8000` by DNS.

## Prerequisites

```powershell
docker network create internal-assistant-net
```

## Configuration

Each service uses its own `.env` (never commit secrets):

```powershell
cd ml-api
copy .env.example .env

cd ..\laravel
copy .env.example .env
```

## Run

```powershell
cd C:\Docker\ai\internal-assistant-project\ml-api
docker compose up --build -d

cd C:\Docker\ai\internal-assistant-project\laravel
docker compose up --build -d
```

| Endpoint | Purpose |
|----------|---------|
| http://127.0.0.1:8080 | Analyze UI |
| http://127.0.0.1:8080/ml-health | Dependency health |
| http://127.0.0.1:8000/docs | OpenAPI |
| http://127.0.0.1:8000/health | ml-api liveness |

Identical CSV uploads are served from Redis (`cached: true`) for 30 minutes.

## Shutdown

```powershell
cd ml-api
docker compose down

cd ..\laravel
docker compose down
```

## Roadmap (product)

- Tabular ML train (`docs` in ml-api) → `POST /predict`
- Document ingest → chunk → embeddings (pgvector)
- `POST /ask` with citations
- SSO / RBAC, audit log, cost & latency metrics

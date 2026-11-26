# Internal Assistant — ML API

FastAPI service for tabular analysis, classical ML training, and future retrieval / LLM workloads.

**ML training & metrics:** [`docs/ML.md`](docs/ML.md)  
**sklearn lecture:** [`docs/sklearn-lecture.md`](docs/sklearn-lecture.md)  
**Retrieval:** [`docs/RETRIEVAL.md`](docs/RETRIEVAL.md) · [`retrieval-lecture.md`](docs/retrieval-lecture.md) · [`retrieval-deep-lecture.md`](docs/retrieval-deep-lecture.md)

```powershell
uv sync --extra retrieval
uv run python -m app.retrieval.build
uv run python -m app.retrieval.cli_search "cannot connect vpn"
```

```powershell
uv sync
uv run python -m app.ml.train
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/metrics` | Last train metrics (baseline + model) |
| POST | `/predict` | JSON features → `is_open` + probabilities |
| POST | `/analyze` | Multipart CSV → aggregate JSON (utility) |

## Configuration

```powershell
copy .env.example .env
```

## Run

```powershell
docker network create internal-assistant-net   # once
docker compose up --build -d
```

- OpenAPI: http://127.0.0.1:8000/docs  
- From other containers on the network: `http://ml-api:8000`

## Local development

```powershell
uv sync --extra dev
uv run uvicorn app.main:app --reload --port 8000
uv run pytest
```

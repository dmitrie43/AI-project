# Internal Assistant — Gateway (Laravel)

Laravel application: UI and HTTP gateway to the `ml-api` service. Responses for identical payloads are cached in Redis.

## Configuration

```powershell
copy .env.example .env
```

Key settings in `.env`: database, Redis, `ML_API_URL`, published host ports.

## Run

```powershell
docker network create internal-assistant-net   # once

# ml-api must be up on the same network
cd ..\ml-api
docker compose up --build -d

cd ..\laravel
docker compose up --build -d
```

- App (analyze): http://127.0.0.1:8080  
- Predict UI: http://127.0.0.1:8080/predict  
- Health: http://127.0.0.1:8080/ml-health  
- Postgres (host): `localhost:5433`  
- Redis (host): `localhost:6380`

## Request flow

1. Client uploads CSV → `POST /analyze`
2. Gateway hashes content → Redis lookup
3. On miss → `POST http://ml-api:8000/analyze` (timeout + retry)
4. Result stored in Redis (TTL 30 min)

Sample input: `storage/app/samples/tickets.csv`

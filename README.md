# Polaris Lab Console API

Polaris Lab is a long-term unified AppSec platform. This MVP provides the web console backend for user, organization, project, service, policy, and integration management without any scanning or analysis features.

If you are migrating from older Sentinel.AI naming, remove the old MySQL volume to recreate tables:
```bash
docker compose down -v
```

## Local Run

1) Copy env file:
```bash
cp .env.example .env
```

2) Start services:
```bash
docker compose up -d
```

3) Run migrations:
```bash
alembic upgrade head
```

4) Start API locally:
```bash
uvicorn app.main:app --reload
```

## API Docs
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Sample curl

Register:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@example.com","password":"PolarisPass1!","name":"Owner"}'
```

Login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@example.com","password":"PolarisPass1!"}'
```

Create Org:
```bash
curl -X POST http://localhost:8000/api/orgs \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Polaris Lab Org"}'
```

Create Project:
```bash
curl -X POST http://localhost:8000/api/orgs/<org_id>/projects \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Web Console","key":"WEB"}'
```

Create Service:
```bash
curl -X POST http://localhost:8000/api/projects/<project_id>/services \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Console API","type":"API","environment":"PROD"}'
```

Dashboard Summary:
```bash
curl -X GET http://localhost:8000/api/dashboard/summary \
  -H "Authorization: Bearer <access_token>"
```

## Tests

Tests run on SQLite while production uses MySQL. The test suite creates and drops tables automatically.

```bash
pytest
```

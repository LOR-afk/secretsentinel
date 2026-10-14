# SecretSentinel — Source Code Secret Exposure Detector

A locally runnable full-stack MVP: React/Vite dashboard, FastAPI REST API, PostgreSQL, Alembic migrations, and defensive ZIP scanning. Redis is unnecessary for this synchronous MVP.

## Assumptions and scope

- Scan only code you own or have permission to inspect.
- A single trusted local user is assumed. **There is no authentication or tenant isolation: do not publish this deployment to the public internet.**
- Detects four pattern classes: AWS-style key IDs, GitHub-style tokens, private-key headers, and generic secret assignments.
- Findings may be false positives or false negatives. This is not a replacement for mature scanners like Gitleaks or TruffleHog.
- Source archives are held in process memory during scanning and never intentionally written to disk or database. The DB stores finding metadata only. Uploaded file names and file paths may still contain sensitive information.
- The ZIP parser applies member-count and size limits and rejects traversal paths and symbolic links. The system is not a hardened malware sandbox: do not upload untrusted executable archives.
- Secrets found in committed Git history are **not** scanned; only current text files in the ZIP are checked.

## File layout

```text
secretsentinel/
├── backend/
│   ├── app/{config,database,models,schemas,scanner,main}.py
│   ├── migrations/versions/001_initial.py
│   ├── tests/{test_api,test_scanner}.py
│   ├── schema.sql
│   ├── seed.py
│   └── Dockerfile
├── frontend/
│   ├── src/{App.jsx,main.jsx,style.css}
│   └── Dockerfile
├── docs/{erd.md,openapi.yaml}
├── docker-compose.yml
└── .env.example
```

## Quick start (Docker Desktop)

```bash
docker compose up --build -d
```

Then open:

- React dashboard: http://localhost:5173
- FastAPI docs: http://localhost:8000/docs
- API health: http://localhost:8000/api/health

Run migrations separately when your schema changes:

```bash
docker compose exec backend alembic upgrade head
```

Seed one deterministic demo finding:

```bash
docker compose exec backend python seed.py
```

Stop:

```bash
docker compose down
```

To erase all demo database records: `docker compose down -v` (destructive).

## Local development without Docker for API

Install PostgreSQL and create database/user matching `.env.example`; copy `.env.example` to `backend/.env`. From `backend/`:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

The frontend Vite proxy defaults to the Docker hostname `backend`. For running Vite directly on your PC, change `frontend/vite.config.js` target temporarily to `http://localhost:8000`.

```bash
cd frontend
npm install
npm run dev
```

## Tests

From `backend/`:

```bash
pip install -r requirements-dev.txt
pytest -q
```

Tests use an in-memory SQLite database, while actual deployment uses PostgreSQL. CI and production hardening should additionally test PostgreSQL migrations and concurrent scans.

## Example scan

Create a ZIP containing `example.py` with `password = "dummy_example_password_123"`. Use the dashboard or:

```bash
curl -F 'file=@sample.zip' http://localhost:8000/api/scans
```

`GET /api/scans`, `GET /api/scans/{id}`, and `DELETE /api/scans/{id}` are also supported.

## API and schema

- OpenAPI document: `docs/openapi.yaml` (a compact route contract). FastAPI additionally generates the complete response-schema specification at `/openapi.json`.
- Mermaid ERD and DBML: `docs/erd.md`.
- PostgreSQL DDL: `backend/schema.sql`.
- Alembic revision: `backend/migrations/versions/001_initial.py`.

## Security work before public deployment

Add authentication, authorization, TLS, request throttling, audit access controls, limits at reverse proxy, isolated workers, secret-safe logging, ZIP-bomb defenses, CI security tests and an explicit data-retention policy. Never persist raw code, raw tokens or matched line content. Migrate scanning to sandboxed async jobs before allowing arbitrary third-party archives.

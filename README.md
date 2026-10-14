# SecretSentinel — Source Code Secret Exposure Detector

**A full-stack cybersecurity application for identifying potentially exposed credentials, API keys, authentication tokens, and private-key material in source code archives.**

SecretSentinel helps developers detect accidental credential exposure before source code reaches public repositories or production environments. The application uses a rule-based scanning engine, provides severity-classified findings, and maintains scan history without intentionally storing detected secret values.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | Python + FastAPI |
| Database (Local) | MySQL/MariaDB via XAMPP |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| API Architecture | RESTful API |
| Detection Engine | Python-based pattern matching |
| API Documentation | Swagger UI / OpenAPI |
| Version Control | Git + GitHub |

The original project also supports a PostgreSQL-oriented Docker configuration. The locally tested setup uses XAMPP MySQL/MariaDB without Docker.

## Features

### 1. Source Code ZIP Scanning
- Upload ZIP archives containing source code.
- Analyze supported text-based source files.
- Apply archive size and file-count limits.
- Reject unsafe archive paths and symbolic links.

### 2. Secret Exposure Detection

The scanner provides four detection categories:

- AWS-style access key identifiers
- GitHub-style authentication tokens
- Private-key headers
- Generic hardcoded secret assignments

Detection is rule-based and may produce false positives or false negatives.

### 3. Security Findings
- Identify potential credential exposure.
- Classify findings by severity.
- Display affected file paths and line numbers.
- Associate findings with detection rules.
- Provide descriptive security messages.

### 4. Scan History
- Save previous scan records.
- Retrieve previous findings.
- Display scan history in the dashboard.
- Delete previous scan records.

### 5. Security Dashboard
- Total scans and findings indicators.
- Available detection rule count.
- ZIP upload interface.
- Recent scan history.
- Detailed findings table.

### 6. Privacy-Conscious Reporting

SecretSentinel is designed to retain finding metadata rather than raw source code or detected secret values.

File names and paths may still contain sensitive information. The application should therefore be used only with trusted local access.

## System Architecture

```text
React + Vite Dashboard
          |
          v
FastAPI REST API
          |
          v
ZIP Validation and Extraction
          |
          v
Rule-Based Secret Detection
          |
          v
SQLAlchemy ORM
          |
          v
MySQL/MariaDB Database
          |
          v
Scan History and Findings
```

## Project Structure

```text
secretsentinel/
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── scanner.py
│   │   └── main.py
│   ├── migrations/
│   │   └── versions/
│   │       └── 001_initial.py
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_scanner.py
│   ├── .env
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── alembic.ini
│   ├── schema.sql
│   ├── seed.py
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── style.css
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docs/
│   ├── erd.md
│   └── openapi.yaml
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Installation — Windows Without Docker

### Prerequisites

- Python 3.11 or newer
- Node.js and npm
- XAMPP with MySQL/MariaDB
- Visual Studio Code
- Git

### Step 1 — Clone the Repository

```bash
git clone https://github.com/LOR-afk/secretsentinel.git
cd secretsentinel
```

**Note:** The GitHub repository must exist before this command can be used. Alternatively, open an existing extracted project folder.

### Step 2 — Start XAMPP

1. Open XAMPP Control Panel.
2. Start MySQL.
3. Start Apache if using phpMyAdmin.
4. Open http://localhost/phpmyadmin/.

### Step 3 — Create Database

Create a database named:

```sql
CREATE DATABASE IF NOT EXISTS secretsentinel
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Database tables are created through Alembic migrations.

### Step 4 — Configure Backend

Create `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://root@127.0.0.1:3306/secretsentinel?charset=utf8mb4
CORS_ORIGINS=http://localhost:5173
MAX_UPLOAD_BYTES=5000000
```

This example assumes default XAMPP development credentials and an empty root password. Adjust the connection string for your environment.

Never commit `.env` files to GitHub.

The backend must be configured to load this environment file through its settings module.

### Step 5 — Install Python Dependencies

From the backend directory:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install pymysql
```

### Step 6 — Run Database Migrations

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Expected database tables:

```text
secretsentinel
├── alembic_version
├── scans
└── findings
```

### Step 7 — Start FastAPI

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000

Swagger documentation: http://127.0.0.1:8000/docs

Health endpoint: http://127.0.0.1:8000/api/health

### Step 8 — Configure React API Proxy

Set the `/api` proxy target in `frontend/vite.config.js` to:

```javascript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
```

### Step 9 — Start React

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Dashboard: http://localhost:5173

Keep the FastAPI and React terminals running simultaneously.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check API health |
| POST | `/api/scans` | Upload ZIP and create scan |
| GET | `/api/scans` | List previous scans |
| GET | `/api/scans/{scan_id}` | Retrieve scan findings |
| DELETE | `/api/scans/{scan_id}` | Delete scan |

Interactive API documentation is available at `/docs`.

## Database Design

### Scans
Stores scan metadata, including filenames, scan status, number of files checked, total findings, and timestamps.

### Findings
Stores the detected rule, severity, affected source file, line number, and descriptive finding message.

Each scan can contain multiple findings.

Database schema documentation is available in `docs/erd.md`.

## Testing

### Automated Backend Tests

From the backend directory:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The original automated tests use an in-memory SQLite database for isolation. Passing these tests does not by itself verify MySQL compatibility.

### Manual Functional Testing

1. Open the React dashboard.
2. Upload a ZIP containing authorized test source files.
3. Run the security scan.
4. Review the detected findings.
5. Refresh the dashboard.
6. Confirm previous scans remain available.
7. Verify scan metadata in the database.

### Local MVP Verification

The following functionality was demonstrated during local testing:

- React dashboard loading successfully.
- FastAPI server and Swagger UI running.
- Frontend-to-backend API communication.
- ZIP archive submission.
- Detection of a simulated hardcoded credential.
- Display of severity, rule, file path, and line number.
- Scan history remaining available after browser refresh.

Observed demo result:

| Test | Result |
|---|---|
| Archive | `secretsentinel-demo.zip` |
| Files checked | 2 |
| Findings | 1 |
| Detection rule | `GENERIC_SECRET` |
| Severity | MEDIUM |
| File | `src/config.py` |
| Line | 2 |

Further testing is recommended for malformed ZIP files, oversized archives, false positives, deletion behavior, and database privacy guarantees.

## Optional Docker Setup

The original Docker configuration targets PostgreSQL rather than the local XAMPP database.

For environments configured with Docker Desktop and the corresponding PostgreSQL connection settings:

```bash
docker compose up --build -d
```

Stop the containers:

```bash
docker compose down
```

This deployment path has not yet been verified in the current Windows/XAMPP environment.

## Security Limitations

SecretSentinel is a defensive, educational MVP.

- No user authentication or tenant isolation is currently implemented.
- The API must not be exposed directly to the public internet.
- The scanner is not a malware execution sandbox.
- Detection rules are limited and can miss real secrets.
- Historical Git commits are not scanned.
- ZIP contents are processed during scanning.
- Scan metadata, including filenames and paths, may contain sensitive information.
- The application must not be treated as a replacement for professional secret-scanning tools.

### Recommended Future Security Improvements

- Authentication and authorization
- Per-user scan isolation
- Stronger detection rules and entropy analysis
- Configurable scanning exclusions
- Secret-safe logging
- Request rate limiting
- Isolated scanning workers
- Secure report export
- Audit logging and retention controls
- CI/CD integration
- Automated vulnerability and dependency scanning

## Project Status

**Version:** 0.1.0 — Functional Local MVP

Core source code scanning, API communication, findings display, and scan history have been demonstrated locally.

The project is not yet production-ready. Additional security hardening, integration testing, and public-deployment safeguards are required.

## Developer

**Lore Lindell Tamayo**  
BS Information Technology Student  
Full-Stack Web Development and Cybersecurity

GitHub: https://github.com/LOR-afk

Portfolio: https://lorelindell.vercel.app/

## License

No license has been selected yet. A license file should be added before declaring open-source redistribution permissions.
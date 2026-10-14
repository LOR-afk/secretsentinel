# SecretSentinel

A source code scanner that helps detect accidentally exposed credentials in ZIP archives. Built with React, FastAPI, and MySQL.

I built SecretSentinel to explore how secret detection works and to practice building a security-focused full-stack application. It scans source files for common credential patterns and displays findings without saving the detected values.

## Features

- Scan ZIP archives containing source code
- Detect hardcoded passwords, API keys, GitHub tokens, and private-key headers
- View findings with severity levels, filenames, and line numbers
- Keep track of previous scans
- Delete scan records
- Review results through a simple web dashboard

The scanner uses pattern matching, so it may miss some secrets or flag harmless values.

## Tech Stack

- **Frontend:** React, Vite
- **Backend:** Python, FastAPI
- **Database:** MySQL/MariaDB (XAMPP)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic

## Getting Started

### Requirements

- Python
- Node.js and npm
- XAMPP with MySQL/MariaDB

### Database Setup

Start MySQL in XAMPP and create a database named `secretsentinel` using phpMyAdmin.

Create a `.env` file inside the `backend` directory:

```env
DATABASE_URL=mysql+pymysql://root@127.0.0.1:3306/secretsentinel?charset=utf8mb4
CORS_ORIGINS=http://localhost:5173
MAX_UPLOAD_BYTES=5000000
```

The connection string assumes the default local XAMPP configuration.

### Backend

Open a terminal in the `backend` folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install pymysql
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

API documentation: `http://127.0.0.1:8000/docs`

### Frontend

Open another terminal in the `frontend` folder:

```powershell
npm install
npm run dev
```

Open `http://127.0.0.1:5173` in your browser.

Make sure the API proxy in `vite.config.js` points to `http://127.0.0.1:8000`.

## Testing

Run the backend tests from the `backend` directory:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

To test the scanner manually, create a ZIP containing a Python file with a dummy hardcoded credential:

```python
password = "dummy_example_password_123"
```

Upload the ZIP through the dashboard and check the findings.

## Notes

SecretSentinel currently scans files inside ZIP archives, not Git commit history. Detection is limited to predefined patterns.

This is a local development project without user authentication. It should not be exposed publicly in its current state. Only scan source code you own or have permission to inspect.

## Author

**Lore Lindell Tamayo**

GitHub: https://github.com/LOR-afk

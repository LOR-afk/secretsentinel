import os
os.environ["DATABASE_URL"] = "sqlite://"
import io
import zipfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_db():
    with TestingSession() as db:
        yield db

app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def make_zip():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zipf:
        zipf.writestr("config.py", 'password = "example_dummy_password_123"')
    return buffer.getvalue()


def test_full_scan_lifecycle():
    response = client.post("/api/scans", files={"file": ("code.zip", make_zip(), "application/zip")})
    assert response.status_code == 201
    data = response.json()
    assert data["findings_count"] == 1
    assert "example_dummy_password_123" not in response.text
    scan_id = data["id"]
    assert client.get(f"/api/scans/{scan_id}").status_code == 200
    assert client.get("/api/scans").status_code == 200
    assert client.delete(f"/api/scans/{scan_id}").status_code == 204
    assert client.get(f"/api/scans/{scan_id}").status_code == 404

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.config import settings
from app.database import get_db
from app.models import Finding, Scan
from app.scanner import InvalidArchive, scan_zip
from app.schemas import ScanDetail, ScanSummary


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="SecretSentinel API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_methods=["GET", "POST", "DELETE"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/scans", response_model=ScanDetail, status_code=201)
async def create_scan(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Upload a .zip archive")
    contents = await file.read(settings.max_upload_bytes + 1)
    if len(contents) > settings.max_upload_bytes:
        raise HTTPException(413, "Upload exceeds 5 MB limit")
    try:
        files_scanned, hits = scan_zip(contents)
    except InvalidArchive as exc:
        raise HTTPException(400, str(exc)) from exc
    scan = Scan(filename=file.filename.replace("\\", "/").rsplit("/", 1)[-1][:255], files_scanned=files_scanned, findings_count=len(hits))
    for hit in hits:
        scan.findings.append(Finding(file_path=hit.file_path, line_number=hit.line_number, rule_id=hit.rule_id, severity=hit.severity, message=hit.message))
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return db.scalar(select(Scan).options(selectinload(Scan.findings)).where(Scan.id == scan.id))


@app.get("/api/scans", response_model=list[ScanSummary])
def list_scans(db: Session = Depends(get_db)):
    return db.scalars(select(Scan).order_by(Scan.created_at.desc()).limit(100)).all()


@app.get("/api/scans/{scan_id}", response_model=ScanDetail)
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    scan = db.scalar(select(Scan).options(selectinload(Scan.findings)).where(Scan.id == scan_id))
    if scan is None:
        raise HTTPException(404, "Scan not found")
    return scan


@app.delete("/api/scans/{scan_id}", status_code=204)
def delete_scan(scan_id: str, db: Session = Depends(get_db)):
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(404, "Scan not found")
    db.delete(scan)
    db.commit()

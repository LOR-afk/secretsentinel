from app.database import SessionLocal
from app.models import Finding, Scan


def main():
    with SessionLocal() as session:
        if session.query(Scan).filter_by(filename="demo-example.zip").first():
            return
        scan = Scan(id="00000000-0000-0000-0000-000000000001", filename="demo-example.zip", status="completed", files_scanned=2, findings_count=1)
        scan.findings.append(Finding(id="00000000-0000-0000-0000-000000000002", file_path="src/settings.py", line_number=4, rule_id="GENERIC_SECRET", severity="medium", message="Possible hardcoded secret assignment"))
        session.add(scan)
        session.commit()


if __name__ == "__main__":
    main()

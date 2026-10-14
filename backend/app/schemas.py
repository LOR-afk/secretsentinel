from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    file_path: str
    line_number: int
    rule_id: str
    severity: str
    message: str


class ScanSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    status: str
    files_scanned: int
    findings_count: int
    created_at: datetime


class ScanDetail(ScanSummary):
    findings: list[FindingOut]

import io
import re
import stat
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath

MAX_FILES = 300
MAX_TOTAL_UNCOMPRESSED = 10_000_000
MAX_FILE_BYTES = 1_000_000
IGNORED_DIRS = {"node_modules", ".git", "dist", "build", "vendor", "__pycache__"}
TEXT_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".php", ".json", ".yml", ".yaml", ".env", ".txt", ".ini", ".toml", ".properties", ".sh", ".go", ".java", ".rb", ".md", ".xml"}


class InvalidArchive(ValueError):
    pass


@dataclass(frozen=True)
class Hit:
    file_path: str
    line_number: int
    rule_id: str
    severity: str
    message: str


RULES = [
    ("AWS_ACCESS_KEY", "high", "Possible AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("GITHUB_TOKEN", "critical", "Possible GitHub access token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("PRIVATE_KEY", "critical", "Private key header", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("GENERIC_SECRET", "medium", "Possible hardcoded secret assignment", re.compile(r"(?i)\b(?:api[_-]?key|secret[_-]?key|client[_-]?secret|password|auth[_-]?token)\b\s*[:=]\s*['\"]?([A-Za-z0-9_./+!@#$%^&*=-]{12,})")),
]


def scan_text(path: str, text: str) -> list[Hit]:
    hits = []
    for number, line in enumerate(text.splitlines(), start=1):
        for rule_id, severity, message, pattern in RULES:
            if pattern.search(line):
                hits.append(Hit(path, number, rule_id, severity, message))
    return hits


def scan_zip(contents: bytes) -> tuple[int, list[Hit]]:
    try:
        archive = zipfile.ZipFile(io.BytesIO(contents))
    except (zipfile.BadZipFile, OSError) as exc:
        raise InvalidArchive("Invalid ZIP archive") from exc
    with archive:
        members = archive.infolist()
        if len(members) > MAX_FILES:
            raise InvalidArchive("Archive contains too many entries")
        total = 0
        for member in members:
            total += member.file_size
            if member.file_size > MAX_FILE_BYTES or total > MAX_TOTAL_UNCOMPRESSED:
                raise InvalidArchive("Archive exceeds decompressed size limits")
            path = PurePosixPath(member.filename.replace("\\", "/"))
            if path.is_absolute() or ".." in path.parts or not path.parts:
                raise InvalidArchive("Unsafe archive path")
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise InvalidArchive("Symbolic links are not supported")
        scanned = 0
        findings = []
        for member in members:
            if member.is_dir():
                continue
            path = PurePosixPath(member.filename.replace("\\", "/"))
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS and path.name != ".env":
                continue
            try:
                with archive.open(member) as file:
                    content = file.read(MAX_FILE_BYTES + 1)
                if len(content) > MAX_FILE_BYTES or b"\0" in content:
                    continue
                text = content.decode("utf-8")
            except (UnicodeDecodeError, RuntimeError, zipfile.BadZipFile):
                continue
            scanned += 1
            findings.extend(scan_text(str(path), text))
        return scanned, findings

import io
import zipfile
import pytest
from app.scanner import scan_text, scan_zip, InvalidArchive


def archive(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as z:
        for path, body in files.items():
            z.writestr(path, body)
    return stream.getvalue()


def test_finds_secret_without_storing_value():
    raw = 'password = "this_is_a_dummy_password_123"'
    results = scan_text("app.py", raw)
    assert len(results) == 1
    assert results[0].rule_id == "GENERIC_SECRET"
    assert "this_is_a_dummy_password_123" not in repr(results)


def test_zip_scanning():
    count, findings = scan_zip(archive({"src/settings.py": 'api_key = "example_dummy_value_123"', "image.png": "not checked"}))
    assert count == 1
    assert len(findings) == 1


def test_zip_slip_rejected():
    with pytest.raises(InvalidArchive):
        scan_zip(archive({"../outside.py": "password=some_dummy_secret_123"}))


def test_binary_ignored():
    count, findings = scan_zip(archive({"test.py": b"\x00password=some_dummy_secret_123"}))
    assert count == 0
    assert findings == []

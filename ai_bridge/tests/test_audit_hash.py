import json
from pathlib import Path

from ai_bridge.tools import audit_report


def _write_record(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def test_hash_chain_validation(tmp_path: Path) -> None:
    log_path = tmp_path / "session.jsonl"
    record1 = {"timestamp": "t1", "event": "a", "payload": {}, "prev_hash": None}
    record1["record_hash"] = audit_report._hash_record(record1)
    _write_record(log_path, record1)
    record2 = {"timestamp": "t2", "event": "b", "payload": {}, "prev_hash": record1["record_hash"]}
    record2["record_hash"] = audit_report._hash_record(record2)
    _write_record(log_path, record2)

    valid, _ = audit_report._validate_chain(log_path)
    assert valid is True

    tampered = json.loads(log_path.read_text(encoding="utf-8").splitlines()[1])
    tampered["event"] = "tampered"
    log_path.write_text(json.dumps(record1) + "\n" + json.dumps(tampered) + "\n", encoding="utf-8")
    valid, _ = audit_report._validate_chain(log_path)
    assert valid is False

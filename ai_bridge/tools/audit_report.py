from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path


def _hash_record(record: dict) -> str:
    encoded = json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_chain(log_path: Path) -> tuple[bool, str | None]:
    last_hash = None
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("prev_hash") != last_hash:
            return False, record.get("record_hash")
        record_hash = record.get("record_hash")
        calculated = _hash_record({k: v for k, v in record.items() if k != "record_hash"})
        if record_hash != calculated:
            return False, record_hash
        last_hash = record_hash
    return True, last_hash


def _summarize(log_path: Path) -> dict:
    mode_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    rule_counts: dict[str, int] = {}
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        event = record.get("event")
        payload = record.get("payload", {})
        if event == "action_eval":
            decision = payload.get("decision", {})
            mode = decision.get("mode", "unknown")
            rule_id = decision.get("rule_id", "unknown")
            target = decision.get("target", "unknown")
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
            rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
            target_counts[target] = target_counts.get(target, 0) + 1
    return {
        "mode_counts": mode_counts,
        "target_counts": target_counts,
        "rule_counts": rule_counts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate audit report for a session.")
    parser.add_argument("session_dir", type=Path)
    args = parser.parse_args()

    log_path = args.session_dir / "session.jsonl"
    if not log_path.exists():
        print("Missing session.jsonl")
        return 1
    valid, last_hash = _validate_chain(log_path)
    summary = _summarize(log_path)
    summary["hash_chain_valid"] = valid
    summary["last_hash"] = last_hash
    print(json.dumps(summary, indent=2))
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())

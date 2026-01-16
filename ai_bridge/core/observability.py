from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ai_bridge.core.actions import Action
from ai_bridge.core.policy import PolicyDecision
from ai_bridge.vision.frame_types import RedactedFrame


@dataclass
class SessionRecorder:
    session_dir: Path

    def __post_init__(self) -> None:
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.frames_dir = self.session_dir / "frames"
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.actions_path = self.session_dir / "actions.jsonl"

    def record_frame(self, frame: RedactedFrame, metadata: dict) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        frame_path = self.frames_dir / f"{timestamp}.png"
        frame.save(str(frame_path))
        self._append(self.session_dir / "frames.jsonl", {"path": str(frame_path), **metadata})
        return frame_path

    def record_action(self, action: Action, decision: PolicyDecision, dry_run: bool) -> None:
        payload = {
            "action": action.action_type.value,
            "x": action.x,
            "y": action.y,
            "text_length": len(action.text) if action.text else 0,
            "dry_run": dry_run,
            "decision": {
                "allowed": decision.allowed,
                "requires_confirmation": decision.requires_confirmation,
                "risk": decision.risk.value,
                "rule_id": decision.rule_id,
                "target": decision.target,
                "mode": decision.mode.value,
            },
        }
        self._append(self.actions_path, payload)

    def _append(self, path: Path, payload: dict) -> None:
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

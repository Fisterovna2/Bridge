from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

from ai_bridge.core.actions import Action
from ai_bridge.core.modes import RunMode
from ai_bridge.core.router import ModelRouter
from ai_bridge.core.safety import GuardrailDecision, assess_action
from ai_bridge.input.ghost_cursor import GhostCursorOverlay
from ai_bridge.input.host_input import HostInputController
from ai_bridge.vision.capture import capture_screen
from ai_bridge.vision.ocr import OcrEngine
from ai_bridge.vision.pii import PiiDetector
from ai_bridge.vision.redact import redact_image
from ai_bridge.vm.adapter_base import VmAdapter
from ai_bridge.vm.adapter_placeholder import PlaceholderVmAdapter


@dataclass
class OrchestratorConfig:
    allowlist_paths: Iterable[str]
    logs_path: Path
    dry_run: bool = True


@dataclass
class OrchestratorState:
    mode: RunMode = RunMode.NORMAL
    last_redacted_path: Path | None = None
    guardrail: GuardrailDecision | None = None
    status: str = "idle"


class BridgeOrchestrator:
    def __init__(
        self,
        router: ModelRouter,
        ocr: OcrEngine,
        pii: PiiDetector,
        host_input: HostInputController,
        ghost_cursor: GhostCursorOverlay,
        vm_adapter: VmAdapter | None = None,
        config: OrchestratorConfig | None = None,
    ) -> None:
        self.router = router
        self.ocr = ocr
        self.pii = pii
        self.host_input = host_input
        self.ghost_cursor = ghost_cursor
        self.vm_adapter = vm_adapter or PlaceholderVmAdapter()
        self.config = config or OrchestratorConfig(
            allowlist_paths=["Documents", "Downloads"],
            logs_path=Path("logs/session.jsonl"),
        )
        self.state = OrchestratorState()

    def set_mode(self, mode: RunMode) -> None:
        self.state.mode = mode
        self.log_event("mode_change", {"mode": mode.value})

    def capture_and_redact(self) -> Path:
        frame = capture_screen()
        text_boxes = self.ocr.detect_text_boxes(frame)
        pii_boxes = self.pii.find_pii_boxes(text_boxes)
        redacted = redact_image(frame, pii_boxes)
        output_path = Path("logs/redacted_preview.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        redacted.save(output_path)
        self.state.last_redacted_path = output_path
        self.log_event("redacted_frame", {"path": str(output_path)})
        return output_path

    def dry_run_action(self, action: Action, rationale: str) -> GuardrailDecision:
        decision = assess_action(rationale, self.config.allowlist_paths)
        self.state.guardrail = decision
        self.log_event(
            "action_eval",
            {
                "action": action.action_type.value,
                "x": action.x,
                "y": action.y,
                "text": action.text,
                "decision": decision.__dict__,
            },
        )
        self.ghost_cursor.preview_action(action)
        return decision

    def execute_action(self, action: Action, rationale: str) -> GuardrailDecision:
        decision = self.dry_run_action(action, rationale)
        if self.config.dry_run or not decision.allowed:
            return decision
        if decision.requires_confirmation:
            return decision
        self.host_input.apply_action(action)
        self.log_event("action_executed", {"action": action.action_type.value})
        return decision

    def log_event(self, event: str, payload: dict) -> None:
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "payload": payload,
        }
        self.config.logs_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config.logs_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def vm_status(self) -> str:
        return self.vm_adapter.status()

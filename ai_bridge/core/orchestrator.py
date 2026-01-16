from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Protocol, TYPE_CHECKING

from ai_bridge.core.actions import Action, ActionType
from ai_bridge.core.cancellation import CancellationToken
from ai_bridge.core.modes import RunMode
from ai_bridge.core.router import ModelRouter
from ai_bridge.core.safety import GuardrailDecision, RiskLevel, assess_action
from ai_bridge.vision.ocr import OcrEngine
from ai_bridge.vision.pii import PiiDetector
from ai_bridge.vision.frame_types import RedactedFrame
from ai_bridge.vision.redact import redact_image
from ai_bridge.vm.adapter_base import VmAdapter
from ai_bridge.vm.adapter_placeholder import PlaceholderVmAdapter

if TYPE_CHECKING:
    from ai_bridge.input.ghost_cursor import GhostCursorOverlay
    from ai_bridge.input.host_input import HostInputController
    from ai_bridge.input.kill_switch import KillSwitchListener


class GhostCursorClient(Protocol):
    def preview_action(self, action: Action) -> None: ...


class HostInputClient(Protocol):
    def apply_action(self, action: Action) -> None: ...


class KillSwitchClient(Protocol):
    def start(self) -> None: ...

    def stop(self) -> None: ...


@dataclass
class OrchestratorConfig:
    allowlist_paths: Iterable[str]
    logs_path: Path
    dry_run: bool = True
    click_delay_ms: int = 350
    enable_kill_switch: bool = True


@dataclass
class OrchestratorState:
    mode: RunMode = RunMode.NORMAL
    last_redacted_path: Path | None = None
    last_redacted_frame: RedactedFrame | None = None
    guardrail: GuardrailDecision | None = None
    status: str = "idle"


class BridgeOrchestrator:
    def __init__(
        self,
        router: ModelRouter,
        ocr: OcrEngine,
        pii: PiiDetector,
        host_input: HostInputClient,
        ghost_cursor: GhostCursorClient,
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
        self.cancellation_token = CancellationToken.create()
        self.kill_switch: KillSwitchClient | None = None
        self._kill_switch_active = False
        if self.config.enable_kill_switch:
            from ai_bridge.input.kill_switch import KillSwitchListener

            self.kill_switch = KillSwitchListener(self.cancellation_token, self._handle_cancel)
            self._update_kill_switch()

    def set_mode(self, mode: RunMode) -> None:
        self.state.mode = mode
        self.log_event("mode_change", {"mode": mode.value})
        self._update_kill_switch()
        if mode == RunMode.NORMAL:
            self.reset_cancellation()

    def capture_and_redact(self) -> RedactedFrame:
        from ai_bridge.vision.capture import capture_screen

        frame = capture_screen()
        text_boxes = self.ocr.detect_text_boxes(frame)
        pii_boxes = self.pii.find_pii_boxes(text_boxes)
        redacted = redact_image(frame, pii_boxes)
        output_path = Path("logs/redacted_preview.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        redacted.save(str(output_path))
        self.state.last_redacted_path = output_path
        self.state.last_redacted_frame = redacted
        self.log_event(
            "redacted_frame",
            {
                "path": str(output_path),
                "ocr_boxes": len(text_boxes),
                "pii_boxes": len(pii_boxes),
                "redacted_boxes": [
                    {"left": box.left, "top": box.top, "width": box.width, "height": box.height}
                    for box in pii_boxes
                ],
            },
        )
        return redacted

    def describe_screen(self, prompt: str) -> str:
        if not self.state.last_redacted_frame:
            raise ValueError("No redacted frame available")
        return self.router.describe_screen(self.state.last_redacted_frame, prompt)

    def dry_run_action(self, action: Action, rationale: str) -> GuardrailDecision:
        decision = assess_action(rationale, self.config.allowlist_paths)
        self.state.guardrail = decision
        self.log_event(
            "action_eval",
            {
                "action": action.action_type.value,
                "x": action.x,
                "y": action.y,
                "text_length": len(action.text) if action.text else 0,
                "decision": {
                    "allowed": decision.allowed,
                    "requires_confirmation": decision.requires_confirmation,
                    "risk": decision.risk.value,
                    "reason": decision.reason,
                },
            },
        )
        self.ghost_cursor.preview_action(action)
        return decision

    def execute_action(self, action: Action, rationale: str, confirmed: bool = False) -> GuardrailDecision:
        if self.cancellation_token.is_cancelled():
            self.log_event("action_cancelled", {"reason": "kill_switch"})
            return GuardrailDecision(
                allowed=False,
                requires_confirmation=True,
                reason="Cancelled by user input",
                risk=RiskLevel.HIGH,
            )
        decision = self.dry_run_action(action, rationale)
        if self.config.dry_run or not decision.allowed:
            return decision
        if decision.requires_confirmation and not confirmed:
            self.log_event("action_confirmation_required", {"risk": decision.risk.value})
            return decision
        if self.state.mode != RunMode.NORMAL:
            self.vm_adapter.send_input(action)
            self.log_event("vm_action_executed", {"action": action.action_type.value})
            return decision
        if action.action_type == ActionType.CLICK:
            time.sleep(self.config.click_delay_ms / 1000)
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

    def _handle_cancel(self, reason: str) -> None:
        self.state.status = reason
        self.log_event("cancelled", {"reason": reason})

    def reset_cancellation(self) -> None:
        self.cancellation_token.reset()
        self.state.status = "idle"
        self.log_event("cancel_reset", {})

    def _update_kill_switch(self) -> None:
        if not self.kill_switch:
            return
        should_be_active = self.state.mode == RunMode.NORMAL
        if should_be_active and not self._kill_switch_active:
            self.kill_switch.start()
            self._kill_switch_active = True
        elif not should_be_active and self._kill_switch_active:
            self.kill_switch.stop()
            self._kill_switch_active = False

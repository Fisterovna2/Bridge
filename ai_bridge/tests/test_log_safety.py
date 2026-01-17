from pathlib import Path

from ai_bridge.core.actions import Action, ActionType
from ai_bridge.core.modes import RunMode
from ai_bridge.core.model_provider import RedactionGuardModelProvider, SimpleModelProvider
from ai_bridge.core.orchestrator import BridgeOrchestrator, OrchestratorConfig
from ai_bridge.core.router import ModelRouter
from ai_bridge.vision.ocr import OcrEngine
from ai_bridge.vision.pii import PiiDetector


class DummyHostInput:
    def apply_action(self, action: Action) -> None:
        return None


class DummyGhostCursor:
    def preview_action(self, action: Action) -> None:
        return None


def test_logs_do_not_store_raw_text(tmp_path: Path) -> None:
    router = ModelRouter(
        vision_provider=RedactionGuardModelProvider(SimpleModelProvider("test")),
        reasoner_provider=SimpleModelProvider("test"),
        executor_provider=SimpleModelProvider("test"),
    )
    logs_path = tmp_path / "session.jsonl"
    orchestrator = BridgeOrchestrator(
        router=router,
        ocr=OcrEngine(),
        pii=PiiDetector(),
        host_input=DummyHostInput(),
        ghost_cursor=DummyGhostCursor(),
        config=OrchestratorConfig(
            allowlist_paths=["Documents"],
            logs_path=logs_path,
            dry_run=True,
            enable_kill_switch=False,
        ),
    )
    orchestrator.set_mode(RunMode.NORMAL)
    action = Action(ActionType.TYPE, text="secret@example.com")
    orchestrator.dry_run_action(action, "Type secret@example.com in Documents")

    log_text = logs_path.read_text(encoding="utf-8")
    assert "secret@example.com" not in log_text
    assert "\"text\"" not in log_text

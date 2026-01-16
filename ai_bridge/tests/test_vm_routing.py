from ai_bridge.core.actions import Action, ActionType
from ai_bridge.core.modes import RunMode
from ai_bridge.core.orchestrator import BridgeOrchestrator, OrchestratorConfig
from ai_bridge.core.router import ModelRouter
from ai_bridge.core.model_provider import SimpleModelProvider, RedactionGuardModelProvider
from pathlib import Path
from ai_bridge.vision.ocr import OcrEngine
from ai_bridge.vision.pii import PiiDetector
from ai_bridge.vm.adapter_base import VmAdapter


class DummyHostInput:
    def __init__(self) -> None:
        self.called = False

    def apply_action(self, action: Action) -> None:
        self.called = True


class DummyVmAdapter(VmAdapter):
    def __init__(self) -> None:
        self.called = False

    def start_vm(self) -> None:
        return None

    def stop_vm(self) -> None:
        return None

    def snapshot_revert(self, snapshot_name: str | None = None) -> None:
        return None

    def get_frame(self):
        return None

    def send_input(self, action: Action) -> None:
        self.called = True

    def status(self) -> str:
        return "ok"

class DummyGhostCursor:
    def preview_action(self, action: Action) -> None:
        return None


def test_vm_mode_routes_input_to_vm(monkeypatch) -> None:
    router = ModelRouter(
        vision_provider=RedactionGuardModelProvider(SimpleModelProvider("test")),
        reasoner_provider=SimpleModelProvider("test"),
        executor_provider=SimpleModelProvider("test"),
    )
    host_input = DummyHostInput()
    vm_adapter = DummyVmAdapter()
    orchestrator = BridgeOrchestrator(
        router=router,
        ocr=OcrEngine(),
        pii=PiiDetector(),
        host_input=host_input,
        ghost_cursor=DummyGhostCursor(),
        vm_adapter=vm_adapter,
        config=OrchestratorConfig(
            allowlist_paths=["Documents"],
            logs_path=Path("logs/test.jsonl"),
            dry_run=False,
            enable_kill_switch=False,
        ),
    )
    orchestrator.set_mode(RunMode.GAME)
    action = Action(ActionType.TYPE, text="hello")
    orchestrator.execute_action(action, "Type in VM", confirmed=True)
    assert vm_adapter.called is True
    assert host_input.called is False

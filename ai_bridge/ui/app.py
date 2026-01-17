from __future__ import annotations

import importlib.util
import sys

from ai_bridge.core.model_provider import RedactionGuardModelProvider, SimpleModelProvider
from ai_bridge.core.modes import RunMode
from ai_bridge.core.router import ModelRouter
from ai_bridge.preflight import PreflightResult, run_preflight


def build_orchestrator():
    from ai_bridge.core.orchestrator import BridgeOrchestrator
    from ai_bridge.input.ghost_cursor import GhostCursorOverlay
    from ai_bridge.input.host_input import HostInputController
    from ai_bridge.vm.adapter_virtualbox import VirtualBoxAdapter
    from ai_bridge.vision.ocr import OcrEngine
    from ai_bridge.vision.pii import PiiDetector

    base_provider = SimpleModelProvider("mvp")
    backup_provider = SimpleModelProvider("backup")
    provider = RedactionGuardModelProvider(base_provider)
    router = ModelRouter(
        vision_provider=provider,
        reasoner_provider=base_provider,
        executor_provider=base_provider,
        per_mode_providers={
            RunMode.GAME: {
                "vision": [provider],
                "reasoner": [base_provider, backup_provider],
                "executor": [base_provider],
            },
            RunMode.SANDBOX: {
                "vision": [provider],
                "reasoner": [backup_provider, base_provider],
                "executor": [backup_provider, base_provider],
            },
        },
    )
    ocr = OcrEngine()
    pii = PiiDetector()
    host_input = HostInputController()
    ghost_cursor = GhostCursorOverlay()
    vm_adapter = VirtualBoxAdapter()
    return BridgeOrchestrator(router, ocr, pii, host_input, ghost_cursor, vm_adapter=vm_adapter)


def _show_preflight_warning(qt_widgets, result: PreflightResult) -> None:
    if result.is_ok:
        return
    message = "\n".join(result.messages)
    qt_widgets.QMessageBox.warning(None, "AI-Bridge preflight warning", message)


def main() -> int:
    if importlib.util.find_spec("PySide6") is None:
        print("Missing PySide6. Install with: pip install -r requirements.txt")
        return 1

    from PySide6 import QtWidgets
    from ai_bridge.ui.main_window import MainWindow

    app = QtWidgets.QApplication(sys.argv)
    preflight = run_preflight()
    _show_preflight_warning(QtWidgets, preflight)
    orchestrator = build_orchestrator()
    window = MainWindow(orchestrator)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import sys

from PySide6 import QtWidgets

from ai_bridge.core.orchestrator import BridgeOrchestrator
from ai_bridge.core.router import ModelRoleConfig, ModelRouter
from ai_bridge.input.ghost_cursor import GhostCursorOverlay
from ai_bridge.input.host_input import HostInputController
from ai_bridge.ui.main_window import MainWindow
from ai_bridge.vision.ocr import OcrEngine
from ai_bridge.vision.pii import PiiDetector


def build_orchestrator() -> BridgeOrchestrator:
    router = ModelRouter(
        vision=ModelRoleConfig("vision", "local", "mvp"),
        reasoner=ModelRoleConfig("reasoner", "local", "mvp"),
        executor=ModelRoleConfig("executor", "local", "mvp"),
    )
    ocr = OcrEngine()
    pii = PiiDetector()
    host_input = HostInputController()
    ghost_cursor = GhostCursorOverlay()
    return BridgeOrchestrator(router, ocr, pii, host_input, ghost_cursor)


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    orchestrator = build_orchestrator()
    window = MainWindow(orchestrator)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

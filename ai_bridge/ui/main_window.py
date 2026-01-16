from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtWidgets

from ai_bridge.core.actions import Action, ActionType
from ai_bridge.core.modes import RunMode
from ai_bridge.core.orchestrator import BridgeOrchestrator
from ai_bridge.ui.widgets import ImagePreview, LogConsole


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, orchestrator: BridgeOrchestrator) -> None:
        super().__init__()
        self.orchestrator = orchestrator
        self.setWindowTitle("AI-Bridge MVP")
        self.resize(980, 720)
        self._build_ui()

    def _build_ui(self) -> None:
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_modes_tab(), "Modes")
        tabs.addTab(self._build_models_tab(), "Models")
        tabs.addTab(self._build_privacy_tab(), "Privacy")
        tabs.addTab(self._build_logs_tab(), "Logs / Dev")
        tabs.addTab(self._build_vm_tab(), "VM")
        self.setCentralWidget(tabs)

    def _build_modes_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        self.preview = ImagePreview()

        button_row = QtWidgets.QHBoxLayout()
        for mode in (RunMode.NORMAL, RunMode.GAME, RunMode.SANDBOX):
            button = QtWidgets.QPushButton(mode.value.title())
            button.clicked.connect(lambda _, m=mode: self._set_mode(m))
            button_row.addWidget(button)

        capture_button = QtWidgets.QPushButton("Capture + Redact")
        capture_button.clicked.connect(self._capture_and_redact)
        demo_button = QtWidgets.QPushButton("Dry-run Demo Action")
        demo_button.clicked.connect(self._demo_action)

        layout.addLayout(button_row)
        layout.addWidget(capture_button)
        layout.addWidget(demo_button)
        layout.addWidget(self.preview)
        return widget

    def _build_models_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        self.vision_model = QtWidgets.QLineEdit("local/vision")
        self.reasoner_model = QtWidgets.QLineEdit("local/reasoner")
        self.executor_model = QtWidgets.QLineEdit("local/executor")
        layout.addRow("Vision model", self.vision_model)
        layout.addRow("Reasoner model", self.reasoner_model)
        layout.addRow("Executor model", self.executor_model)
        return widget

    def _build_privacy_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        self.pii_words = QtWidgets.QPlainTextEdit("secret\nconfidential")
        layout.addWidget(QtWidgets.QLabel("Blocked keywords"))
        layout.addWidget(self.pii_words)
        return widget

    def _build_logs_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        self.log_console = LogConsole()
        self.dry_run_toggle = QtWidgets.QCheckBox("Dry-run (simulate input)")
        self.dry_run_toggle.setChecked(True)
        self.dry_run_toggle.toggled.connect(self._toggle_dry_run)
        export_button = QtWidgets.QPushButton("Export logs")
        export_button.clicked.connect(self._export_logs)
        layout.addWidget(self.dry_run_toggle)
        layout.addWidget(export_button)
        layout.addWidget(self.log_console)
        return widget

    def _build_vm_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        self.vm_status = QtWidgets.QLabel("VM adapter not configured")
        start_button = QtWidgets.QPushButton("Start VM")
        stop_button = QtWidgets.QPushButton("Stop VM")
        revert_button = QtWidgets.QPushButton("Revert snapshot")
        start_button.clicked.connect(self._vm_start)
        stop_button.clicked.connect(self._vm_stop)
        revert_button.clicked.connect(self._vm_revert)
        layout.addWidget(self.vm_status)
        layout.addWidget(start_button)
        layout.addWidget(stop_button)
        layout.addWidget(revert_button)
        return widget

    def _set_mode(self, mode: RunMode) -> None:
        self.orchestrator.set_mode(mode)
        self.log_console.append_line(f"Mode set to {mode.value}")

    def _capture_and_redact(self) -> None:
        path = self.orchestrator.capture_and_redact()
        self.preview.set_image(str(path))
        self.log_console.append_line(f"Redacted preview saved: {path}")

    def _demo_action(self) -> None:
        action = Action(ActionType.CLICK, x=320, y=240)
        decision = self.orchestrator.execute_action(action, "Click demo in Documents")
        self.log_console.append_line(f"Dry-run action: {decision.reason}")

    def _toggle_dry_run(self, checked: bool) -> None:
        self.orchestrator.config.dry_run = checked
        self.log_console.append_line(f"Dry-run set to {checked}")

    def _export_logs(self) -> None:
        target = QtWidgets.QFileDialog.getSaveFileName(self, "Export logs", "session.jsonl")[0]
        if not target:
            return
        source = self.orchestrator.config.logs_path
        if source.exists():
            Path(target).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            self.log_console.append_line(f"Logs exported to {target}")
        else:
            self.log_console.append_line("No logs to export")

    def _vm_start(self) -> None:
        self.orchestrator.vm_adapter.start_vm()
        self._update_vm_status()

    def _vm_stop(self) -> None:
        self.orchestrator.vm_adapter.stop_vm()
        self._update_vm_status()

    def _vm_revert(self) -> None:
        self.orchestrator.vm_adapter.snapshot_revert()
        self._update_vm_status()

    def _update_vm_status(self) -> None:
        self.vm_status.setText(self.orchestrator.vm_status())

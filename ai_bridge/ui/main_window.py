from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtWidgets

from ai_bridge.core.actions import Action, ActionType
from ai_bridge.core.modes import RunMode
from ai_bridge.core.orchestrator import BridgeOrchestrator
from ai_bridge.ui.widgets import ImagePreview, LogConsole
from ai_bridge import __version__
from ai_bridge.tools.selfcheck import run_selfcheck
from ai_bridge.game.calibration import compute_calibration
from ai_bridge.game.loop import GameLoop, GameProfile


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, orchestrator: BridgeOrchestrator) -> None:
        super().__init__()
        self.orchestrator = orchestrator
        self.setWindowTitle("AI-Bridge MVP")
        self.resize(980, 720)
        self.game_loop = None
        self._build_ui()
        self._status_timer = QtCore.QTimer(self)
        self._status_timer.timeout.connect(self._refresh_status)
        self._status_timer.start(250)

    def _build_ui(self) -> None:
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_modes_tab(), "Modes")
        tabs.addTab(self._build_models_tab(), "Models")
        tabs.addTab(self._build_privacy_tab(), "Privacy")
        tabs.addTab(self._build_logs_tab(), "Logs / Dev")
        tabs.addTab(self._build_vm_tab(), "VM")
        tabs.addTab(self._build_selfcheck_tab(), "Self-check")
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
        self.game_profile = QtWidgets.QComboBox()
        self.game_profile.addItems(["default", "shooter"])
        self.game_metrics = QtWidgets.QLabel("Game loop metrics: idle")
        start_loop_button = QtWidgets.QPushButton("Start Game Loop (VM)")
        stop_loop_button = QtWidgets.QPushButton("Stop Game Loop")
        start_loop_button.clicked.connect(self._start_game_loop)
        stop_loop_button.clicked.connect(self._stop_game_loop)

        layout.addLayout(button_row)
        layout.addWidget(capture_button)
        layout.addWidget(demo_button)
        layout.addWidget(QtWidgets.QLabel("Game profile"))
        layout.addWidget(self.game_profile)
        layout.addWidget(start_loop_button)
        layout.addWidget(stop_loop_button)
        layout.addWidget(self.game_metrics)
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
        reset_cancel_button = QtWidgets.QPushButton("Reset cancellation")
        reset_cancel_button.clicked.connect(self._reset_cancellation)
        about_button = QtWidgets.QPushButton("About")
        about_button.clicked.connect(self._show_about)
        self.status_label = QtWidgets.QLabel("Status: idle")
        layout.addWidget(self.status_label)
        layout.addWidget(self.dry_run_toggle)
        layout.addWidget(reset_cancel_button)
        layout.addWidget(about_button)
        layout.addWidget(export_button)
        layout.addWidget(self.log_console)
        return widget

    def _build_vm_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        self.vm_status = QtWidgets.QLabel(self.orchestrator.vm_status())
        start_button = QtWidgets.QPushButton("Start VM")
        stop_button = QtWidgets.QPushButton("Stop VM")
        revert_button = QtWidgets.QPushButton("Revert snapshot")
        demo_button = QtWidgets.QPushButton("Run VM demo")
        start_button.clicked.connect(self._vm_start)
        stop_button.clicked.connect(self._vm_stop)
        revert_button.clicked.connect(self._vm_revert)
        demo_button.clicked.connect(self._vm_demo)
        layout.addWidget(self.vm_status)
        layout.addWidget(start_button)
        layout.addWidget(stop_button)
        layout.addWidget(revert_button)
        layout.addWidget(demo_button)
        return widget

    def _build_selfcheck_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        self.selfcheck_output = QtWidgets.QPlainTextEdit()
        self.selfcheck_output.setReadOnly(True)
        run_button = QtWidgets.QPushButton("Run self-check")
        run_button.clicked.connect(self._run_selfcheck)
        layout.addWidget(run_button)
        layout.addWidget(self.selfcheck_output)
        return widget

    def _set_mode(self, mode: RunMode) -> None:
        self.orchestrator.set_mode(mode)
        self.log_console.append_line(f"Mode set to {mode.value}")

    def _capture_and_redact(self) -> None:
        redacted = self.orchestrator.capture_and_redact()
        if self.orchestrator.state.last_redacted_path:
            self.preview.set_image(str(self.orchestrator.state.last_redacted_path))
            self.log_console.append_line(
                f"Redacted preview saved: {self.orchestrator.state.last_redacted_path}"
            )
        else:
            self.log_console.append_line("Redacted frame ready")

    def _demo_action(self) -> None:
        action = Action(ActionType.CLICK, x=320, y=240)
        decision = self.orchestrator.execute_action(action, "Click demo in Documents")
        if decision.requires_confirmation and not self.orchestrator.config.dry_run:
            confirmed = self._confirm_action(decision)
            if confirmed:
                decision = self.orchestrator.execute_action(
                    action,
                    "Click demo in Documents",
                    confirmed=True,
                )
        self.log_console.append_line(f"Action eval: {decision.reason}")

    def _confirm_action(self, decision) -> bool:
        message = (
            f"{decision.reason}\n"
            f"Risk: {decision.risk.value}\n"
            f"Rule: {decision.rule_id}\n"
            f"Target: {decision.target}\n"
            f"Mode: {decision.mode.value}\n\nConfirm action?"
        )
        result = QtWidgets.QMessageBox.question(
            self,
            "Confirm action",
            message,
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
        )
        return result == QtWidgets.QMessageBox.StandardButton.Yes

    def _toggle_dry_run(self, checked: bool) -> None:
        self.orchestrator.config.dry_run = checked
        self.log_console.append_line(f"Dry-run set to {checked}")

    def _reset_cancellation(self) -> None:
        self.orchestrator.reset_cancellation()
        self.log_console.append_line("Cancellation reset")

    def _show_about(self) -> None:
        QtWidgets.QMessageBox.information(
            self,
            "About AI-Bridge",
            f"AI-Bridge MVP\nVersion: {__version__}",
        )

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
        self._run_vm_action(self.orchestrator.vm_adapter.start_vm)

    def _vm_stop(self) -> None:
        self._run_vm_action(self.orchestrator.vm_adapter.stop_vm)

    def _vm_revert(self) -> None:
        self._run_vm_action(self.orchestrator.vm_adapter.snapshot_revert)

    def _vm_demo(self) -> None:
        def _demo() -> None:
            self.orchestrator.set_mode(RunMode.SANDBOX)
            self.orchestrator.vm_adapter.snapshot_revert("clean")
            self.orchestrator.vm_adapter.start_vm()
            frame = self.orchestrator.vm_adapter.get_frame()
            if frame:
                frame_path = Path("logs/vm_demo.png")
                frame_path.parent.mkdir(parents=True, exist_ok=True)
                frame.save(frame_path)
                self.preview.set_image(str(frame_path))
                self.log_console.append_line(f"VM frame saved: {frame_path}")
            self.orchestrator.ghost_cursor.preview_action(Action(ActionType.MOVE, x=300, y=200))
            self.orchestrator.vm_adapter.send_input(
                Action(ActionType.TYPE, text="hello from AI Bridge\n")
            )
            self.log_console.append_line("VM demo input sent.")

        self._run_vm_action(_demo)

    def _update_vm_status(self) -> None:
        self.vm_status.setText(self.orchestrator.vm_status())

    def _refresh_status(self) -> None:
        mode = self.orchestrator.state.mode.value
        self.status_label.setText(f"Status: {self.orchestrator.state.status} | Mode: {mode}")
        if hasattr(self, "game_loop") and self.game_loop:
            metrics = self.game_loop.metrics.snapshot()
            self.game_metrics.setText(
                "Game loop metrics: "
                f"frame {metrics['frame_time_ms']:.1f}ms, "
                f"decision {metrics['decision_time_ms']:.1f}ms, "
                f"input {metrics['input_time_ms']:.1f}ms"
            )

    def _run_vm_action(self, action) -> None:
        try:
            action()
        except RuntimeError as exc:
            self.log_console.append_line(f"VM error: {exc}")
        finally:
            self._update_vm_status()

    def _run_selfcheck(self) -> None:
        report = run_selfcheck()
        self.selfcheck_output.setPlainText("\n".join(report.format_lines()))

    def _start_game_loop(self) -> None:
        self.orchestrator.set_mode(RunMode.GAME)
        profile_name = self.game_profile.currentText()
        profile = GameProfile(name=profile_name, resolution=(1280, 720))
        calibration = compute_calibration(
            frame_width=profile.resolution[0],
            frame_height=profile.resolution[1],
            vm_width=profile.resolution[0],
            vm_height=profile.resolution[1],
        )
        self.game_loop = GameLoop(
            adapter=self.orchestrator.vm_adapter,
            ghost_cursor=self.orchestrator.ghost_cursor.preview_action,
            cancellation=self.orchestrator.cancellation_token,
            dry_run=self.orchestrator.config.dry_run,
            calibration=calibration,
        )
        self.game_loop.start()
        self.log_console.append_line("Game loop started (VM-only).")

    def _stop_game_loop(self) -> None:
        if hasattr(self, "game_loop") and self.game_loop:
            self.game_loop.stop()
            self.log_console.append_line("Game loop stopped.")

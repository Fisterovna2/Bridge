from __future__ import annotations

import json
import sys
from pathlib import Path

from ai_bridge.core.actions import Action, ActionType


def _load_actions(path: Path) -> list[Action]:
    actions: list[Action] = []
    if not path.exists():
        return actions
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        payload = record.get("payload", {})
        action_type = payload.get("action")
        if action_type in {ActionType.MOVE.value, ActionType.CLICK.value}:
            actions.append(
                Action(
                    ActionType(action_type),
                    x=payload.get("x"),
                    y=payload.get("y"),
                )
            )
    return actions


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python -m ai_bridge.tools.replay <session_dir>")
        return 1
    session_dir = Path(sys.argv[1])
    actions = _load_actions(session_dir / "actions.jsonl")
    if not actions:
        print("No actions found to replay.")
        return 0
    try:
        from PySide6 import QtCore, QtWidgets
        from ai_bridge.input.ghost_cursor import GhostCursorOverlay
    except ImportError:
        print("PySide6 not available. Replay requires a GUI environment.")
        return 1

    app = QtWidgets.QApplication(sys.argv)
    ghost = GhostCursorOverlay()
    index = {"value": 0}

    def step() -> None:
        if index["value"] >= len(actions):
            app.quit()
            return
        ghost.preview_action(actions[index["value"]])
        index["value"] += 1

    timer = QtCore.QTimer()
    timer.timeout.connect(step)
    timer.start(200)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

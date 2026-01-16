from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from ai_bridge.core.actions import Action, ActionType


class GhostCursorOverlay(QtWidgets.QWidget):
    status_changed = QtCore.Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._status = "idle"
        self._target = QtCore.QPoint(100, 100)
        self._pos = QtCore.QPoint(100, 100)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.Tool
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(QtWidgets.QApplication.primaryScreen().size())
        self.show()

    def preview_action(self, action: Action) -> None:
        if action.x is None or action.y is None:
            return
        self._target = QtCore.QPoint(action.x, action.y)
        if action.action_type == ActionType.CLICK:
            self.set_status("clicking")
        elif action.action_type == ActionType.MOVE:
            self.set_status("moving")
        else:
            self.set_status("thinking")

    def set_status(self, status: str) -> None:
        if status != self._status:
            self._status = status
            self.status_changed.emit(status)
            self.update()

    def _tick(self) -> None:
        delta = self._target - self._pos
        step = QtCore.QPoint(int(delta.x() * 0.2), int(delta.y() * 0.2))
        if step.manhattanLength() == 0:
            return
        self._pos += step
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        color = QtGui.QColor(0, 200, 255, 180)
        if self._status == "clicking":
            color = QtGui.QColor(255, 120, 0, 200)
        elif self._status == "thinking":
            color = QtGui.QColor(120, 120, 255, 160)
        painter.setPen(QtGui.QPen(color, 2))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
        painter.drawEllipse(self._pos, 12, 12)
        painter.drawLine(self._pos + QtCore.QPoint(16, 0), self._pos + QtCore.QPoint(28, 0))
        painter.drawLine(self._pos + QtCore.QPoint(0, 16), self._pos + QtCore.QPoint(0, 28))

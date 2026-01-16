from __future__ import annotations

from typing import Optional, Tuple

# ВАЖНО: PySide6 может падать в headless CI из-за отсутствия libEGL.so.1.
# Поэтому импортируем безопасно и делаем no-op fallback.
_PYSIDE_OK = False
_PYSIDE_ERR: Optional[BaseException] = None

try:
    from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore

    _PYSIDE_OK = True
except BaseException as e:  # ловим и ImportError, и OSError (libEGL.so.1)
    _PYSIDE_OK = False
    _PYSIDE_ERR = e


class GhostCursorOverlay:
    """
    Ghost cursor overlay used for demo/dry-run visualization.

    In headless environments (CI), PySide6 may be unavailable or fail to load
    (e.g. missing libEGL.so.1). In that case this becomes a no-op implementation
    so imports/tests do not crash.
    """

    def __init__(self) -> None:
        self._enabled = _PYSIDE_OK
        self._pos: Tuple[int, int] = (0, 0)

        # Real implementation only if PySide6 loaded successfully
        if not self._enabled:
            return

        self._app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        self._window = _GhostCursorWindow()
        self._window.hide()

    @property
    def available(self) -> bool:
        return self._enabled

    def start(self) -> None:
        if not self._enabled:
            return
        self._window.show()

    def stop(self) -> None:
        if not self._enabled:
            return
        self._window.hide()

    def move_to(self, x: int, y: int) -> None:
        self._pos = (int(x), int(y))
        if not self._enabled:
            return

        self._window.move_cursor(self._pos[0], self._pos[1])

    def explain_unavailable(self) -> str:
        if self._enabled:
            return "Ghost cursor overlay is available."
        return f"Ghost cursor overlay is unavailable in this environment: {_PYSIDE_ERR!r}"


if _PYSIDE_OK:

    class _GhostCursorWindow(QtWidgets.QWidget):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowFlags(
                QtCore.Qt.FramelessWindowHint
                | QtCore.Qt.WindowStaysOnTopHint
                | QtCore.Qt.Tool
            )
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
            self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

            self._x = 0
            self._y = 0
            self.resize(32, 32)

        def move_cursor(self, x: int, y: int) -> None:
            self._x = x
            self._y = y
            self.move(self._x, self._y)
            self.update()

        def paintEvent(self, event: QtGui.QPaintEvent) -> None:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            pen = QtGui.QPen(QtGui.QColor(0, 255, 255, 200))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 255, 255, 80)))

            r = self.rect().adjusted(4, 4, -4, -4)
            painter.drawEllipse(r)

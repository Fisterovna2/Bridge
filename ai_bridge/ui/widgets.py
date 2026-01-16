from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets


class LogConsole(QtWidgets.QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumBlockCount(5000)

    def append_line(self, line: str) -> None:
        self.appendPlainText(line)


class ImagePreview(QtWidgets.QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(240)
        self.setStyleSheet("border: 1px solid #3a3a3a;")

    def set_image(self, path: str) -> None:
        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            self.setText("No preview")
            return
        self.setPixmap(pixmap.scaled(self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if self.pixmap():
            self.setPixmap(self.pixmap().scaled(self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        super().resizeEvent(event)

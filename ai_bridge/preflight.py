from __future__ import annotations

import importlib.util
import shutil
from dataclasses import dataclass, field
from typing import List


@dataclass
class PreflightResult:
    is_ok: bool
    messages: List[str] = field(default_factory=list)


def run_preflight() -> PreflightResult:
    messages: List[str] = []
    if importlib.util.find_spec("pytesseract") is None:
        messages.append("Missing pytesseract. Install with: pip install -r requirements.txt")
    if shutil.which("tesseract") is None:
        messages.append(
            "Tesseract binary not found. Install Tesseract and ensure it is on PATH."
        )
    return PreflightResult(is_ok=not messages, messages=messages)


def check_gui_dependency() -> PreflightResult:
    messages: List[str] = []
    if importlib.util.find_spec("PySide6") is None:
        messages.append("Missing PySide6. Install with: pip install -r requirements.txt")
    return PreflightResult(is_ok=not messages, messages=messages)

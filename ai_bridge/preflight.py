from __future__ import annotations

import importlib.util
import shutil
import subprocess
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
    if shutil.which("VBoxManage") is None:
        messages.append(
            "VBoxManage not found. Install VirtualBox and ensure VBoxManage is on PATH "
            "to enable VM control."
        )
    else:
        try:
            result = subprocess.run(
                ["VBoxManage", "list", "extpacks"],
                check=False,
                capture_output=True,
                text=True,
            )
            if "Extension Packs: 0" in result.stdout:
                messages.append(
                    "VirtualBox Extension Pack not found. VRDE/RDP may be unavailable."
                )
        except OSError:
            messages.append("Unable to query VirtualBox Extension Pack status.")
    return PreflightResult(is_ok=not messages, messages=messages)


def check_gui_dependency() -> PreflightResult:
    messages: List[str] = []
    if importlib.util.find_spec("PySide6") is None:
        messages.append("Missing PySide6. Install with: pip install -r requirements.txt")
    return PreflightResult(is_ok=not messages, messages=messages)

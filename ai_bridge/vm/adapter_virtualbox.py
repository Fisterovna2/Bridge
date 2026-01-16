from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image

from ai_bridge.core.actions import Action, ActionType
from ai_bridge.vm.adapter_base import VmAdapter


SCAN_CODE_MAP = {
    "a": 0x1E,
    "b": 0x30,
    "c": 0x2E,
    "d": 0x20,
    "e": 0x12,
    "f": 0x21,
    "g": 0x22,
    "h": 0x23,
    "i": 0x17,
    "j": 0x24,
    "k": 0x25,
    "l": 0x26,
    "m": 0x32,
    "n": 0x31,
    "o": 0x18,
    "p": 0x19,
    "q": 0x10,
    "r": 0x13,
    "s": 0x1F,
    "t": 0x14,
    "u": 0x16,
    "v": 0x2F,
    "w": 0x11,
    "x": 0x2D,
    "y": 0x15,
    "z": 0x2C,
    " ": 0x39,
    "\n": 0x1C,
}


@dataclass
class VirtualBoxAdapter(VmAdapter):
    vm_name: str = "AI-Bridge"
    snapshot_name: str = "clean"
    vboxmanage_path: str | None = None
    frame_path: Path = Path("logs/vm_frame.png")

    def __post_init__(self) -> None:
        if not self.vboxmanage_path:
            self.vboxmanage_path = shutil.which("VBoxManage")
        self._state = "stopped"
        self._status = self._initial_status()

    def start_vm(self) -> None:
        self._run("startvm", self.vm_name, "--type", "headless")
        self._state = "running"
        self._status = "Running"

    def stop_vm(self) -> None:
        self._run("controlvm", self.vm_name, "poweroff")
        self._state = "stopped"
        self._status = "Stopped"

    def snapshot_revert(self, snapshot_name: str | None = None) -> None:
        target = snapshot_name or self.snapshot_name
        self._status = f"Reverting to snapshot '{target}'"
        self._run("snapshot", self.vm_name, "restore", target)
        self._status = f"Reverted to snapshot '{target}'"

    def get_frame(self) -> Image.Image | None:
        self.frame_path.parent.mkdir(parents=True, exist_ok=True)
        self._run("controlvm", self.vm_name, "screenshotpng", str(self.frame_path))
        if not self.frame_path.exists():
            self._status = "Failed to capture frame"
            return None
        self._status = f"Frame captured: {self.frame_path}"
        return Image.open(self.frame_path)

    def send_input(self, action: Action) -> None:
        if action.action_type == ActionType.TYPE and action.text:
            self._type_text(action.text)
            self._status = "Typed text in VM"
            return
        if action.action_type == ActionType.MOVE and action.x is not None and action.y is not None:
            self._mouse_move(action.x, action.y)
            self._status = "Moved mouse in VM"
            return
        if action.action_type == ActionType.CLICK and action.x is not None and action.y is not None:
            self._mouse_click(action.x, action.y)
            self._status = "Clicked in VM"
            return
        self._status = f"Input ignored: {action.action_type.value}"

    def status(self) -> str:
        return f"{self._status} (state: {self._state})"

    def _run(self, *args: str) -> None:
        if not self.vboxmanage_path:
            self._status = "VBoxManage not found. Install VirtualBox and add to PATH."
            raise RuntimeError(self._status)
        command = [self.vboxmanage_path, *args]
        subprocess.run(command, check=True, capture_output=True)

    def _initial_status(self) -> str:
        if not self.vboxmanage_path:
            return "VBoxManage not found. Install VirtualBox and add to PATH."
        return "Ready"

    def _type_text(self, text: str) -> None:
        for char in text:
            self._send_scancode(char.lower())

    def _send_scancode(self, char: str) -> None:
        code = SCAN_CODE_MAP.get(char)
        if code is None:
            return
        self._run(
            "controlvm",
            self.vm_name,
            "keyboardputscancode",
            f"{code:02x}",
            f"{code | 0x80:02x}",
        )

    def _mouse_move(self, x: int, y: int) -> None:
        self._run("controlvm", self.vm_name, "mouseputstate", str(x), str(y), "0")

    def _mouse_click(self, x: int, y: int) -> None:
        self._run("controlvm", self.vm_name, "mouseputstate", str(x), str(y), "1")
        self._run("controlvm", self.vm_name, "mouseputstate", str(x), str(y), "0")

from __future__ import annotations

import socket
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from PIL import Image

from ai_bridge.core.actions import Action, ActionType
from ai_bridge.vm.adapter_base import VmAdapter
from ai_bridge.core.selfcheck_types import CheckResult


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
        self._vrde_port: int | None = None

    def start_vm(self) -> None:
        if not self._vm_exists():
            raise RuntimeError(
                f"VM '{self.vm_name}' not found. Create the VM or update config."
            )
        self._enforce_network()
        self._run("startvm", self.vm_name, "--type", "headless")
        self._state = "running"
        self._status = "Running"

    def stop_vm(self) -> None:
        self._run("controlvm", self.vm_name, "poweroff")
        self._state = "stopped"
        self._status = "Stopped"

    def snapshot_revert(self, snapshot_name: str | None = None) -> None:
        target = snapshot_name or self.snapshot_name
        if not self._snapshot_exists(target):
            raise RuntimeError(
                f"Snapshot '{target}' not found. Create the snapshot before reverting."
            )
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

    def selfcheck(self) -> List[CheckResult]:
        results: List[CheckResult] = []
        if not self.vboxmanage_path:
            return [
                CheckResult(
                    name="VirtualBox",
                    passed=False,
                    detail="VBoxManage not found",
                    fix="Install VirtualBox and add VBoxManage to PATH",
                )
            ]
        results.append(
            CheckResult(
                name="VirtualBox",
                passed=True,
                detail=f"VBoxManage at {self.vboxmanage_path}",
            )
        )
        vm_exists = self._vm_exists()
        results.append(
            CheckResult(
                name="VM exists",
                passed=vm_exists,
                detail=self.vm_name if vm_exists else f"{self.vm_name} not found",
                fix="Create a VM with the configured name",
            )
        )
        snapshot_ok = self._snapshot_exists(self.snapshot_name)
        results.append(
            CheckResult(
                name="Snapshot",
                passed=snapshot_ok,
                detail=self.snapshot_name if snapshot_ok else f"{self.snapshot_name} missing",
                fix=f"Create snapshot '{self.snapshot_name}'",
            )
        )
        vrde_enabled, vrde_port = self._vrde_info()
        results.append(
            CheckResult(
                name="VRDE",
                passed=vrde_enabled,
                detail="enabled" if vrde_enabled else "disabled",
                fix="Install VirtualBox Extension Pack and enable VRDE",
            )
        )
        if vrde_enabled and vrde_port:
            reachable = self._check_port("127.0.0.1", vrde_port)
            results.append(
                CheckResult(
                    name="VRDE port",
                    passed=reachable,
                    detail=f"{vrde_port}" if reachable else f"{vrde_port} unreachable",
                    fix="Ensure VRDE is enabled and port is not blocked",
                )
            )
        network_ok, network_mode = self._network_mode()
        results.append(
            CheckResult(
                name="Network mode",
                passed=network_ok,
                detail=network_mode,
                fix="Set adapter to NAT or Host-only (avoid Bridged)",
            )
        )
        return results

    def _run(self, *args: str) -> None:
        if not self.vboxmanage_path:
            self._status = "VBoxManage not found. Install VirtualBox and add to PATH."
            raise RuntimeError(self._status)
        command = [self.vboxmanage_path, *args]
        subprocess.run(command, check=True, capture_output=True)

    def _run_output(self, *args: str) -> str:
        if not self.vboxmanage_path:
            self._status = "VBoxManage not found. Install VirtualBox and add to PATH."
            raise RuntimeError(self._status)
        command = [self.vboxmanage_path, *args]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        return result.stdout

    def _initial_status(self) -> str:
        if not self.vboxmanage_path:
            return "VBoxManage not found. Install VirtualBox and add to PATH."
        return "Ready"

    def _vm_exists(self) -> bool:
        output = self._run_output("list", "vms")
        return f"\"{self.vm_name}\"" in output

    def _snapshot_exists(self, snapshot_name: str) -> bool:
        output = self._run_output("snapshot", self.vm_name, "list")
        return snapshot_name in output

    def _vrde_info(self) -> tuple[bool, int | None]:
        output = self._run_output("showvminfo", self.vm_name, "--machinereadable")
        enabled = "VRDEEnabled=\"on\"" in output
        port = None
        for line in output.splitlines():
            if line.startswith("VRDEPort="):
                _, value = line.split("=", 1)
                try:
                    port = int(value.strip().strip("\""))
                except ValueError:
                    port = None
        self._vrde_port = port
        return enabled, port

    def _network_mode(self) -> tuple[bool, str]:
        output = self._run_output("showvminfo", self.vm_name, "--machinereadable")
        mode = "unknown"
        for line in output.splitlines():
            if line.startswith("nic1="):
                _, value = line.split("=", 1)
                mode = value.strip().strip("\"")
                break
        if mode in {"nat", "hostonly"}:
            return True, mode
        return False, mode

    def _enforce_network(self) -> None:
        ok, mode = self._network_mode()
        if not ok:
            raise RuntimeError(
                f"Unsupported network mode '{mode}'. Use NAT or Host-only for VM isolation."
            )

    def _check_port(self, host: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            return sock.connect_ex((host, port)) == 0

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

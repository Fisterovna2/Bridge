from __future__ import annotations

from ai_bridge.core.actions import Action
from ai_bridge.vm.adapter_base import VmAdapter


class PlaceholderVmAdapter(VmAdapter):
    def __init__(self) -> None:
        self._status = self._build_status()

    def start_vm(self) -> None:
        self._status = "Start requested (no-op). Configure a VM adapter first."

    def stop_vm(self) -> None:
        self._status = "Stop requested (no-op). Configure a VM adapter first."

    def snapshot_revert(self) -> None:
        self._status = "Revert requested (no-op). Configure a VM adapter first."

    def get_frame(self) -> bytes | None:
        return None

    def send_input(self, action: Action) -> None:
        self._status = f"Input ignored: {action.action_type.value}. Configure a VM adapter first."

    def status(self) -> str:
        return self._status

    def _build_status(self) -> str:
        return (
            "VM adapter not configured. Checklist: "
            "1) Choose VirtualBox or QEMU/KVM. "
            "2) Enable RDP/VNC. "
            "3) Map snapshot revert command. "
            "4) Set adapter in config."
        )

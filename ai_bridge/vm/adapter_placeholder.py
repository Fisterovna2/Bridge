from __future__ import annotations

from ai_bridge.core.actions import Action
from ai_bridge.vm.adapter_base import VmAdapter


class PlaceholderVmAdapter(VmAdapter):
    def __init__(self) -> None:
        self._status = "VM adapter not configured"

    def start_vm(self) -> None:
        self._status = "start requested (no-op)"

    def stop_vm(self) -> None:
        self._status = "stop requested (no-op)"

    def snapshot_revert(self) -> None:
        self._status = "revert requested (no-op)"

    def get_frame(self) -> bytes | None:
        return None

    def send_input(self, action: Action) -> None:
        self._status = f"input ignored: {action.action_type.value}"

    def status(self) -> str:
        return self._status

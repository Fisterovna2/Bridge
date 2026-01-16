from __future__ import annotations

from ai_bridge.core.actions import Action
from ai_bridge.vm.adapter_base import VmAdapter


class VmInputController:
    def __init__(self, adapter: VmAdapter) -> None:
        self.adapter = adapter

    def send(self, action: Action) -> None:
        self.adapter.send_input(action)

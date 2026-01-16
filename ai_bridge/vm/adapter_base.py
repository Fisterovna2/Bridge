from __future__ import annotations

from abc import ABC, abstractmethod

from ai_bridge.core.actions import Action


class VmAdapter(ABC):
    @abstractmethod
    def start_vm(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_vm(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def snapshot_revert(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_frame(self) -> bytes | None:
        raise NotImplementedError

    @abstractmethod
    def send_input(self, action: Action) -> None:
        raise NotImplementedError

    @abstractmethod
    def status(self) -> str:
        raise NotImplementedError

from __future__ import annotations

from abc import ABC, abstractmethod

from PIL import Image

from ai_bridge.core.actions import Action


class VmAdapter(ABC):
    @abstractmethod
    def start_vm(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_vm(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def snapshot_revert(self, snapshot_name: str | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_frame(self) -> Image.Image | None:
        raise NotImplementedError

    @abstractmethod
    def send_input(self, action: Action) -> None:
        raise NotImplementedError

    @abstractmethod
    def status(self) -> str:
        raise NotImplementedError

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ai_bridge.vision.frame_types import RedactedFrame


class ModelProvider(ABC):
    @abstractmethod
    def describe(self, frame: RedactedFrame, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def plan(self, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def execute(self, prompt: str) -> str:
        raise NotImplementedError


@dataclass
class SimpleModelProvider(ModelProvider):
    name: str

    def describe(self, frame: RedactedFrame, prompt: str) -> str:
        return f"[{self.name}] {prompt}"

    def plan(self, prompt: str) -> str:
        return f"[{self.name}] {prompt}"

    def execute(self, prompt: str) -> str:
        return f"[{self.name}] {prompt}"


class RedactionGuardModelProvider(ModelProvider):
    def __init__(self, inner: ModelProvider) -> None:
        self.inner = inner

    def describe(self, frame: RedactedFrame, prompt: str) -> str:
        if not frame.redacted:
            raise ValueError("Frame must be redacted before model use")
        return self.inner.describe(frame, prompt)

    def plan(self, prompt: str) -> str:
        return self.inner.plan(prompt)

    def execute(self, prompt: str) -> str:
        return self.inner.execute(prompt)

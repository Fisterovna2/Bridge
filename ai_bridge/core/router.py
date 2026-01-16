from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ai_bridge.core.model_provider import ModelProvider
from ai_bridge.core.modes import RunMode
from ai_bridge.vision.frame_types import RedactedFrame


@dataclass
class ModelRoleConfig:
    name: str
    provider: str
    model: str


class ModelRouter:
    def __init__(
        self,
        vision_provider: ModelProvider | None = None,
        reasoner_provider: ModelProvider | None = None,
        executor_provider: ModelProvider | None = None,
        **kwargs: ModelProvider,
    ) -> None:
        self.vision_provider = vision_provider or kwargs.get("vision_provider")
        self.reasoner_provider = reasoner_provider or kwargs.get("reasoner_provider")
        self.executor_provider = executor_provider or kwargs.get("executor_provider")
        self.per_mode_providers: dict[RunMode, dict[str, list[ModelProvider]]] = kwargs.get(
            "per_mode_providers", {}
        )
        if not self.vision_provider or not self.reasoner_provider or not self.executor_provider:
            raise ValueError("ModelRouter requires vision_provider, reasoner_provider, executor_provider")

    def describe_screen(self, frame: RedactedFrame, prompt: str, mode: RunMode | None = None) -> str:
        providers = self._providers_for("vision", mode) or [self.vision_provider]
        return self._call_with_fallback([lambda p=p: p.describe(frame, prompt) for p in providers])

    def plan(self, prompt: str, mode: RunMode | None = None) -> str:
        providers = self._providers_for("reasoner", mode) or [self.reasoner_provider]
        return self._call_with_fallback([lambda p=p: p.plan(prompt) for p in providers])

    def execute(self, prompt: str, mode: RunMode | None = None) -> str:
        providers = self._providers_for("executor", mode) or [self.executor_provider]
        return self._call_with_fallback([lambda p=p: p.execute(prompt) for p in providers])

    def _providers_for(self, role: str, mode: RunMode | None) -> list[ModelProvider] | None:
        if mode is None:
            return None
        return self.per_mode_providers.get(mode, {}).get(role)

    def _call_with_fallback(self, calls: list[Callable[[], str]]) -> str:
        last_error: Exception | None = None
        for call in calls:
            try:
                return call()
            except Exception as exc:  # noqa: BLE001 - fallback to next provider
                last_error = exc
                continue
        if last_error:
            raise last_error
        raise RuntimeError("No providers available")

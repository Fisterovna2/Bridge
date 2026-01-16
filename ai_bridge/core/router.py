from __future__ import annotations

from dataclasses import dataclass

from ai_bridge.core.model_provider import ModelProvider
from ai_bridge.vision.redact import RedactedFrame


@dataclass
class ModelRoleConfig:
    name: str
    provider: str
    model: str


class ModelRouter:
    def __init__(
        self,
        vision_provider: ModelProvider,
        reasoner_provider: ModelProvider,
        executor_provider: ModelProvider,
    ) -> None:
        self.vision_provider = vision_provider
        self.reasoner_provider = reasoner_provider
        self.executor_provider = executor_provider

    def describe_screen(self, frame: RedactedFrame, prompt: str) -> str:
        return self.vision_provider.describe(frame, prompt)

    def plan(self, prompt: str) -> str:
        return self.reasoner_provider.plan(prompt)

    def execute(self, prompt: str) -> str:
        return self.executor_provider.execute(prompt)

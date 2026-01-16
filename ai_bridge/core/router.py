from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelRoleConfig:
    name: str
    provider: str
    model: str


class ModelRouter:
    def __init__(self, vision: ModelRoleConfig, reasoner: ModelRoleConfig, executor: ModelRoleConfig) -> None:
        self.vision = vision
        self.reasoner = reasoner
        self.executor = executor

    def describe_screen(self, prompt: str) -> str:
        return f"[vision:{self.vision.provider}/{self.vision.model}] {prompt}"

    def plan(self, prompt: str) -> str:
        return f"[reasoner:{self.reasoner.provider}/{self.reasoner.model}] {prompt}"

    def execute(self, prompt: str) -> str:
        return f"[executor:{self.executor.provider}/{self.executor.model}] {prompt}"

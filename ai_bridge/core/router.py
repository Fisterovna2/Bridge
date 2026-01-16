from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ai_bridge.core.model_provider import ModelProvider


@dataclass(frozen=True)
class RoutedProviders:
    vision_provider: ModelProvider
    reasoner_provider: ModelProvider
    executor_provider: ModelProvider


class ModelRouter:
    """
    Routes which model provider to use for different roles.
    Backward compatible with older constructor kwargs:
      - vision_provider
      - reasoner_provider
      - executor_provider

    Also supports newer names if they exist:
      - vision
      - reasoner
      - executor
    """

    def __init__(
        self,
        vision_provider: Optional[ModelProvider] = None,
        reasoner_provider: Optional[ModelProvider] = None,
        executor_provider: Optional[ModelProvider] = None,
        **kwargs,
    ) -> None:
        # Backward/forward compatible alias support
        if vision_provider is None and "vision" in kwargs:
            vision_provider = kwargs.pop("vision")
        if reasoner_provider is None and "reasoner" in kwargs:
            reasoner_provider = kwargs.pop("reasoner")
        if executor_provider is None and "executor" in kwargs:
            executor_provider = kwargs.pop("executor")

        # Some repos used `vision_model_provider` style - support if present
        if vision_provider is None and "vision_model_provider" in kwargs:
            vision_provider = kwargs.pop("vision_model_provider")
        if reasoner_provider is None and "reasoner_model_provider" in kwargs:
            reasoner_provider = kwargs.pop("reasoner_model_provider")
        if executor_provider is None and "executor_model_provider" in kwargs:
            executor_provider = kwargs.pop("executor_model_provider")

        if kwargs:
            raise TypeError(f"ModelRouter.__init__ unexpected kwargs: {sorted(kwargs.keys())}")

        if vision_provider is None or reasoner_provider is None or executor_provider is None:
            raise TypeError(
                "ModelRouter requires vision_provider, reasoner_provider, executor_provider "
                "(or aliases: vision/reasoner/executor)."
            )

        self.vision_provider = vision_provider
        self.reasoner_provider = reasoner_provider
        self.executor_provider = executor_provider

    def providers(self) -> RoutedProviders:
        return RoutedProviders(
            vision_provider=self.vision_provider,
            reasoner_provider=self.reasoner_provider,
            executor_provider=self.executor_provider,
        )

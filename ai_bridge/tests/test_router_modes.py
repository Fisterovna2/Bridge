from PIL import Image

from ai_bridge.core.modes import RunMode
from ai_bridge.core.model_provider import ModelProvider
from ai_bridge.core.router import ModelRouter
from ai_bridge.vision.frame_types import RedactedFrame


class FailingProvider(ModelProvider):
    def describe(self, frame: RedactedFrame, prompt: str) -> str:
        raise RuntimeError("fail")

    def plan(self, prompt: str) -> str:
        raise RuntimeError("fail")

    def execute(self, prompt: str) -> str:
        raise RuntimeError("fail")


class WorkingProvider(ModelProvider):
    def __init__(self, name: str) -> None:
        self.name = name

    def describe(self, frame: RedactedFrame, prompt: str) -> str:
        return f"{self.name}:{prompt}"

    def plan(self, prompt: str) -> str:
        return f"{self.name}:{prompt}"

    def execute(self, prompt: str) -> str:
        return f"{self.name}:{prompt}"


def test_mode_router_fallback() -> None:
    base = WorkingProvider("base")
    fallback = WorkingProvider("fallback")
    router = ModelRouter(
        vision_provider=base,
        reasoner_provider=base,
        executor_provider=base,
        per_mode_providers={
            RunMode.SANDBOX: {
                "vision": [FailingProvider(), fallback],
                "reasoner": [FailingProvider(), fallback],
                "executor": [FailingProvider(), fallback],
            }
        },
    )
    frame = RedactedFrame(Image.new("RGB", (10, 10)), redacted=True)
    assert router.describe_screen(frame, "screen", RunMode.SANDBOX) == "fallback:screen"
    assert router.plan("plan", RunMode.SANDBOX) == "fallback:plan"
    assert router.execute("exec", RunMode.SANDBOX) == "fallback:exec"

from PIL import Image
import pytest

from ai_bridge.core.model_provider import RedactionGuardModelProvider, SimpleModelProvider
from ai_bridge.vision.redact import RedactedFrame


def test_model_guard_blocks_unredacted_frame() -> None:
    provider = RedactionGuardModelProvider(SimpleModelProvider("test"))
    frame = RedactedFrame(Image.new("RGB", (10, 10)), redacted=False)
    with pytest.raises(ValueError, match="redacted"):
        provider.describe(frame, "describe")


def test_model_guard_allows_redacted_frame() -> None:
    provider = RedactionGuardModelProvider(SimpleModelProvider("test"))
    frame = RedactedFrame(Image.new("RGB", (10, 10)), redacted=True)
    assert "describe" in provider.describe(frame, "describe")

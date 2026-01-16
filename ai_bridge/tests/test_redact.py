from PIL import Image

from ai_bridge.vision.ocr import TextBox
from ai_bridge.vision.redact import redact_image


def test_redact_image_draws_black_box() -> None:
    image = Image.new("RGB", (100, 100), (255, 255, 255))
    boxes = [TextBox(text="secret", left=10, top=10, width=20, height=20)]
    redacted = redact_image(image, boxes)
    assert redacted.image.getpixel((15, 15)) == (0, 0, 0)
    assert redacted.image.getpixel((0, 0)) == (255, 255, 255)
    assert redacted.redacted is True

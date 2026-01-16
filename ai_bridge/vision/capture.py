from __future__ import annotations

from PIL import Image
import mss


def capture_screen() -> Image.Image:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        return Image.frombytes("RGB", screenshot.size, screenshot.rgb)

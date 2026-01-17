from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Calibration:
    scale_x: float
    scale_y: float
    offset_x: float = 0.0
    offset_y: float = 0.0

    def map_point(self, x: int, y: int) -> tuple[int, int]:
        mapped_x = int(x * self.scale_x + self.offset_x)
        mapped_y = int(y * self.scale_y + self.offset_y)
        return mapped_x, mapped_y


def compute_calibration(frame_width: int, frame_height: int, vm_width: int, vm_height: int) -> Calibration:
    if frame_width == 0 or frame_height == 0:
        raise ValueError("Frame dimensions must be non-zero")
    return Calibration(
        scale_x=vm_width / frame_width,
        scale_y=vm_height / frame_height,
    )

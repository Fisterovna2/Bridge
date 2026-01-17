from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_bridge.game.calibration import compute_calibration


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrate frame->VM coordinate mapping.")
    parser.add_argument("--frame-width", type=int, required=True)
    parser.add_argument("--frame-height", type=int, required=True)
    parser.add_argument("--vm-width", type=int, required=True)
    parser.add_argument("--vm-height", type=int, required=True)
    parser.add_argument("--output", type=Path, default=Path("logs/calibration.json"))
    args = parser.parse_args()

    calibration = compute_calibration(
        frame_width=args.frame_width,
        frame_height=args.frame_height,
        vm_width=args.vm_width,
        vm_height=args.vm_height,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "scale_x": calibration.scale_x,
                "scale_y": calibration.scale_y,
                "offset_x": calibration.offset_x,
                "offset_y": calibration.offset_y,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Calibration saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

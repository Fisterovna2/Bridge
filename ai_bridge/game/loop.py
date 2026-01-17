from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable

from ai_bridge.core.actions import Action, ActionType
from ai_bridge.core.cancellation import CancellationToken
from ai_bridge.game.calibration import Calibration
from ai_bridge.game.metrics import LoopMetrics
from ai_bridge.vm.adapter_base import VmAdapter


@dataclass
class GameProfile:
    name: str
    resolution: tuple[int, int]
    sensitivity: float = 1.0
    roi: tuple[int, int, int, int] | None = None


class GameLoop:
    def __init__(
        self,
        adapter: VmAdapter,
        ghost_cursor: Callable[[Action], None],
        cancellation: CancellationToken,
        dry_run: bool = True,
        calibration: Calibration | None = None,
    ) -> None:
        self.adapter = adapter
        self.ghost_cursor = ghost_cursor
        self.cancellation = cancellation
        self.dry_run = dry_run
        self.calibration = calibration
        self.metrics = LoopMetrics()
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _run(self) -> None:
        while self._running and not self.cancellation.is_cancelled():
            frame_start = time.perf_counter()
            frame = self.adapter.get_frame()
            frame_end = time.perf_counter()
            self.metrics.frame_time.push(frame_end - frame_start)

            decision_start = time.perf_counter()
            action = self._plan_action(frame)
            decision_end = time.perf_counter()
            self.metrics.decision_time.push(decision_end - decision_start)

            if action:
                self.ghost_cursor(action)
                if not self.dry_run:
                    input_start = time.perf_counter()
                    self.adapter.send_input(action)
                    input_end = time.perf_counter()
                    self.metrics.input_time.push(input_end - input_start)
            time.sleep(0.1)

    def _plan_action(self, frame) -> Action | None:
        if frame is None:
            return None
        width, height = frame.size
        target_x, target_y = width // 2, height // 2
        if self.calibration:
            target_x, target_y = self.calibration.map_point(target_x, target_y)
        return Action(ActionType.MOVE, x=target_x, y=target_y)

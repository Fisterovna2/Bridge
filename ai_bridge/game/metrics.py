from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class RollingMetric:
    window: int = 50
    values: deque[float] = field(default_factory=lambda: deque(maxlen=50))

    def push(self, value: float) -> None:
        self.values.append(value)

    @property
    def avg(self) -> float:
        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)


@dataclass
class LoopMetrics:
    frame_time: RollingMetric = field(default_factory=RollingMetric)
    decision_time: RollingMetric = field(default_factory=RollingMetric)
    input_time: RollingMetric = field(default_factory=RollingMetric)

    def snapshot(self) -> dict[str, float]:
        return {
            "frame_time_ms": self.frame_time.avg * 1000,
            "decision_time_ms": self.decision_time.avg * 1000,
            "input_time_ms": self.input_time.avg * 1000,
        }

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str
    fix: str | None = None


@dataclass
class SelfCheckReport:
    results: List[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.results)

    def format_lines(self) -> List[str]:
        lines = []
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            line = f"[{status}] {result.name}: {result.detail}"
            if result.fix:
                line += f" | Fix: {result.fix}"
            lines.append(line)
        return lines

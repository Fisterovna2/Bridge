from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


DESTRUCTIVE_KEYWORDS = {
    "format",
    "rm -rf",
    "delete system",
    "registry",
    "powershell remove-item",
    "shutdown /s",
    "del /s",
}

HIGH_RISK_KEYWORDS = {
    "cmd.exe",
    "powershell",
    "bash",
    ".exe",
    ".bat",
    ".ps1",
    "reg add",
    "reg delete",
    "schtasks",
    "netsh",
    "curl",
    "wget",
}

MEDIUM_RISK_KEYWORDS = {
    "install",
    "download",
    "open browser",
    "upload",
    "move",
    "copy",
}
PROCESS_CONTROL_KEYWORDS = {
    "taskkill",
    "kill ",
    "terminate",
    "stop process",
    "service",
    "systemctl",
}


@dataclass
class GuardrailDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str
    risk: RiskLevel


def destructive_match(text: str) -> str | None:
    for keyword in DESTRUCTIVE_KEYWORDS:
        if keyword in text:
            return keyword
    return None


def score_risk(text: str) -> RiskLevel:
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in text:
            return RiskLevel.HIGH
    for keyword in MEDIUM_RISK_KEYWORDS:
        if keyword in text:
            return RiskLevel.MEDIUM
    return RiskLevel.LOW


def allowlist_ok(text: str, allowlist_paths: Iterable[str]) -> bool:
    allowlist = [Path(path).as_posix().lower() for path in allowlist_paths]
    if not looks_like_path(text):
        return True
    return any(path and path in text for path in allowlist)


def looks_like_path(text: str) -> bool:
    return ":\\" in text or text.startswith("/") or "/" in text or "\\" in text


def process_control_match(text: str) -> str | None:
    for keyword in PROCESS_CONTROL_KEYWORDS:
        if keyword in text:
            return keyword
    return None


def assess_action(text: str, allowlist_paths: Iterable[str]) -> GuardrailDecision:
    lowered = text.lower()
    destructive = destructive_match(lowered)
    if destructive:
        return GuardrailDecision(
            allowed=False,
            requires_confirmation=True,
            reason=f"Blocked destructive keyword: {destructive}",
            risk=RiskLevel.HIGH,
        )
    if not allowlist_ok(lowered, allowlist_paths):
        return GuardrailDecision(
            allowed=False,
            requires_confirmation=True,
            reason="File action outside allowlist",
            risk=RiskLevel.MEDIUM,
        )
    risk = score_risk(lowered)
    return GuardrailDecision(
        allowed=True,
        requires_confirmation=risk in {RiskLevel.MEDIUM, RiskLevel.HIGH},
        reason=f"Risk level {risk.value}",
        risk=risk,
    )

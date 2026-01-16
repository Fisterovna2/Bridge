from __future__ import annotations

from dataclasses import dataclass

from ai_bridge.core.modes import RunMode
from ai_bridge.core.safety import RiskLevel, score_risk, allowlist_ok, destructive_match


@dataclass
class PolicyDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str
    rule_id: str
    risk: RiskLevel
    target: str
    mode: RunMode


class PolicyEngine:
    def evaluate(self, mode: RunMode, text: str, allowlist_paths: list[str]) -> PolicyDecision:
        lowered = text.lower()
        destructive = destructive_match(lowered)
        target = "host" if mode == RunMode.NORMAL else "vm"
        if destructive:
            return PolicyDecision(
                allowed=False,
                requires_confirmation=True,
                reason=f"Blocked destructive keyword: {destructive}",
                rule_id="block-destructive",
                risk=RiskLevel.HIGH,
                target=target,
                mode=mode,
            )
        if not allowlist_ok(lowered, allowlist_paths):
            return PolicyDecision(
                allowed=False,
                requires_confirmation=True,
                reason="File action outside allowlist",
                rule_id="deny-outside-allowlist",
                risk=RiskLevel.MEDIUM,
                target=target,
                mode=mode,
            )
        risk = score_risk(lowered)
        if mode == RunMode.NORMAL:
            if risk == RiskLevel.HIGH:
                return PolicyDecision(
                    allowed=True,
                    requires_confirmation=True,
                    reason="High risk action requires confirmation",
                    rule_id="confirm-high-risk",
                    risk=risk,
                    target=target,
                    mode=mode,
                )
            if risk == RiskLevel.MEDIUM:
                return PolicyDecision(
                    allowed=True,
                    requires_confirmation=True,
                    reason="Medium risk action requires confirmation",
                    rule_id="confirm-medium-risk",
                    risk=risk,
                    target=target,
                    mode=mode,
                )
        if mode == RunMode.GAME and risk == RiskLevel.HIGH:
            return PolicyDecision(
                allowed=True,
                requires_confirmation=True,
                reason="High risk action in VM requires confirmation",
                rule_id="confirm-high-risk-vm",
                risk=risk,
                target=target,
                mode=mode,
            )
        return PolicyDecision(
            allowed=True,
            requires_confirmation=False,
            reason="Allowed by policy",
            rule_id="allow",
            risk=risk,
            target=target,
            mode=mode,
        )

from __future__ import annotations

from pathlib import Path

from ai_bridge.core.model_provider import RedactionGuardModelProvider, SimpleModelProvider
from ai_bridge.core.modes import RunMode
from ai_bridge.core.router import ModelRouter
from ai_bridge.core.selfcheck_types import CheckResult, SelfCheckReport
from ai_bridge.vm.adapter_virtualbox import VirtualBoxAdapter


def run_selfcheck() -> SelfCheckReport:
    report = SelfCheckReport()

    config_path = Path("ai_bridge/config/default.yaml")
    report.results.append(
        CheckResult(
            name="Config",
            passed=config_path.exists(),
            detail=str(config_path) if config_path.exists() else "Missing default.yaml",
            fix="Restore ai_bridge/config/default.yaml" if not config_path.exists() else None,
        )
    )

    try:
        router = ModelRouter(
            vision_provider=RedactionGuardModelProvider(SimpleModelProvider("mvp")),
            reasoner_provider=SimpleModelProvider("mvp"),
            executor_provider=SimpleModelProvider("mvp"),
            per_mode_providers={RunMode.SANDBOX: {"vision": [SimpleModelProvider("backup")]}},
        )
        _ = router
        report.results.append(
            CheckResult(
                name="ModelRouter",
                passed=True,
                detail="Router initialized with per-mode providers",
            )
        )
    except Exception as exc:  # noqa: BLE001
        report.results.append(
            CheckResult(
                name="ModelRouter",
                passed=False,
                detail=str(exc),
                fix="Check provider config and per-mode routing",
            )
        )

    adapter = VirtualBoxAdapter()
    report.results.extend(adapter.selfcheck())
    return report

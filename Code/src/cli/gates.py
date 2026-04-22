"""Quality gates — pass/fail thresholds for CI builds."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ThresholdConfig:
    """Only specified thresholds are enforced; the rest are ignored."""
    min_score: Optional[float] = None
    max_errors: Optional[int] = None
    max_warnings: Optional[int] = None


@dataclass
class GateResult:
    """Pass/fail plus a list of failure reasons."""
    passed: bool
    failures: List[str] = field(default_factory=list)


def evaluate_gates(
    score: float,
    error_count: int,
    warning_count: int,
    config: ThresholdConfig,
) -> GateResult:
    """Check score/error/warning counts against thresholds."""
    failures: List[str] = []

    if config.min_score is not None and score < config.min_score:
        failures.append(
            f"Score {score:.1f}% is below minimum threshold {config.min_score:.1f}%"
        )

    if config.max_errors is not None and error_count > config.max_errors:
        failures.append(
            f"Error count {error_count} exceeds maximum allowed {config.max_errors}"
        )

    if config.max_warnings is not None and warning_count > config.max_warnings:
        failures.append(
            f"Warning count {warning_count} exceeds maximum allowed {config.max_warnings}"
        )

    return GateResult(passed=len(failures) == 0, failures=failures)

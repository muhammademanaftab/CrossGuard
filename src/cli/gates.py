"""Quality gate evaluation for CI/CD integration.

Provides threshold-based pass/fail logic so builds can be
rejected when compatibility scores or issue counts exceed limits.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ThresholdConfig:
    """Configuration for quality gate thresholds.

    All fields are optional — only specified thresholds are enforced.
    """
    min_score: Optional[float] = None
    max_errors: Optional[int] = None
    max_warnings: Optional[int] = None


@dataclass
class GateResult:
    """Outcome of a quality-gate evaluation."""
    passed: bool
    failures: List[str] = field(default_factory=list)


def evaluate_gates(
    score: float,
    error_count: int,
    warning_count: int,
    config: ThresholdConfig,
) -> GateResult:
    """Evaluate quality gates against analysis results.

    Args:
        score: Overall compatibility score (0-100).
        error_count: Number of unsupported features.
        warning_count: Number of partially-supported features.
        config: Threshold configuration.

    Returns:
        GateResult with ``passed=True`` if all gates pass.
    """
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

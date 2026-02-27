"""Shared helper functions."""

from __future__ import annotations

from typing import Dict

from utils.constants import DEFAULT_WEIGHTS


def clamp(value: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    return max(min_value, min(max_value, value))


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def normalize_weights(weights: Dict[str, float] | None) -> Dict[str, float]:
    if not weights:
        return DEFAULT_WEIGHTS.copy()

    cleaned = {k: max(0.0, float(v)) for k, v in weights.items()}
    total = sum(cleaned.values())
    if total <= 0:
        return DEFAULT_WEIGHTS.copy()
    return {k: v / total for k, v in cleaned.items()}


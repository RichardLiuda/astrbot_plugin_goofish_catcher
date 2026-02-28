from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.scheduler import calculate_retry_delay  # noqa: E402


def test_retry_delay_grows_exponentially_without_jitter():
    d1 = calculate_retry_delay(
        failure_count=1,
        base_sec=10,
        max_sec=1000,
        jitter_ratio=0.2,
        rng=lambda: 0.0,
    )
    d2 = calculate_retry_delay(
        failure_count=2,
        base_sec=10,
        max_sec=1000,
        jitter_ratio=0.2,
        rng=lambda: 0.0,
    )
    d3 = calculate_retry_delay(
        failure_count=3,
        base_sec=10,
        max_sec=1000,
        jitter_ratio=0.2,
        rng=lambda: 0.0,
    )
    assert d1 == 10
    assert d2 == 20
    assert d3 == 40


def test_retry_delay_caps_at_max():
    delay = calculate_retry_delay(
        failure_count=10,
        base_sec=30,
        max_sec=120,
        jitter_ratio=0.2,
        rng=lambda: 0.0,
    )
    assert delay == 120

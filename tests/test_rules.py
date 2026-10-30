from __future__ import annotations

import pytest

from verifier.rules import score


@pytest.mark.parametrize(
    ("competitors", "years", "has_sub", "hundredths", "recommendation"),
    [
        (2, 14, True, 22, "INVEST"),  # Amplitude in 2026: 30 + 20 - 28
        (0, 14, False, 12, "INVEST"),  # Benchling in 2026: 30 + 0 - 28 + 10
        (1, 3, True, 34, "INVEST"),  # just under 35
        (1, 2, True, 36, "FURTHER_DD"),  # just over 35
        (3, 3, True, 54, "FURTHER_DD"),  # just under 55
        (3, 2, True, 56, "PASS"),  # just over 55
        (9, 0, False, 80, "PASS"),  # competitors count at most 4
        (0, 40, True, 0, "INVEST"),  # years count at most 15, and the score never goes below 0
        (0, 0, True, 30, "INVEST"),  # boundary: the batch year itself
    ],
)
def test_score(competitors, years, has_sub, hundredths, recommendation) -> None:
    assert score(competitors, years, has_sub) == (hundredths, recommendation)


def test_negative_inputs_are_refused() -> None:
    with pytest.raises(ValueError):
        score(-1, 0, True)
    with pytest.raises(ValueError):
        score(0, -1, True)

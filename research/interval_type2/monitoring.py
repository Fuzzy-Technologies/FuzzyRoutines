# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Bounded interval Type-2 Sugeno experiment for service monitoring."""

from fractions import Fraction
from math import isfinite

type Interval = tuple[float, float]
type Rule = tuple[float, Interval]

LIMIT = 32
CONSEQUENCES = (100.0, 260.0)
BASES = (65.0, 60.0)
WIDTH = 30.0
UNCERTAINTY = 5.0


def Reduce(rules: tuple[Rule, ...]) -> Interval:
    """Find the extreme normalized averages over independent firing intervals."""

    if not 1 <= len(rules) <= LIMIT:
        raise ValueError(f"Expected between one and {LIMIT} rules")

    ordered = []

    for value, (lower, upper) in sorted(rules):
        if not isfinite(value) or not 0 <= lower <= upper <= 1:
            raise ValueError("Consequents must be finite and firing bounds must be ordered in [0, 1]")

        ordered.append((Fraction(value), Fraction(lower), Fraction(upper)))

    if not any(upper for _, _, upper in ordered):
        raise ValueError("No rule can fire")

    minima = []
    maxima = []

    # At a minimizing average, increasing the weight of a consequence below
    # that average cannot raise it. The maximizing case reverses the endpoints.
    for split in range(len(ordered) + 1):
        small = tuple(upper if index < split else lower for index, (_, lower, upper) in enumerate(ordered))
        large = tuple(lower if index < split else upper for index, (_, lower, upper) in enumerate(ordered))

        for weights, results in ((small, minima), (large, maxima)):
            total = sum(weights)

            if total:
                results.append(sum(weight * value for weight, (value, _, _) in zip(weights, ordered, strict=True)) / total)

    return float(min(minima)), float(max(maxima))


def Ramp(load: float, start: float) -> float:
    """Return a rising degree with the declared fixed transition width."""

    return max(0.0, min(1.0, (load - start) / WIDTH))


def Monitor(load: float, shift: float = UNCERTAINTY) -> Interval:
    """Propagate independent threshold shifts to a service latency interval in ms."""

    if not 0 <= load <= 100 or not 0 <= shift <= UNCERTAINTY:
        raise ValueError("Load must be in [0, 100] and shift in [0, 5] percentage points")

    nominal, overloaded = BASES
    bounds = (
        (1 - Ramp(load, nominal - shift), 1 - Ramp(load, nominal + shift)),
        (Ramp(load, overloaded + shift), Ramp(load, overloaded - shift)),
    )

    return Reduce(tuple(zip(CONSEQUENCES, bounds, strict=True)))


def Main() -> None:
    """Print deterministic intervals for a fixed sequence of CPU loads."""

    print("load_pct,lower_ms,upper_ms")

    for load in (50, 65, 75, 80, 85, 100):
        lower, upper = Monitor(load)
        print(f"{load},{lower:.3f},{upper:.3f}")


if __name__ == "__main__":
    Main()

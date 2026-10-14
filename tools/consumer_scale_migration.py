# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Measure sanitized consumer scale boundaries using an installed release.

The fixture describes the public TKSBrokerAPI risk normalization contract.
It contains synthetic prices, not production observations or strategy settings.
JSON output keeps membership, selected labels and centroids separate; it does
not evaluate trading decisions or import the consumer's execution engine.
"""

import argparse
import hashlib
import json
import math
import platform
from importlib.metadata import version
from pathlib import Path

from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale


def NormalizedRisk(current: float, lower: float, upper: float, direction: str) -> float:
    """Apply the pinned public consumer's clipping and degenerate-range policy.

    Args:
        current: Synthetic current coordinate before consumer-side clipping.
        lower: Finite lower range boundary.
        upper: Finite upper range boundary, at least the lower boundary.
        direction: `long` measures from the lower boundary; `short` from upper.

    Raises:
        ValueError: A value is nonfinite, a range is reversed or direction invalid.
    """

    if not all(math.isfinite(value) for value in (current, lower, upper)):
        raise ValueError("Consumer fixture coordinates must be finite")

    if upper < lower or direction not in {"long", "short"}:
        raise ValueError("Consumer range or direction is invalid")

    clipped = min(upper, max(lower, current))
    width = upper - lower if upper != lower else 1.0
    origin = lower if direction == "long" else upper

    return abs(clipped - origin) / width


def MeasureCases(cases: list[dict]) -> dict:
    """Report public facade results without a network or consumer dependency.

    Args:
        cases: Synthetic scalar inputs with stable IDs and direction fields.

    Returns:
        Ordered grades, labels, output percentages and separate centroid values.
    """

    scale = UniversalFuzzyScale()
    measurements = []

    for case in cases:
        coordinate = NormalizedRisk(case["current"], case["lower"], case["upper"], case["direction"])
        measurements.append({
            "id": case["id"], "coordinate": coordinate,
            "grades": [level["fSet"].mFunction.mju(coordinate) for level in scale.levels],
            "label": scale.Fuzzy(coordinate)["name"], "percent": 100 * coordinate,
        })

    centroids = [level["fSet"].Defuz() for level in scale.levels]

    for level in scale.levels:
        level["fSet"].mFunction.accuracy = 100

    return {
        "term_order": list(scale.levelsNames),
        "integration_windows": [list(level["fSet"].supportSet) for level in scale.levels],
        "cases": measurements,
        "centroids": centroids,
        "centroids_after_accuracy_100": [level["fSet"].Defuz() for level in scale.levels],
    }


def CheckPublishedBoundary(measurements: dict, reference: dict) -> None:
    """Reject a candidate that changes the frozen 2.0 consumer observations.

    Coordinate normalization, term order and labels are exact contracts.
    Grade and centroid tolerances are absolute bounds for these fixtures only.
    """

    for field in ("term_order", "integration_windows"):
        if measurements[field] != reference[field]:
            raise ValueError(f"Consumer boundary changed: {field}")

    for actual, expected in zip(measurements["cases"], reference["cases"], strict=True):
        for field in ("id", "coordinate", "label", "percent"):
            if actual[field] != expected[field]:
                raise ValueError(f"Consumer boundary changed: {actual['id']} {field}")

        if any(not math.isclose(value, target, rel_tol=0, abs_tol=1e-12) for value, target in zip(actual["grades"], expected["grades"], strict=True)):
            raise ValueError(f"Consumer membership changed: {actual['id']}")

    for field in ("centroids", "centroids_after_accuracy_100"):
        if any(not math.isclose(value, target, rel_tol=0, abs_tol=1e-10) for value, target in zip(measurements[field], reference[field], strict=True)):
            raise ValueError(f"Consumer centroid boundary changed: {field}")


def Main(arguments: list[str] | None = None) -> int:
    """Emit installed-version migration observations as JSON and optionally a file."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-current", action="store_true", dest="checkCurrent")
    options = parser.parse_args(arguments)
    fixture = json.loads(options.fixture.read_text(encoding="utf-8"))
    report = {
        "package_version": version("fuzzyroutines"),
        "python_version": platform.python_version(),
        "fixture_sha256": hashlib.sha256(options.fixture.read_bytes()).hexdigest(),
        "consumer_revision": fixture["consumer_revision"],
        "fixture_kind": "synthetic inputs derived from public consumer semantics",
        "measurements": MeasureCases(fixture["inputs"]),
    }

    if options.checkCurrent:
        CheckPublishedBoundary(report["measurements"], fixture["baseline_2_0_0"])
        report["published_boundary_check"] = "passed"

    payload = json.dumps(report, indent=2, allow_nan=False) + "\n"

    if options.output is not None:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(payload, encoding="utf-8")

    print(payload, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())

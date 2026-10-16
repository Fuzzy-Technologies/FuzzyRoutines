# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Check the pinned consumer boundary against frozen historical observations."""

import hashlib
import json
import math
from copy import deepcopy
from pathlib import Path

import pytest

from tools import consumer_scale_migration as migration

FIXTURE = Path(__file__).parent / "fixtures" / "consumer_scale_migration.json"


def test_ConsumerLabelsGradesAndPercentagesRetainHistoricalMeaning():
    """Synthetic long/short cases preserve decisions, including weak coverage."""

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    actual = migration.MeasureCases(fixture["inputs"])
    historical = fixture["baseline_1_0_3"]
    released = fixture["baseline_2_0_0"]

    assert actual["term_order"] == historical["term_order"] == released["term_order"]
    assert actual["integration_windows"] == historical["integration_windows"]
    assert len(actual["cases"]) == len(historical["cases"]) == 27

    for measured, old, stable in zip(actual["cases"], historical["cases"], released["cases"], strict=True):
        assert measured["id"] == old["id"] == stable["id"]
        assert measured["label"] == old["label"] == stable["label"]
        assert measured["coordinate"] == old["coordinate"] == stable["coordinate"]
        assert measured["percent"] == old["percent"] == stable["percent"]
        assert measured["grades"] == pytest.approx(old["grades"], abs=1e-12, rel=0)
        assert measured["grades"] == pytest.approx(stable["grades"], abs=1e-12, rel=0)


def test_CentroidCorrectionIsExplicitAndRetainsPublishedTwoPointZero():
    """Endpoint numerical corrections are not mislabeled as exact old parity."""

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    actual = migration.MeasureCases(fixture["inputs"])
    old = fixture["baseline_1_0_3"]["centroids"]
    released = fixture["baseline_2_0_0"]["centroids"]

    assert actual["centroids"] == pytest.approx(released, abs=1e-10, rel=0)
    assert actual["centroids_after_accuracy_100"] == pytest.approx(released, abs=1e-10, rel=0)
    assert 5e-5 < abs(actual["centroids"][0] - old[0]) < 7e-5
    assert 5e-5 < abs(actual["centroids"][-1] - old[-1]) < 7e-5
    assert actual["centroids"][1:4] == pytest.approx([0.285, 0.5, 0.715], abs=1e-10, rel=0)


@pytest.mark.parametrize("current,direction,expected", [
    (90, "long", 0), (210, "long", 1), (125, "long", 0.25),
    (90, "short", 1), (210, "short", 0), (125, "short", 0.75),
])
def test_ConsumerNormalizationClipsBeforeScaleEvaluation(current, direction, expected):
    """Clipping belongs to this consumer contract, not membership evaluation."""

    assert migration.NormalizedRisk(current, 100, 200, direction) == expected


@pytest.mark.parametrize("direction", ["long", "short"])
def test_DegenerateConsumerRangeHasZeroDistance(direction):
    """The consumer's replacement denominator is observable for a flat range."""

    assert migration.NormalizedRisk(200, 123, 123, direction) == 0


@pytest.mark.parametrize("current,lower,upper,direction", [
    (math.nan, 0, 1, "long"), (0, -math.inf, 1, "short"),
    (0, 0, math.inf, "long"), (0, 2, 1, "long"), (0, 0, 1, "sideways"),
])
def test_InvalidFixtureCoordinatesFail(current, lower, upper, direction):
    """Malformed evidence cannot silently become a plausible risk coordinate."""

    with pytest.raises(ValueError):
        migration.NormalizedRisk(current, lower, upper, direction)


def test_CommandReportsItsInstalledVersionAndMatchingJson(tmpPath, monkeypatch, capsys):
    """The CLI keeps evidence machine-readable and does not guess its version."""

    monkeypatch.setattr(migration, "version", lambda name: "2.1.0.dev0")
    outputPath = tmpPath / "nested" / "consumer.json"
    assert migration.Main(["--fixture", str(FIXTURE), "--output", str(outputPath), "--check-current"]) == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert captured.err == ""
    assert report == json.loads(outputPath.read_text(encoding="utf-8"))
    assert report["package_version"] == "2.1.0.dev0"
    assert report["fixture_sha256"] == hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert len(report["python_version"].split(".")) == 3
    assert report["consumer_revision"] == "b963c54039f013d432220186ae35a22359c5a773"
    assert report["fixture_kind"] == "synthetic inputs derived from public consumer semantics"
    assert report["published_boundary_check"] == "passed"


@pytest.mark.parametrize("change", ["label", "grade", "centroid", "missing_case", "nonfinite"])
def test_InstalledCheckRejectsObservableConsumerDrift(change):
    """The installed entry point fails instead of merely printing a changed result."""

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    reference = fixture["baseline_2_0_0"]
    changed = deepcopy(reference)

    if change == "label":
        changed["cases"][0]["label"] = "Max"

    elif change == "grade":
        changed["cases"][0]["grades"][0] += 0.01

    elif change == "centroid":
        changed["centroids"][0] += 0.01

    elif change == "nonfinite":
        changed["centroids"][0] = math.nan

    else:
        changed["cases"].pop()

    with pytest.raises(ValueError):
        migration.CheckPublishedBoundary(changed, reference)

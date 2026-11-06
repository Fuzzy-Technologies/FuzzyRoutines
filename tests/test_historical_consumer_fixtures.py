# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Exercise consumer-side normalization and the historical scalar scale."""

import json
from pathlib import Path

import pytest

from fuzzyroutines import CreateUniversalFuzzyScale, FuzzificationPolicy, UniversalFuzzyScalePolicy
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale
from tools.consumer_scale_migration import NormalizedRisk

FIXTURES = Path(__file__).parent / "fixtures"
SYNTHETIC = json.loads((FIXTURES / "historical_consumer_synthetic.json").read_text(encoding="utf-8"))["cases"]
UPSTREAM = json.loads((FIXTURES / "public_consumer_batches.json").read_text(encoding="utf-8"))["replays"]
BASELINE = json.loads((FIXTURES / "consumer_scale_migration.json").read_text(encoding="utf-8"))["baseline_1_0_3"]
HISTORICAL = {case["id"]: case for case in BASELINE["cases"]}
GRADE_TOLERANCE = 1e-12


def CheckScale(coordinate, label):
    """Compare the exact expected label and ordered legacy/modern grades."""

    legacy = UniversalFuzzyScale()
    modern = CreateUniversalFuzzyScale().Fuzzify(coordinate, UniversalFuzzyScalePolicy())
    grades = tuple(term.grade for term in modern.memberships)
    prior = tuple(level["fSet"].mFunction.mju(coordinate) for level in legacy.levels)

    assert tuple(item.term.name for item in modern.memberships) == tuple(legacy.levelsNames) == tuple(BASELINE["term_order"]), (
        "The historical scale vector order changed"
    )
    assert tuple(term.name for term in modern.selectedTerms) == (legacy.Fuzzy(coordinate)["name"],) == (label,), (
        f"The historical winning label changed at {coordinate!r}"
    )
    assert grades == pytest.approx(prior, abs=GRADE_TOLERANCE, rel=0), (
        f"Legacy and modern membership grades differ at {coordinate!r}"
    )

    return modern


@pytest.mark.parametrize("case", SYNTHETIC, ids=lambda case: case["id"])
def test_SyntheticAdapterCoordinatesRetainHistoricalMeaning(case):
    """Check explicit range mapping against hand-picked anchors and the 1.0.3 capture."""

    coordinate = (case["sample"] - case["lower"]) / (case["upper"] - case["lower"])
    prior = HISTORICAL[case["historical_case"]]
    assert coordinate == case["coordinate"] == prior["coordinate"], "The adapter changed the normalized coordinate"
    assert case["label"] == prior["label"], "The declared anchor diverges from the pinned historical label"
    result = CheckScale(coordinate, case["label"])
    grades = tuple(term.grade for term in result.memberships)

    assert result.confidence == pytest.approx(case["confidence"], abs=GRADE_TOLERANCE, rel=0), (
        f"The expected confidence changed for {case['id']}"
    )
    assert grades == pytest.approx(prior["grades"], abs=GRADE_TOLERANCE, rel=0), (
        f"The membership vector changed since 1.0.3 for {case['id']}"
    )


def test_WeakConfidenceIsPreservedUntilTheConsumerChoosesToAbstain():
    """Distinguish historical weak membership from an application confidence policy."""

    coordinate = 17 / 100
    historical = CheckScale(coordinate, "Min")
    assert 0 < historical.confidence < 0.003, "The positive Min tail must remain a weak match"

    threshold = FuzzificationPolicy(minimumConfidence=0.01)
    explicit = CreateUniversalFuzzyScale().Fuzzify(coordinate, threshold)
    assert not explicit.isMatch, "An explicit consumer threshold must abstain on weak coverage"


@pytest.mark.parametrize("replay", UPSTREAM, ids=lambda replay: replay["function"])
def test_PublicBrokerCoordinatesAndOutputsUseThePinnedScalarContract(replay):
    """Replay public long/short cases without importing the broker or NumPy."""

    direction = {"RiskLong": "long", "RiskShort": "short"}[replay["function"]]

    for case, expected in zip(replay["cases"], replay["coordinates"], strict=True):
        prices = case["prices"]
        coordinate = NormalizedRisk(prices["current"], prices["lowest"], prices["highest"], direction)
        assert coordinate == expected, f"{replay['function']} normalization changed for {prices!r}"
        assert round(100 * coordinate, 4) == case["expected_percent_rounded_4"], (
            f"{replay['function']} percentage changed for {prices!r}"
        )
        CheckScale(coordinate, case["expected_label"])

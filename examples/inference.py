# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compare Mamdani and Sugeno monitoring responses using installed public APIs.

Run `python examples/inference.py` after installing the 2.1 candidate. The
example is dependency-free, deterministic and headless; stdout is JSON. This
illustrative two-term model is not a calibrated security policy or the
historical five-term Universal Fuzzy Scale.
"""

import argparse
import json
import math

from fuzzyroutines import (
    ContinuousUniverse,
    IntegrationDomain,
    LinguisticTerm,
    NegationPolicy,
    ScalarFuzzySet,
    SNormPolicy,
    TNormPolicy,
)
from fuzzyroutines.inference import (
    AffineConsequent,
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    MamdaniModel,
    MamdaniRule,
    SugenoModel,
    SugenoRule,
    TermCondition,
)


def Low(coordinate: float) -> float:
    """Return the decreasing membership ramp on the declared unit interval."""

    return 1 - coordinate


def High(coordinate: float) -> float:
    """Return the increasing membership ramp on the declared unit interval."""

    return coordinate


def BuildModels() -> tuple[MamdaniModel, SugenoModel, SugenoModel]:
    """Build fixed monitoring rules with independently calculable outputs."""

    universe = ContinuousUniverse(0, 1, True, True)
    terms = (
        LinguisticTerm("low", ScalarFuzzySet(universe, Low)),
        LinguisticTerm("high", ScalarFuzzySet(universe, High)),
    )
    inputs = (FuzzyVariable("risk", terms),)
    policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
    low = TermCondition("risk", "low")
    high = TermCondition("risk", "high")
    mamdani = MamdaniModel(
        inputs, FuzzyVariable("response", terms),
        (MamdaniRule("low response", low, "low"), MamdaniRule("high response", high, "high")),
        policy, TNormPolicy("logic"), SNormPolicy("logic"),
    )
    zeroOrder = SugenoModel(inputs, (
        SugenoRule("low response", low, ConstantConsequent(0.2)),
        SugenoRule("high response", high, ConstantConsequent(0.8)),
    ), policy, universe)
    firstOrder = SugenoModel(inputs, (
        SugenoRule("low response", low, AffineConsequent(0, (("risk", 0.5),))),
        SugenoRule("high response", high, AffineConsequent(0.5, (("risk", 0.5),))),
    ), policy, universe)

    return mamdani, zeroOrder, firstOrder


def Run() -> dict:
    """Check exact reference predictions and return JSON-compatible evidence."""

    mamdani, zeroOrder, firstOrder = BuildModels()
    inputs = {"risk": 0.25}
    result = mamdani.Evaluate(inputs, IntegrationDomain(0, 1))
    zeroResult = zeroOrder.Evaluate(inputs)
    firstResult = firstOrder.Evaluate(inputs)
    assert result.value is not None and math.isclose(result.value, 37 / 96, rel_tol=0, abs_tol=1e-12), "Mamdani centroid must match the independent piecewise integral"
    assert math.isclose(zeroResult.value, 0.35, rel_tol=0, abs_tol=1e-15), "Zero-order Sugeno must match its hand-calculated weighted average"
    assert math.isclose(firstResult.value, 0.25, rel_tol=0, abs_tol=1e-15), "First-order Sugeno must match its affine reference"

    return {
        "inputs": inputs,
        "firingStrengths": [trace.firingStrength for trace in result.rules],
        "mamdani": {"value": result.value, "method": result.method},
        "sugenoZero": {
            "value": zeroResult.value,
            "consequences": [trace.consequentValue for trace in zeroResult.rules],
            "contributions": [trace.contribution for trace in zeroResult.rules],
        },
        "sugenoFirst": {
            "value": firstResult.value,
            "consequences": [trace.consequentValue for trace in firstResult.rules],
            "contributions": [trace.contribution for trace in firstResult.rules],
        },
    }


def Main(arguments=None) -> int:
    """Expose a headless executable example with parseable evidence."""

    argparse.ArgumentParser(description=__doc__).parse_args(arguments)
    print(json.dumps(Run(), sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())

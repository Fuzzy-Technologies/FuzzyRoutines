# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Independent references for the bounded interval Type-2 experiment."""

from fractions import Fraction
from itertools import product

import pytest

from fuzzyroutines import ContinuousUniverse, LinguisticTerm, NegationPolicy, ScalarFuzzySet, SNormPolicy, TNormPolicy
from fuzzyroutines.inference import ConstantConsequent, FuzzyVariable, InferencePolicy, SugenoModel, SugenoRule, TermCondition
from research.interval_type2.monitoring import BASES, CONSEQUENCES, Monitor, Ramp, Reduce


def Nominal(load):
    """Evaluate the nominal threshold as a decreasing scalar degree."""

    return 1 - Ramp(load, BASES[0])


def Overloaded(load):
    """Evaluate the overload threshold as an increasing scalar degree."""

    return Ramp(load, BASES[1])


@pytest.mark.parametrize("load", (0, 50, 65, 75, 80, 85, 100))
def test_CoincidentMembershipsMatchScalarSugeno(load):
    """Require exact collapse to the scalar model up to numerical rounding."""

    universe = ContinuousUniverse(0, 100, True, True)
    terms = tuple(LinguisticTerm(name, ScalarFuzzySet(universe, evaluator)) for name, evaluator in (
        ("nominal", Nominal), ("overloaded", Overloaded),
    ))
    rules = tuple(SugenoRule(term.name, TermCondition("load", term.name), ConstantConsequent(value))
                  for term, value in zip(terms, CONSEQUENCES, strict=True))
    policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
    model = SugenoModel((FuzzyVariable("load", terms),), rules, policy, ContinuousUniverse(0, 500, True, True))
    expected = model.Evaluate({"load": load}).value
    lower, upper = Monitor(load, shift=0)

    assert lower == upper, "Coincident firing bounds must yield one output"
    assert lower == pytest.approx(expected, rel=0, abs=1e-12), "Collapsed reduction must agree with scalar Sugeno"


@pytest.mark.parametrize("rules", (
    ((20.0, (0.25, 0.75)), (10.0, (0.25, 0.75))),
    ((1.0, (0.0, 0.25)), (-7.0, (0.0, 1.0)), (0.0, (0.0, 0.5))),
    ((1.0, (0.0, 0.25)), (-7.0, (0.5, 1.0)), (0.0, (0.25, 0.5)), (1.0, (0.0, 0.5))),
))
def test_SwitchSearchAgreesWithAllVertices(rules):
    """Enumerate the entire endpoint box and compare the extremal values."""

    values = []

    for weights in product(*(bounds for _, bounds in rules)):
        if sum(weights):
            moment = sum(Fraction(weight) * Fraction(value)
                         for weight, (value, _) in zip(weights, rules, strict=True))
            values.append(moment / sum(map(Fraction, weights)))

    assert Reduce(rules) == (float(min(values)), float(max(values))), "Switch search must attain both vertex extrema"


@pytest.mark.parametrize("bounds", ((0.0, 0.0), (0.7, 0.3), (-0.1, 0.2), (0.1, 1.2), (0.1, float("nan"))))
def test_RejectsInvalidOrEmptyFiring(bounds):
    """Reject invalid membership grades or absence of positive firing."""

    message = "No rule can fire" if bounds == (0.0, 0.0) else "firing bounds must be ordered"

    with pytest.raises(ValueError, match=message):
        Reduce(((10.0, bounds),))


def test_ThresholdUncertaintyChangesInterpretation():
    """The conditional range can cross the alert threshold at a fixed input."""

    lower, upper = Monitor(80.0)
    point, _ = Monitor(80.0, shift=0)

    assert lower <= point < 200 < upper, "At 80% CPU, the uncertain range should straddle 200 ms"


def test_MembershipEnvelopeRemainsOrderedOnGrid():
    """Verify interval ordering and containment of the zero-uncertainty model."""

    for load in range(101):
        lower, upper = Monitor(load)
        point, _ = Monitor(load, shift=0)

        assert lower <= point <= upper, f"Threshold envelope lost the nominal model at load {load}"

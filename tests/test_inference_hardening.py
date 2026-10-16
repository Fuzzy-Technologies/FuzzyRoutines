# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Independent piecewise envelopes and exact-input numerical audit regressions."""

from fractions import Fraction
from itertools import combinations, pairwise

import pytest

from fuzzyroutines import (
    Bell,
    Centroid,
    CentroidPolicy,
    ContinuousUniverse,
    IntegrationDomain,
    LinguisticTerm,
    NegationPolicy,
    ScalarFuzzySet,
    SNormPolicy,
    SShoulder,
    TNormPolicy,
    Trapezoid,
    Triangle,
)
from fuzzyroutines.exceptions import NumericalError
from fuzzyroutines.inference import (
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    MamdaniModel,
    MamdaniRule,
    SugenoModel,
    SugenoRule,
    TermCondition,
)

POLICY = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))


def One(coordinate):
    """Activate every audit rule independently of its input coordinate."""

    return 1.0


def EnvelopeCentroid(shapes, heights, bounds):
    """Integrate an independently constructed exact clipped-triangle envelope."""

    lower, upper = map(Fraction, bounds)
    pieces = []
    knots = {lower, upper}

    for shape, height in zip(shapes, heights, strict=True):
        left, peak, right = map(Fraction, shape)
        height = Fraction(height)
        vertices = ((left, Fraction(0)), (left + (peak - left) * height, height),
                    (right - (right - peak) * height, height), (right, Fraction(0)))

        for (start, first), (stop, last) in pairwise(vertices):
            if start < stop:
                slope = (last - first) / (stop - start)
                pieces.append((start, stop, slope, first - slope * start))
                knots.update((max(lower, min(upper, start)), max(lower, min(upper, stop))))

    for first, second in combinations(pieces, 2):
        start = max(lower, first[0], second[0])
        stop = min(upper, first[1], second[1])

        if first[2] != second[2]:
            crossing = (second[3] - first[3]) / (first[2] - second[2])

            if start < crossing < stop:
                knots.add(crossing)

    area, moment = Fraction(0), Fraction(0)
    ordered = sorted(knots)

    for start, stop in pairwise(ordered):
        midpoint = (start + stop) / 2
        active = [piece for piece in pieces if piece[0] <= midpoint <= piece[1]]

        if active:
            piece = max(active, key=lambda item: item[2] * midpoint + item[3])
            first, last = piece[2] * start + piece[3], piece[2] * stop + piece[3]
            width = stop - start
            segmentArea = width * (first + last) / 2
            area += segmentArea
            moment += start * segmentArea + width**2 * (first + 2 * last) / 6

    return float(moment / area)


@pytest.mark.parametrize(("shapes", "weights", "bounds"), (
    (((0.1, 0.15, 0.2),), (1.0,), (0.0, 1.0)),
    (((0.16, 0.18, 0.20), (0.60, 0.75, 0.90)), (1.0, 1.0), (0.0, 1.0)),
    (((0.1, 0.3, 0.7), (0.2, 0.6, 0.9)), (0.3, 0.7), (0.0, 1.0)),
    (((0.1, 0.3, 0.7), (0.2, 0.6, 0.9)), (0.3, 0.7), (0.12, 0.84)),
    (((0.16, 0.18, 0.20), (0.60, 0.75, 0.90)), (0.0, 0.4), (0.0, 1.0)),
    (((100.1, 100.15, 100.2), (100.6, 100.75, 100.9)), (0.2, 0.8), (100.0, 101.0)),
    (((-10.0, -9.0, -8.0), (2.0, 4.0, 6.0)), (0.8, 0.3), (-12.0, 8.0)),
))
def test_MamdaniRetainsEveryBuiltInConsequent(shapes, weights, bounds):
    """Compare missing, clipped, overlapping and translated pieces to exact geometry."""

    universe = ContinuousUniverse(bounds[0], bounds[1], True, True)
    inputVariable = FuzzyVariable("x", (LinguisticTerm("on", ScalarFuzzySet(universe, One)),))
    output = FuzzyVariable("y", tuple(
        LinguisticTerm(str(index), ScalarFuzzySet(universe, Triangle(*shape)))
        for index, shape in enumerate(shapes)
    ))
    rules = tuple(MamdaniRule(str(index), TermCondition("x", "on"), str(index), weight)
                  for index, weight in enumerate(weights))
    model = MamdaniModel((inputVariable,), output, rules, POLICY, TNormPolicy("logic"), SNormPolicy("logic"))
    domain = IntegrationDomain(*bounds)
    result = model.Evaluate({"x": bounds[0]}, domain)
    expected = EnvelopeCentroid(shapes, weights, bounds)

    assert result.value == pytest.approx(expected, rel=0, abs=2e-10), "Every fired piece must participate in the global centroid"
    assert Centroid(result.outputSet, domain) == result.value, "Exposed output must retain the same trusted partition"
    assert result.method == "adaptive-simpson", "A partition is not an analytical certificate"


def test_LocalizedTriangleNeedsNoAdditionalDepth():
    """Known linear pieces must be integrated even with zero subdivision budget."""

    from fuzzyroutines.defuzzification import _IntegrationPoints, _PartitionedMembership

    source = ScalarFuzzySet(ContinuousUniverse(), Triangle(0.1, 0.15, 0.2))
    wrapped = ScalarFuzzySet(source.universe, _PartitionedMembership(source.Membership, _IntegrationPoints(source)))
    actual = Centroid(wrapped, IntegrationDomain(0, 1), CentroidPolicy(maximumDepth=0))

    assert actual == pytest.approx(0.15, rel=0, abs=1e-15), "Trusted knots must expose positive area before adaptive refinement"


@pytest.mark.parametrize(("grade", "bounds"), ((1.0, (1e-200, 3e-200)), (1e-200, (1e-200, 3e-200)), (1.0, (0.0, 5e-324))))
def test_AdaptiveUnderflowCannotReturnAnErasedCentroid(grade, bounds):
    """Reject lost constant-area moments instead of returning a false zero."""

    source = ScalarFuzzySet(ContinuousUniverse(), lambda coordinate: grade)

    with pytest.raises(NumericalError, match="underflow"):
        Centroid(source, IntegrationDomain(*bounds))


@pytest.mark.parametrize(("membership", "bounds", "expected"), (
    (Triangle(1e-200, 2e-200, 3e-200), (0, 4e-200), 2e-200),
    (Triangle(1e-160, 2e-160, 3e-160), (0, 4e-160), 2e-160),
    (Trapezoid(1e-200, 2e-200, 3e-200, 4e-200), (0, 5e-200), 2.5e-200),
    (SShoulder(0, 1e-200), (0, 1e-200), 17 / 24 * 1e-200),
    (Bell(0, 1e-200, 2e-200), (0, 3e-200), 1.5e-200),
    (Triangle(1e200, 2e200, 3e200), (0, 4e200), 2e200),
))
def test_PolynomialCentroidDoesNotRequireRepresentableMoments(membership, bounds, expected):
    """Keep a representable ratio when polynomial moments underflow or overflow."""

    actual = Centroid(ScalarFuzzySet(ContinuousUniverse(), membership), IntegrationDomain(*bounds))

    assert actual == pytest.approx(expected, rel=2e-15, abs=0), "Moment intermediates must not erase a representable centroid"


def test_PositiveProductUnderflowIsNotNoFire():
    """Reject lost positive firing strength without changing the float trace contract."""

    def Tiny(coordinate):
        """Return an explicitly positive representable antecedent grade."""

        return 1e-200

    variable = FuzzyVariable("x", (LinguisticTerm("on", ScalarFuzzySet(ContinuousUniverse(), Tiny)),))
    model = SugenoModel((variable,), (SugenoRule("tiny", TermCondition("x", "on"), ConstantConsequent(0.5), 1e-200),), POLICY, ContinuousUniverse())

    with pytest.raises(NumericalError, match="positive rule firing strength underflowed"):
        model.Evaluate({"x": 0})


def test_PartitionsShareOneGlobalMomentBudget():
    """Integrate a non-Simpson-exact polynomial across many initial partitions."""

    from fuzzyroutines.defuzzification import _AdaptiveMoments, _PartitionedMembership

    def SixthPower(coordinate):
        """Provide independent elementary moments 1/7 and 1/8 on the unit interval."""

        return coordinate**6

    points = tuple(index / 10 for index in range(1, 10))
    fuzzySet = ScalarFuzzySet(ContinuousUniverse(), _PartitionedMembership(SixthPower, points))
    area, moment = _AdaptiveMoments(fuzzySet, IntegrationDomain(0, 1), CentroidPolicy(1e-13, 1e-13))

    assert area == pytest.approx(1 / 7, rel=0, abs=2e-13), "Each partition must share rather than reset the area tolerance"
    assert moment == pytest.approx(1 / 8, rel=0, abs=2e-13), "The first-moment tolerance must apply to the global sum"


@pytest.mark.parametrize("weight", (5e-324, 1e-323, 1e-320))
def test_SubnormalNormalizedWeightRetainsFiniteContribution(weight):
    """Use exact binary64-input ratios as an oracle for tiny weights and huge outputs."""

    variable = FuzzyVariable("x", (LinguisticTerm("on", ScalarFuzzySet(ContinuousUniverse(), One)),))
    weights, values = (weight, 1.0, 1.0), (1e308, 0.0, 0.0)
    rules = tuple(SugenoRule(str(index), TermCondition("x", "on"), ConstantConsequent(value), strength)
                  for index, (strength, value) in enumerate(zip(weights, values, strict=True)))
    result = SugenoModel((variable,), rules, POLICY, ContinuousUniverse()).Evaluate({"x": 0})
    expected = float(Fraction(weight) * Fraction(1e308) / (Fraction(weight) + 2))

    assert result.value == pytest.approx(expected, rel=2e-15, abs=0), "Normalization must preserve representable tiny contributions"
    assert result.rules[0].normalizedStrength > 0, "A positive exact normalized trace must not become a zero sentinel"
    assert result.rules[0].contribution == expected, "The retained exact weight must explain its numerical contribution"

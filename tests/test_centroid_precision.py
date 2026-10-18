# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Independent exact polynomial integrals at restricted centroid boundaries."""

import math
from fractions import Fraction

import pytest

from fuzzyroutines import (
    Bell,
    Centroid,
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
    FuzzyVariable,
    InferencePolicy,
    MamdaniModel,
    MamdaniRule,
    TermCondition,
)


def PolynomialCentroid(coefficients, bounds):
    """Integrate exact monomials independently of the production shifted panels."""

    left, right = map(Fraction, bounds)
    area = sum((Fraction(value) * (right ** (power + 1) - left ** (power + 1)) / (power + 1)
                for power, value in enumerate(coefficients)), Fraction(0))
    moment = sum((Fraction(value) * (right ** (power + 2) - left ** (power + 2)) / (power + 2)
                  for power, value in enumerate(coefficients)), Fraction(0))

    return moment / area


@pytest.mark.parametrize(("membership", "coefficients", "left"), (
    (Triangle(0.0, 1.0, 2.0), (0, 1), 0.99),
    (Triangle(0.0, 1.0, 2.0), (2, -1), 1.99),
    (Trapezoid(0.0, 1.0, 2.0, 3.0), (0, 1), 0.99),
    (Trapezoid(0.0, 1.0, 2.0, 3.0), (1,), 1.99),
    (Trapezoid(0.0, 1.0, 2.0, 3.0), (3, -1), 2.99),
    (SShoulder(0.0, 1.0), (0, 0, 2), 0.49),
    (SShoulder(0.0, 1.0), (-1, 4, -2), 0.99),
    (Bell(0.0, 1.0, 2.0), (0, 0, 2), 0.49),
    (Bell(0.0, 1.0, 2.0), (-1, 4, -2), 0.99),
    (Bell(0.0, 1.0, 2.0), (1,), 1.99),
    (Bell(0.0, 1.0, 2.0), (-7, 8, -2), 2.49),
    (Bell(0.0, 1.0, 2.0), (18, -12, 2), 2.99),
))
@pytest.mark.parametrize("width", (9 * math.ulp(0.99), 1e-10))
def test_RestrictedPolynomialWindowsMatchExactIntegrals(membership, coefficients, left, width):
    """Keep every polynomial branch accurate and contained on narrow float windows."""

    domain = IntegrationDomain(left, left + width)
    expected = float(PolynomialCentroid(coefficients, (domain.left, domain.right)))
    actual = Centroid(ScalarFuzzySet(ContinuousUniverse(), membership), domain)

    assert domain.Contains(actual), "A positive-area centroid must remain inside its integration window"
    assert abs(actual - expected) <= 2 * math.ulp(expected), "Nearby antiderivative endpoints must not erase significant digits"


@pytest.mark.parametrize("bounds", ((0.9, 0.9000000001), (0.99, 0.990000000000001)))
def test_RestrictedTriangleAuditWindowsRetainContainment(bounds):
    """Reproduce both release-audit windows against the exact integral of mu(x)=x."""

    domain = IntegrationDomain(*bounds)
    actual = Centroid(ScalarFuzzySet(ContinuousUniverse(), Triangle(0.0, 1.0, 2.0)), domain)
    expected = float(PolynomialCentroid((0, 1), bounds))

    assert domain.Contains(actual), "Restricted-window cancellation must not return an out-of-domain centroid"
    assert abs(actual - expected) <= 2 * math.ulp(expected), "The narrow-window centroid must match exact input arithmetic"


@pytest.mark.parametrize("base", (Fraction(1), Fraction(1) + Fraction(1, 10**30), 2**54))
@pytest.mark.parametrize("family", ("triangle", "trapezoid", "shoulder", "bell"))
def test_OriginalRationalGeometrySurvivesBinary64Collapse(base, family):
    """Preserve exact vertices, windows and centroids when distinct reals share a float."""

    step = Fraction(1) if isinstance(base, int) else Fraction(1, 10**30)
    left, first, second, right = (base + index * step for index in range(4))

    if family == "triangle":
        membership = Triangle(left, first, second)
        domain = IntegrationDomain(left, second)
        expected = (Fraction(left) + first + second) / 3

    elif family == "trapezoid":
        membership = Trapezoid(left, first, second, right)
        domain = IntegrationDomain(left, right)
        expected = (Fraction(left) + right) / 2

    elif family == "shoulder":
        membership = SShoulder(left, second)
        domain = IntegrationDomain(left, second)
        expected = left + Fraction(17, 24) * (second - left)

    else:
        membership = Bell(left, first, second)
        domain = IntegrationDomain(left, right)
        expected = (Fraction(left) + right) / 2

    actual = Centroid(ScalarFuzzySet(ContinuousUniverse(), membership), domain)

    assert domain.Contains(actual), "Rounding exact geometry must not move its centroid outside the original window"
    assert actual == expected, "Polynomial rational fallback must preserve original values before taking the ratio"


def test_RationalTriangleRetainsPositiveAreaOnBroadFloatWindow():
    """Avoid merging rational vertices even when only the shape needs exact arithmetic."""

    step = Fraction(1, 10**30)
    membership = Triangle(Fraction(1), 1 + step, 1 + 2 * step)
    actual = Centroid(ScalarFuzzySet(ContinuousUniverse(), membership), IntegrationDomain(0, 2))

    assert actual == 1 + step, "Valid positive-area rational shapes must not become zero-width float shapes"


def RationalMamdani(shapes):
    """Build fully fired max/min rules independently of input geometry."""

    inputVariable = FuzzyVariable("x", (LinguisticTerm("on", ScalarFuzzySet(ContinuousUniverse(), lambda coordinate: 1.0)),))
    outputVariable = FuzzyVariable("y", tuple(
        LinguisticTerm(str(index), ScalarFuzzySet(ContinuousUniverse(), Triangle(*shape)))
        for index, shape in enumerate(shapes)
    ))
    rules = tuple(MamdaniRule(str(index), TermCondition("x", "on"), str(index)) for index in range(len(shapes)))
    policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))

    return MamdaniModel((inputVariable,), outputVariable, rules, policy, TNormPolicy("logic"), SNormPolicy("logic"))


@pytest.mark.parametrize("arrangement", ("single", "disjoint", "overlapping"))
def test_MamdaniRetainsOriginalRationalSupportKnots(arrangement):
    """Expose every trusted positive-area support even when its float vertices coincide."""

    step = Fraction(1, 10**30)
    shapes = ((Fraction(1), 1 + step, 1 + 2 * step),)
    expected = 1 + step

    if arrangement == "disjoint":
        second = Fraction(3, 2)
        shapes += ((second, second + 2 * step, second + 4 * step),)
        # Disjoint triangle areas are step and 2*step, respectively.
        expected = ((1 + step) + 2 * (second + 2 * step)) / 3

    elif arrangement == "overlapping":
        shapes = ((Fraction(1), 1 + 2 * step, 1 + 4 * step),
                  (1 + 2 * step, 1 + 4 * step, 1 + 6 * step))
        # Reflection about 1+3*step preserves the complete maximum envelope.
        expected = 1 + 3 * step

    domain = IntegrationDomain(0, 2)
    result = RationalMamdani(shapes).Evaluate({"x": 0}, domain)

    assert domain.Contains(result.value), "Trusted rational support must produce a contained centroid"
    assert result.value == pytest.approx(float(expected), rel=0, abs=2e-15), "Every fired support must participate in the independent envelope oracle"


def test_MamdaniRejectsRoundedCentroidOutsideRationalWindow():
    """Fail explicitly when mixed adaptive arithmetic cannot represent a contained output."""

    step = Fraction(1, 10**30)
    shape = (1 + step, 1 + 2 * step, 1 + 3 * step)
    domain = IntegrationDomain(shape[0], shape[2])

    with pytest.raises(NumericalError, match="outside integration domain at working precision"):
        RationalMamdani((shape,)).Evaluate({"x": 0}, domain)


def test_AdaptiveFloatCallbackRejectsUnrepresentableRationalWindow():
    """Reject a rounded float centroid when no float belongs to the requested window."""

    step = Fraction(1, 10**30)
    domain = IntegrationDomain(1 + step, 1 + 3 * step)
    source = ScalarFuzzySet(ContinuousUniverse(), lambda coordinate: 1.0)

    with pytest.raises(NumericalError, match="outside integration domain at working precision"):
        Centroid(source, domain)


def test_AdaptiveRationalCallbackRetainsContainedExactCentroid():
    """Preserve wholly rational adaptive arithmetic inside a window without float coordinates."""

    step = Fraction(1, 10**30)
    domain = IntegrationDomain(1 + step, 1 + 3 * step)
    source = ScalarFuzzySet(ContinuousUniverse(), lambda coordinate: Fraction(1))
    actual = Centroid(source, domain)

    assert actual == 1 + 2 * step, "A rational callback must retain its exact constant-area centroid"
    assert domain.Contains(actual), "Exact rational arithmetic must remain usable when binary64 has no interior coordinate"


def test_AdjacentFloatWindowRetainsRoundedContainedCentroid():
    """Accept a contained rounded centroid when adjacent float endpoints have no float interior."""

    domain = IntegrationDomain(1.0, math.nextafter(1.0, math.inf))
    source = ScalarFuzzySet(ContinuousUniverse(), lambda coordinate: 1.0)
    expected = float((Fraction(domain.left) + Fraction(domain.right)) / 2)
    actual = Centroid(source, domain)

    assert actual == expected, "An exact midpoint may round to an included endpoint without becoming invalid"
    assert domain.Contains(actual), "Adjacent included float endpoints must retain a valid rounded result"

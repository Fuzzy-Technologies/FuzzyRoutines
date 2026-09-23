# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic centroid defuzzification for continuous scalar fuzzy sets.

Analytical moments are used for the supported polynomial and Gaussian
membership families. Other continuous callables use explicitly configured
adaptive Simpson quadrature. Importing this module performs no evaluation or
I/O.
"""

import math
from dataclasses import dataclass
from numbers import Integral, Real

from fuzzyroutines.domain import (
    ContinuousUniverse,
    IntegrationDomain,
    _RequireFiniteReal,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet, _ContinuousAnalyticalSource


class CentroidConvergenceError(ArithmeticError):
    """Adaptive centroid integration that exhausted its subdivision limit."""


@dataclass(frozen=True, slots=True)
class CentroidPolicy:
    """Immutable error and work limits for adaptive centroid integration.

    Attributes:
        absoluteTolerance: Absolute error target for the membership area.
        relativeTolerance: Relative error target for both calculated moments.
        maximumDepth: Maximum recursive bisection depth for one interval.

    Notes:
        The first-moment absolute target is `absoluteTolerance` multiplied by
        the largest absolute coordinate in the integration domain. Analytical
        paths do not consume this policy because they do not iterate.
    """

    absoluteTolerance: Real = 1e-12
    relativeTolerance: Real = 1e-10
    maximumDepth: int = 20

    def __post_init__(self):
        """Validate finite positive tolerances and a non-negative work limit."""

        absoluteTolerance = _RequireFiniteReal(self.absoluteTolerance, "absoluteTolerance")
        relativeTolerance = _RequireFiniteReal(self.relativeTolerance, "relativeTolerance")

        if absoluteTolerance <= 0:
            raise ValueError("absoluteTolerance must be greater than zero")

        if relativeTolerance <= 0:
            raise ValueError("relativeTolerance must be greater than zero")

        if isinstance(self.maximumDepth, bool) or not isinstance(self.maximumDepth, Integral):
            raise TypeError("maximumDepth must be an integer")

        if self.maximumDepth < 0:
            raise ValueError("maximumDepth must be non-negative")


def _PolynomialMoments(left, right, origin, constant, linear, quadratic):
    """Return exact binary64 integrals of a shifted quadratic and its moment."""

    leftOffset = left - origin
    rightOffset = right - origin
    firstPower = rightOffset - leftOffset
    secondPower = rightOffset**2 - leftOffset**2
    thirdPower = rightOffset**3 - leftOffset**3
    fourthPower = rightOffset**4 - leftOffset**4
    area = constant * firstPower + linear * secondPower / 2 + quadratic * thirdPower / 3
    localMoment = constant * secondPower / 2 + linear * thirdPower / 3 + quadratic * fourthPower / 4
    return area, origin * area + localMoment


def _AddSegment(moments, domain, left, right, origin, constant, linear, quadratic):
    """Add one clipped shifted-polynomial segment to accumulated moments."""

    clippedLeft = max(domain.left, left)
    clippedRight = min(domain.right, right)

    if clippedLeft >= clippedRight:
        return moments

    area, firstMoment = _PolynomialMoments(
        clippedLeft,
        clippedRight,
        origin,
        constant,
        linear,
        quadratic,
    )
    return moments[0] + area, moments[1] + firstMoment


def _PolynomialFamilyMoments(membershipFunction, domain):
    """Return analytical moments for supported piecewise-polynomial families."""

    parameters = membershipFunction.parameters
    familyName = membershipFunction.name
    moments = (0.0, 0.0)

    if familyName == "Triangle":
        leftFoot = parameters["a"]
        rightFoot = parameters["b"]
        apex = parameters["c"]
        moments = _AddSegment(moments, domain, leftFoot, apex, leftFoot, 0.0, 1 / (apex - leftFoot), 0.0)

        if apex == rightFoot:
            return moments

        return _AddSegment(moments, domain, apex, rightFoot, rightFoot, 0.0, -1 / (rightFoot - apex), 0.0)

    if familyName == "Trapezium":
        leftFoot = parameters["a"]
        rightFoot = parameters["b"]
        leftCore = parameters["c"]
        rightCore = parameters["d"]
        moments = _AddSegment(moments, domain, leftFoot, leftCore, leftFoot, 0.0, 1 / (leftCore - leftFoot), 0.0)
        moments = _AddSegment(moments, domain, leftCore, rightCore, leftCore, 1.0, 0.0, 0.0)
        return _AddSegment(moments, domain, rightCore, rightFoot, rightFoot, 0.0, -1 / (rightFoot - rightCore), 0.0)

    left = parameters["a"]
    right = parameters["b"]
    width = right - left
    midpoint = (left + right) / 2
    moments = _AddSegment(moments, domain, left, midpoint, left, 0.0, 0.0, 2 / width**2)
    moments = _AddSegment(moments, domain, midpoint, right, right, 1.0, 0.0, -2 / width**2)

    if familyName == "Parabolic":
        return _AddSegment(moments, domain, right, domain.right, right, 1.0, 0.0, 0.0)

    coreRight = parameters["c"]
    rightBoundary = coreRight + width
    rightMidpoint = coreRight + width / 2
    moments = _AddSegment(moments, domain, right, coreRight, right, 1.0, 0.0, 0.0)
    moments = _AddSegment(moments, domain, coreRight, rightMidpoint, coreRight, 1.0, 0.0, -2 / width**2)
    return _AddSegment(moments, domain, rightMidpoint, rightBoundary, rightBoundary, 0.0, 0.0, 2 / width**2)


def _GaussianMoments(membershipFunction, domain):
    """Return stable closed-form Gaussian area and first moment when resolvable."""

    centre = membershipFunction.parameters["a"]
    deviation = membershipFunction.parameters["b"]
    leftDistance = (domain.left - centre) / deviation
    rightDistance = (domain.right - centre) / deviation
    errorDifference = math.erf(rightDistance / math.sqrt(2)) - math.erf(leftDistance / math.sqrt(2))
    area = deviation * math.sqrt(math.pi / 2) * errorDifference
    firstMoment = centre * area + deviation**2 * (
        math.exp(-0.5 * leftDistance**2) - math.exp(-0.5 * rightDistance**2)
    )
    return area, firstMoment


def _SimpsonEstimate(left, right, leftValues, midpointValues, rightValues):
    """Return Simpson estimates for area and first moment on one interval."""

    scale = (right - left) / 6
    return (
        scale * (leftValues[0] + 4 * midpointValues[0] + rightValues[0]),
        scale * (leftValues[1] + 4 * midpointValues[1] + rightValues[1]),
    )


def _AdaptiveMoments(fuzzySet, domain, policy):
    """Integrate both centroid moments with deterministic adaptive Simpson work."""

    def Evaluate(coordinate):
        grade = fuzzySet.Membership(coordinate)
        return grade, coordinate * grade

    coordinateScale = max(abs(domain.left), abs(domain.right), 1.0)

    def Refine(left, right, leftValues, midpointValues, rightValues, estimate, depth):
        midpoint = (left + right) / 2
        leftMidpoint = (left + midpoint) / 2
        rightMidpoint = (midpoint + right) / 2
        leftMidpointValues = Evaluate(leftMidpoint)
        rightMidpointValues = Evaluate(rightMidpoint)
        leftEstimate = _SimpsonEstimate(left, midpoint, leftValues, leftMidpointValues, midpointValues)
        rightEstimate = _SimpsonEstimate(midpoint, right, midpointValues, rightMidpointValues, rightValues)
        refined = (leftEstimate[0] + rightEstimate[0], leftEstimate[1] + rightEstimate[1])
        areaError = abs(refined[0] - estimate[0]) / 15
        momentError = abs(refined[1] - estimate[1]) / 15
        areaTarget = policy.absoluteTolerance + policy.relativeTolerance * abs(refined[0])
        momentTarget = policy.absoluteTolerance * coordinateScale + policy.relativeTolerance * abs(refined[1])

        if areaError <= areaTarget and momentError <= momentTarget:
            return (
                refined[0] + (refined[0] - estimate[0]) / 15,
                refined[1] + (refined[1] - estimate[1]) / 15,
            )

        if depth >= policy.maximumDepth:
            raise CentroidConvergenceError(
                "centroid integration did not converge within maximumDepth="
                f"{policy.maximumDepth}"
            )

        leftResult = Refine(
            left,
            midpoint,
            leftValues,
            leftMidpointValues,
            midpointValues,
            leftEstimate,
            depth + 1,
        )
        rightResult = Refine(
            midpoint,
            right,
            midpointValues,
            rightMidpointValues,
            rightValues,
            rightEstimate,
            depth + 1,
        )
        return leftResult[0] + rightResult[0], leftResult[1] + rightResult[1]

    midpoint = (domain.left + domain.right) / 2
    leftValues = Evaluate(domain.left)
    midpointValues = Evaluate(midpoint)
    rightValues = Evaluate(domain.right)
    estimate = _SimpsonEstimate(domain.left, domain.right, leftValues, midpointValues, rightValues)
    return Refine(
        domain.left,
        domain.right,
        leftValues,
        midpointValues,
        rightValues,
        estimate,
        0,
    )


def Centroid(fuzzySet: ScalarFuzzySet, integrationDomain: IntegrationDomain, policy: CentroidPolicy | None = None):
    r"""Return the continuous center-of-area over an explicit finite domain.

    The result is
    $\int x\mu(x)\,dx / \int \mu(x)\,dx$. Piecewise-polynomial and Gaussian
    `MFunction` sources use analytical moments when the closed form is stable;
    all other callables use adaptive Simpson quadrature.

    Args:
        fuzzySet: Continuous scalar fuzzy set evaluated without retained state.
        integrationDomain: Finite closed interval contained in the set universe.
        policy: Immutable adaptive tolerance and work configuration. `None`
            selects [CentroidPolicy][fuzzyroutines.defuzzification.CentroidPolicy].

    Returns:
        Finite centroid coordinate within `integrationDomain`.

    Raises:
        TypeError: The set, universe, domain, or policy has the wrong type.
        ValueError: The domain lies outside the universe or membership area is
            zero or non-finite.
        CentroidConvergenceError: Adaptive quadrature exceeds `maximumDepth`.

    Notes:
        Generic callables are assumed sufficiently regular for adaptive
        quadrature. A callable with unresolved features between every sampled
        coordinate requires an analytical family or a separately approved
        partitioned-domain API; no fixed fallback grid is used.
    """

    if not isinstance(fuzzySet, ScalarFuzzySet):
        raise TypeError("fuzzySet must be a ScalarFuzzySet")

    if not isinstance(fuzzySet.universe, ContinuousUniverse):
        raise TypeError("continuous centroid requires a ContinuousUniverse")

    if not isinstance(integrationDomain, IntegrationDomain):
        raise TypeError("integrationDomain must be an IntegrationDomain")

    if policy is None:
        policy = CentroidPolicy()

    elif not isinstance(policy, CentroidPolicy):
        raise TypeError("policy must be a CentroidPolicy")

    integrationDomain.ValidateWithin(fuzzySet.universe)
    analyticalSource = _ContinuousAnalyticalSource(fuzzySet)
    moments = None

    if analyticalSource is not None and analyticalSource.name in {"Triangle", "Trapezium", "Parabolic", "Bell"}:
        moments = _PolynomialFamilyMoments(analyticalSource, integrationDomain)

    elif analyticalSource is not None and analyticalSource.name == "Exponential":
        candidateMoments = _GaussianMoments(analyticalSource, integrationDomain)

        if candidateMoments[0] > 0 and all(math.isfinite(value) for value in candidateMoments):
            moments = candidateMoments

    if moments is None:
        moments = _AdaptiveMoments(fuzzySet, integrationDomain, policy)

    area, firstMoment = moments

    if not math.isfinite(area) or not math.isfinite(firstMoment):
        raise ValueError("centroid moments must be finite")

    if area <= 0:
        raise ValueError("centroid is undefined for zero membership area")

    centroid = firstMoment / area

    if not math.isfinite(centroid):
        raise ValueError("centroid must be finite")

    return centroid

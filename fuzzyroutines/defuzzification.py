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
from collections.abc import Mapping
from dataclasses import dataclass
from numbers import Integral
from typing import cast

from fuzzyroutines.domain import (
    ContinuousUniverse,
    IntegrationDomain,
)
from fuzzyroutines.exceptions import (
    InvalidParameterError,
    InvalidParameterTypeError,
    NumericalError,
    UndefinedResultError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet, _ContinuousAnalyticalSource
from fuzzyroutines.membership import MembershipScalar, _AnalyticalSource
from fuzzyroutines.numeric import _RequireFiniteReal


class CentroidConvergenceError(NumericalError):
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
        the largest absolute coordinate in the integration domain. Polynomial
        analytical paths do not iterate. Gaussian moments use
        `relativeTolerance` to reject unresolved closed-form subtraction before
        delegating to adaptive integration with this same policy.
    """

    absoluteTolerance: MembershipScalar = 1e-12
    relativeTolerance: MembershipScalar = 1e-10
    maximumDepth: int = 20

    def __post_init__(self) -> None:
        """Validate finite positive tolerances and a non-negative work limit."""

        absoluteTolerance = _RequireFiniteReal(self.absoluteTolerance, "absoluteTolerance")
        relativeTolerance = _RequireFiniteReal(self.relativeTolerance, "relativeTolerance")

        if absoluteTolerance <= 0:
            raise InvalidParameterError("absoluteTolerance must be greater than zero")

        if relativeTolerance <= 0:
            raise InvalidParameterError("relativeTolerance must be greater than zero")

        if isinstance(self.maximumDepth, bool) or not isinstance(self.maximumDepth, Integral):
            raise InvalidParameterTypeError("maximumDepth must be an integer")

        if self.maximumDepth < 0:
            raise InvalidParameterError("maximumDepth must be non-negative")


def _PolynomialMoments(
    left: float,
    right: float,
    origin: float,
    constant: float,
    linear: float,
    quadratic: float,
) -> tuple[float, float]:
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


def _AddSegment(
    moments: tuple[float, float],
    domain: IntegrationDomain,
    left: float,
    right: float,
    origin: float,
    constant: float,
    linear: float,
    quadratic: float,
) -> tuple[float, float]:
    """Add one clipped shifted-polynomial segment to accumulated moments."""

    clippedLeft = max(cast(float, domain.left), left)
    clippedRight = min(cast(float, domain.right), right)

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


def _PolynomialFamilyMoments(
    membershipFunction: _AnalyticalSource,
    domain: IntegrationDomain,
) -> tuple[float, float]:
    """Return analytical moments for supported piecewise-polynomial families."""

    parameters = cast(Mapping[str, float], membershipFunction.parameters)
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
        return _AddSegment(moments, domain, right, cast(float, domain.right), right, 1.0, 0.0, 0.0)

    coreRight = parameters["c"]
    rightBoundary = coreRight + width
    rightMidpoint = coreRight + width / 2
    moments = _AddSegment(moments, domain, right, coreRight, right, 1.0, 0.0, 0.0)
    moments = _AddSegment(moments, domain, coreRight, rightMidpoint, coreRight, 1.0, 0.0, -2 / width**2)
    return _AddSegment(moments, domain, rightMidpoint, rightBoundary, rightBoundary, 0.0, 0.0, 2 / width**2)


def _GaussianMoments(
    membershipFunction: _AnalyticalSource,
    domain: IntegrationDomain,
    policy: CentroidPolicy,
) -> tuple[float, float] | None:
    """Return resolved Gaussian moments, or request configured adaptive work.

    Same-sided tails subtract erfc values rather than two erf values near one.
    A first-order resolution estimate accounts for endpoint normalization and
    special-function rounding; it is a method-selection guard, not a rigorous
    error certificate. Unresolved or out-of-domain results fail closed to the
    caller's existing adaptive policy instead of being clamped.
    """

    centre = cast(float, membershipFunction.parameters["a"])
    deviation = cast(float, membershipFunction.parameters["b"])
    leftDistance = (cast(float, domain.left) - centre) / deviation
    rightDistance = (cast(float, domain.right) - centre) / deviation
    rootTwo = math.sqrt(2)
    leftArgument = leftDistance / rootTwo
    rightArgument = rightDistance / rootTwo

    if leftDistance >= 0:
        leftValue = math.erfc(leftArgument)
        rightValue = math.erfc(rightArgument)
        errorDifference = leftValue - rightValue

    elif rightDistance <= 0:
        leftValue = math.erfc(-leftArgument)
        rightValue = math.erfc(-rightArgument)
        errorDifference = rightValue - leftValue

    else:
        leftValue = math.erf(leftArgument)
        rightValue = math.erf(rightArgument)
        errorDifference = rightValue - leftValue

    if errorDifference <= 0 or not math.isfinite(errorDifference):
        return None

    resolutionEstimate = math.ulp(leftValue) + math.ulp(rightValue)

    for distance, argument in (
        (leftDistance, leftArgument),
        (rightDistance, rightArgument),
    ):
        if math.isfinite(argument):
            # Two normalizing operations precede division by sqrt(2). The
            # erf/erfc derivative converts their ULP scale to area resolution.
            argumentResolution = 2 * math.ulp(distance) / rootTwo + math.ulp(argument)
            resolutionEstimate += (
                2 / math.sqrt(math.pi)
                * math.exp(-argument * argument)
                * argumentResolution
            )

    if resolutionEstimate > cast(float, policy.relativeTolerance) * errorDifference:
        return None

    leftExponent = -0.5 * leftDistance * leftDistance
    rightExponent = -0.5 * rightDistance * rightDistance
    squaredDistanceDifference = (rightDistance - leftDistance) * (
        rightDistance + leftDistance
    )

    if not math.isfinite(squaredDistanceDifference):
        # At an infinite standardized endpoint its exponential is exactly
        # zero in binary64, so direct subtraction cannot cancel two tails.
        exponentialDifference = math.exp(leftExponent) - math.exp(rightExponent)

    elif squaredDistanceDifference >= 0:
        exponentialDifference = math.exp(leftExponent) * (
            -math.expm1(-0.5 * squaredDistanceDifference)
        )

    else:
        exponentialDifference = math.exp(rightExponent) * math.expm1(
            0.5 * squaredDistanceDifference
        )

    standardizedArea = math.sqrt(math.pi / 2) * errorDifference
    area = deviation * standardizedArea
    centroid = centre + deviation * (exponentialDifference / standardizedArea)
    firstMoment = area * centroid

    if (
        area <= 0
        or not all(math.isfinite(value) for value in (area, firstMoment, centroid))
        or not domain.Contains(centroid)
    ):
        return None

    return area, firstMoment


def _SimpsonEstimate(
    left: float,
    right: float,
    leftValues: tuple[float, float],
    midpointValues: tuple[float, float],
    rightValues: tuple[float, float],
) -> tuple[float, float]:
    """Return Simpson estimates for area and first moment on one interval."""

    scale = (right - left) / 6
    return (
        scale * (leftValues[0] + 4 * midpointValues[0] + rightValues[0]),
        scale * (leftValues[1] + 4 * midpointValues[1] + rightValues[1]),
    )


def _AdaptiveMoments(
    fuzzySet: ScalarFuzzySet,
    domain: IntegrationDomain,
    policy: CentroidPolicy,
) -> tuple[float, float]:
    """Integrate both centroid moments with deterministic adaptive Simpson work."""

    def Evaluate(coordinate: float) -> tuple[float, float]:
        """Evaluate both real moments without coercing callback results."""

        grade = cast(float, fuzzySet.Membership(coordinate))
        return grade, coordinate * grade

    coordinateScale = max(abs(cast(float, domain.left)), abs(cast(float, domain.right)), 1.0)

    def Refine(
        left: float,
        right: float,
        leftValues: tuple[float, float],
        midpointValues: tuple[float, float],
        rightValues: tuple[float, float],
        estimate: tuple[float, float],
        depth: int,
    ) -> tuple[float, float]:
        """Refine both moments until the configured error target is met."""

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
        areaTarget = cast(float, policy.absoluteTolerance) + cast(float, policy.relativeTolerance) * abs(refined[0])
        momentTarget = cast(float, policy.absoluteTolerance) * coordinateScale + cast(float, policy.relativeTolerance) * abs(refined[1])

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

    midpoint = (cast(float, domain.left) + cast(float, domain.right)) / 2
    leftValues = Evaluate(cast(float, domain.left))
    midpointValues = Evaluate(midpoint)
    rightValues = Evaluate(cast(float, domain.right))
    estimate = _SimpsonEstimate(cast(float, domain.left), cast(float, domain.right), leftValues, midpointValues, rightValues)
    return Refine(
        cast(float, domain.left),
        cast(float, domain.right),
        leftValues,
        midpointValues,
        rightValues,
        estimate,
        0,
    )


def Centroid(
    fuzzySet: ScalarFuzzySet,
    integrationDomain: IntegrationDomain,
    policy: CentroidPolicy | None = None,
) -> MembershipScalar:
    r"""Return the continuous center-of-area over an explicit finite domain.

    The result is
    $\int x\mu(x)\;\mathrm{d}x / \int \mu(x)\;\mathrm{d}x$. Piecewise-polynomial and Gaussian
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
        InvalidParameterTypeError: The set, universe, domain, or policy has the wrong type.
        InvalidDomainError: The domain lies outside the universe.
        UndefinedResultError: Membership area is zero or a computed moment or
            centroid is non-finite.
        CentroidConvergenceError: Adaptive quadrature exceeds `maximumDepth`.

    Notes:
        Generic callables are assumed sufficiently regular for adaptive
        quadrature. A callable with unresolved features between every sampled
        coordinate requires an analytical family or a separately approved
        partitioned-domain API; no fixed fallback grid is used.
    """

    return _Centroid(fuzzySet, integrationDomain, policy, UndefinedResultError)


def _Centroid(
    fuzzySet: ScalarFuzzySet,
    integrationDomain: IntegrationDomain,
    policy: CentroidPolicy | None,
    undefinedError: type[Exception],
) -> MembershipScalar:
    """Evaluate centroid with the caller boundary's explicit result-error type.

    Only engine-owned zero-area and non-finite-result checks use this type.
    Evaluator exceptions and the existing convergence error remain unchanged.
    """

    if not isinstance(fuzzySet, ScalarFuzzySet):
        raise InvalidParameterTypeError("fuzzySet must be a ScalarFuzzySet")

    if not isinstance(fuzzySet.universe, ContinuousUniverse):
        raise InvalidParameterTypeError("continuous centroid requires a ContinuousUniverse")

    if not isinstance(integrationDomain, IntegrationDomain):
        raise InvalidParameterTypeError("integrationDomain must be an IntegrationDomain")

    if policy is None:
        policy = CentroidPolicy()

    elif not isinstance(policy, CentroidPolicy):
        raise InvalidParameterTypeError("policy must be a CentroidPolicy")

    integrationDomain.ValidateWithin(fuzzySet.universe)
    analyticalSource = _ContinuousAnalyticalSource(fuzzySet)
    moments = None

    if analyticalSource is not None and analyticalSource.name in {"Triangle", "Trapezium", "Parabolic", "Bell"}:
        moments = _PolynomialFamilyMoments(analyticalSource, integrationDomain)

    elif analyticalSource is not None and analyticalSource.name == "Exponential":
        moments = _GaussianMoments(analyticalSource, integrationDomain, policy)

    if moments is None:
        moments = _AdaptiveMoments(fuzzySet, integrationDomain, policy)

    area, firstMoment = moments

    if not math.isfinite(area) or not math.isfinite(firstMoment):
        raise undefinedError("centroid moments must be finite")

    if area <= 0:
        raise undefinedError("centroid is undefined for zero membership area")

    centroid = firstMoment / area

    if not math.isfinite(centroid):
        raise undefinedError("centroid must be finite")

    return centroid

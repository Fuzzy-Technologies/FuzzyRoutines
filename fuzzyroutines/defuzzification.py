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
    membership_function: _AnalyticalSource,
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

    centre = cast(float, membership_function.parameters["a"])
    deviation = cast(float, membership_function.parameters["b"])
    left_distance = (cast(float, domain.left) - centre) / deviation
    right_distance = (cast(float, domain.right) - centre) / deviation
    root_two = math.sqrt(2)
    left_argument = left_distance / root_two
    right_argument = right_distance / root_two

    if left_distance >= 0:
        left_value = math.erfc(left_argument)
        right_value = math.erfc(right_argument)
        error_difference = left_value - right_value

    elif right_distance <= 0:
        left_value = math.erfc(-left_argument)
        right_value = math.erfc(-right_argument)
        error_difference = right_value - left_value

    else:
        left_value = math.erf(left_argument)
        right_value = math.erf(right_argument)
        error_difference = right_value - left_value

    if error_difference <= 0 or not math.isfinite(error_difference):
        return None

    resolution_estimate = math.ulp(left_value) + math.ulp(right_value)

    for distance, argument in (
        (left_distance, left_argument),
        (right_distance, right_argument),
    ):
        if math.isfinite(argument):
            # Two normalizing operations precede division by sqrt(2). The
            # erf/erfc derivative converts their ULP scale to area resolution.
            argument_resolution = 2 * math.ulp(distance) / root_two + math.ulp(argument)
            resolution_estimate += (
                2 / math.sqrt(math.pi)
                * math.exp(-argument * argument)
                * argument_resolution
            )

    if resolution_estimate > cast(float, policy.relativeTolerance) * error_difference:
        return None

    left_exponent = -0.5 * left_distance * left_distance
    right_exponent = -0.5 * right_distance * right_distance
    squared_distance_difference = (right_distance - left_distance) * (
        right_distance + left_distance
    )

    if not math.isfinite(squared_distance_difference):
        # At an infinite standardized endpoint its exponential is exactly
        # zero in binary64, so direct subtraction cannot cancel two tails.
        exponential_difference = math.exp(left_exponent) - math.exp(right_exponent)

    elif squared_distance_difference >= 0:
        exponential_difference = math.exp(left_exponent) * (
            -math.expm1(-0.5 * squared_distance_difference)
        )

    else:
        exponential_difference = math.exp(right_exponent) * math.expm1(
            0.5 * squared_distance_difference
        )

    standardized_area = math.sqrt(math.pi / 2) * error_difference
    area = deviation * standardized_area
    centroid = centre + deviation * (exponential_difference / standardized_area)
    first_moment = area * centroid

    if (
        area <= 0
        or not all(math.isfinite(value) for value in (area, first_moment, centroid))
        or not domain.Contains(centroid)
    ):
        return None

    return area, first_moment


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
    fuzzy_set: ScalarFuzzySet,
    integration_domain: IntegrationDomain,
    policy: CentroidPolicy | None,
    undefined_error: type[Exception],
) -> MembershipScalar:
    """Evaluate centroid with the caller boundary's explicit result-error type.

    Only engine-owned zero-area and non-finite-result checks use this type.
    Evaluator exceptions and the existing convergence error remain unchanged.
    """

    if not isinstance(fuzzy_set, ScalarFuzzySet):
        raise InvalidParameterTypeError("fuzzySet must be a ScalarFuzzySet")

    if not isinstance(fuzzy_set.universe, ContinuousUniverse):
        raise InvalidParameterTypeError("continuous centroid requires a ContinuousUniverse")

    if not isinstance(integration_domain, IntegrationDomain):
        raise InvalidParameterTypeError("integrationDomain must be an IntegrationDomain")

    if policy is None:
        policy = CentroidPolicy()

    elif not isinstance(policy, CentroidPolicy):
        raise InvalidParameterTypeError("policy must be a CentroidPolicy")

    integration_domain.ValidateWithin(fuzzy_set.universe)
    analytical_source = _ContinuousAnalyticalSource(fuzzy_set)
    moments = None

    if analytical_source is not None and analytical_source.name in {"Triangle", "Trapezium", "Parabolic", "Bell"}:
        moments = _PolynomialFamilyMoments(analytical_source, integration_domain)

    elif analytical_source is not None and analytical_source.name == "Exponential":
        moments = _GaussianMoments(analytical_source, integration_domain, policy)

    if moments is None:
        moments = _AdaptiveMoments(fuzzy_set, integration_domain, policy)

    area, first_moment = moments

    if not math.isfinite(area) or not math.isfinite(first_moment):
        raise undefined_error("centroid moments must be finite")

    if area <= 0:
        raise undefined_error("centroid is undefined for zero membership area")

    centroid = first_moment / area

    if not math.isfinite(centroid):
        raise undefined_error("centroid must be finite")

    return centroid

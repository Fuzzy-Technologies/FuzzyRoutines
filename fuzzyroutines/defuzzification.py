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
from fractions import Fraction
from heapq import heappop, heappush
from itertools import pairwise
from numbers import Integral, Rational
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
from fuzzyroutines.membership import (
    MembershipCallable,
    MembershipScalar,
    _AnalyticalSource,
)
from fuzzyroutines.numeric import _RequireFiniteReal

type _Moment = float | Fraction


class CentroidConvergenceError(NumericalError):
    """Adaptive centroid integration that exhausted its subdivision limit."""


@dataclass(frozen=True, slots=True)
class _PartitionedMembership:
    """Retain engine-owned sampling knots without analytical certification."""

    source: MembershipCallable
    points: tuple[MembershipScalar, ...]

    def __call__(self, coordinate: MembershipScalar) -> MembershipScalar:
        """Evaluate the original composition without changing its grades."""

        return self.source(coordinate)


def _IntegrationPoints(fuzzySet: ScalarFuzzySet, level: float | None = None) -> tuple[MembershipScalar, ...]:
    """Extract trusted built-in geometry or an engine-owned partition snapshot."""

    membership = fuzzySet.membershipFunction

    if type(membership) is _PartitionedMembership:
        return membership.points

    source = _ContinuousAnalyticalSource(fuzzySet)

    if source is None:
        return ()

    parameters = {name: cast(float, value) for name, value in source.parameterItems}
    name = source.name

    if name in {"Triangle", "Trapezium"}:
        points = tuple(parameters.values())

    elif name in {"Parabolic", "Bell"}:
        left, right = parameters["a"], parameters["b"]
        width = right - left
        points = (left, left / 2 + right / 2, right)

        if name == "Bell":
            coreRight = parameters["c"]
            points += (coreRight, coreRight + width / 2, coreRight + width)

    elif name == "Exponential":
        centre, deviation = parameters["a"], parameters["b"]
        points = (centre - deviation, centre, centre + deviation)

    elif name == "Sigmoidal":
        points = (parameters["b"],)

    elif name == "Hyperbolic":
        points = (parameters["c"],)

    else:
        points = ()

    ordered = tuple(sorted({point for point in points if math.isfinite(point)}))

    if level is not None and name in {"Triangle", "Trapezium"}:
        crossings = []

        for left, right in pairwise(ordered):
            first, last = source.mju(left), source.mju(right)

            if min(first, last) < level < max(first, last):
                fraction = (level - first) / (last - first)
                crossings.append((1 - fraction) * left + fraction * right)

        return tuple(sorted({*ordered, *crossings}))

    return ordered


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
    left: _Moment,
    right: _Moment,
    origin: _Moment,
    constant: _Moment,
    linear: _Moment,
    quadratic: _Moment,
) -> tuple[_Moment, _Moment]:
    """Integrate a shifted quadratic, retaining rational fallback arithmetic."""

    if isinstance(left, Fraction) or isinstance(right, Fraction):
        constant, linear, quadratic = (Fraction(value) for value in (constant, linear, quadratic))

    # Integrate in distance from the clipped left endpoint. Subtracting powers
    # at two nearby offsets can lose every useful digit on a narrow window.
    width = right - left
    leftOffset = left - origin
    leftGrade = constant + leftOffset * (linear + leftOffset * quadratic)
    leftSlope = linear + 2 * leftOffset * quadratic
    area = width * (leftGrade + width * (leftSlope / 2 + width * quadratic / 3))
    localMoment = width**2 * (leftGrade / 2 + width * (leftSlope / 3 + width * quadratic / 4))

    return area, left * area + localMoment


def _AddSegment(
    moments: tuple[_Moment, _Moment],
    domain: IntegrationDomain,
    left: _Moment,
    right: _Moment,
    origin: _Moment,
    constant: _Moment,
    linear: _Moment,
    quadratic: _Moment,
) -> tuple[_Moment, _Moment]:
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


def _ExactPolynomialValue(value: MembershipScalar) -> Fraction:
    """Preserve original rational geometry and the binary64 image of other reals."""

    return Fraction(value) if isinstance(value, Rational) else Fraction(float(value))


def _PolynomialFamilyMoments(
    membershipFunction: _AnalyticalSource,
    domain: IntegrationDomain,
    exact: bool = False,
) -> tuple[_Moment, _Moment]:
    """Return analytical moments for supported piecewise-polynomial families."""

    parameters: Mapping[str, _Moment] = {
        name: _ExactPolynomialValue(value) if exact else float(value)
        for name, value in membershipFunction.parameterItems
    }
    familyName = membershipFunction.name
    moments: tuple[_Moment, _Moment] = (Fraction(0), Fraction(0)) if exact else (0.0, 0.0)

    if exact:
        domain = IntegrationDomain(_ExactPolynomialValue(domain.left), _ExactPolynomialValue(domain.right))

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

    if left == right:
        return 0.0, 0.0

    scale = (right - left) / 6
    result = (
        scale * (leftValues[0] + 4 * midpointValues[0] + rightValues[0]),
        scale * (leftValues[1] + 4 * midpointValues[1] + rightValues[1]),
    )

    if result[0] == 0 and max(leftValues[0], midpointValues[0], rightValues[0]) > 0:
        raise NumericalError("positive centroid area estimate underflowed to zero")

    moments = (leftValues[1], midpointValues[1], rightValues[1])

    if result[1] == 0 and (min(moments) >= 0 and max(moments) > 0 or max(moments) <= 0 and min(moments) < 0):
        raise NumericalError("nonzero centroid first-moment estimate underflowed to zero")

    return result


@dataclass(frozen=True, slots=True)
class _SimpsonPanel:
    """Cache one Simpson panel and the samples needed for its two children."""

    left: float
    right: float
    values: tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
    samples: tuple[tuple[float, float], tuple[float, float]]
    estimates: tuple[tuple[float, float], tuple[float, float]]
    result: tuple[float, float]
    error: tuple[float, float]
    depth: int



def _AdaptiveMoments(
    fuzzySet: ScalarFuzzySet,
    domain: IntegrationDomain,
    policy: CentroidPolicy,
) -> tuple[float, float]:
    """Refine trusted partitions against a single global estimated-error target."""

    def Evaluate(coordinate: float) -> tuple[float, float]:
        """Evaluate both moments without coercing or masking callback failures."""

        grade = cast(float, fuzzySet.Membership(coordinate))
        moment = coordinate * grade

        if coordinate != 0 and grade > 0 and moment == 0:
            raise NumericalError("nonzero centroid first-moment sample underflowed to zero")

        return grade, moment

    def Measure(
        left: float,
        right: float,
        values: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
        estimate: tuple[float, float],
        depth: int,
    ) -> _SimpsonPanel:
        """Estimate one panel's error while retaining every reusable sample."""

        midpoint = left / 2 + right / 2
        samples = (Evaluate(left / 2 + midpoint / 2), Evaluate(midpoint / 2 + right / 2))
        estimates = (
            _SimpsonEstimate(left, midpoint, values[0], samples[0], values[1]),
            _SimpsonEstimate(midpoint, right, values[1], samples[1], values[2]),
        )
        refined = tuple(estimates[0][index] + estimates[1][index] for index in (0, 1))
        error = tuple(abs(refined[index] - estimate[index]) / 15 for index in (0, 1))
        result = tuple(refined[index] + (refined[index] - estimate[index]) / 15 for index in (0, 1))

        return _SimpsonPanel(left, right, values, samples, estimates, (result[0], result[1]), (error[0], error[1]), depth)

    # Casts retain exact rational coordinates and callback arithmetic at runtime.
    left, right = cast(float, domain.left), cast(float, domain.right)
    coordinateScale = max(abs(left), abs(right), 1.0)
    points = (left, *(cast(float, point) for point in _IntegrationPoints(fuzzySet) if left < cast(float, point) < right), right)
    panels: dict[int, _SimpsonPanel] = {}
    pending: list[tuple[float, int]] = []
    serial = 0
    finitePanels = True

    def Add(panel: _SimpsonPanel) -> None:
        """Queue refinable panels by their absolute contribution to global error."""

        nonlocal serial, finitePanels
        finitePanels &= all(math.isfinite(value) for value in (*panel.result, *panel.error))

        if not finitePanels:
            return

        serial += 1
        panels[serial] = panel

        if panel.depth < policy.maximumDepth and any(panel.error):
            priority = max(panel.error[0], panel.error[1] / coordinateScale)
            heappush(pending, (-priority, serial))

    for lower, upper in pairwise(points):
        values = (Evaluate(lower), Evaluate(lower / 2 + upper / 2), Evaluate(upper))
        Add(Measure(lower, upper, values, _SimpsonEstimate(lower, upper, *values), 0))

    def Totals() -> tuple[tuple[float, ...], tuple[float, ...]]:
        """Recompute global evidence before acceptance, avoiding per-split scans."""

        return (
            tuple(_SumMoments(tuple(panel.result[index] for panel in panels.values())) for index in (0, 1)),
            tuple(_SumMoments(tuple(panel.error[index] for panel in panels.values())) for index in (0, 1)),
        )

    absoluteTarget = float(policy.absoluteTolerance) / 4
    relativeTarget = float(policy.relativeTolerance) / 4

    def Satisfied(result: tuple[float, ...], error: tuple[float, ...]) -> bool:
        """Reserve margin for the ratio of two independently estimated moments."""

        return (
            error[0] <= absoluteTarget + relativeTarget * abs(result[0])
            and error[1] <= absoluteTarget * coordinateScale + relativeTarget * abs(result[1])
        )

    result, error = Totals()

    while True:
        if not finitePanels or not all(math.isfinite(value) for value in (*result, *error)):
            return math.inf, math.inf

        if Satisfied(result, error) or not pending:
            # Cached replacement sums guide refinement; only a full compensated
            # sum of the active partition can certify the estimated budget.
            result, error = Totals()

            if Satisfied(result, error):
                return result[0], result[1]

            if not pending:
                raise CentroidConvergenceError(
                    "centroid integration did not converge within maximumDepth="
                    f"{policy.maximumDepth}"
                )

        _, identifier = heappop(pending)
        panel = panels.pop(identifier)
        midpoint = panel.left / 2 + panel.right / 2
        children = (
            Measure(panel.left, midpoint, (panel.values[0], panel.samples[0], panel.values[1]), panel.estimates[0], panel.depth + 1),
            Measure(midpoint, panel.right, (panel.values[1], panel.samples[1], panel.values[2]), panel.estimates[1], panel.depth + 1),
        )

        for child in children:
            Add(child)

        result = tuple(_SumMoments((result[index], -panel.result[index], children[0].result[index], children[1].result[index])) for index in (0, 1))
        error = tuple(_SumMoments((error[index], -panel.error[index], children[0].error[index], children[1].error[index])) for index in (0, 1))



def _SumMoments(values: tuple[float, ...]) -> float:
    """Use compensated binary64 sums without coercing wholly rational panels."""

    if values and isinstance(values[0], Fraction) and all(isinstance(value, Fraction) for value in values):
        return cast(float, sum(values, Fraction(0)))

    try:
        return math.fsum(values)

    except OverflowError:
        return math.inf


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
        NumericalError: A nonzero adaptive area or moment estimate/sample
            underflows to zero, or numerical rounding moves the centroid
            outside its integration domain.
        CentroidConvergenceError: Adaptive quadrature exceeds `maximumDepth`.

    Notes:
        Engine-owned inference compositions retain trusted built-in geometry
        as initial integration knots, without analytical certification. All
        accepted panels share the policy's global estimated-error targets.
        Arbitrary callables still require sufficient regularity: unsampled
        features cannot be excluded by numerical quadrature. Unsafe polynomial
        moments use bounded rational recomputation before taking their ratio.
        Polynomial geometry supplied as non-binary64 rationals retains its
        original exact values and returns a rational centroid, including when
        the integration window contains no binary64 coordinate.
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
        # Preserve exact geometry when binary64 conversion would merge vertices
        # or alter a rational integration boundary. Ordinary float/int presets
        # retain the inexpensive floating-point path.
        exactInputs = any(
            isinstance(value, Rational) and float(value) != value
            for value in (
                *(value for _, value in analyticalSource.parameterItems),
                integrationDomain.left, integrationDomain.right,
            )
        )

        if not exactInputs:
            try:
                moments = _PolynomialFamilyMoments(analyticalSource, integrationDomain)

            except (OverflowError, ZeroDivisionError):
                moments = None

        if (
            moments is None
            or not all(math.isfinite(value) for value in moments)
            or moments[0] < float.fromhex("0x1.0p-1022")
            or abs(cast(float, moments[1])) < float.fromhex("0x1.0p-1022")
        ):
            # Five bounded-degree pieces at most: exact original-rational or
            # binary64-input moments retain ratios with unrepresentable moments.
            exactArea, exactMoment = _PolynomialFamilyMoments(analyticalSource, integrationDomain, exact=True)

            if exactArea <= 0:
                raise undefinedError("centroid is undefined for zero membership area")

            exactCentroid = exactMoment / exactArea if exactInputs else float(exactMoment / exactArea)

            if not math.isfinite(exactCentroid):
                raise undefinedError("centroid must be finite")

            return exactCentroid

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

    if not integrationDomain.Contains(centroid):
        raise NumericalError("centroid is outside integration domain at working precision")

    return centroid

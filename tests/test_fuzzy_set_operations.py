# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Set-level contracts for explicit fuzzy negation, t-norm, and s-norm policies."""

import math

import pytest

from fuzzyroutines import (
    Complement,
    ContinuousUniverse,
    Difference,
    DiscreteUniverse,
    Intersection,
    NegationPolicy,
    ScalarFuzzySet,
    SNormPolicy,
    TNormPolicy,
    Union,
)
from fuzzyroutines.FuzzyRoutines import FuzzyNOT, FuzzyNOTParabolic, SCoNorm, TNorm

GRID = tuple(index / 10 for index in range(11))
FAMILIES = ("logic", "algebraic", "boundary", "drastic")


def BuildContinuousSet(membershipFunction):
    """Build one set over the canonical closed unit universe."""

    return ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True),
        membershipFunction,
    )


def test_StandardComplementUsesExplicitOneMinusMembershipPolicy():
    """Verify that standard complement uses explicit one minus membership policy."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)

    complement = Complement(fuzzySet, NegationPolicy("standard"))

    for coordinate in GRID:
        assert complement.Membership(coordinate) == pytest.approx(1.0 - coordinate), (
            "Standard complement must apply N(x) = 1 - x pointwise."
        )


@pytest.mark.parametrize(("family", "alpha"), [("parametric", 0.3), ("parabolic", 0.7)])
def test_ParameterizedComplementsMatchAcceptedLegacyScalarContracts(family, alpha):
    """Verify that parameterized complements match accepted legacy scalar contracts."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)
    policy = NegationPolicy(family, alpha)
    expectedOperator = FuzzyNOT if family == "parametric" else FuzzyNOTParabolic

    complement = Complement(fuzzySet, policy)

    for coordinate in GRID:
        assert complement.Membership(coordinate) == pytest.approx(
            expectedOperator(coordinate, alpha=alpha),
            abs=1e-12,
            rel=0.0,
        ), f"{family!r} set complement must retain the accepted scalar formula."


@pytest.mark.parametrize(
    ("family", "alpha", "errorType"),
    [
        ("standard", 0.5, ValueError),
        ("parametric", None, TypeError),
        ("parametric", 0.0, ValueError),
        ("parametric", 1.0, ValueError),
        ("parabolic", 0.2, ValueError),
        ("parabolic", 0.8, ValueError),
        ("unknown", None, ValueError),
    ],
)
def test_NegationPoliciesRejectIncompleteOrInvalidConfiguration(family, alpha, errorType):
    """Verify that negation policies reject incomplete or invalid configuration."""

    with pytest.raises(errorType):
        NegationPolicy(family, alpha)


def test_ComplementRequiresAnExplicitPolicyObject():
    """Verify that complement requires an explicit policy object."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)

    with pytest.raises(TypeError, match="NegationPolicy"):
        Complement(fuzzySet, None)


@pytest.mark.parametrize("family", FAMILIES)
def test_SetIntersectionAndUnionMatchAcceptedScalarFamilies(family):
    """Verify that set intersection and union match accepted scalar families."""

    leftSet = BuildContinuousSet(lambda coordinate: coordinate)
    rightSet = BuildContinuousSet(lambda coordinate: 1.0 - coordinate)
    intersection = Intersection(leftSet, rightSet, TNormPolicy(family))
    union = Union(leftSet, rightSet, SNormPolicy(family))

    for coordinate in GRID:
        leftGrade = leftSet.Membership(coordinate)
        rightGrade = rightSet.Membership(coordinate)

        assert intersection.Membership(coordinate) == pytest.approx(
            TNorm(leftGrade, rightGrade, normType=family),
            abs=1e-12,
            rel=0.0,
        ), f"Intersection must apply the {family!r} t-norm pointwise."
        assert union.Membership(coordinate) == pytest.approx(
            SCoNorm(leftGrade, rightGrade, normType=family),
            abs=1e-12,
            rel=0.0,
        ), f"Union must apply the {family!r} s-norm pointwise."


def test_BinaryOperationsRequireExplicitPolicyObjects():
    """Verify that binary operations require explicit policy objects."""

    leftSet = BuildContinuousSet(lambda coordinate: coordinate)
    rightSet = BuildContinuousSet(lambda coordinate: 1.0 - coordinate)

    with pytest.raises(TypeError, match="TNormPolicy"):
        Intersection(leftSet, rightSet, None)

    with pytest.raises(TypeError, match="SNormPolicy"):
        Union(leftSet, rightSet, None)


@pytest.mark.parametrize("policyType", [TNormPolicy, SNormPolicy])
def test_BinaryPoliciesRejectUnknownFamilies(policyType):
    """Verify that binary policies reject unknown families."""

    with pytest.raises(ValueError, match="unknown"):
        policyType("unknown")


def test_BinaryOperationsFailClosedForDifferentUniverses():
    """Verify that binary operations fail closed for different universes."""

    closedUniverseSet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True),
        lambda coordinate: coordinate,
    )
    openUniverseSet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, leftClosed=False, rightClosed=False),
        lambda coordinate: coordinate,
    )

    with pytest.raises(ValueError, match="equal universes"):
        Intersection(closedUniverseSet, openUniverseSet, TNormPolicy("logic"))

    with pytest.raises(ValueError, match="equal universes"):
        Union(closedUniverseSet, openUniverseSet, SNormPolicy("logic"))


def test_DiscreteSetOperationsPreserveTheDeclaredUniverse():
    """Verify that discrete set operations preserve the declared universe."""

    universe = DiscreteUniverse((0.0, 0.5, 1.0))
    leftSet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
    rightSet = ScalarFuzzySet(universe, lambda coordinate: 1.0 - coordinate)

    intersection = Intersection(leftSet, rightSet, TNormPolicy("logic"))
    union = Union(leftSet, rightSet, SNormPolicy("logic"))

    assert intersection.universe is universe
    assert union.universe is universe
    assert tuple(intersection.Membership(point) for point in universe.points) == (0.0, 0.5, 0.0)
    assert tuple(union.Membership(point) for point in universe.points) == (1.0, 0.5, 1.0)


def test_SetMembershipRejectsCoordinatesOutsideItsUniverse():
    """Verify that set membership rejects coordinates outside its universe."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)

    with pytest.raises(ValueError, match="belong"):
        fuzzySet.Membership(-0.1)

    with pytest.raises(ValueError, match="belong"):
        fuzzySet.Membership(1.1)


@pytest.mark.parametrize("invalidGrade", [-0.1, 1.1, math.nan, math.inf, True])
def test_SetMembershipRejectsInvalidGrades(invalidGrade):
    """Verify that set membership rejects invalid grades."""

    fuzzySet = BuildContinuousSet(lambda coordinate: invalidGrade)

    with pytest.raises((TypeError, ValueError)):
        fuzzySet.Membership(0.5)


@pytest.mark.parametrize("family", FAMILIES)
def test_SetOperationsAreCommutativeAndAssociative(family):
    """Verify that set operations are commutative and associative."""

    firstSet = BuildContinuousSet(lambda coordinate: coordinate)
    secondSet = BuildContinuousSet(lambda coordinate: 0.25)
    thirdSet = BuildContinuousSet(lambda coordinate: 1.0 - coordinate / 2)
    tNormPolicy = TNormPolicy(family)
    sNormPolicy = SNormPolicy(family)

    for coordinate in GRID:
        assert Intersection(firstSet, secondSet, tNormPolicy).Membership(coordinate) == pytest.approx(
            Intersection(secondSet, firstSet, tNormPolicy).Membership(coordinate),
            abs=1e-12,
            rel=0.0,
        ), f"The {family!r} intersection must be commutative."
        assert Union(firstSet, secondSet, sNormPolicy).Membership(coordinate) == pytest.approx(
            Union(secondSet, firstSet, sNormPolicy).Membership(coordinate),
            abs=1e-12,
            rel=0.0,
        ), f"The {family!r} union must be commutative."

        leftAssociatedIntersection = Intersection(
            Intersection(firstSet, secondSet, tNormPolicy),
            thirdSet,
            tNormPolicy,
        )
        rightAssociatedIntersection = Intersection(
            firstSet,
            Intersection(secondSet, thirdSet, tNormPolicy),
            tNormPolicy,
        )
        leftAssociatedUnion = Union(Union(firstSet, secondSet, sNormPolicy), thirdSet, sNormPolicy)
        rightAssociatedUnion = Union(firstSet, Union(secondSet, thirdSet, sNormPolicy), sNormPolicy)

        assert leftAssociatedIntersection.Membership(coordinate) == pytest.approx(
            rightAssociatedIntersection.Membership(coordinate),
            abs=1e-12,
            rel=0.0,
        ), f"The {family!r} intersection must be associative."
        assert leftAssociatedUnion.Membership(coordinate) == pytest.approx(
            rightAssociatedUnion.Membership(coordinate),
            abs=1e-12,
            rel=0.0,
        ), f"The {family!r} union must be associative."


@pytest.mark.parametrize("family", FAMILIES)
def test_SetOperationsSatisfyBoundaryAndDeMorganLaws(family):
    """Verify that set operations satisfy boundary and De Morgan laws."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)
    otherSet = BuildContinuousSet(lambda coordinate: 0.25 + coordinate / 2)
    zeroSet = BuildContinuousSet(lambda coordinate: 0.0)
    oneSet = BuildContinuousSet(lambda coordinate: 1.0)
    tNormPolicy = TNormPolicy(family)
    sNormPolicy = SNormPolicy(family)
    standardNegation = NegationPolicy("standard")

    for coordinate in GRID:
        assert Intersection(fuzzySet, oneSet, tNormPolicy).Membership(coordinate) == pytest.approx(
            fuzzySet.Membership(coordinate),
            abs=1e-12,
            rel=0.0,
        ), f"The {family!r} t-norm must preserve the one identity."
        assert Union(fuzzySet, zeroSet, sNormPolicy).Membership(coordinate) == pytest.approx(
            fuzzySet.Membership(coordinate),
            abs=1e-12,
            rel=0.0,
        ), f"The {family!r} s-norm must preserve the zero identity."

        complementOfIntersection = Complement(
            Intersection(fuzzySet, otherSet, tNormPolicy),
            standardNegation,
        )
        unionOfComplements = Union(
            Complement(fuzzySet, standardNegation),
            Complement(otherSet, standardNegation),
            sNormPolicy,
        )
        complementOfUnion = Complement(
            Union(fuzzySet, otherSet, sNormPolicy),
            standardNegation,
        )
        intersectionOfComplements = Intersection(
            Complement(fuzzySet, standardNegation),
            Complement(otherSet, standardNegation),
            tNormPolicy,
        )

        assert complementOfIntersection.Membership(coordinate) == pytest.approx(
            unionOfComplements.Membership(coordinate),
            abs=1e-12,
            rel=0.0,
        ), f"The {family!r} pair must satisfy the first De Morgan law."
        assert complementOfUnion.Membership(coordinate) == pytest.approx(
            intersectionOfComplements.Membership(coordinate),
            abs=1e-12,
            rel=0.0,
        ), f"The {family!r} pair must satisfy the second De Morgan law."


def test_OperationsDoNotMutateTheirOperands():
    """Verify that operations do not mutate their operands."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)
    otherSet = BuildContinuousSet(lambda coordinate: 1.0 - coordinate)
    originalGrades = tuple(fuzzySet.Membership(coordinate) for coordinate in GRID)
    originalOtherGrades = tuple(otherSet.Membership(coordinate) for coordinate in GRID)

    Complement(fuzzySet, NegationPolicy("standard"))
    Difference(
        fuzzySet,
        otherSet,
        TNormPolicy("algebraic"),
        NegationPolicy("standard"),
    )
    Intersection(fuzzySet, otherSet, TNormPolicy("algebraic"))
    Union(fuzzySet, otherSet, SNormPolicy("algebraic"))

    assert tuple(fuzzySet.Membership(coordinate) for coordinate in GRID) == originalGrades, (
        "Constructing derived sets must not mutate either source membership definition."
    )
    assert tuple(otherSet.Membership(coordinate) for coordinate in GRID) == originalOtherGrades, (
        "Constructing derived sets must not mutate either source membership definition."
    )


@pytest.mark.parametrize("tNormFamily", FAMILIES)
@pytest.mark.parametrize(
    ("negationFamily", "alpha"),
    [("standard", None), ("parametric", 0.3), ("parabolic", 0.7)],
)
def test_DifferenceMatchesExplicitIntersectionWithComplement(
    tNormFamily,
    negationFamily,
    alpha,
):
    """Verify that difference matches explicit intersection with complement."""

    leftSet = BuildContinuousSet(lambda coordinate: 0.2 + coordinate / 2)
    rightSet = BuildContinuousSet(lambda coordinate: 0.8 - coordinate / 2)
    tNormPolicy = TNormPolicy(tNormFamily)
    negationPolicy = NegationPolicy(negationFamily, alpha)
    difference = Difference(leftSet, rightSet, tNormPolicy, negationPolicy)
    explicitComposition = Intersection(
        leftSet,
        Complement(rightSet, negationPolicy),
        tNormPolicy,
    )

    for coordinate in GRID:
        assert difference.Membership(coordinate) == pytest.approx(
            explicitComposition.Membership(coordinate),
            abs=1e-12,
            rel=0.0,
        ), "Directed difference must equal T(mu_A(x), N(mu_B(x))) pointwise."


def test_DifferenceIsDirectionalRatherThanCommutative():
    """Verify that difference is directional rather than commutative."""

    leftSet = BuildContinuousSet(lambda coordinate: 0.8)
    rightSet = BuildContinuousSet(lambda coordinate: 0.2)
    tNormPolicy = TNormPolicy("logic")
    negationPolicy = NegationPolicy("standard")

    leftMinusRight = Difference(leftSet, rightSet, tNormPolicy, negationPolicy)
    rightMinusLeft = Difference(rightSet, leftSet, tNormPolicy, negationPolicy)

    assert leftMinusRight.Membership(0.5) == pytest.approx(0.8)
    assert rightMinusLeft.Membership(0.5) == pytest.approx(0.2)
    assert leftMinusRight.Membership(0.5) != rightMinusLeft.Membership(0.5), (
        "Fuzzy-set difference is directed and must not be treated as commutative."
    )


def test_DifferenceMatchesClassicalSetDifferenceForCrispGrades():
    """Verify that difference matches classical set difference for crisp grades."""

    universe = DiscreteUniverse((0.0, 1.0, 2.0))
    leftSet = ScalarFuzzySet(universe, {0.0: 1.0, 1.0: 1.0, 2.0: 0.0}.__getitem__)
    rightSet = ScalarFuzzySet(universe, {0.0: 0.0, 1.0: 1.0, 2.0: 1.0}.__getitem__)

    difference = Difference(
        leftSet,
        rightSet,
        TNormPolicy("logic"),
        NegationPolicy("standard"),
    )

    assert tuple(difference.Membership(point) for point in universe.points) == (1.0, 0.0, 0.0), (
        "Standard negation with the logic t-norm must recover crisp set difference."
    )


def test_FuzzySelfDifferenceDoesNotClaimClassicalEmptiness():
    """Verify that fuzzy self difference does not claim classical emptiness."""

    fuzzySet = BuildContinuousSet(lambda coordinate: coordinate)

    difference = Difference(
        fuzzySet,
        fuzzySet,
        TNormPolicy("logic"),
        NegationPolicy("standard"),
    )

    assert difference.Membership(0.5) == pytest.approx(0.5), (
        "Generic fuzzy self-difference must retain the selected operator result."
    )


def test_DifferenceRequiresExplicitPolicyObjects():
    """Verify that difference requires explicit policy objects."""

    leftSet = BuildContinuousSet(lambda coordinate: coordinate)
    rightSet = BuildContinuousSet(lambda coordinate: 1.0 - coordinate)

    with pytest.raises(TypeError, match="TNormPolicy"):
        Difference(leftSet, rightSet, None, NegationPolicy("standard"))

    with pytest.raises(TypeError, match="NegationPolicy"):
        Difference(leftSet, rightSet, TNormPolicy("logic"), None)


def test_DifferenceFailsClosedForDifferentUniverses():
    """Verify that difference fails closed for different universes."""

    closedUniverseSet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True),
        lambda coordinate: coordinate,
    )
    openUniverseSet = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, leftClosed=False, rightClosed=False),
        lambda coordinate: coordinate,
    )

    with pytest.raises(ValueError, match="equal universes"):
        Difference(
            closedUniverseSet,
            openUniverseSet,
            TNormPolicy("logic"),
            NegationPolicy("standard"),
        )


def test_DifferencePreservesTheDeclaredUniverse():
    """Verify that difference preserves the declared universe."""

    universe = DiscreteUniverse((0.0, 0.5, 1.0))
    leftSet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
    rightSet = ScalarFuzzySet(universe, lambda coordinate: 1.0 - coordinate)

    difference = Difference(
        leftSet,
        rightSet,
        TNormPolicy("algebraic"),
        NegationPolicy("standard"),
    )

    assert difference.universe is universe

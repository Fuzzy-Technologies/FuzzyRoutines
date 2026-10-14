# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Reference parity and failure evidence for the explicit public NumPy backend."""

from dataclasses import replace
from fractions import Fraction

import pytest

from fuzzyroutines import (
    Bell,
    ContinuousUniverse,
    CreateUniversalFuzzyScale,
    DiscreteUniverse,
    FuzzificationPolicy,
    Gaussian,
    HarringtonDesirability,
    Hyperbolic,
    LinguisticScale,
    LinguisticTerm,
    Logistic,
    ScalarFuzzySet,
    SShoulder,
    Trapezoid,
    Triangle,
    UniversalFuzzyScalePolicy,
)
from fuzzyroutines.batches import EvaluateMembershipBatch, FuzzifyBatch

np = pytest.importorskip("numpy")
FAMILIES = (
    Hyperbolic(2.0, 1.5, 0.0), Bell(-2.0, -1.0, 1.0),
    SShoulder(-2.0, 2.0), Triangle(-2.0, 0.5, 2.0),
    Trapezoid(-2.0, -0.5, 0.5, 2.0), Gaussian(0.5, 0.25),
    Logistic(2.0, 0.5), HarringtonDesirability(),
    Triangle(-2.0, 2.0, 2.0), Bell(-2.0, 0.0, 0.0),
    Trapezoid(-2.0, 0.0, 0.0, 2.0), Logistic(-2.0, 0.5),
)


def _Scale(*functions, universe=None):
    """Build named independent terms without depending on a preset factory."""

    if universe is None:
        universe = ContinuousUniverse(-5.0, 5.0, True, True)

    return LinguisticScale(tuple(
        LinguisticTerm(f"term{index}", ScalarFuzzySet(universe, function))
        for index, function in enumerate(functions)
    ))


@pytest.mark.parametrize("function", FAMILIES)
def test_AllFamiliesMatchScalarAtGridEndpointsAndAdjacentFloats(function):
    """Guard each kernel against canonical scalar formulas and branch boundaries."""

    boundaries = np.array([-3, -2, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3], dtype=np.float64)
    values = np.concatenate((np.linspace(-5, 5, 601), boundaries,
                             np.nextafter(boundaries, -np.inf), np.nextafter(boundaries, np.inf)))
    expected = np.array([float(function(float(value))) for value in values])
    actual = EvaluateMembershipBatch(function, values, backend="numpy")
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)


@pytest.mark.parametrize("function,values", (
    (Gaussian(-1e308, 1e308), [1e308, -1e308]),
    (Logistic(1e-308, -1e308), [1e308, -1e308]),
    (Logistic(-1e-308, 1e308), [-1e308, 1e308]),
    (Triangle(-1e308, 0.0, 1e308), [-1e308, -5e307, 0.0, 5e307, 1e308]),
    (Triangle(-1e308, 1e308, 1e308), [-1e308, 0.0, 1e308]),
    (Trapezoid(-1e308, -5e307, 5e307, 1e308), [-1e308, -8e307, 0.0, 8e307, 1e308]),
    (HarringtonDesirability(), [-1e308, -710.0, 710.0, 1e308]),
    (Hyperbolic(1e308, 2.0, -1e308), [-1e308, 0.0, 1e308]),
))
def test_ExtremeFiniteSaturationAndSafeRatiosMatchScalar(function, values):
    """Preserve corrected scalar overflow handling rather than the old prototype."""

    expected = [float(function(value)) for value in values]
    np.testing.assert_allclose(EvaluateMembershipBatch(function, values), expected, rtol=0, atol=1e-12)


@pytest.mark.parametrize("function,values", (
    (SShoulder(2**1023, 3 * 2**1022), [float(2**1023), float(3 * 2**1022)]),
    (Triangle(-2**1023, 2**1023, 2**1023), [float(-2**1023), float(2**1023)]),
    (Bell(0, 2**1023, 2**1023), [0.0, float(2**1023)]),
    (Trapezoid(-2**1023, 0, 0, 2**1023), [float(-2**1023), 0.0, float(2**1023)]),
    (Gaussian(2**1023, 2**1023), [float(2**1023)]),
    (Logistic(2**1023, 2**1023), [float(2**1023)]),
))
def test_ExactIntegerParametersRetainScalarIntermediateArithmetic(function, values):
    """Preserve scalar integer arithmetic and skip inactive extreme corrections."""

    expected = [float(function(value)) for value in values]
    np.testing.assert_allclose(EvaluateMembershipBatch(function, values), expected, rtol=0, atol=1e-12)


@pytest.mark.parametrize("function,value,error", (
    (Hyperbolic(1.0, 2.0, 0.0), 1e308, OverflowError),
    (SShoulder(0.0, 1e-200), 0.5e-200, ZeroDivisionError),
    (SShoulder(-1e308, 1e308), 0.0, OverflowError),
    (Bell(-1e308, 0.0, 1e308), 1.5e308, OverflowError),
))
def test_SelectedUnrepresentableBranchesFailWithoutPartialResults(function, value, error):
    """Retain representative scalar arithmetic failures at active branches."""

    with pytest.raises(error):
        function(value)

    with pytest.raises(error):
        EvaluateMembershipBatch(function, [value])


@pytest.mark.parametrize("values", (True, 0.5, [True], [0.5, True], [[False, 0.5]],
                                    [0.5, np.bool_(True)], [np.array([True]), np.array([0.5])],
                                    [1j], ["0.5"], np.array([0.5], dtype=object)))
def test_UnsupportedInputKindsFailExplicitly(values):
    """Reject coercions that conceal unsupported scalar coordinate types."""

    with pytest.raises(TypeError):
        EvaluateMembershipBatch(Gaussian(0, 1), values)


@pytest.mark.parametrize("values", ([float("nan")], [float("inf")], [float("-inf")]))
def test_NonFiniteCoordinatesFailBeforeAnyKernel(values):
    """Require finite coordinates after the documented binary64 conversion."""

    with pytest.raises(ValueError, match="finite"):
        EvaluateMembershipBatch(Gaussian(0, 1), values)


def test_OwnershipShapesAndEmptyNoncontiguousInputs():
    """Keep conversion and output ownership separate from caller-owned buffers."""

    source = np.arange(24, dtype=np.int32).reshape(4, 6)[:, ::2]
    snapshot = source.copy()
    result = EvaluateMembershipBatch(Gaussian(0, 5), source)
    assert result.shape == source.shape and result.dtype == np.float64
    assert result.flags.owndata and not np.shares_memory(result, source)
    result[0, 0] = 0
    np.testing.assert_array_equal(source, snapshot)
    empty = EvaluateMembershipBatch(Gaussian(0, 1), np.empty((3, 0, 2)))
    assert empty.shape == (3, 0, 2) and empty.size == 0


def test_ParametersRemainFrozenAndCustomCallablesStayScalar():
    """Do not infer eligibility from a callable carrying built-in-looking state."""

    parameters = {"center": 0.0, "scale": 1.0}
    function = Gaussian(**parameters)
    parameters["scale"] = 5
    np.testing.assert_allclose(EvaluateMembershipBatch(function, [0.0, 1.0]), [1.0, np.exp(-0.5)])

    with pytest.raises(TypeError, match="built-in"):
        EvaluateMembershipBatch(lambda value: 0.5, [0.0])

    with pytest.raises(TypeError, match="binary64"):
        EvaluateMembershipBatch(Gaussian(Fraction(0), Fraction(1)), [0.0])

    with pytest.raises(ValueError, match="backend"):
        EvaluateMembershipBatch(function, [0.0], backend="auto")


def test_AmbientErrorSettingsRestoredOnSuccessAndFailure():
    """Keep NumPy's caller policy untouched even when an array branch fails."""

    with np.errstate(over="ignore", under="raise", invalid="warn", divide="ignore"):
        before = np.geterr()
        EvaluateMembershipBatch(Gaussian(0, 1), [1e308])
        assert np.geterr() == before

        with pytest.raises(OverflowError):
            EvaluateMembershipBatch(Hyperbolic(1, 2, 0), [1e308])

        assert np.geterr() == before


def test_ExtendedFloatConversionIgnoresBenignUnderflowAndRestoresSettings():
    """A coordinate rounded to finite binary64 zero remains a valid batch input."""

    values = np.array([np.finfo(np.longdouble).tiny], dtype=np.longdouble)

    with np.errstate(all="raise"):
        before = np.geterr()
        result = EvaluateMembershipBatch(Gaussian(0, 1), values)
        assert result.tolist() == [1.0]
        assert np.geterr() == before


def test_BatchesRejectOverriddenScalarSemantics():
    """Do not bypass custom methods hidden behind otherwise eligible definitions."""

    class CustomUniverse(ContinuousUniverse):
        """Universe whose membership rule differs from stored endpoint fields."""

        def Contains(self, coordinate):
            """Exclude every coordinate to expose a bypass of this override."""

            return False

    class CustomSet(ScalarFuzzySet):
        """Set whose active grade computation is not its stored family formula."""

        def Membership(self, coordinate):
            """Return a deliberately different valid grade."""

            return 0.1

    class CustomScale(LinguisticScale):
        """Scale with its own classification implementation."""

        def Fuzzify(self, coordinate, policy=None):
            """Reject classification to expose attempts to ignore this override."""

            raise RuntimeError("custom scale")

    standard = _Scale(Gaussian(0, 1))
    cases = (
        _Scale(Gaussian(0, 1), universe=CustomUniverse()),
        LinguisticScale((LinguisticTerm("custom", CustomSet(ContinuousUniverse(), Gaussian(0, 1))),)),
        CustomScale(standard.terms),
    )

    for scale in cases:
        with pytest.raises(TypeError):
            FuzzifyBatch(scale, [0.0])


def test_BatchesRejectMethodsBoundToDifferentScalarObjects(monkeypatch):
    """A canonical method bound to another receiver is not analytical evidence."""

    otherSet = ScalarFuzzySet(ContinuousUniverse(), Gaussian(1, 1))
    otherScale = _Scale(Gaussian(1, 1))

    class RedirectedSet(ScalarFuzzySet):
        """Expose a canonical evaluator owned by a different fuzzy set."""

        def Membership(self):
            """Return an authentic method whose receiver contradicts our fields."""

            return otherSet.Membership

    class RedirectedScale(LinguisticScale):
        """Expose a canonical classification method owned by a different scale."""

        def Fuzzify(self):
            """Return a real scale method with a different declared term set."""

            return otherScale.Fuzzify

    # Install descriptor overrides of protected PascalCase methods explicitly;
    # ordinary authored properties follow the repository's camelCase contract.
    monkeypatch.setattr(RedirectedSet, "Membership", property(RedirectedSet.Membership))
    monkeypatch.setattr(RedirectedScale, "Fuzzify", property(RedirectedScale.Fuzzify))
    ownSet = RedirectedSet(ContinuousUniverse(), Gaussian(0, 1))
    assert ownSet.Membership(0.0) == pytest.approx(np.exp(-0.5))
    ownScale = _Scale(Gaussian(0, 1))

    for scale in (LinguisticScale((LinguisticTerm("redirected", ownSet),)), RedirectedScale(ownScale.terms)):
        with pytest.raises(TypeError, match="overridden"):
            FuzzifyBatch(scale, [0.0])


@pytest.mark.parametrize("tiePolicy", ("first", "last", "all"))
@pytest.mark.parametrize("tolerance", (0.0, 0.1, 1e-12))
def test_ScaleDecisionsMatchModernScalarPolicies(tiePolicy, tolerance):
    """Check ordered evidence and decision parity including zeros and near ties."""

    scale = _Scale(Triangle(-2, 0, 2), Triangle(-2, 0, 2), SShoulder(0, 2))
    values = np.array([[-5, -1, 0], [0.9, 1, 5]], dtype=np.float64)
    policy = FuzzificationPolicy(tiePolicy, minimumConfidence=0.1, tieTolerance=tolerance)
    batch = FuzzifyBatch(scale, values, policy)

    for position in np.ndindex(values.shape):
        scalar = scale.Fuzzify(float(values[position]), policy)
        np.testing.assert_allclose(batch.memberships[position], [value.grade for value in scalar.memberships], rtol=0, atol=1e-12)
        assert batch.confidence[position] == pytest.approx(scalar.confidence, rel=0, abs=1e-12)
        assert tuple(name for name, selected in zip(batch.termNames, batch.selected[position], strict=True) if selected) == tuple(term.name for term in scalar.selectedTerms)
        assert tuple(name for name, tied in zip(batch.termNames, batch.tied[position], strict=True) if tied) == tuple(term.name for term in scalar.tiedTerms)


def test_ScaleThresholdEqualityNearTieAndGradeNonNormalization():
    """Preserve threshold equality and explicit decimal-boundary accommodation."""

    scale = _Scale(Triangle(0, 1, 2), Triangle(0, 2, 3))
    policy = FuzzificationPolicy("all", minimumConfidence=0.3, tieTolerance=0.3)
    batch = FuzzifyBatch(scale, [0.3, 0.6, 1.0], policy)
    assert not batch.selected[0].any()
    assert batch.tied[1].tolist() == [True, True]
    assert batch.memberships[2].sum() == 1.5, "Grades must not be normalized as probabilities."


def test_ScaleUniverseAndEmptyBatchContracts():
    """Validate each universe, including open endpoints and discrete membership."""

    scale = _Scale(Triangle(0, 1, 2), universe=ContinuousUniverse(0, 2, False, True))

    with pytest.raises(ValueError, match="universe"):
        FuzzifyBatch(scale, [0.0, 1.0])

    empty = FuzzifyBatch(scale, np.empty((2, 0)))
    assert empty.memberships.shape == (2, 0, 1) and empty.confidence.shape == (2, 0)
    discrete = _Scale(Triangle(0, 1, 2), universe=DiscreteUniverse((0, 1, 2)))
    assert FuzzifyBatch(discrete, [1]).selected.tolist() == [[True]]

    with pytest.raises(ValueError, match="universe"):
        FuzzifyBatch(discrete, [0.5])

    with pytest.raises(TypeError, match="built-in"):
        FuzzifyBatch(_Scale(lambda value: 0.5), [0.5])


def test_ScaleResultRejectsForgedEvidenceAndOwnsReadonlyArrays():
    """Make public result records self-consistent and independent of other results."""

    scale = _Scale(Triangle(-1, 0, 1), Triangle(-1, 0, 1))
    result = FuzzifyBatch(scale, [[0.0, 0.5]])

    for name in ("memberships", "confidence", "tied", "selected"):
        values = getattr(result, name)
        assert values.flags.owndata and not values.flags.writeable

    copied = replace(result)
    assert not np.shares_memory(result.memberships, copied.memberships)

    with pytest.raises(ValueError, match="contradicts"):
        replace(result, confidence=np.zeros_like(result.confidence))

    with pytest.raises(ValueError, match="contradicts"):
        replace(result, selected=~result.selected)

    with pytest.raises(TypeError):
        replace(result, tied=result.tied.astype(np.float64))


@pytest.mark.parametrize("policy", (FuzzificationPolicy(), UniversalFuzzyScalePolicy(),
                                  FuzzificationPolicy("all", minimumConfidence=0.1, tieTolerance=0.01)))
def test_HistoricalFiveLevelPresetPreservesGradesAndSelections(policy):
    """Use the actual modern preset with historical term order and scalar policy."""

    scale = CreateUniversalFuzzyScale()
    boundaries = np.array([0.0, 0.17, 0.23, 0.34, 0.40, 0.60, 0.66, 0.77, 0.83, 0.95, 1.0])
    values = np.concatenate((np.linspace(0, 1, 1001), boundaries,
                             np.nextafter(boundaries[1:-1], 0), np.nextafter(boundaries[1:-1], 1)))
    batch = FuzzifyBatch(scale, values, policy)
    assert batch.termNames == ("Min", "Low", "Med", "High", "Max")

    for index, coordinate in enumerate(values):
        scalar = scale.Fuzzify(float(coordinate), policy)
        np.testing.assert_allclose(batch.memberships[index], [value.grade for value in scalar.memberships], rtol=0, atol=1e-12)
        assert tuple(name for name, selected in zip(batch.termNames, batch.selected[index], strict=True) if selected) == tuple(term.name for term in scalar.selectedTerms)

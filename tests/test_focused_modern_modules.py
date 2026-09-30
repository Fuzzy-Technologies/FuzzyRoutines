# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Modern formula ownership, immutable geometry, and historical adapter evidence."""

import importlib
import math
import subprocess
import sys
from dataclasses import FrozenInstanceError
from fractions import Fraction
from typing import ClassVar

import pytest

from fuzzyroutines import (
    Centroid,
    ContinuousUniverse,
    DeriveProperties,
    Height,
    IntegrationDomain,
    Normalize,
    ScalarFuzzySet,
)
from fuzzyroutines.FuzzyRoutines import MFunction
from fuzzyroutines.membership import (
    Bell,
    Gaussian,
    HarringtonDesirability,
    Hyperbolic,
    Logistic,
    MembershipFunction,
    SShoulder,
    Trapezoid,
    Triangle,
)
from fuzzyroutines.operators import NegationPolicy, SNormPolicy, TNormPolicy

FAMILY_CASES = (
    (Hyperbolic(2, 3, -1), "hyperbolic", {"a": 2, "b": 3, "c": -1}),
    (Bell(-2, -1, 1), "bell", {"a": -2, "b": -1, "c": 1}),
    (SShoulder(-2, 2), "parabolic", {"a": -2, "b": 2}),
    (Triangle(-2, 0, 3), "triangle", {"a": -2, "b": 3, "c": 0}),
    (Triangle(-2, 3, 3), "triangle", {"a": -2, "b": 3, "c": 3}),
    (Trapezoid(-2, -1, 1, 3), "trapezium", {"a": -2, "b": 3, "c": -1, "d": 1}),
    (Gaussian(0, 2), "gaussian", {"a": 0, "b": 2}),
    (Logistic(-2, 1), "logistic", {"a": -2, "b": 1}),
    (HarringtonDesirability(), "desirability", {}),
)


@pytest.mark.parametrize(("modern", "identifier", "parameters"), FAMILY_CASES)
def test_CoreFactoriesRetainHistoricalArithmeticAndAnalyticalProperties(modern, identifier, parameters):
    """Compare established scalar branches and exact geometry after adaptation."""

    legacy = MFunction(identifier, **parameters)
    coordinates = (-1000, -3, -2, -1.5, -1, 0, 0.5, 1, 2, 3, 4, 1000)

    assert [modern(x) for x in coordinates] == [legacy.mju(x) for x in coordinates]
    assert [modern.Evaluate(x) for x in coordinates] == [modern(x) for x in coordinates]
    universe = ContinuousUniverse()
    assert DeriveProperties(modern, universe) == DeriveProperties(legacy, universe)
    assert Height(ScalarFuzzySet(universe, modern)) == Height(ScalarFuzzySet(universe, legacy.mju))


@pytest.mark.parametrize(("modern", "identifier", "parameters"), FAMILY_CASES)
def test_CoreFamiliesRetainAnalyticalAndAdaptiveCentroid(modern, identifier, parameters):
    """Use the same bounded centroid evidence for modern and historical inputs."""

    universe = ContinuousUniverse()
    domain = IntegrationDomain(-3, 4)
    legacy = MFunction(identifier, **parameters)
    expected = Centroid(ScalarFuzzySet(universe, legacy.mju), domain)

    assert Centroid(ScalarFuzzySet(universe, modern), domain) == expected
    assert Centroid(ScalarFuzzySet(universe, modern.Evaluate), domain) == expected


def test_TriangleAndTrapezoidUseConventionalGeometricOrder():
    """Reject historical parameter order rather than silently interpreting it."""

    triangle = Triangle(left=0, peak=2, right=5)
    trapezoid = Trapezoid(left=0, plateau_start=1, plateau_end=3, right=5)

    assert tuple(triangle(x) for x in (0, 1, 2, 3.5, 5)) == (0, 0.5, 1, 0.5, 0)
    assert tuple(trapezoid(x) for x in (0, 0.5, 1, 3, 4, 5)) == (0, 0.5, 1, 1, 0.5, 0)

    with pytest.raises(ValueError):
        Triangle(left=0, peak=5, right=2)

    with pytest.raises(ValueError):
        MembershipFunction("triangle", a=0, b=5, c=2)


def test_CoincidentTrianglePeakRemainsOneAtRightAndZeroBeyond():
    """Retain the supported high-term endpoint without dividing by zero."""

    function = Triangle(0, 1, 1)

    assert function(0) == 0
    assert function(0.5) == 0.5
    assert function(1) == 1
    assert function(math.nextafter(1, math.inf)) == 0
    assert Centroid(ScalarFuzzySet(ContinuousUniverse(), function), IntegrationDomain(0, 1)) == pytest.approx(2 / 3)


def test_ModernParametersAreCopiedReadOnlyAndFunctionIsFrozen():
    """Prevent both direct parameter edits and dataclass field replacement."""

    parameters = {"left": 0, "peak": 1, "right": 2}
    function = MembershipFunction("triangle", **parameters)
    parameters["peak"] = 0.5

    assert function.parameters["peak"] == 1

    with pytest.raises(TypeError):
        function.parameters["peak"] = 0.5

    with pytest.raises(FrozenInstanceError):
        function.family = "gaussian"

    assert function(1) == 1


@pytest.mark.parametrize("invalid", [True, False, math.nan, math.inf, -math.inf, "1", None])
def test_ModernFamilyRejectsInvalidParameters(invalid):
    """Do not convert invalid geometry inputs into plausible membership values."""

    with pytest.raises(ValueError):
        Triangle(0, invalid, 2)


@pytest.mark.parametrize("invalid", [True, False, "1", None])
def test_ModernEvaluationRejectsNonRealCoordinates(invalid):
    """Keep scalar runtime type errors distinct from non-finite value errors."""

    with pytest.raises(TypeError):
        Gaussian(0, 1)(invalid)


@pytest.mark.parametrize("invalid", [math.nan, math.inf, -math.inf])
def test_ModernEvaluationRejectsNonFiniteCoordinates(invalid):
    """Reject non-finite coordinates before evaluating the selected formula."""

    with pytest.raises(ValueError):
        Gaussian(0, 1)(invalid)


def test_ModernAcceptsRealFractionsWhileLegacyBuiltinRestrictionRemains():
    """Retain historical validation while allowing the modern Real contract."""

    modern = Triangle(Fraction(0), Fraction(1), Fraction(2))

    assert modern(Fraction(1, 2)) == Fraction(1, 2)

    with pytest.raises(ValueError):
        MFunction("triangle", a=Fraction(0), b=2, c=1)

    with pytest.raises(ValueError):
        MFunction("triangle", a=0, b=2, c=1).mju(Fraction(1, 2))


def test_NormalizedHistoricalSourceIsFrozenAndModernSourceHasExactHeight():
    """Normalization must preserve evidence independently of mutable adapters."""

    universe = ContinuousUniverse(0, 0.5, True, True)
    historical = MFunction("triangle", a=0, b=2, c=1)
    normalized = Normalize(ScalarFuzzySet(universe, historical.mju))
    modern = Normalize(ScalarFuzzySet(universe, Triangle(0, 1, 2)))
    historical.parameters["c"] = 0.25

    assert normalized.Membership(0.25) == 0.5
    assert modern.Membership(0.25) == 0.5
    assert Height(normalized) == Height(modern) == 1


def test_ModernPolicyImportsRetainExistingPublicClassIdentity():
    """Preserve historical modern import paths when relocating policy ownership."""

    root = importlib.import_module("fuzzyroutines")
    previous_path = importlib.import_module("fuzzyroutines.fuzzysets")

    for policy in (NegationPolicy, TNormPolicy, SNormPolicy):
        assert getattr(root, policy.__name__) is policy
        assert getattr(previous_path, policy.__name__) is policy
        assert policy.__module__ == "fuzzyroutines.operators"


def test_ModernImportsAndExactOperationsDoNotLoadLegacyModule():
    """Block compatibility imports in a clean subprocess exercising modern math."""

    program = '''import importlib.abc
import sys

class LegacyBlocker(importlib.abc.MetaPathFinder):
    """Reject any attempt by modern modules to load the legacy implementation."""

    def find_spec(self, fullname, path=None, target=None):
        """Block the protected module and leave unrelated discovery untouched."""

        if fullname == "fuzzyroutines.FuzzyRoutines":
            raise AssertionError("modern core must not import compatibility implementation")

sys.meta_path.insert(0, LegacyBlocker())
from fuzzyroutines import Centroid, ContinuousUniverse, DeriveProperties, Height, IntegrationDomain, Normalize, ScalarFuzzySet
from fuzzyroutines.membership import Triangle
from fuzzyroutines.operators import TNormPolicy
function = Triangle(0, 1, 2)
universe = ContinuousUniverse()
fuzzy_set = ScalarFuzzySet(universe, function)
assert DeriveProperties(function, universe).height == 1
assert Height(fuzzy_set) == 1
assert Height(Normalize(fuzzy_set)) == 1
assert Centroid(fuzzy_set, IntegrationDomain(0, 2)) == 1
assert TNormPolicy("algebraic").Evaluate(0.5, 0.5) == 0.25
assert "fuzzyroutines.FuzzyRoutines" not in sys.modules
'''
    completed = subprocess.run([sys.executable, "-c", program], text=True, capture_output=True, timeout=30, check=False)

    assert completed.returncode == 0, completed.stderr


def test_AlteredLegacyEvaluatorCannotRetainExactContinuousFormulaEvidence():
    """Reject an analytical source once its registered evaluator is replaced."""

    historical = MFunction("triangle", a=0, b=2, c=1)
    historical.mju = lambda coordinate: 0.5

    with pytest.raises(ValueError, match="unchanged registered evaluator"):
        DeriveProperties(historical, ContinuousUniverse())

    with pytest.raises(ValueError):
        Height(ScalarFuzzySet(ContinuousUniverse(), historical.mju))


def test_GenericCallableLookalikeCannotClaimAnalyticalHeight():
    """Require owned formula evidence rather than caller-supplied metadata."""

    class Lookalike:
        """Arbitrary callable with intentionally misleading analytical attributes."""

        name = "Triangle"
        parameters: ClassVar[dict[str, int]] = {"a": 0, "b": 2, "c": 1}

        def __call__(self, coordinate):
            """Return a constant despite the lookalike triangle metadata."""

            return 0.5

    with pytest.raises(ValueError, match="generic membership callable"):
        Height(ScalarFuzzySet(ContinuousUniverse(), Lookalike()))

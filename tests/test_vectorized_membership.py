# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Scalar-parity and rejection evidence for the optional NumPy experiment."""

import math

import pytest

from experiments.vectorized_membership import EvaluateMembership
from fuzzyroutines.FuzzyRoutines import MFunction

np = pytest.importorskip("numpy", reason="NumPy prototype is an optional experiment")

PARITY_TOLERANCE = 1e-12
FAMILY_CASES = (
    ("hyperbolic", {"a": 2.0, "b": 1.5, "c": 0.0}),
    ("bell", {"a": -2.0, "b": 0.0, "c": 1.0}),
    ("bell", {"a": -2.0, "b": 0.0, "c": 0.0}),
    ("parabolic", {"a": -2.0, "b": 2.0}),
    ("sShoulder", {"a": -2.0, "b": 2.0}),
    ("triangle", {"a": -2.0, "b": 2.0, "c": 0.5}),
    ("triangle", {"a": -2.0, "b": 2.0, "c": 2.0}),
    ("trapezium", {"a": -2.0, "b": 2.0, "c": -0.5, "d": 0.5}),
    ("trapezium", {"a": -2.0, "b": 2.0, "c": 0.0, "d": 0.0}),
    ("exponential", {"a": 0.5, "b": 0.25}),
    ("gaussian", {"a": 0.5, "b": 0.25}),
    ("sigmoidal", {"a": 2.0, "b": 0.5}),
    ("logistic", {"a": -2.0, "b": 0.5}),
    ("desirability", {}),
    ("harringtonDesirability", {}),
)


def _AssertParity(identifier, parameters, values):
    """Compare at binary64 coordinates without using an array formula as oracle."""

    source = np.asarray(values, dtype=np.float64)
    snapshot = source.copy()
    scalarFunction = MFunction(identifier, **parameters)
    expected = np.array([scalarFunction.mju(float(value)) for value in source.flat]).reshape(source.shape)
    result = EvaluateMembership(identifier, source, **parameters)
    np.testing.assert_allclose(result, expected, rtol=0, atol=PARITY_TOLERANCE)
    np.testing.assert_array_equal(source, snapshot)
    assert result.shape == source.shape, "Array membership must preserve coordinate topology."
    assert result.dtype == np.float64, "Prototype arithmetic must use the documented binary64 dtype."
    assert not np.shares_memory(result, source), "Returned grades must not alias caller coordinates."


@pytest.mark.parametrize(("identifier", "parameters"), FAMILY_CASES)
def test_AllFamiliesAndAliasesMatchScalarDenseAndBoundaryEvidence(identifier, parameters):
    """Exercise endpoints, neighboring floats, seeded samples, and noncontiguous arrays."""

    boundaries = list(parameters.values()) + [-2.0, -1.0, 0.0, 0.5, 1.0, 2.0, 3.0]
    anchors = np.asarray(boundaries)
    values = np.concatenate((
        np.linspace(-5.0, 5.0, 501),
        np.random.default_rng(107).uniform(-10.0, 10.0, 501),
        anchors,
        np.nextafter(anchors, -np.inf),
        np.nextafter(anchors, np.inf),
    ))
    _AssertParity(identifier, parameters, values)
    _AssertParity(identifier, parameters, np.arange(24.0).reshape(4, 6)[:, ::2])


@pytest.mark.parametrize(("identifier", "parameters"), FAMILY_CASES)
def test_EmptyArraysAndNumericSequencesPreserveShape(identifier, parameters):
    """Permit empty workloads and float-converted integer or float32 coordinates."""

    _AssertParity(identifier, parameters, np.empty((2, 0, 3)))
    _AssertParity(identifier, parameters, [[-2, 0], [1, 3]])
    _AssertParity(identifier, parameters, np.array([-1.0, 0.0, 1.0], dtype=np.float32))


@pytest.mark.parametrize("values", (
    0.5, True, [True, False], [float("nan")], [float("inf")], [float("-inf")],
    [complex(1, 0)], ["1"], np.array([1], dtype=object),
))
def test_InvalidCoordinatesFailClosed(values):
    """Reject coercions that would silently change the array coordinate contract."""

    with pytest.raises(ValueError, match="values"):
        EvaluateMembership("gaussian", values, a=0.0, b=1.0)


@pytest.mark.parametrize(("identifier", "parameters"), (
    ("unknown", {}), ("gaussian", {"a": 0.0, "b": 0.0}),
    ("triangle", {"a": 0.0, "b": 1.0, "c": 2.0}),
    ("logistic", {"a": True, "b": 1.0}), ("desirability", {"a": 1.0}),
))
def test_ParametersRetainScalarValidation(identifier, parameters):
    """Use the scalar validator for identifiers, geometry, and exact parameter sets."""

    with pytest.raises(ValueError):
        EvaluateMembership(identifier, [0.5], **parameters)


@pytest.mark.parametrize(("identifier", "parameters"), (
    ("gaussian", {"a": 0.0, "b": 1.0}),
    ("logistic", {"a": 2.0, "b": 0.5}),
    ("logistic", {"a": -2.0, "b": 0.5}),
    ("desirability", {}),
))
def test_SaturatingFamiliesMatchExtremeFiniteScalarValues(identifier, parameters):
    """Keep stable logistic branches and Gaussian/desirability representable limits."""

    values = [-1e308, -1000.0, -710.0, -709.0, 0.0, 709.0, 710.0, 1000.0, 1e308]

    with np.errstate(all="raise"):
        _AssertParity(identifier, parameters, values)


def test_InactivePiecewiseBranchesDoNotRaiseForRemoteCoordinates():
    """Avoid eager branch evaluation, including a valid c-equals-b triangle."""

    with np.errstate(all="raise"):
        _AssertParity("triangle", {"a": 0.0, "b": 1.0, "c": 1.0}, [-1e308, 0, 1, 1e308])
        _AssertParity("parabolic", {"a": 0.0, "b": 1.0}, [-1e308, 0, 1, 1e308])
        _AssertParity("bell", {"a": 0.0, "b": 1.0, "c": 1.0}, [-1e308, 0, 1, 1e308])


def test_DesirabilityMatchesAtInnerExponentialOverflowBoundary():
    """Preserve the scalar binary64 cutoff and its adjacent representable values."""

    cutoff = -math.log(float.fromhex("0x1.fffffffffffffp+1023"))
    values = [np.nextafter(cutoff, -np.inf), cutoff, np.nextafter(cutoff, np.inf)]

    with np.errstate(all="raise"):
        _AssertParity("desirability", {}, values)


def test_UnrepresentablePowerAndSquaredDenominatorRaiseExplicitly():
    """Do not turn scalar intermediate failures into plausible zero grades."""

    with pytest.raises(OverflowError):
        EvaluateMembership("hyperbolic", [1e308], a=2.0, b=2.0, c=0.0)

    with pytest.raises(ZeroDivisionError):
        EvaluateMembership("parabolic", [1e-301], a=0.0, b=1e-300)


def test_EvaluationKeepsCallerParametersAndNumpyErrorPolicyUnchanged():
    """Snapshot scalar validation and restore the ambient NumPy error policy."""

    parameters = {"a": 0.0, "b": 1.0}
    original = parameters.copy()
    errorPolicy = np.geterr().copy()
    EvaluateMembership("gaussian", [0.0, 1.0], **parameters)
    assert parameters == original, "Evaluation must not rewrite caller-owned parameters."
    assert np.geterr() == errorPolicy, "Experiment must not alter process-wide NumPy error settings."

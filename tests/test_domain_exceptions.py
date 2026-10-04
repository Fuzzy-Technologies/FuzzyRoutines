# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Domain error categories, built-in catch compatibility, and adapter boundaries."""

import math
import pickle

import pytest

from fuzzyroutines import CentroidConvergenceError as ExportedConvergenceError
from fuzzyroutines import exceptions
from fuzzyroutines.alphacuts import AlphaCut
from fuzzyroutines.defuzzification import (
    Centroid,
    CentroidConvergenceError,
    CentroidPolicy,
)
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse, IntegrationDomain
from fuzzyroutines.exceptions import (
    FuzzyRoutinesError,
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
    NumericalError,
    UndefinedResultError,
)
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction
from fuzzyroutines.fuzzysets import Intersection, Normalize, ScalarFuzzySet
from fuzzyroutines.linguistic import LinguisticTerm
from fuzzyroutines.membership import Triangle
from fuzzyroutines.operators import NegationPolicy, TNormPolicy
from fuzzyroutines.properties import ContinuousInterval
from fuzzyroutines.relations import ComparisonDomain


@pytest.mark.parametrize(
    ("error_type", "builtin_type"),
    [
        (InvalidParameterTypeError, TypeError),
        (InvalidParameterError, ValueError),
        (InvalidDomainError, ValueError),
        (NumericalError, ArithmeticError),
        (UndefinedResultError, ValueError),
        (UndefinedResultError, ArithmeticError),
        (CentroidConvergenceError, ArithmeticError),
    ],
)
def test_ErrorCategoriesPreserveBuiltInHandlersAndSerialization(error_type, builtin_type):
    """Domain categories remain compatible with built-in catches and pickles."""

    error = error_type("invalid test input")
    assert isinstance(error, FuzzyRoutinesError), "Owned errors must share the modern base category"

    with pytest.raises(builtin_type) as captured:
        raise error

    restored = pickle.loads(pickle.dumps(captured.value))
    assert type(restored) is error_type, "Serialization changed the error category"
    assert restored.args == error.args, "Serialization changed the exception message"


def test_ExceptionModuleDefinesOnlyExplicitPublicCategories():
    """The dedicated module is the authoritative import path for new errors."""

    assert set(exceptions.__all__) == {
        "FuzzyRoutinesError",
        "InvalidParameterTypeError",
        "InvalidParameterError",
        "InvalidDomainError",
        "NumericalError",
        "UndefinedResultError",
    }
    assert ExportedConvergenceError is CentroidConvergenceError, "The root export changed convergence identity"
    assert CentroidConvergenceError.__module__ == "fuzzyroutines.defuzzification", "The existing error moved modules"
    assert issubclass(InvalidDomainError, InvalidParameterError)
    assert issubclass(UndefinedResultError, NumericalError)


@pytest.mark.parametrize(
    ("operation", "error_type"),
    [
        (lambda: ContinuousUniverse(1.0, 0.0), InvalidDomainError),
        (lambda: IntegrationDomain(0.0, 0.0), InvalidDomainError),
        (lambda: DiscreteUniverse((0.0, 0.0)), InvalidDomainError),
        (lambda: ComparisonDomain(()), InvalidDomainError),
        (lambda: ContinuousInterval(1.0, 0.0), InvalidDomainError),
        (lambda: Triangle(left=1.0, peak=0.0, right=2.0), InvalidParameterError),
        (lambda: Triangle(left=0.0, peak=0.5, right=1.0).Evaluate(True), InvalidParameterTypeError),
        (lambda: NegationPolicy("unknown"), InvalidParameterError),
        (lambda: NegationPolicy("standard").Evaluate(float("nan")), InvalidParameterError),
        (lambda: CentroidPolicy(maximumDepth=True), InvalidParameterTypeError),
        (lambda: LinguisticTerm("", None), InvalidParameterError),
        (lambda: AlphaCut(None, 0.5), InvalidParameterTypeError),
    ],
)
def test_ModernBoundariesRaiseSpecificCategories(operation, error_type):
    """Each mathematical module uses the applicable owned validation category."""

    with pytest.raises(error_type) as captured:
        operation()

    assert type(captured.value) is error_type, "The boundary changed the concrete exception type"


def test_UniverseRelationshipsHaveDomainErrors():
    """Out-of-universe evaluation and mismatched set operations share a category."""

    fuzzy_set = ScalarFuzzySet(DiscreteUniverse((0.0,)), lambda coordinate: 1.0)
    other_set = ScalarFuzzySet(DiscreteUniverse((1.0,)), lambda coordinate: 1.0)

    with pytest.raises(InvalidDomainError):
        fuzzy_set.Membership(1.0)

    with pytest.raises(InvalidDomainError):
        Intersection(fuzzy_set, other_set, TNormPolicy("logic"))

    with pytest.raises(InvalidDomainError):
        IntegrationDomain(-1.0, 1.0).ValidateWithin(ContinuousUniverse(0.0, 1.0, True, True))


def test_ZeroAreaAndZeroHeightUseUndefinedResultErrors():
    """Undefined results support numerical and existing ValueError handlers."""

    continuous_set = ScalarFuzzySet(ContinuousUniverse(0.0, 1.0, True, True), lambda coordinate: 0.0)
    discrete_set = ScalarFuzzySet(DiscreteUniverse((0.0,)), lambda coordinate: 0.0)

    with pytest.raises(UndefinedResultError, match="zero membership area"):
        Centroid(continuous_set, IntegrationDomain(0.0, 1.0))

    with pytest.raises(UndefinedResultError, match="zero-height"):
        Normalize(discrete_set)


def test_ConvergenceFailureRetainsExistingClassAndNumericalCategory():
    """The pre-existing convergence class remains the actual raised exception."""

    fuzzy_set = ScalarFuzzySet(
        ContinuousUniverse(0.0, 1.0, True, True),
        lambda coordinate: math.exp(coordinate) / math.e,
    )

    with pytest.raises(NumericalError) as captured:
        Centroid(fuzzy_set, IntegrationDomain(0.0, 1.0), CentroidPolicy(1e-16, 1e-16, 0))

    assert type(captured.value) is CentroidConvergenceError, "Numerical categorization replaced the convergence class"


@pytest.mark.parametrize("error_type", [ValueError, UndefinedResultError, InvalidParameterError, RuntimeError, CentroidConvergenceError])
@pytest.mark.parametrize("boundary", ["modern", "historical"])
def test_CallbackFailuresPropagateTheSameObject(error_type, boundary):
    """Even an evaluator's own domain error must escape adapter translation."""

    error = error_type("user evaluator failed")

    def FailingMembership(coordinate):
        """Raise a retained user-owned error from a custom evaluator."""

        raise error

    if boundary == "modern":
        fuzzy_set = ScalarFuzzySet(ContinuousUniverse(0.0, 1.0, True, True), FailingMembership)
        operation = lambda: Centroid(fuzzy_set, IntegrationDomain(0.0, 1.0))

    else:
        function = MFunction("desirability")
        function.mju = FailingMembership
        fuzzy_set = FuzzySet(function, (0.0, 1.0))
        operation = fuzzy_set.Defuz

    with pytest.raises(error_type) as captured:
        operation()

    assert captured.value is error, "The operation replaced the evaluator's exception object"


@pytest.mark.parametrize(
    ("interval", "error_type"),
    [([0.0, 1.0], TypeError), ((True, 1.0), TypeError), ((0.0,), ValueError), ((1.0, 0.0), ValueError), ((0.0, math.inf), ValueError)],
)
def test_HistoricalDomainChecksPreserveConcreteBuiltInTypes(interval, error_type):
    """Only known constructor failures translate to historical concrete errors."""

    with pytest.raises(error_type) as captured:
        FuzzySet(MFunction("desirability"), interval)

    assert type(captured.value) is error_type, "The boundary changed the concrete exception type"
    fuzzy_set = FuzzySet(MFunction("desirability"))

    with pytest.raises(error_type) as captured:
        fuzzy_set.supportSet = interval

    assert type(captured.value) is error_type, "The boundary changed the concrete exception type"
    assert fuzzy_set.supportSet == (0.0, 1.0), "Invalid assignment changed the historical interval"


def test_HistoricalGeometryChecksRemainConcreteValueError():
    """The analytical validator shared with historical membership stays protected."""

    with pytest.raises(ValueError) as captured:
        MFunction("triangle", a=1.0, b=2.0, c=0.0)

    assert type(captured.value) is ValueError, "Historical validation lost concrete ValueError compatibility"


def test_HistoricalUndefinedCentroidRemainsConcreteValueError():
    """The adapter chooses its result error inside the engine without catching callbacks."""

    function = MFunction("triangle", a=0.0, b=1.0, c=0.5)
    fuzzy_set = FuzzySet(function, (2.0, 3.0))

    with pytest.raises(ValueError, match="zero membership area") as captured:
        fuzzy_set.Defuz()

    assert type(captured.value) is ValueError, "Historical validation lost concrete ValueError compatibility"



def test_HistoricalAdaptiveFailureRetainsConvergenceClass():
    """Legacy engine failures retain the established arithmetic exception type."""

    function = MFunction("desirability")
    function.mju = lambda coordinate: 1.0 if coordinate < 0.123456789 else 0.0
    fuzzy_set = FuzzySet(function, (0.0, 1.0))

    with pytest.raises(CentroidConvergenceError) as captured:
        fuzzy_set.Defuz()

    assert type(captured.value) is CentroidConvergenceError, "Numerical categorization replaced the convergence class"


def test_HistoricalGenericValidationErrorRemainsConcreteException():
    """Protected historical object-kind checks do not join the modern hierarchy."""

    with pytest.raises(Exception) as captured:
        FuzzySet(MFunction("desirability"), linguisticName=None)

    assert type(captured.value) is Exception, "Historical validation changed its protected generic exception"


def test_HistoricalConstructionDoesNotInvokeOverriddenSupportSetter():
    """Construction initializes the base domain before later property dispatch."""

    class CustomFuzzySet(FuzzySet):
        """Reject explicit interval assignments through a user-owned setter."""

        @FuzzySet.supportSet.setter
        def supportSet(self, value):
            """Expose unexpected constructor dispatch with a deterministic error."""

            raise RuntimeError("custom support setter called")

    fuzzy_set = CustomFuzzySet(MFunction("desirability"), (0.25, 0.75))
    assert fuzzy_set.supportSet == (0.25, 0.75), "Construction did not initialize the inherited domain getter"

    with pytest.raises(RuntimeError, match="custom support setter called"):
        fuzzy_set.supportSet = (0.0, 1.0)

    assert fuzzy_set.supportSet == (0.25, 0.75), "The overridden setter changed the initialized base domain"

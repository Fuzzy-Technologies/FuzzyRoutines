# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private eligibility checks and ordered snapshots for Sugeno batches."""

import inspect
from dataclasses import dataclass

from fuzzyroutines._sugeno_antecedents import _PrepareAntecedents, _PreparedAntecedents
from fuzzyroutines._sugeno_consequents import (
    _Binary64Value,
    _PrepareConsequents,
    _PreparedConsequents,
)
from fuzzyroutines.domain import ContinuousUniverse, DiscreteUniverse
from fuzzyroutines.exceptions import InvalidParameterTypeError
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import FuzzyVariable, SugenoModel, SugenoRule
from fuzzyroutines.linguistic import LinguisticTerm
from fuzzyroutines.membership import (
    MembershipFunction,
    _AnalyticalSource,
    _GetAnalyticalSource,
)


@dataclass(frozen=True, slots=True)
class _PreparedModel:
    """Frozen feature, term and rule metadata in model declaration order."""

    featureNames: tuple[str, ...]
    universes: tuple[ContinuousUniverse | DiscreteUniverse, ...]
    termNames: tuple[tuple[str, str], ...]
    termSources: tuple[tuple[int, _AnalyticalSource], ...]
    ruleNames: tuple[str, ...]
    weights: tuple[float, ...]
    antecedents: _PreparedAntecedents
    consequents: _PreparedConsequents


def _PrepareUniverse(universe: ContinuousUniverse | DiscreteUniverse) -> ContinuousUniverse | DiscreteUniverse:
    """Snapshot the supported finite bounds or points without custom behavior."""

    if type(universe) is ContinuousUniverse:
        return ContinuousUniverse(
            None if universe.left is None else _Binary64Value(universe.left),
            None if universe.right is None else _Binary64Value(universe.right),
            universe.leftClosed,
            universe.rightClosed,
        )

    if type(universe) is DiscreteUniverse:
        return DiscreteUniverse(tuple(_Binary64Value(point) for point in universe.points))

    raise InvalidParameterTypeError("batch model inputs require built-in continuous or discrete universes")


def _PrepareTermSource(function: object) -> _AnalyticalSource:
    """Accept built-in or unchanged inherited membership without calling it."""

    functionType = type(function)

    if (
        type(functionType) is not type
        or not issubclass(functionType, MembershipFunction)
        or inspect.getattr_static(functionType, "__getattribute__") is not object.__getattribute__
        or inspect.getattr_static(functionType, "__call__") is not MembershipFunction.__call__
        or inspect.getattr_static(function, "Evaluate", None) is not MembershipFunction.Evaluate
        or inspect.getattr_static(function, "_source", None) is not inspect.getattr_static(MembershipFunction, "_source")
    ):
        raise InvalidParameterTypeError("batch model terms require an unchanged analytical membership evaluator")

    source = _GetAnalyticalSource(function)

    if source is None:
        raise InvalidParameterTypeError("batch model terms require a trusted analytical membership source")

    for _, value in source.parameterItems:
        # The array kernel also needs the original int/float type for endpoint arithmetic.
        _Binary64Value(value)

    return source


def _PrepareModel(model: object) -> _PreparedModel:
    """Validate an eligible model before any observation or membership evaluation.

    Snapshot every declared input term, including unreferenced terms. Prepared
    arrays can then use the existing analytical kernels without retaining or
    invoking the original membership objects.
    """

    if type(model) is not SugenoModel or (
        type(model.inputs) is not tuple or type(model.rules) is not tuple or not model.inputs or not model.rules
    ):
        raise InvalidParameterTypeError("batch evaluation requires a built-in Sugeno model and immutable tuples")

    featureNames = []
    universes = []
    termNames = []
    termSources = []

    for featureIndex, variable in enumerate(model.inputs):
        if type(variable) is not FuzzyVariable or type(variable.name) is not str or type(variable.terms) is not tuple:
            raise InvalidParameterTypeError("batch model inputs require built-in variables, names and term tuples")

        featureNames.append(variable.name)
        featureUniverse = None

        for term in variable.terms:
            if type(term) is not LinguisticTerm or type(term.name) is not str or type(term.fuzzySet) is not ScalarFuzzySet:
                raise InvalidParameterTypeError("batch model terms require built-in terms, names and fuzzy sets")

            universe = _PrepareUniverse(term.fuzzySet.universe)

            if featureUniverse is None:
                featureUniverse = universe

            termNames.append((variable.name, term.name))
            termSources.append((featureIndex, _PrepareTermSource(term.fuzzySet.membershipFunction)))

        if featureUniverse is None:
            raise InvalidParameterTypeError("batch model inputs require at least one term")

        universes.append(featureUniverse)

    for rule in model.rules:
        if type(rule) is not SugenoRule or type(rule.name) is not str:
            raise InvalidParameterTypeError("batch model rules require built-in rules and names")

    return _PreparedModel(
        tuple(featureNames),
        tuple(universes),
        tuple(termNames),
        tuple(termSources),
        tuple(rule.name for rule in model.rules),
        tuple(_Binary64Value(rule.weight) for rule in model.rules),
        _PrepareAntecedents(
            tuple(rule.antecedent for rule in model.rules),
            {name: index for index, name in enumerate(termNames)},
            model.policy,
        ),
        _PrepareConsequents(
            tuple(rule.consequent for rule in model.rules),
            {name: index for index, name in enumerate(featureNames)},
            model.outputUniverse,
        ),
    )

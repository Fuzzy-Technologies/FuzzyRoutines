"""Shared implementations for exact names in the compatibility registry."""

import pytest

from fuzzyroutines.FuzzyRoutines import MFunction

ALIASCASES = (
    ("sShoulder", "parabolic", {"a": 0.2, "b": 0.8}),
    ("gaussian", "exponential", {"a": 0.5, "b": 0.2}),
    ("logistic", "sigmoidal", {"a": 3.0, "b": 0.5}),
    ("harringtonDesirability", "desirability", {}),
)

GRIDVALUES = (-1.0, 0.0, 0.2, 0.5, 0.8, 1.0, 2.0)


@pytest.mark.parametrize(("alias", "historicalIdentifier", "parameters"), ALIASCASES)
def test_CompatibilityRegistryNamesShareOneImplementation(alias, historicalIdentifier, parameters):
    aliasFunction = MFunction(alias, **parameters)
    historicalFunction = MFunction(historicalIdentifier, **parameters)

    assert aliasFunction.mju.__func__ is historicalFunction.mju.__func__, (
        "Exact registry names must dispatch to one shared implementation."
    )
    assert [aliasFunction.mju(value) for value in GRIDVALUES] == pytest.approx(
        [historicalFunction.mju(value) for value in GRIDVALUES],
        abs=1e-15,
    )


@pytest.mark.parametrize(
    ("alias", "parameters", "message"),
    [
        ("sShoulder", {"a": 0.5, "b": 0.5}, "a < b"),
        ("gaussian", {"a": 0.0, "b": 0.0}, "b > 0"),
        ("logistic", {"a": 0.0, "b": 0.0}, "non-zero"),
        ("harringtonDesirability", {"a": 0.0}, "requires exactly"),
    ],
)
def test_CompatibilityRegistryNameSharesParameterValidation(alias, parameters, message):
    with pytest.raises(ValueError, match=message):
        MFunction(alias, **parameters)

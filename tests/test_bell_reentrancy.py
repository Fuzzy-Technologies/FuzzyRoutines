"""Purity and parity tests for the historical Bell membership family."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from fuzzyroutines.FuzzyRoutines import MFunction

REFERENCEVALUES = (
    (0.1, 0.0),
    (0.2, 0.0),
    (0.3, 0.5),
    (0.4, 1.0),
    (0.5, 1.0),
    (0.6, 1.0),
    (0.7, 0.5),
    (0.8, 0.0),
    (0.9, 0.0),
)


def test_BellEvaluationPreservesParameters():
    membershipFunction = MFunction("bell", a=0.2, b=0.4, c=0.6)
    originalParameters = dict(membershipFunction.parameters)

    for inputValue, expectedValue in REFERENCEVALUES:
        assert membershipFunction.mju(inputValue) == pytest.approx(expectedValue, abs=1e-12), (
            "Bell evaluation changed a historical reference value."
        )

    assert membershipFunction.parameters == originalParameters, (
        "Bell evaluation must not mutate its shared parameter mapping."
    )


def test_BellEvaluationIsReentrantAcrossThreads():
    membershipFunction = MFunction("bell", a=0.2, b=0.4, c=0.6)
    inputValues = tuple(value for value, _ in REFERENCEVALUES) * 100
    expectedValues = tuple(value for _, value in REFERENCEVALUES) * 100

    with ThreadPoolExecutor(max_workers=8) as executor:
        actualValues = tuple(executor.map(membershipFunction.mju, inputValues))

    assert actualValues == pytest.approx(expectedValues, abs=1e-12), (
        "Concurrent Bell evaluation must match the scalar reference values."
    )

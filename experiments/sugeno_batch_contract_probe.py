# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Compare a two-rule NumPy witness with scalar Sugeno and count trace bytes.

Run from the checkout with python -m experiments.sugeno_batch_contract_probe.
This probe assumes trusted fixture shapes and parameters. It is neither a
general inference engine nor an installed performance benchmark.
"""

import json
import math
import sys
from fractions import Fraction

import numpy as np

from fuzzyroutines.domain import ContinuousUniverse
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    NumericalError,
    UndefinedResultError,
)
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import (
    AffineConsequent,
    AllOf,
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    SugenoModel,
    SugenoRule,
    TermCondition,
)
from fuzzyroutines.linguistic import LinguisticTerm
from fuzzyroutines.membership import Triangle
from fuzzyroutines.operators import NegationPolicy, SNormPolicy, TNormPolicy

FEATURES = ("risk", "exposure")
UNIT = ContinuousUniverse(0, 1, True, True)
POLICY = InferencePolicy(TNormPolicy("algebraic"), SNormPolicy("logic"), NegationPolicy("standard"))
RULE_FIELDS = {
    "antecedent": "antecedentGrade",
    "firing": "firingStrength",
    "consequent": "consequentValue",
    "normalized": "normalizedStrength",
    "contribution": "contribution",
}
ERRORS = {1: InvalidParameterError, 2: InvalidDomainError, 3: UndefinedResultError, 4: InvalidDomainError}


def ScalarModel(order: str) -> SugenoModel:
    """Build the two-rule witness using eligible built-in scalar terms."""

    low = LinguisticTerm("low", ScalarFuzzySet(UNIT, Triangle(-1, 0, 1)))
    high = LinguisticTerm("high", ScalarFuzzySet(UNIT, Triangle(0, 1, 1)))
    gate = LinguisticTerm("gate", ScalarFuzzySet(UNIT, Triangle(0, 0.5, 1)))
    unused = LinguisticTerm("unused", low.fuzzySet)
    variables = (FuzzyVariable("risk", (low, high)), FuzzyVariable("exposure", (gate, unused)))
    consequents = (
        ConstantConsequent(0.25) if order != "affine" else AffineConsequent(
            0.125, (("exposure", 0.125), ("risk", 0.25)),
        ),
        ConstantConsequent(0.75) if order == "constant" else AffineConsequent(
            0.5, (("exposure", 0.75), ("risk", 0.125)),
        ),
    )
    rules = tuple(
        SugenoRule(term, AllOf((TermCondition("risk", term), TermCondition("exposure", "gate"))), consequent, weight)
        for term, consequent, weight in zip(("low", "high"), consequents, (0.5, 1.0), strict=True)
    )

    return SugenoModel(variables, rules, POLICY, UNIT)


def EvaluateWitness(
    values: np.ndarray, names: tuple[str, ...], order: str, trace: str, limit: int, policy: str = "mask",
) -> dict[str, np.ndarray]:
    """Evaluate only the closed-form ordinary-range fixture in row chunks."""

    size = len(values)
    axes = [names.index(name) for name in FEATURES]
    result = {"values": np.full(size, np.nan), "status": np.zeros(size, dtype=np.uint8)}

    if trace != "off":
        result.update(fired_rule_count=np.full(size, -1, dtype=np.int64), max_firing_strength=np.full(size, np.nan))

    if trace == "full":
        result.update({key: np.full((size, 2), np.nan) for key in RULE_FIELDS})
        result.update(
            input_grades=np.full((size, 4), np.nan),
            exact_normalized=np.zeros((size, 2), dtype=np.bool_),
            rule_weights=np.array([0.5, 1.0]),
        )

    for start in range(0, size, limit):
        end = min(start + limit, size)

        with np.errstate(over="ignore"):
            coordinates = np.array(values[start:end, axes], dtype=np.float64, order="C")

        status = result["status"][start:end]
        finite = np.isfinite(coordinates).all(axis=1)
        inside = ((coordinates >= 0) & (coordinates <= 1)).all(axis=1)
        status[~finite], status[finite & ~inside] = 1, 2
        rows = np.flatnonzero(status == 0)
        risk, exposure = coordinates[rows].T

        gate = 2 * np.minimum(exposure, 1 - exposure)
        antecedent = np.column_stack((1 - risk, risk)) * gate[:, None]
        firing = antecedent * [0.5, 1.0]
        maximum = firing.max(axis=1)
        fired = maximum > 0
        status[rows[~fired]] = 3

        low = 0.125 + 0.125 * exposure + 0.25 * risk if order == "affine" else np.full(len(rows), 0.25)
        high = np.full(len(rows), 0.75) if order == "constant" else 0.5 + 0.75 * exposure + 0.125 * risk
        consequent = np.column_stack((low, high))
        eligible = ((consequent >= 0) & (consequent <= 1)).all(axis=1)
        status[rows[fired & ~eligible]] = 4

        if policy == "raise" and np.any(status):
            first = int(np.flatnonzero(status)[0])

            raise ERRORS[int(status[first])](f"row {start + first}")

        valid = fired & eligible
        accepted = start + rows[valid]
        scaled = firing[valid] / maximum[valid, None]
        normalized = scaled / scaled.sum(axis=1, keepdims=True)
        contribution = normalized * consequent[valid]
        result["values"][accepted] = contribution.sum(axis=1)

        if trace != "off":
            result["fired_rule_count"][start + rows[~fired]] = 0
            result["max_firing_strength"][start + rows[~fired]] = 0
            result["fired_rule_count"][accepted] = (firing[valid] > 0).sum(axis=1)
            result["max_firing_strength"][accepted] = maximum[valid]

        if trace == "full":
            result["input_grades"][accepted] = np.column_stack((1 - risk, risk, gate, 1 - exposure))[valid]
            result["antecedent"][accepted] = antecedent[valid]
            result["firing"][accepted] = firing[valid]
            result["consequent"][accepted] = consequent[valid]
            result["normalized"][accepted] = normalized
            result["contribution"][accepted] = contribution

    result["valid_mask"] = result["status"] == 0

    for array in result.values():
        array.setflags(write=False)

    return result


def CheckParity(rows: np.ndarray, names: tuple[str, ...], order: str, expected: list[int]) -> float:
    """Check scalar outcomes and all retained fields across layouts and chunks."""

    model = ScalarModel(order)
    reference = EvaluateWitness(rows, names, order, "full", 1)
    np.testing.assert_array_equal(reference["status"], expected)
    np.testing.assert_array_equal(reference["rule_weights"], [0.5, 1.0])
    assert not reference["exact_normalized"].any(), "Ordinary rows need no exact-ratio trace entries"
    delta = 0.0

    for index, (row, status) in enumerate(zip(rows, expected, strict=True)):
        inputs = dict(zip(names, (float(value) for value in row), strict=True))

        if status:
            try:
                model.Evaluate(inputs)

            except ERRORS[status] as error:
                assert type(error) is ERRORS[status], "The scalar exception category must match the declared row witness"

            else:
                raise AssertionError(f"Scalar evaluation unexpectedly accepted witness row {index}")

            assert math.isnan(reference["values"][index]), "Failed rows cannot contain a finite prediction"
            assert not reference["valid_mask"][index], "Failed rows must be masked"
            assert np.isnan(reference["input_grades"][index]).all(), "Failed rows must not retain partial grades"

            for key in RULE_FIELDS:
                assert np.isnan(reference[key][index]).all(), "Failed rows must not retain partial rule trace"

            count = 0 if status == 3 else -1
            assert reference["fired_rule_count"][index] == count, "Only true no-fire has a known zero count"

            if status == 3:
                assert reference["max_firing_strength"][index] == 0, "True no-fire has zero maximum firing"

            else:
                assert math.isnan(reference["max_firing_strength"][index]), "Other failures have no maximum firing"

            continue

        scalar = model.Evaluate(inputs)
        delta = max(delta, abs(reference["values"][index] - scalar.value))
        np.testing.assert_allclose(reference["values"][index], scalar.value, rtol=0, atol=1e-12)
        np.testing.assert_allclose(reference["input_grades"][index], [item.grade for item in scalar.inputGrades], rtol=0, atol=1e-12)

        for key, field in RULE_FIELDS.items():
            np.testing.assert_allclose(reference[key][index], [getattr(rule, field) for rule in scalar.rules], rtol=0, atol=1e-12)

        assert reference["valid_mask"][index], "Every scalar success must remain valid in the batch"
        assert reference["fired_rule_count"][index] == sum(rule.firingStrength > 0 for rule in scalar.rules), "Fired rule count must use strict positivity"
        assert reference["max_firing_strength"][index] == max(rule.firingStrength for rule in scalar.rules), "Summary must retain the strongest firing"

    for limit in (1, 3, 32):
        for trace in ("off", "summary", "full"):
            batch = EvaluateWitness(rows, names, order, trace, limit)
            size = len(rows)
            budget = {"off": 10 * size, "summary": 26 * size, "full": 140 * size + 16}
            assert sum(array.nbytes for array in batch.values()) == budget[trace], "Trace payload must match the stated byte budget"

            for key, array in batch.items():
                np.testing.assert_array_equal(array, reference[key], strict=True)
                assert not array.flags.writeable and not np.shares_memory(rows, array), "Result arrays must be read-only snapshots"

    return delta


def CheckNumerics() -> None:
    """Expose scalar safeguards a general array engine must preserve."""

    term = ScalarModel("constant").inputs[0].terms[1]
    variable = FuzzyVariable("x", (term,))
    condition = TermCondition("x", "high")
    tiny = math.ulp(0.0)
    model = SugenoModel((variable,), (SugenoRule("low weight", condition, ConstantConsequent(1), 0.5),), POLICY, UNIT)

    for coordinate, category in ((0.0, UndefinedResultError), (tiny, NumericalError)):
        try:
            model.Evaluate({"x": coordinate})

        except category as error:
            assert type(error) is category, "True zero and positive firing underflow must remain distinct"

        else:
            raise AssertionError("Expected an explicit scalar failure for zero or lost firing")

    rules = (
        SugenoRule("large value", condition, ConstantConsequent(2.0**1023), tiny),
        SugenoRule("zero a", condition, ConstantConsequent(0)),
        SugenoRule("zero b", condition, ConstantConsequent(0)),
    )
    result = SugenoModel((variable,), rules, POLICY, ContinuousUniverse()).Evaluate({"x": 1.0})
    exact = Fraction(tiny) / (2 + Fraction(tiny))
    assert result.rules[0].normalizedStrength == exact and float(exact) == 0, "The full trace needs a reconstructible exact ratio"
    assert result.rules[0].contribution == result.value == 2.0**-52, "The rounded ratio must not erase a representable contribution"

    variables = (variable, FuzzyVariable("y", (term,)))
    large = 2.0**54
    cancellation = SugenoRule("ordered sum", condition, AffineConsequent(large, (("x", 1), ("y", -large))))
    model = SugenoModel(variables, (cancellation,), POLICY, ContinuousUniverse(1, 2, True, True))
    assert model.Evaluate({"x": 1.0, "y": 1.0}).value == 1, "An unchecked sum would erase the unit residual"


def Main() -> None:
    """Verify the bounded witness and emit its deterministic evidence."""

    rows = np.array([
        [0.25, 0.25], [0.5, 0], [1.5, 0.25], [0, 0.875], [np.nan, 2],
        [1, 0.5], [0.25, 1], [0.5, 0.25], [0, 0.5], [0.1, 0.3],
    ])
    original = rows.copy()
    permuted = rows[:, ::-1]
    permuted.setflags(write=False)
    cases = (
        (rows, FEATURES, slice(None)),
        (permuted, FEATURES[::-1], slice(None)),
        (rows.astype(np.float32), FEATURES, slice(None)),
        (rows.astype(rows.dtype.newbyteorder("S")), FEATURES, slice(None)),
        (rows[::-1], FEATURES, slice(None, None, -1)),
        (rows[:1], FEATURES, slice(0, 1)),
        (rows[:0], FEATURES, slice(0, 0)),
        (np.array([[1, 0]], dtype=np.uint16), FEATURES, slice(1, 2)),
    )

    if np.finfo(np.longdouble).max > np.finfo(np.float64).max:
        oversize = np.array([[np.longdouble(np.finfo(np.float64).max) * 2, 0.5]])
        cases += ((oversize, FEATURES, slice(4, 5)),)

    errors = {}

    for order, analytical in (("constant", 9 / 20), ("affine", 67 / 160), ("mixed", 7 / 16)):
        expected = [0, 3, 2, 0 if order == "constant" else 4, 1, 0, 3, 0, 0, 0]
        errors[order] = max(CheckParity(data, names, order, expected[selected]) for data, names, selected in cases)
        result = EvaluateWitness(rows[:1], FEATURES, order, "off", 1)
        assert abs(result["values"][0] - analytical) <= 1e-12, "The weighted output must agree with the independent rational reference"

    for limit in (1, 3, 32):
        # A later no-fire precedes consequent validation within a kernel, but not in source row order.
        try:
            EvaluateWitness(rows[[0, 3, 1, 4]], FEATURES, "affine", "full", limit, "raise")

        except InvalidDomainError as error:
            assert str(error) == "row 1", "Raise mode must report the earliest source row across stages and chunks"

        else:
            raise AssertionError("Raise mode must fail on the inactive out-of-universe consequent")

    np.testing.assert_array_equal(rows, original)
    CheckNumerics()
    payload = {
        mode: sum(array.nbytes for array in EvaluateWitness(rows, FEATURES, "mixed", mode, 3).values())
        for mode in ("off", "summary", "full")
    }
    print(json.dumps({
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "rows": len(rows),
        "max_absolute_error": errors,
        "trace_payload_bytes": payload,
    }, sort_keys=True))


if __name__ == "__main__":
    Main()

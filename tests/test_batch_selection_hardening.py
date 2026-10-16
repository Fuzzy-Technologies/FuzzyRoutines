# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Check optimized selection against a row-wise policy oracle, including empty axes."""

import itertools

import pytest

from fuzzyroutines import FuzzificationPolicy
from fuzzyroutines.batches import _Selection

np = pytest.importorskip("numpy")


def test_SelectionMatchesIndependentRowWiseChoices():
    """Cover 180 shape/policy combinations without cumulative-scan or argmax oracles."""

    random = np.random.default_rng(20261016)

    for shape, tiePolicy, tolerance, threshold in itertools.product(
        ((100, 5), (2, 3, 7), (0, 5), (2, 0, 3), (100, 1)),
        ("first", "last", "all"), (0.0, 1e-12, 0.1, 1.0), (0.0, 0.5, 1.0),
    ):
        grades = random.choice((0.0, 0.2, 0.5, 0.7, 1.0), size=shape)
        policy = FuzzificationPolicy(tiePolicy=tiePolicy, tieTolerance=tolerance, minimumConfidence=threshold)
        _, tied, selected = _Selection(np, grades, policy)
        expected = np.zeros_like(tied)
        rows = tied.reshape((-1, shape[-1]))
        expectedRows = expected.reshape((-1, shape[-1]))

        for row, target in zip(rows, expectedRows, strict=True):
            choices = [index for index, eligible in enumerate(row) if eligible]

            if choices:
                chosen = choices if tiePolicy == "all" else [choices[0] if tiePolicy == "first" else choices[-1]]
                target[chosen] = True

        assert np.array_equal(selected, expected), f"Selection changed for {shape=}, {tiePolicy=}, {tolerance=}, {threshold=}"

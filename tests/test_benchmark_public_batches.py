# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Verify benchmark workload equivalence without measuring speed in CI."""

import pytest

from experiments.benchmark_public_batches import (
    BACKENDS,
    MODES,
    WORKLOADS,
    BuildOperation,
    BuildReport,
    CheckParity,
)

pytest.importorskip("numpy")


@pytest.mark.parametrize("workload", WORKLOADS)
@pytest.mark.parametrize("mode", MODES)
def test_BenchmarkUsesCurrentPublicOperationsWithEquivalentEvidence(workload, mode):
    """Compare whole results on a shaped workload before any timing is permitted."""

    operations = {backend: BuildOperation(workload, backend, mode, (3, 5))[0] for backend in BACKENDS}
    evidence = CheckParity(operations, workload)
    assert evidence["passed"] and evidence["maximum_absolute_error"] <= 1e-12


def test_BenchmarkRefusesInsufficientSamplingAndInvalidShapes():
    """Fail closed before collecting timing evidence with invalid configuration."""

    with pytest.raises(ValueError, match="seven"):
        BuildReport(((1,),), repeats=6)

    with pytest.raises(ValueError, match="positive"):
        BuildReport(((0,),))

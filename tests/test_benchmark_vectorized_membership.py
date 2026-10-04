# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Deterministic workload and fail-closed benchmark evidence checks."""

import os
from types import SimpleNamespace

import pytest

from experiments.benchmark_vectorized_membership import (
    BACKENDS,
    MODES,
    WORKLOADS,
    BuildCoordinates,
    BuildOperation,
    BuildReport,
    CheckParity,
    GetRssBytes,
    MemoryWorker,
    Summarize,
    ValidateConfiguration,
)

np = pytest.importorskip("numpy", reason="array benchmark is an isolated optional experiment")


@pytest.mark.parametrize("workload", WORKLOADS)
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", (1, 16, 257))
def test_AllBenchmarkWorkloadsRetainScalarParity(workload, mode, size):
    """Check whole arrays and scale decisions without testing speed thresholds."""

    operations = {backend: BuildOperation(workload, backend, mode, size)[0] for backend in BACKENDS}
    result = CheckParity(operations["scalar"], operations["numpy"],
                         workload == "default_scale_classification")
    assert result["passed"], "A workload must have scalar parity before it contributes timing evidence."


@pytest.mark.parametrize("mode", MODES)
def test_ClassificationPreservesLaterLevelTieRule(monkeypatch, mode):
    """Make every scale level identical and use the actual scalar selector oracle."""

    import fuzzyroutines.FuzzyRoutines as legacy

    scale = legacy.FuzzyScale()

    for level in scale.levels:
        level["fSet"].mFunction = legacy.MFunction("triangle", a=0.0, b=1.0, c=0.5)

    def IdenticalLevelScale():
        """Return the deliberately tied scale while retaining its real selector."""

        return scale

    monkeypatch.setattr(legacy, "FuzzyScale", IdenticalLevelScale)
    scalar = BuildOperation("default_scale_classification", "scalar", mode, 17)[0]
    vector = BuildOperation("default_scale_classification", "numpy", mode, 17)[0]
    result = vector()
    assert np.all(result == 2), "All ties must select the final configured scale level."
    assert CheckParity(scalar, vector, True)["passed"], "Batch tie handling must match FuzzyScale.Fuzzy."


def test_ParityFailureRejectsInaccurateTimingCandidates():
    """Disagreement is an error rather than a successful performance record."""

    def Scalar():
        """Return the declared scalar oracle."""

        return [0.5]

    def IncorrectArray():
        """Return an intentionally incompatible candidate."""

        return [0.6]

    with pytest.raises(RuntimeError, match="parity failed"):
        CheckParity(Scalar, IncorrectArray)


@pytest.mark.parametrize(("sizes", "repeats", "warmups", "target"), (
    ((), 7, 1, 1), ((0,), 7, 1, 1), ((True,), 7, 1, 1),
    ((1,), 6, 1, 1), ((1,), 7, 0, 1), ((1,), 7, 1, 0),
))
def test_ConfigurationRejectsNonReproducibleSampling(sizes, repeats, warmups, target):
    """Prevent empty inputs or insufficient sampling from appearing as evidence."""

    with pytest.raises(ValueError):
        ValidateConfiguration(sizes, repeats, warmups, target)


def test_GridAndStatisticsAreDeterministic():
    """Retain exact inputs, raw samples, and inclusive quartile definitions."""

    assert BuildCoordinates(3) == [-5.0, 0.0, 5.0], "The input generator must remain reproducible."
    assert BuildCoordinates(3, True) == [0.0, 0.5, 1.0], "Scale classification must cover its domain."
    samples = list(range(7))
    summary = Summarize(samples)
    assert summary["median"] == 3 and summary["interquartile_range"] == 3, "Summary statistics changed."
    assert summary["raw_samples"] == samples, "Summary must preserve the actual measurements."


def test_FullReportRejectsUnsupportedPlatformBeforeMeasurement(monkeypatch):
    """Keep workload imports portable and reject unsupported resource reporting."""

    import experiments.benchmark_vectorized_membership as benchmark

    monkeypatch.setattr(benchmark, "os", SimpleNamespace(name="nt"))

    with pytest.raises(RuntimeError, match="require POSIX"):
        BuildReport(sizes=(1,), memory=False)


def test_LinuxRssUsesCurrentAddressSpacePeak(monkeypatch):
    """Exclude resource high water inherited from the launcher before exec."""

    import experiments.benchmark_vectorized_membership as benchmark

    def ReadStatus(path):
        """Supply a deterministic Linux process-status fixture."""

        assert str(path) == "/proc/self/status", "RSS must inspect its own current address space."

        return "Name: python\nVmHWM:\t1234 kB\nVmRSS:\t1000 kB\n"

    monkeypatch.setattr(benchmark.sys, "platform", "linux")
    monkeypatch.setattr(benchmark.Path, "read_text", ReadStatus)
    assert GetRssBytes() == 1234 * 1024, "Linux memory evidence must use VmHWM, not inherited ru_maxrss."


@pytest.mark.skipif(os.name != "posix", reason="resource RSS measurement requires POSIX")
def test_MemoryMetricsDistinguishPayloadFromTracingAndRss():
    """Inspect schema and array payload sizes without resource-dependent thresholds."""

    result = MemoryWorker("triangle", "numpy", "evaluation", 16)
    assert result["array_output_payload_bytes"] == 16 * 8, "Output payload must reflect float64 shape."
    assert result["prepared_array_payload_bytes"] == 16 * 8, "Prepared input payload must be explicit."
    assert result["rss_high_water_after_bytes"] >= result["rss_high_water_before_bytes"], (
        "RSS high water must be monotonic within one worker."
    )
    assert result["traced_operation_peak_bytes"] >= 0, "Tracing must produce a valid separate byte count."

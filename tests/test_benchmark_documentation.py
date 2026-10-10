# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Contracts for the published benchmark-evidence inventory."""

from pathlib import Path

from tools.benchmark_fuzzyset_centroid import SHAPES
from tools.benchmark_membership_operators import BuildWorkloads
from tools.benchmark_scale_lookup import SCALES

PROJECTROOT = Path(__file__).parents[1]
BENCHMARKDOCUMENT = PROJECTROOT / "docs" / "BENCHMARKS.md"


def test_PublishedEvidenceCoversEveryCurrentBenchmarkWorkload():
    """Keep the human-readable evidence inventory aligned with benchmark tools."""

    document = BENCHMARKDOCUMENT.read_text(encoding="utf-8")

    for workload in BuildWorkloads():
        assert f"`{workload['name']}`" in document, (
            f"docs/BENCHMARKS.md does not cover benchmark workload {workload['name']}."
        )

    for shapeName in SHAPES:
        assert f"`{shapeName}`" in document, (
            f"docs/BENCHMARKS.md does not cover centroid shape {shapeName}."
        )

    for scaleName in SCALES:
        assert f"`{scaleName}`" in document, (
            f"docs/BENCHMARKS.md does not cover scale workload {scaleName}."
        )


def test_ReadmeLinksPublishedBenchmarkEvidence():
    """Keep the benchmark report discoverable from the repository entry point."""

    readme = (PROJECTROOT / "README.md").read_text(encoding="utf-8")

    assert "[Results](docs/BENCHMARKS.md)" in readme

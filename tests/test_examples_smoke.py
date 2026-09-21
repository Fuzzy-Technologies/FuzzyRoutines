# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""End-to-end smoke coverage for the bundled compatibility example."""

import subprocess
import sys
from pathlib import Path

PROJECTROOT = Path(__file__).resolve().parents[1]


def test_BundledExamplesRunEndToEnd():
    """Execute the user-facing example through Python's module boundary."""

    result = subprocess.run(
        [sys.executable, '-m', 'fuzzyroutines.Examples'],
        cwd=PROJECTROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, (
        'The bundled example must stay executable after public-contract changes.\n'
        f'stdout:\n{result.stdout}\n'
        f'stderr:\n{result.stderr}'
    )
    assert 'FNOT(0.25, alpha=0.9)' in result.stdout
    assert 'Converting some strings to range of sorted unique numbers:' in result.stdout

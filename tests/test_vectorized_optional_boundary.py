# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Dependency-isolation evidence that runs even when NumPy is not installed."""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_ScalarAndExperimentImportsWorkWithoutNumpy():
    """Block NumPy imports in a fresh process and exercise the optional failure path."""

    source = '''
import importlib.abc
import sys

class BlockNumpy(importlib.abc.MetaPathFinder):
    """Simulate an installation without the optional array dependency."""

    def find_spec(self, fullname, path=None, target=None):
        """Reject NumPy while delegating every other import to ordinary finders."""

        if fullname == "numpy" or fullname.startswith("numpy."):
            raise ModuleNotFoundError("NumPy intentionally unavailable", name="numpy")

        return None

sys.meta_path.insert(0, BlockNumpy())
import fuzzyroutines
from fuzzyroutines.FuzzyRoutines import MFunction
from experiments.vectorized_membership import EvaluateMembership
assert "numpy" not in sys.modules, "Imports must not load optional NumPy."
assert MFunction("gaussian", a=0.0, b=1.0).mju(0.0) == 1.0

try:
    EvaluateMembership("gaussian", [0.0], a=0.0, b=1.0)

except ImportError as error:
    assert "requirements-vectorized.txt" in str(error)

else:
    raise AssertionError("Array evaluation must identify the missing optional dependency.")
assert "numpy" not in sys.modules, "Failure must not retain a partial optional dependency."
'''
    completed = subprocess.run(
        [sys.executable, "-c", source], cwd=PROJECT_ROOT,
        capture_output=True, text=True, check=False,
    )
    assert completed.returncode == 0, (
        "Scalar/experiment dependency isolation failed: " + completed.stdout + completed.stderr
    )

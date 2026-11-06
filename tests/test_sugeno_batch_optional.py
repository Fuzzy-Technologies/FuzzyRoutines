# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Import and explicit dependency behavior with NumPy unavailable."""

import subprocess
import sys


def test_PublicSugenoModuleImportsWithoutNumpyAndEmptyCallsStillRequireIt():
    """Check a fresh interpreter so a cached optional module cannot mask the boundary."""

    script = """
import sys
from fuzzyroutines.sugeno_batches import EvaluateSugenoBatch

assert "numpy" not in sys.modules
sys.modules["numpy"] = None
try:
    EvaluateSugenoBatch(object(), [], featureNames=())
except ImportError as error:
    assert "fuzzyroutines[numpy]" in str(error)
else:
    raise AssertionError("An explicit empty batch call must require the NumPy extra")
"""
    process = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=False)

    assert process.returncode == 0, process.stdout + process.stderr

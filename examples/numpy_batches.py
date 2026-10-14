# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Run explicit optional batches against the installed public package."""

import json

from fuzzyroutines import CreateUniversalFuzzyScale, Triangle, UniversalFuzzyScalePolicy
from fuzzyroutines.batches import EvaluateMembershipBatch, FuzzifyBatch


def Main() -> None:
    """Check elementary membership values and report historical scale decisions."""

    grades = EvaluateMembershipBatch(Triangle(0.0, 0.5, 1.0), [0.0, 0.25, 0.5, 0.75, 1.0], backend="numpy")
    assert grades.tolist() == [0.0, 0.5, 1.0, 0.5, 0.0], "Triangle batch must preserve straight-line values."
    result = FuzzifyBatch(CreateUniversalFuzzyScale(), [0.0, 0.3, 0.5, 0.7, 1.0], UniversalFuzzyScalePolicy(), backend="numpy")
    names = [
        [name for name, selected in zip(result.termNames, row, strict=True) if selected]
        for row in result.selected
    ]
    assert names == [["Min"], ["Low"], ["Med"], ["High"], ["Max"]], "Preset batches must preserve historical order."
    print(json.dumps({"backend": "numpy", "triangle": grades.tolist(), "selected": names, "shape": list(result.memberships.shape)}))


if __name__ == "__main__":
    Main()

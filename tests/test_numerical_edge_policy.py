# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Expected-failure evidence for unresolved numerical edge policy."""

import pytest

from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction


@pytest.mark.xfail(strict=True, reason="Task #80 will turn an undefined zero-area centroid into an explicit error.")
def test_ZeroAreaCentroidRaisesValueError():
    membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)

    with pytest.raises(ValueError):
        FuzzySet(membershipFunction, supportSet=(2.0, 3.0))


def test_DegenerateParabolicWidthRaisesValueError():
    with pytest.raises(ValueError):
        MFunction("parabolic", a=0.5, b=0.5)

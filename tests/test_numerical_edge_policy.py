# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Regression evidence for explicit numerical edge behavior."""

import pytest

from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction


def test_ZeroAreaCentroidRaisesValueError():
    membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)

    with pytest.raises(ValueError, match="zero membership area"):
        FuzzySet(membershipFunction, supportSet=(2.0, 3.0)).Defuz()


def test_DegenerateParabolicWidthRaisesValueError():
    with pytest.raises(ValueError):
        MFunction("parabolic", a=0.5, b=0.5)

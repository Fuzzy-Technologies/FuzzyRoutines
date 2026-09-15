import pytest

from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction


@pytest.mark.xfail(strict=True, reason="Task #66 will turn an undefined zero-area centroid into an explicit error.")
def test_ZeroAreaCentroidRaisesValueError():
    membershipFunction = MFunction("exponential", a=0.5, b=0.0)

    with pytest.raises(ValueError):
        FuzzySet(membershipFunction, supportSet=(0.0, 1.0))


@pytest.mark.xfail(strict=True, reason="Task #63 will reject degenerate membership widths at construction.")
def test_DegenerateParabolicWidthRaisesValueError():
    with pytest.raises(ValueError):
        MFunction("parabolic", a=0.5, b=0.5)

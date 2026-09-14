import pytest

from fuzzyroutines.FuzzyRoutines import FuzzyNOT, FuzzyNOTParabolic


@pytest.mark.parametrize("fuzzyNumber", [0.0, 0.125, 0.25, 0.5, 0.875, 1.0])
def test_FuzzyNOTStandardNegationInvolution(fuzzyNumber):
    assert FuzzyNOT(FuzzyNOT(fuzzyNumber)) == pytest.approx(fuzzyNumber)


@pytest.mark.parametrize("fuzzyNumber", [0.0, 1.0])
def test_FuzzyNOTStandardNegationSwapsEndpoints(fuzzyNumber):
    assert FuzzyNOT(fuzzyNumber) == 1.0 - fuzzyNumber


def test_FuzzyNOTStandardNegationFixedPoint():
    assert FuzzyNOT(0.5) == pytest.approx(0.5)


@pytest.mark.parametrize("fuzzyNumber", [0.0, 1.0])
def test_FuzzyNOTParabolicSwapsEndpoints(fuzzyNumber):
    assert FuzzyNOTParabolic(fuzzyNumber, alpha=0.5) == 1.0 - fuzzyNumber


@pytest.mark.xfail(strict=True, reason="Task #57 will replace the historical epsilon scan with the documented closed form.")
@pytest.mark.parametrize("fuzzyNumber", [0.125, 0.25, 0.5, 0.75, 0.875])
def test_FuzzyNOTParabolicHasDocumentedInvolution(fuzzyNumber):
    value = FuzzyNOTParabolic(fuzzyNumber, alpha=0.5)
    assert FuzzyNOTParabolic(value, alpha=0.5) == pytest.approx(fuzzyNumber, abs=1e-12)


@pytest.mark.xfail(strict=True, reason="Task #55 will make invalid negation parameters explicit errors.")
@pytest.mark.parametrize("alpha", [0.0, 1.0, -0.25, 1.25])
def test_FuzzyNOTRejectsInvalidAlpha(alpha):
    with pytest.raises(ValueError):
        FuzzyNOT(0.5, alpha=alpha)


@pytest.mark.xfail(strict=True, reason="Task #57 will enforce the proved parabolic alpha interval [1/4, 3/4].")
@pytest.mark.parametrize("alpha", [0.0, 0.2, 0.8, 1.0])
def test_FuzzyNOTParabolicRejectsAlphaOutsideProvedInterval(alpha):
    with pytest.raises(ValueError):
        FuzzyNOTParabolic(0.5, alpha=alpha)

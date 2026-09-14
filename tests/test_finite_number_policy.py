import math

import pytest

from fuzzyroutines.FuzzyRoutines import FuzzyAND, FuzzyNOT, FuzzyOR, SCoNorm, TNorm


@pytest.mark.parametrize("invalidValue", [True, False, math.nan, math.inf, -math.inf])
def test_FuzzyDegreeHelpersRejectNonFiniteAndBooleanValues(invalidValue):
    assert FuzzyNOT(invalidValue) is None
    assert TNorm(invalidValue, 0.5) is None
    assert SCoNorm(0.5, invalidValue) is None


@pytest.mark.xfail(strict=True, reason="Task #63 will replace silent sentinels with the explicit public finite-scalar contract.")
@pytest.mark.parametrize("operator", [FuzzyNOT, FuzzyAND, FuzzyOR, TNorm, SCoNorm])
@pytest.mark.parametrize("invalidValue", [True, False, math.nan, math.inf, -math.inf])
def test_PublicOperatorsRaiseValueErrorForInvalidScalar(operator, invalidValue):
    with pytest.raises(ValueError):
        if operator is FuzzyNOT:
            operator(invalidValue)

        else:
            operator(invalidValue, 0.5)

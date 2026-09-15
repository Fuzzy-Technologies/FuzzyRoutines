"""Regression tests for legacy membership-parameter conventions.

These checks protect historical argument meaning without declaring mathematically
invalid parameter combinations to be compatibility requirements.
"""

import pytest

from fuzzyroutines.FuzzyRoutines import MFunction


def test_TriangleKeepsItsHistoricalABCPParameterMeaning():
    membershipFunction = MFunction("triangle", a=0.1, b=0.9, c=0.4)

    assert membershipFunction.mju(0.1) == 0.0, "Legacy triangle parameter a is the left foot."
    assert membershipFunction.mju(0.4) == 1.0, "Legacy triangle parameter c is the apex."
    assert membershipFunction.mju(0.9) == 0.0, "Legacy triangle parameter b is the right foot."


def test_TrapeziumKeepsItsHistoricalABCDParameterMeaning():
    membershipFunction = MFunction("trapezium", a=0.1, b=0.9, c=0.3, d=0.7)

    assert membershipFunction.mju(0.1) == 0.0, "Legacy trapezium parameter a is the left foot."
    assert membershipFunction.mju(0.3) == 1.0, "Legacy trapezium parameter c starts the plateau."
    assert membershipFunction.mju(0.7) == 1.0, "Legacy trapezium parameter d ends the plateau."
    assert membershipFunction.mju(0.9) == 0.0, "Legacy trapezium parameter b is the right foot."


def test_BellDerivesItsHistoricalRightFootFromABC():
    membershipFunction = MFunction("bell", a=0.1, b=0.3, c=0.6)

    assert membershipFunction.mju(0.3) == 1.0, "Legacy bell parameter b starts the plateau."
    assert membershipFunction.mju(0.6) == 1.0, "Legacy bell parameter c ends the plateau."
    assert membershipFunction.mju(0.8) == 0.0, (
        "The legacy bell right foot must remain c + b - a."
    )


def test_ExponentialKeepsItsHistoricalCentreAndScaleKeywords():
    membershipFunction = MFunction("exponential", a=0.5, b=0.25)

    assert membershipFunction.mju(0.5) == 1.0, "Legacy exponential parameter a is the centre."
    assert membershipFunction.mju(0.25) == pytest.approx(
        membershipFunction.mju(0.75),
        abs=1e-12,
        rel=0.0,
    ), "Legacy exponential parameter b defines symmetric scale."

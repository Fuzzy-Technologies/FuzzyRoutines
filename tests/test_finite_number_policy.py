# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Finite-number validation contracts for fuzzy operators."""

import math

import pytest

from fuzzyroutines.FuzzyRoutines import (
    FuzzyAND,
    FuzzyNOT,
    FuzzyNOTParabolic,
    FuzzyOR,
    MFunction,
    SCoNorm,
    SCoNormCompose,
    TNorm,
    TNormCompose,
)


@pytest.mark.parametrize("operator", [FuzzyNOT, FuzzyAND, FuzzyOR, TNorm, SCoNorm])
@pytest.mark.parametrize("invalidValue", [True, False, math.nan, math.inf, -math.inf, -0.1, 1.1, "0.5", None])
def test_PublicOperatorsRaiseValueErrorForInvalidScalar(operator, invalidValue):
    with pytest.raises(ValueError, match="finite real number|closed interval"):
        if operator is FuzzyNOT:
            operator(invalidValue)

        else:
            operator(invalidValue, 0.5)


@pytest.mark.parametrize("operator", [TNorm, SCoNorm])
def test_BinaryOperatorRejectsUnknownFamily(operator):
    with pytest.raises(ValueError, match="unknown .*norm family"):
        operator(0.25, 0.75, normType="unknown")


@pytest.mark.parametrize("composition", [TNormCompose, SCoNormCompose])
def test_CompositionRejectsEmptyInputExplicitly(composition):
    with pytest.raises(ValueError, match="requires at least one fuzzy degree"):
        composition()


def test_ParabolicNegationRejectsInvalidFuzzyDegreeExplicitly():
    with pytest.raises(ValueError, match="closed interval"):
        FuzzyNOTParabolic(1.1)


@pytest.mark.parametrize(
    "membershipFunction",
    [
        MFunction("hyperbolic", a=2.0, b=2.0, c=0.0),
        MFunction("bell", a=0.0, b=0.25, c=0.5),
        MFunction("parabolic", a=0.0, b=1.0),
        MFunction("triangle", a=0.0, b=1.0, c=0.5),
        MFunction("trapezium", a=0.0, b=1.0, c=0.25, d=0.75),
        MFunction("exponential", a=0.5, b=0.25),
        MFunction("sigmoidal", a=2.0, b=0.5),
        MFunction("desirability"),
    ],
)
@pytest.mark.parametrize("invalidValue", [True, False, math.nan, math.inf, -math.inf, "0.5", None])
def test_MembershipEvaluatorRejectsInvalidCoordinate(membershipFunction, invalidValue):
    with pytest.raises(ValueError, match="finite real number"):
        membershipFunction.mju(invalidValue)


def test_InternalParameterCorruptionIsNotSwallowedAsZero():
    membershipFunction = MFunction("exponential", a=0.5, b=0.25)
    membershipFunction.parameters["b"] = 0.0

    with pytest.raises(ZeroDivisionError):
        membershipFunction.mju(0.5)


def test_StableMembershipFormulasHandleExtremeFiniteCoordinates():
    gaussianFunction = MFunction("exponential", a=0.0, b=1.0)
    logisticFunction = MFunction("sigmoidal", a=1.0, b=0.0)
    desirabilityFunction = MFunction("desirability")

    assert gaussianFunction.mju(float.fromhex("0x1.fffffffffffffp+1023")) == 0.0
    assert logisticFunction.mju(float.fromhex("0x1.fffffffffffffp+1023")) == 1.0
    assert logisticFunction.mju(-float.fromhex("0x1.fffffffffffffp+1023")) == 0.0
    assert desirabilityFunction.mju(-float.fromhex("0x1.fffffffffffffp+1023")) == 0.0
    assert desirabilityFunction.mju(float.fromhex("0x1.fffffffffffffp+1023")) == 1.0

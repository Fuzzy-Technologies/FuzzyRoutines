# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Optional CPU graph parity, independent references and gradient evidence."""

import math
from itertools import product

import pytest

torch = pytest.importorskip("torch")

from fuzzyroutines.exceptions import UndefinedResultError
from research.differentiable_sugeno import (
    MAX_WIDTH,
    MIN_GAP,
    MIN_WIDTH,
    DifferentiableSugeno,
    EvaluateSugeno,
    MembershipParameters,
)


@pytest.fixture(autouse=True)
def DeterministicThreads():
    """Bound tiny tensor tests to one thread while restoring caller settings."""

    originalThreads = torch.get_num_threads()
    torch.set_num_threads(1)

    yield

    torch.set_num_threads(originalThreads)


@pytest.mark.parametrize("order", (0, 1))
def test_FrozenForwardMatchesScalarEngineAndIndependentFormula(order):
    """Check endpoints and a grid against the scalar engine and direct Gaussians."""

    model = DifferentiableSugeno(order)

    if order:
        with torch.no_grad():
            model.consequences[:, 1:] = torch.tensor(((0.1, -0.2), (0.2, 0.05), (-0.1, 0.3), (0.4, -0.1)), dtype=torch.float64)

    coordinates = tuple(product((0.0, 0.1, 0.25, 0.5, 0.75, 1.0), repeat=2))
    predictions = model.Evaluate(torch.tensor(coordinates, dtype=torch.float64)).tolist()
    scalar = model.ScalarReference()
    centers = (0.25, 0.75)
    coefficients = model.consequences.tolist()

    for coordinatesPair, prediction in zip(coordinates, predictions, strict=True):
        strengths = tuple(math.exp(-0.5 * (((coordinatesPair[0] - first) / 0.25)**2 + ((coordinatesPair[1] - second) / 0.25)**2)) for first, second in product(centers, repeat=2))
        consequences = tuple(values[0] + (values[1] * coordinatesPair[0] + values[2] * coordinatesPair[1] if order else 0) for values in coefficients)
        expected = math.fsum(weight * value for weight, value in zip(strengths, consequences, strict=True)) / math.fsum(strengths)
        assert prediction == pytest.approx(expected, rel=0, abs=1e-12), "Torch forward must match the independent product-Gaussian weighted average"
        assert prediction == pytest.approx(scalar.Evaluate(dict(zip(("input0", "input1"), coordinatesPair, strict=True))).value, rel=0, abs=1e-12), "Frozen forward must retain the scalar Sugeno contract within float64 tolerance"


@pytest.mark.parametrize("order", (0, 1))
def test_FullGraphPassesNumericalJacobianCheck(order):
    """Compare all input, membership and consequence gradients to finite differences."""

    model = DifferentiableSugeno(order)
    inputs = torch.tensor(((0.13, 0.27), (0.61, 0.84)), dtype=torch.float64, requires_grad=True)

    def Forward(inputs, gaps, widths, consequences):
        """Expose every trainable graph input while holding rule weights fixed."""

        return EvaluateSugeno(inputs, gaps, widths, consequences, model.ruleWeights)

    assert torch.autograd.gradcheck(Forward, (inputs, model.rawGaps, model.rawWidths, model.consequences), eps=1e-6, atol=1e-7, rtol=1e-5), "Autograd Jacobian must match central finite differences away from domain boundaries"
    model.Evaluate(inputs).square().sum().backward()
    assert all(value.grad is not None and bool(torch.isfinite(value.grad).all()) and bool((value.grad != 0).any()) for value in (inputs,) + model.Parameters()), "Every enabled parameter family must receive finite nonzero gradients"


def test_MembershipConstraintsSurviveExtremeFiniteParameters():
    """Keep smooth centers ordered and Gaussian widths positive after extreme updates."""

    rawGaps = torch.tensor(((1000, -1000, 0), (-1000, 1000, 0)), dtype=torch.float64)
    rawWidths = torch.tensor(((-1000, 1000), (1000, -1000)), dtype=torch.float64)
    centers, widths = MembershipParameters(rawGaps, rawWidths)
    assert bool((centers[:, 0] >= MIN_GAP).all()) and bool((centers[:, 1] <= 1 - MIN_GAP).all()), "Centers must stay inside the unit interval"
    assert bool((centers[:, 1] - centers[:, 0] >= MIN_GAP - 1e-15).all()), "Minimum term separation must survive saturated softmax rounding"
    assert bool(((widths >= MIN_WIDTH) & (widths <= MAX_WIDTH)).all()), "Widths must preserve their explicit finite positive bounds"
    output = EvaluateSugeno(torch.tensor(((0, 1), (1, 0)), dtype=torch.float64), rawGaps, rawWidths, torch.ones((4, 1), dtype=torch.float64), torch.ones(4, dtype=torch.float64))
    assert output.tolist() == pytest.approx([1, 1], rel=0, abs=1e-15), "Bounded log-space firing must remain usable at domain corners"


def test_NoFireDisabledRulesAndUnderflowPolicy():
    """Fail all-zero weights, honor disabled rules and retain tiny positive weights."""

    model = DifferentiableSugeno(0)
    inputs = torch.tensor(((0.13, 0.81), (1.0, 0.0)), dtype=torch.float64)
    reference = model.Evaluate(inputs).tolist()
    model.ruleWeights.fill_(float.fromhex("0x0.0000000000001p-1022"))
    assert model.Evaluate(inputs).tolist() == pytest.approx(reference, rel=0, abs=1e-12), "Common subnormal weights must not create false no-fire in the log-space graph"
    model.ruleWeights.zero_()

    with pytest.raises(UndefinedResultError, match="every rule weight is zero"):
        model.Evaluate(inputs)

    model.ruleWeights[2] = 1
    assert model.Evaluate(inputs).tolist() == [0.6, 0.6], "Only the explicitly enabled constant rule may contribute"
    model.Evaluate(inputs).sum().backward()
    assert all(bool(torch.isfinite(value.grad).all()) for value in model.Parameters()), "Disabled fixed rules must not introduce non-finite parameter gradients"


@pytest.mark.parametrize("invalid", (torch.tensor(((0.2, 0.5),), dtype=torch.float32), torch.tensor(((0.2, 0.5),), device="meta", dtype=torch.float64)))
def test_RejectUnsupportedDtypeAndDevice(invalid):
    """Reject unsupported tensor representations before arithmetic or device access."""

    with pytest.raises(TypeError, match="CPU float64"):
        DifferentiableSugeno().Evaluate(invalid)


@pytest.mark.parametrize("values", (((-0.01, 0.4),), ((0.1, 1.01),), ((math.nan, 0.2),), ((math.inf, 0.2),), ((0.2, 0.3, 0.4),)))
def test_RejectInvalidInputCoordinatesAndShape(values):
    """Reject non-finite, out-of-domain and incorrectly shaped samples."""

    with pytest.raises(ValueError):
        DifferentiableSugeno().Evaluate(torch.tensor(values, dtype=torch.float64))


def test_RejectNonfiniteParametersTrainableWeightsAndOverflow():
    """Report malformed parameters and arithmetic failure without a plausible result."""

    model = DifferentiableSugeno()
    inputs = torch.tensor(((1, 1),), dtype=torch.float64)
    model.ruleWeights.requires_grad_(True)

    with pytest.raises(ValueError, match="fixed"):
        model.Evaluate(inputs)

    model.ruleWeights.requires_grad_(False)

    with torch.no_grad():
        model.rawWidths[0, 0] = math.nan

    with pytest.raises(ValueError, match="finite"):
        model.Evaluate(inputs)

    with torch.no_grad():
        model.rawWidths.zero_()
        model.consequences.fill_(float.fromhex("0x1.fffffffffffffp+1023"))

    with pytest.raises(ValueError, match="non-finite result"):
        model.Evaluate(inputs)


def test_InitializationAndFrozenGraphAreReproducible():
    """Retain global RNG state, deterministic values and explicit frozen parameters."""

    before = torch.random.get_rng_state().clone()
    first = DifferentiableSugeno(0, trainMembership=False, trainConsequences=False)
    second = DifferentiableSugeno(0, trainMembership=False, trainConsequences=False)
    assert torch.equal(before, torch.random.get_rng_state()), "Prototype initialization must not consume caller RNG state"
    assert first.Parameters() == (), "Frozen rule model must expose no trainable parameters"
    inputs = torch.tensor(((0.31, 0.71),), dtype=torch.float64)
    assert torch.equal(first.Evaluate(inputs), second.Evaluate(inputs)), "Identical initialization must give bit-identical frozen predictions"
    assert not first.Evaluate(inputs).requires_grad, "A completely frozen graph must retain no unnecessary gradient state"

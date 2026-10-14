# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Repository-only differentiable two-input Sugeno feasibility prototype.

This optional research module is not shipped in the fuzzyroutines wheel. All
forward calculations stay in Torch on CPU float64. Its smooth Gaussian terms
are independent from the historical Universal Fuzzy Scale.
"""

import math
from itertools import product

import torch
from torch import Tensor

from fuzzyroutines import (
    ContinuousUniverse,
    Gaussian,
    LinguisticTerm,
    NegationPolicy,
    ScalarFuzzySet,
    SNormPolicy,
    TNormPolicy,
)
from fuzzyroutines.exceptions import UndefinedResultError
from fuzzyroutines.inference import (
    AffineConsequent,
    AllOf,
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    SugenoModel,
    SugenoRule,
    TermCondition,
)

MIN_GAP = 0.02
MIN_WIDTH = 0.05
MAX_WIDTH = 0.8
RULE_TERMS = tuple(product(range(2), repeat=2))


def RequireTensor(value: Tensor, name: str, shape: tuple[int, ...]) -> None:
    """Validate the bounded CPU float64 tensor contract without replacing values."""

    if not isinstance(value, Tensor):
        raise TypeError(f"{name} must be a Torch tensor")

    if value.dtype != torch.float64 or value.device.type != "cpu":
        raise TypeError(f"{name} must use CPU float64")

    if tuple(value.shape) != shape:
        raise ValueError(f"{name} must have shape {shape}")

    if not bool(torch.isfinite(value).all()):
        raise ValueError(f"{name} must contain only finite values")


def MembershipParameters(rawGaps: Tensor, rawWidths: Tensor) -> tuple[Tensor, Tensor]:
    """Constrain centers by positive gaps and widths by a bounded sigmoid."""

    gaps = MIN_GAP + (1 - 3 * MIN_GAP) * torch.softmax(rawGaps, dim=1)
    centers = torch.cumsum(gaps, dim=1)[:, :2]
    widths = MIN_WIDTH + (MAX_WIDTH - MIN_WIDTH) * torch.sigmoid(rawWidths)

    return centers, widths


def EvaluateSugeno(
    inputs: Tensor,
    rawGaps: Tensor,
    rawWidths: Tensor,
    consequences: Tensor,
    ruleWeights: Tensor,
) -> Tensor:
    """Evaluate a complete smooth rule graph with constant or affine conclusions.

    Args:
        inputs: CPU float64 matrix `(samples, 2)` with coordinates in `[0,1]`.
        rawGaps: Finite matrix `(2,3)` controlling ordered membership centers.
        rawWidths: Finite matrix `(2,2)` controlling positive Gaussian widths.
        consequences: Finite matrix `(4,1)` for constants or `(4,3)` for affine rules.
        ruleWeights: Fixed nonnegative degree vector `(4,)`; at least one is positive.

    Returns:
        CPU float64 prediction vector retaining all enabled gradient paths.

    Raises:
        TypeError: A tensor uses an unsupported type, dtype or device.
        ValueError: Shape, finiteness or domain validation fails.
        UndefinedResultError: Every rule weight is zero.
    """

    if not isinstance(inputs, Tensor) or inputs.ndim != 2:
        raise TypeError("inputs must be a rank-two Torch tensor")

    RequireTensor(inputs, "inputs", (inputs.shape[0], 2))
    RequireTensor(rawGaps, "rawGaps", (2, 3))
    RequireTensor(rawWidths, "rawWidths", (2, 2))
    RequireTensor(ruleWeights, "ruleWeights", (4,))

    if ruleWeights.requires_grad:
        raise ValueError("rule weights are fixed in this bounded prototype")

    if not isinstance(consequences, Tensor) or consequences.ndim != 2 or consequences.shape[1] not in (1, 3):
        raise ValueError("consequences must have shape (4,1) or (4,3)")

    RequireTensor(consequences, "consequences", (4, consequences.shape[1]))

    if not bool(((inputs >= 0) & (inputs <= 1)).all()):
        raise ValueError("inputs must lie in the closed unit square")

    if not bool(((ruleWeights >= 0) & (ruleWeights <= 1)).all()):
        raise ValueError("rule weights must lie in [0,1]")

    if not bool((ruleWeights > 0).any()):
        raise UndefinedResultError("no Sugeno rule fires: every rule weight is zero")

    centers, widths = MembershipParameters(rawGaps, rawWidths)
    logGrades = -0.5 * ((inputs[:, :, None] - centers) / widths).square()
    logStrengths = (logGrades[:, 0, :, None] + logGrades[:, 1, None, :]).reshape(-1, 4)
    logStrengths = logStrengths + torch.log(ruleWeights)
    normalized = torch.softmax(logStrengths, dim=1)

    if consequences.shape[1] == 1:
        ruleValues = consequences[:, 0].expand(inputs.shape[0], 4)

    else:
        ruleValues = inputs @ consequences[:, 1:].T + consequences[:, 0]

    result = torch.sum(normalized * ruleValues, dim=1)

    if not bool(torch.isfinite(ruleValues).all()) or not bool(torch.isfinite(result).all()):
        raise ValueError("consequence arithmetic produced a non-finite result")

    return result


class DifferentiableSugeno:
    """Small trainable parameter holder with no public-backend compatibility promise."""

    def __init__(self, order: int = 1, trainMembership: bool = True, trainConsequences: bool = True) -> None:
        """Initialize four reproducible rules without changing Torch's global RNG."""

        if isinstance(order, bool) or order not in (0, 1):
            raise ValueError("order must be zero or one")

        if not isinstance(trainMembership, bool) or not isinstance(trainConsequences, bool):
            raise TypeError("training flags must be boolean")

        gapValues = tuple((value - MIN_GAP) / (1 - 3 * MIN_GAP) for value in (0.25, 0.5, 0.25))
        widthFraction = (0.25 - MIN_WIDTH) / (MAX_WIDTH - MIN_WIDTH)
        widthLogit = math.log(widthFraction / (1 - widthFraction))
        self.rawGaps = torch.nn.Parameter(torch.tensor([gapValues, gapValues], dtype=torch.float64).log(), requires_grad=trainMembership)
        self.rawWidths = torch.nn.Parameter(torch.full((2, 2), widthLogit, dtype=torch.float64), requires_grad=trainMembership)
        consequences = torch.zeros((4, 1 if order == 0 else 3), dtype=torch.float64)
        consequences[:, 0] = torch.tensor((0.15, 0.4, 0.6, 0.85), dtype=torch.float64)
        self.consequences = torch.nn.Parameter(consequences, requires_grad=trainConsequences)
        self.ruleWeights = torch.ones(4, dtype=torch.float64)

    def Evaluate(self, inputs: Tensor) -> Tensor:
        """Evaluate the graph with the current trainable or frozen parameters."""

        return EvaluateSugeno(inputs, self.rawGaps, self.rawWidths, self.consequences, self.ruleWeights)

    def Parameters(self) -> tuple[Tensor, ...]:
        """Return only the parameters explicitly enabled for optimization."""

        return tuple(value for value in (self.rawGaps, self.rawWidths, self.consequences) if value.requires_grad)

    def ScalarReference(self) -> SugenoModel:
        """Snapshot current parameters into the scalar engine for parity evidence.

        This explicit evaluation-only boundary leaves autograd. It is never
        called by Evaluate or the training forward pass.
        """

        centers, widths = MembershipParameters(self.rawGaps, self.rawWidths)
        centerValues = centers.detach().tolist()
        widthValues = widths.detach().tolist()
        consequenceValues = self.consequences.detach().tolist()
        weights = self.ruleWeights.tolist()
        universe = ContinuousUniverse(0, 1, True, True)
        variables = tuple(FuzzyVariable(f"input{axis}", tuple(
            LinguisticTerm(f"term{term}", ScalarFuzzySet(universe, Gaussian(centerValues[axis][term], widthValues[axis][term])))
            for term in range(2)
        )) for axis in range(2))
        rules = []

        for index, terms in enumerate(RULE_TERMS):
            values = consequenceValues[index]
            consequent = ConstantConsequent(values[0]) if len(values) == 1 else AffineConsequent(values[0], (("input0", values[1]), ("input1", values[2])))
            rules.append(SugenoRule(f"rule{index}", AllOf(tuple(TermCondition(f"input{axis}", f"term{term}") for axis, term in enumerate(terms))), consequent, weights[index]))

        policy = InferencePolicy(TNormPolicy("algebraic"), SNormPolicy("logic"), NegationPolicy("standard"))

        return SugenoModel(variables, tuple(rules), policy, ContinuousUniverse())

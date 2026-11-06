# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Private prototype for ordered, independent scalar model composition.

Bindings route exact external IDs to existing scalar models. Evaluation adds
no normalization, callbacks, dependencies, or changes to scalar traces.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
import re
from typing import Literal

from fuzzyroutines.defuzzification import CentroidConvergenceError, CentroidPolicy
from fuzzyroutines.domain import IntegrationDomain
from fuzzyroutines.exceptions import (
    InvalidDomainError,
    InvalidParameterError,
    InvalidParameterTypeError,
    NumericalError,
    UndefinedResultError,
)
from fuzzyroutines.inference import MamdaniModel, MamdaniResult, SugenoModel, SugenoResult
from fuzzyroutines.membership import MembershipScalar
from fuzzyroutines.numeric import _RequireFiniteReal

_MAX_OUTPUTS = 64
_MAX_INPUTS = 256
_MAX_BINDINGS = 4096
_EXTERNAL_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")

type FailurePolicy = Literal["fail-fast", "per-output"]
type FailureCategory = Literal["domain", "undefined", "convergence", "numerical", "parameter"]
type ScalarFailure = InvalidParameterError | InvalidParameterTypeError | NumericalError


def _RequireExternalId(value: object) -> None:
    """Require one exact ASCII ID using the v1 identifier grammar."""

    if not isinstance(value, str) or _EXTERNAL_ID.fullmatch(value) is None:
        raise InvalidParameterError("external IDs require 1–64 ASCII identifier characters")


@dataclass(frozen=True, slots=True)
class OutputBinding:
    """Bind exact scalar inputs and optional centroid settings to one output ID."""

    outputId: str
    model: MamdaniModel | SugenoModel
    inputs: tuple[tuple[str, str], ...]
    integrationDomain: IntegrationDomain | None = None
    centroidPolicy: CentroidPolicy | None = None

    def __post_init__(self) -> None:
        """Reject malformed routes and unsupported scalar model options."""

        _RequireExternalId(self.outputId)

        if type(self.model) not in (MamdaniModel, SugenoModel):
            raise InvalidParameterTypeError("an output binding requires a built-in scalar model")

        if not isinstance(self.inputs, tuple):
            raise InvalidParameterTypeError("input bindings must be a tuple")

        if len(self.inputs) > _MAX_BINDINGS:
            raise InvalidParameterError("composition exceeds the input binding limit")

        for pair in self.inputs:
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise InvalidParameterTypeError("input bindings require pairs of names")

            _RequireExternalId(pair[1])

        if tuple(name for name, _ in self.inputs) != tuple(variable.name for variable in self.model.inputs):
            raise InvalidParameterError("input bindings must match declared scalar names and order")

        if isinstance(self.model, SugenoModel) and (self.integrationDomain is not None or self.centroidPolicy is not None):
            raise InvalidParameterError("Sugeno bindings do not accept centroid options")

        if self.integrationDomain is not None and not isinstance(self.integrationDomain, IntegrationDomain):
            raise InvalidParameterTypeError("integrationDomain must be an IntegrationDomain")

        if self.centroidPolicy is not None:
            if self.integrationDomain is None:
                raise InvalidParameterError("centroidPolicy requires integrationDomain")

            if not isinstance(self.centroidPolicy, CentroidPolicy):
                raise InvalidParameterTypeError("centroidPolicy must be a CentroidPolicy")


@dataclass(frozen=True, slots=True)
class OutputFailure:
    """Carry a stable scalar error category and a diagnostic without a result."""

    category: FailureCategory
    message: str


@dataclass(frozen=True, slots=True)
class OutputRecord:
    """Pair one output ID with its original scalar result or explicit failure."""

    outputId: str
    outcome: MamdaniResult | SugenoResult | OutputFailure


class CompositionEvaluationError(Exception):
    """Identify the failed output while retaining its scalar error as the cause."""

    def __init__(self, outputId: str) -> None:
        """Identify the first output that failed under the fail-fast policy."""

        super().__init__(f"composition output {outputId!r} failed")
        self.outputId = outputId


def _FailureCategory(error: ScalarFailure) -> FailureCategory:
    """Classify scalar failures before their broader exception categories."""

    if isinstance(error, InvalidDomainError):
        return "domain"

    if isinstance(error, UndefinedResultError):
        return "undefined"

    if isinstance(error, CentroidConvergenceError):
        return "convergence"

    if isinstance(error, NumericalError):
        return "numerical"

    return "parameter"


@dataclass(frozen=True, slots=True)
class ModelComposition:
    """Evaluate ordered scalar bindings with exact external input IDs."""

    outputs: tuple[OutputBinding, ...]
    failurePolicy: FailurePolicy
    inputIds: tuple[str, ...] = field(init=False)

    def __post_init__(self) -> None:
        """Check composition bounds and record required IDs in declaration order."""

        if self.failurePolicy not in ("fail-fast", "per-output"):
            raise InvalidParameterError("composition requires an explicit failure policy")

        if not isinstance(self.outputs, tuple):
            raise InvalidParameterTypeError("composition outputs must be a tuple")

        if not 1 <= len(self.outputs) <= _MAX_OUTPUTS:
            raise InvalidParameterError("composition requires 1–64 output bindings")

        if any(type(output) is not OutputBinding for output in self.outputs):
            raise InvalidParameterTypeError("composition outputs require exact OutputBinding records")

        if len({output.outputId for output in self.outputs}) != len(self.outputs):
            raise InvalidParameterError("composition output IDs must be unique")

        if sum(len(output.inputs) for output in self.outputs) > _MAX_BINDINGS:
            raise InvalidParameterError("composition exceeds the input binding limit")

        inputIds = tuple(dict.fromkeys(externalId for output in self.outputs for _, externalId in output.inputs))

        if len(inputIds) > _MAX_INPUTS:
            raise InvalidParameterError("composition exceeds the distinct input limit")

        object.__setattr__(self, "inputIds", inputIds)

    def Evaluate(self, inputs: Mapping[str, MembershipScalar]) -> tuple[OutputRecord, ...]:
        """Validate all input keys and scalars, then evaluate each output once.

        Args:
            inputs: Exact external IDs mapped to original finite real coordinates.

        Returns:
            Records in output declaration order with unchanged scalar results.

        Raises:
            InvalidParameterTypeError: The mapping or a coordinate has the wrong type.
            InvalidParameterError: The input keys are incomplete or a coordinate is non-finite.
            CompositionEvaluationError: A scalar output failed under the fail-fast policy.
        """

        if not isinstance(inputs, Mapping):
            raise InvalidParameterTypeError("composition inputs must be a mapping")

        if len(inputs) != len(self.inputIds):
            raise InvalidParameterError("composition inputs must contain exactly the declared external IDs")

        snapshot = dict(inputs)

        if snapshot.keys() != set(self.inputIds):
            raise InvalidParameterError("composition inputs must contain exactly the declared external IDs")

        coordinates = {inputId: _RequireFiniteReal(snapshot[inputId], inputId) for inputId in self.inputIds}
        records = []

        for output in self.outputs:
            values = {name: coordinates[externalId] for name, externalId in output.inputs}

            try:
                outcome: MamdaniResult | SugenoResult | OutputFailure

                if isinstance(output.model, MamdaniModel):
                    outcome = output.model.Evaluate(values, output.integrationDomain, output.centroidPolicy)

                else:
                    outcome = output.model.Evaluate(values)

            except (InvalidParameterError, InvalidParameterTypeError, NumericalError) as error:
                if self.failurePolicy == "fail-fast":
                    raise CompositionEvaluationError(output.outputId) from error

                outcome = OutputFailure(_FailureCategory(error), str(error))

            records.append(OutputRecord(output.outputId, outcome))

        return tuple(records)

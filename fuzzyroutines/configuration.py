# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Standalone v1 configuration of immutable scalar models and scale libraries.

The codec takes and returns bytes. Callers choose where to read or write them.
Validation uses the optional `fuzzyroutines[config]` extra and an offline
schema shipped with the package.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import cast

from ._config_envelope import ConfigEnvelopeError
from ._config_export import EncodeModel, _EncodeModelBytes, _Model
from ._config_json import ConfigurationError, DecodeConfigJson
from ._config_mamdani_model import MamdaniCentroid, _ConfiguredMamdani, _DecodeMamdani
from ._config_scale_model import (
    ScaleDefinition,
    ScaleRepresentatives,
    _DecodeDefinitions,
    _Object,
    _ScaleModel,
)
from ._config_schema import ReadConfigV1Schema
from ._config_structure import CheckConfigStructure
from ._config_sugeno_model import _ConfiguredSugeno, _DecodeSugeno
from .domain import ContinuousUniverse, DiscreteUniverse
from .inference import MamdaniModel, SugenoModel
from .membership import MembershipFunction

__all__ = [
    "AssembleModel",
    "ConfigurationError",
    "DumpModel",
    "LoadModel",
    "MamdaniBinding",
    "MamdaniCentroid",
    "ModelConfiguration",
    "ScaleDefinition",
    "ScaleRepresentatives",
    "SugenoBinding",
]


@dataclass(frozen=True, slots=True)
class MamdaniBinding:
    """A runtime Mamdani rule base with explicit wire IDs and optional centroid.

    Attributes:
        model: Immutable runtime rule base.
        inputs: Ordered pairs of `(inputId, scaleId)` matching `model.inputs`.
        ruleIds: Exact wire IDs in the runtime rule declaration order.
        outputId: Output variable ID, distinct from every input ID.
        outputScaleId: ID of the continuous scale bound to the output.
        centroid: Closed window and numerical policy when explicitly declared.
    """

    model: MamdaniModel
    inputs: tuple[tuple[str, str], ...]
    ruleIds: tuple[str, ...]
    outputId: str
    outputScaleId: str
    centroid: MamdaniCentroid | None = None


@dataclass(frozen=True, slots=True)
class SugenoBinding:
    """A runtime Sugeno rule base with explicit wire IDs.

    Attributes:
        model: Immutable runtime rule base.
        inputs: Ordered pairs of `(inputId, scaleId)` matching `model.inputs`.
        ruleIds: Exact wire IDs in the runtime rule declaration order.
        outputUniverseId: ID of the model's declared continuous output universe.
    """

    model: SugenoModel
    inputs: tuple[tuple[str, str], ...]
    ruleIds: tuple[str, ...]
    outputUniverseId: str


@dataclass(frozen=True, slots=True)
class ModelConfiguration:
    """A validated standalone v1 snapshot obtained by loading or assembly.

    The named definitions use exact case-sensitive wire IDs. A scale library
    has `inference=None`. Consumers can evaluate a bound runtime model
    explicitly using its runtime variable names.
    """

    _snapshot: _Model

    @property
    def universes(self) -> Mapping[str, ContinuousUniverse | DiscreteUniverse]:
        """Read-only universe definitions keyed by wire ID."""

        return self._Definitions().universes

    @property
    def memberships(self) -> Mapping[str, MembershipFunction]:
        """Read-only built-in membership definitions keyed by wire ID."""

        return self._Definitions().memberships

    @property
    def scales(self) -> Mapping[str, ScaleDefinition]:
        """Read-only scale definitions with their ordered term bindings."""

        return self._Definitions().scales

    @property
    def inference(self) -> MamdaniBinding | SugenoBinding | None:
        """Explicit inference binding, or no inference for a scale library."""

        snapshot = self._snapshot

        if isinstance(snapshot, _ScaleModel):
            return None

        inputs = tuple(zip(snapshot.inputIds, snapshot.inputScaleIds, strict=True))

        if isinstance(snapshot, _ConfiguredMamdani):
            return MamdaniBinding(
                snapshot.model, inputs, snapshot.ruleIds, snapshot.outputId, snapshot.outputScaleId, snapshot.centroid,
            )

        return SugenoBinding(snapshot.model, inputs, snapshot.ruleIds, snapshot.outputUniverseId)

    def _Definitions(self) -> _ScaleModel:
        """Return the immutable local definitions of any standalone variant."""

        snapshot = self._snapshot

        return snapshot if isinstance(snapshot, _ScaleModel) else snapshot.definitions


def AssembleModel(
    universes: Mapping[str, ContinuousUniverse | DiscreteUniverse],
    memberships: Mapping[str, MembershipFunction],
    scales: Mapping[str, ScaleDefinition],
    *,
    inference: MamdaniBinding | SugenoBinding | None = None,
) -> ModelConfiguration:
    """Validate and snapshot explicit wire bindings for existing runtime objects.

    Args:
        universes: Local universe definitions under exact v1 IDs.
        memberships: Allowlisted built-in families under exact v1 IDs.
        scales: Scale definitions with explicit universe, term and membership IDs.
        inference: Optional rule base bound to the definitions by exact ordered IDs.

    Returns:
        An immutable standalone configuration with separately owned definition maps.

    Raises:
        ConfigurationError: The binding, runtime source or resulting wire data is invalid.
        ImportError: The configuration validation extra is unavailable.
    """

    definitions = _ScaleModel(
        MappingProxyType(dict(universes)), MappingProxyType(dict(memberships)), MappingProxyType(dict(scales)),
    )
    snapshot: _Model = definitions

    if inference is not None:
        inputIds = tuple(inputId for inputId, _ in inference.inputs)
        scaleIds = tuple(scaleId for _, scaleId in inference.inputs)
        ruleIds = tuple(inference.ruleIds)

        if isinstance(inference, MamdaniBinding):
            snapshot = _ConfiguredMamdani(
                inference.model, definitions, inputIds, scaleIds, ruleIds,
                inference.outputId, inference.outputScaleId, inference.centroid,
            )

        else:
            snapshot = _ConfiguredSugeno(
                inference.model, definitions, inputIds, scaleIds, ruleIds, inference.outputUniverseId,
            )

    return LoadModel(_EncodeModelBytes(snapshot))


def LoadModel(encoded: bytes) -> ModelConfiguration:
    """Load a standalone v1 model without reading files or evaluating rules.

    Args:
        encoded: One bounded UTF-8 JSON model document.

    Returns:
        An immutable scale library, Mamdani configuration or Sugeno configuration.

    Raises:
        ConfigurationError: Parsing, schema validation, or model binding fails.
        ImportError: The configuration validation extra is unavailable.
    """

    wire = DecodeConfigJson(encoded)
    CheckConfigStructure(wire, ReadConfigV1Schema())
    document = cast(_Object, wire)

    if document["kind"] != "model":
        raise ConfigEnvelopeError("unsupported-kind", ("kind",), "Expected a standalone model document.")

    inference = cast(_Object, document.get("inference"))

    if not inference:
        return ModelConfiguration(_DecodeDefinitions(document))

    if inference["kind"] == "mamdani":
        return ModelConfiguration(_DecodeMamdani(document, inference, ()))

    return ModelConfiguration(_DecodeSugeno(document, inference, ()))


def DumpModel(configuration: ModelConfiguration) -> bytes:
    """Return canonical v1 JSON bytes for a standalone configuration.

    Args:
        configuration: An immutable snapshot returned by loading or assembly.

    Returns:
        Deterministic UTF-8 bytes with ASCII key order and a final LF.

    Raises:
        ConfigurationError: A source value or wire binding cannot be encoded.
        ImportError: The configuration validation extra is unavailable.
    """

    return EncodeModel(configuration._snapshot)

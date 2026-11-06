# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Public standalone configuration API, assembly and optional validator contract."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from fuzzyroutines import _config_structure as configStructure
from fuzzyroutines.configuration import (
    AssembleModel,
    ConfigurationError,
    DumpModel,
    LoadModel,
    MamdaniBinding,
    MamdaniCentroid,
    ScaleDefinition,
    SugenoBinding,
)
from fuzzyroutines.defuzzification import CentroidPolicy
from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.inference import (
    ConstantConsequent,
    FuzzyVariable,
    InferencePolicy,
    MamdaniModel,
    MamdaniRule,
    SugenoModel,
    SugenoRule,
    TermCondition,
)
from fuzzyroutines.linguistic import LinguisticScale, LinguisticTerm
from fuzzyroutines.membership import Triangle
from fuzzyroutines.operators import NegationPolicy, SNormPolicy, TNormPolicy

_FIXTURES = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "config-v1" / "fixtures"


@pytest.fixture(name="validator")
def RequireValidator():
    """Select codec tests that exercise the installed optional validator."""

    return pytest.importorskip("jsonschema")


def _ConstructScale():
    """Build one modern scale without reading a configuration."""

    universe = ContinuousUniverse(0, 1, True, True)
    membership = Triangle(0, 0.5, 1)
    term = LinguisticTerm("Middle", ScalarFuzzySet(universe, membership))
    scale = ScaleDefinition(LinguisticScale((term,)), "unit", ("middle",), ("triangle",))

    return universe, membership, term, scale


def test_AssembleScaleOwnsDefinitionsAndPreservesDeterministicBytes(validator):
    """Assemble exact runtime bindings and keep a read-only scale snapshot."""

    universe, membership, term, scale = _ConstructScale()
    scopes = {"scale": scale}
    configuration = AssembleModel({"unit": universe}, {"triangle": membership}, scopes)
    scopes.clear()
    encoded = DumpModel(configuration)
    loaded = LoadModel(encoded)

    assert configuration.inference is None and loaded.inference is None, "Keep a standalone scale library."
    assert loaded.scales["scale"].scale.terms[0].name == term.name, "Preserve runtime term names."
    assert DumpModel(loaded) == encoded, "Require identical canonical bytes after reload."

    with pytest.raises(TypeError):
        configuration.scales["alternate"] = scale


@pytest.mark.parametrize("kind", ("mamdani", "sugeno"))
def test_AssembleInferenceFromPublicRuntimeObjects(validator, kind):
    """Bind real runtime models by exact ordered IDs and preserve outputs."""

    universe, membership, term, scale = _ConstructScale()
    variable = FuzzyVariable("Risk", (term,))
    condition = TermCondition("Risk", "Middle")
    policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))

    if kind == "sugeno":
        model = SugenoModel(
            (variable,), (SugenoRule("Respond", condition, ConstantConsequent(0.25)),), policy, universe,
        )
        binding = SugenoBinding(model, (("risk", "scale"),), ("respond",), "unit")

    else:
        model = MamdaniModel(
            (variable,), FuzzyVariable("Response", (term,)), (MamdaniRule("Respond", condition, "Middle"),),
            policy, TNormPolicy("logic"), SNormPolicy("logic"),
        )
        binding = MamdaniBinding(
            model, (("risk", "scale"),), ("respond",), "response", "scale",
            MamdaniCentroid(IntegrationDomain(0.125, 0.875), CentroidPolicy(1e-9, 1e-8, 12)),
        )

    configuration = AssembleModel({"unit": universe}, {"triangle": membership}, {"scale": scale}, inference=binding)
    encoded = DumpModel(configuration)
    loaded = LoadModel(encoded)
    inference = loaded.inference

    assert inference is not None, "Retain the explicit inference configuration."
    assert inference.inputs == (("risk", "scale"),) and inference.ruleIds == ("respond",), "Preserve wire IDs."
    assert DumpModel(loaded) == encoded, "Keep stable canonical bytes through the public API."

    if kind == "sugeno":
        assert isinstance(inference, SugenoBinding), "Load the Sugeno binding."
        result = inference.model.Evaluate({"Risk": 0.25})
        assert result.value == 0.25 and result.rules[0].firingStrength == 0.5, "Retain the Sugeno result and trace."

    else:
        assert isinstance(inference, MamdaniBinding) and inference.centroid is not None, "Load the Mamdani centroid."
        result = inference.model.Evaluate({"Risk": 0.25}, inference.centroid.domain, inference.centroid.policy)
        assert result.value == pytest.approx(0.5, rel=0, abs=1e-12), "Retain the Mamdani centroid."
        assert result.rules[0].firingStrength == 0.5, "Retain the Mamdani trace."


def test_PublicRoundTripPreservesHistoricalCoefficientsAndSettings(validator):
    """Retain the complete normative historical definition through public calls."""

    fixture = (_FIXTURES / "valid-historical-scale.json").read_bytes()
    configuration = LoadModel(fixture)
    encoded = DumpModel(configuration)
    assert json.loads(encoded) == json.loads(fixture), "Retain normative coefficients, order, tie settings and windows."
    assert DumpModel(LoadModel(encoded)) == encoded, "Emit the same canonical bytes after loading."


def test_PublicErrorCategoryAndPointerForUnserializableSource(validator):
    """Reject an arbitrary runtime callback without invoking or sampling it."""

    def Callback(coordinate):
        """Fail if an arbitrary source is executed."""

        raise AssertionError("Configuration assembly must never evaluate a source.")

    universe, membership, _, _ = _ConstructScale()
    term = LinguisticTerm("Middle", ScalarFuzzySet(universe, Callback))
    scale = ScaleDefinition(LinguisticScale((term,)), "unit", ("middle",), ("triangle",))

    with pytest.raises(ConfigurationError) as failure:
        AssembleModel({"unit": universe}, {"triangle": membership}, {"scale": scale})

    assert failure.value.category == "unsupported-source", "Reject arbitrary runtime evaluators explicitly."
    assert failure.value.pointer == "/scales/scale/terms/0/membership", "Locate the unsupported source."
    assert "built-in membership family" in str(failure.value), "Provide supported-source guidance."


def test_PublicLoadRejectsProjectsAndMalformedInput(validator):
    """Expose stable error categories at the public standalone boundary."""

    with pytest.raises(ConfigurationError) as project:
        LoadModel((_FIXTURES / "valid-project.json").read_bytes())

    assert project.value.category == "unsupported-kind" and project.value.pointer == "/kind", "Use the standalone contract."

    with pytest.raises(ConfigurationError) as malformed:
        LoadModel(b'{"kind":"model","kind":"model"}')

    assert malformed.value.category == "malformed-document" and malformed.value.pointer == "/kind", "Reject duplicate keys."


def test_OptionalValidatorHasActionableInstallGuidance(monkeypatch):
    """Fail on use with configuration-extra guidance when the validator is absent."""

    def RejectValidator(name):
        """Simulate a core-only package installation."""

        raise ModuleNotFoundError(name)

    monkeypatch.setattr(configStructure, "importlib", SimpleNamespace(import_module=RejectValidator))

    with pytest.raises(ImportError, match=r"fuzzyroutines\[config\]"):
        LoadModel((_FIXTURES / "valid-historical-scale.json").read_bytes())

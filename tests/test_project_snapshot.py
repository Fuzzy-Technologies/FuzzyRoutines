# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Exercise the typed JSON and YAML project boundary with checked-in v1 fixtures."""

import json
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType

import pytest

from fuzzyroutines._project_snapshot import LoadProjectJson, LoadProjectYaml
from fuzzyroutines.configuration import ConfigurationError, MamdaniBinding, SugenoBinding
from fuzzyroutines.inference import MamdaniModel, SugenoModel
from fuzzyroutines.yaml_configuration import ConvertProjectJsonToYaml

pytest.importorskip("jsonschema")

_FIXTURES = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "config-v1" / "fixtures"
_PROJECT = _FIXTURES / "valid-project.json"


@pytest.mark.parametrize("formatName", ("json", "yaml"))
def test_LoadProjectRetainsModelsAndReadOnlySettings(formatName):
    """Wrap both inference kinds and preserve exact project presentation and scenarios."""

    encoded = _PROJECT.read_bytes()

    if formatName == "yaml":
        pytest.importorskip("yaml")
        project = LoadProjectYaml(ConvertProjectJsonToYaml(encoded))

    else:
        project = LoadProjectJson(encoded)

    assert tuple(project.models) == ("centroid", "weighted")
    assert isinstance(project.SelectModel("centroid").inference, MamdaniBinding)
    selected = project.SelectModel()
    assert selected is project.models["weighted"]
    assert isinstance(selected.inference, SugenoBinding)
    assert selected.inference.model.Evaluate({"Risk": 0.25}).value == 0.296875
    assert project.defaults is not None
    assert (project.defaults.modelId, project.defaults.plotId, project.defaults.evaluationId) == (
        "weighted", "risk", "quarter",
    )
    assert project.units == {"weighted": {"normalized": "normalized ratio"}}
    plot = project.plots["risk"]
    assert (plot.modelId, plot.scaleId, plot.title, plot.xLabel) == (
        "weighted", "risk", "Risk / Риск / 风险", "Risk",
    )
    assert plot.termColors == {"high": "#8E44AD"}
    assert selected.scales[plot.scaleId].termIds == ("high",)
    scenario = project.evaluations["quarter"]
    assert (scenario.modelId, scenario.inputs, scenario.trace) == ("weighted", {"risk": 0.25}, True)
    assert all(isinstance(value, MappingProxyType) for value in (
        project.models, project.units, project.units["weighted"], project.plots,
        plot.termColors, project.evaluations, scenario.inputs,
    ))

    with pytest.raises(FrozenInstanceError):
        setattr(project, "defaults", None)

    with pytest.raises(KeyError, match="Weighted"):
        project.SelectModel("Weighted")


def test_LoadProjectNeverInfersASingletonDefault():
    """Require an explicit model ID while retaining the historical scale exactly."""

    historical = json.loads((_FIXTURES / "valid-historical-scale.json").read_bytes())
    project = LoadProjectJson(json.dumps({
        "kind": "project", "schemaVersion": 1, "models": {"legacy": historical},
    }).encode())
    assert project.defaults is None

    with pytest.raises(KeyError, match="explicit project model ID"):
        project.SelectModel()

    scale = next(iter(project.SelectModel("legacy").scales.values()))
    assert tuple(term.name for term in scale.scale.terms) == ("Min", "Low", "Med", "High", "Max")
    assert scale.scale.terms[0].fuzzySet.membershipFunction.parameters == {
        "scale": 8.0, "exponent": 20.0, "cutoff": 0.0,
    }


@pytest.mark.parametrize(
    ("identifier", "category", "pointer"),
    (
        ("missing", "unresolved-reference", "/defaults/model"),
        ("centroid", "invalid-relationship", "/defaults/evaluation"),
    ),
)
def test_LoadProjectRetainsTheExactDefaultDiagnostic(identifier, category, pointer):
    """Propagate dangling and mismatched defaults at their original wire pointers."""

    document = json.loads(_PROJECT.read_bytes())
    defaults = document["defaults"]
    defaults["model"] = identifier

    if identifier == "missing":
        del defaults["evaluation"]
        del defaults["plot"]

    with pytest.raises(ConfigurationError) as failure:
        LoadProjectJson(json.dumps(document).encode())

    assert failure.value.category == category
    assert failure.value.pointer == pointer


def test_LoadProjectLeavesDeclaredScenariosUnevaluated(monkeypatch):
    """Load and select all models without invoking an inference evaluator."""

    def RejectEvaluation(*arguments, **options):
        """Report an accidental eager evaluation."""

        raise AssertionError("Project loading must not evaluate scenarios.")

    monkeypatch.setattr(MamdaniModel, "Evaluate", RejectEvaluation)
    monkeypatch.setattr(SugenoModel, "Evaluate", RejectEvaluation)
    project = LoadProjectJson(_PROJECT.read_bytes())
    assert project.evaluations["quarter"].modelId == "weighted"
    assert project.SelectModel() is project.models["weighted"]

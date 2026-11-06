# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Golden v1 project reconstruction and precise scoped reference diagnostics."""

import json
import math
from pathlib import Path

import pytest

from fuzzyroutines._config_envelope import ConfigEnvelopeError
from fuzzyroutines._config_mamdani_model import _ConfiguredMamdani
from fuzzyroutines._config_project import DecodeProject
from fuzzyroutines._config_scale_model import ScaleModelDecodeError, _ScaleModel
from fuzzyroutines._config_sugeno_model import _ConfiguredSugeno
from fuzzyroutines.inference import MamdaniModel, SugenoModel
from fuzzyroutines.membership import MembershipFunction

pytest.importorskip("jsonschema")

_FIXTURES = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "config-v1" / "fixtures"
_PROJECT_FIXTURE = _FIXTURES / "valid-project.json"


def test_ReconstructsNamedModelsAndScopedSettings():
    """Retain golden project selections without changing inference mathematics."""

    project = DecodeProject(_PROJECT_FIXTURE.read_bytes())
    assert set(project.models) == {"centroid", "weighted"}, "Retain both exact model IDs."
    assert project.defaults is not None, "Keep explicit defaults."
    assert (project.defaults.modelId, project.defaults.plotId, project.defaults.evaluationId) == (
        "weighted", "risk", "quarter",
    ), "Keep independent selections scoped to the default model."
    assert project.units == {"weighted": {"normalized": "normalized ratio"}}, "Keep exact universe units."
    plot = project.plots["risk"]
    assert (plot.modelId, plot.scaleId, plot.xLabel) == ("weighted", "risk", "Risk"), "Bind the exact scale ID."
    assert plot.title == "Risk / Риск / 风险", "Preserve Unicode title spelling."
    assert plot.termColors == {"high": "#8E44AD"}, "Retain the exact color override."

    scenario = project.evaluations["quarter"]
    assert scenario.inputs == {"risk": 0.25} and scenario.trace, "Preserve input IDs, coordinates and trace selection."
    sugeno = project.models[scenario.modelId]
    mamdani = project.models["centroid"]
    assert isinstance(sugeno, _ConfiguredSugeno), "Dispatch the scenario model to Sugeno."
    assert isinstance(mamdani, _ConfiguredMamdani), "Dispatch the other inline model to Mamdani."
    assert mamdani.centroid is not None, "Retain the centroid policy within its model."
    runtimeInputs = {
        variable.name: scenario.inputs[inputId]
        for inputId, variable in zip(sugeno.inputIds, sugeno.model.inputs, strict=True)
    }
    assert sugeno.model.Evaluate(runtimeInputs).value == 0.296875, "Preserve the standalone Sugeno result."
    centroid = mamdani.model.Evaluate({"Risk": 0.25}, mamdani.centroid.domain, mamdani.centroid.policy)
    assert centroid.value == pytest.approx(0.5, rel=0, abs=1e-12), "Preserve the standalone Mamdani result."


def test_LoadsModelAndScenarioDataWithoutEvaluation(monkeypatch):
    """Construct a project while all inference and membership evaluation is forbidden."""

    def RejectEvaluation(*arguments, **options):
        """Fail if loading runs any evaluator."""

        raise AssertionError("Project loading must be data-only.")

    monkeypatch.setattr(MembershipFunction, "Evaluate", RejectEvaluation)
    monkeypatch.setattr(MamdaniModel, "Evaluate", RejectEvaluation)
    monkeypatch.setattr(SugenoModel, "Evaluate", RejectEvaluation)
    decoded = DecodeProject(_PROJECT_FIXTURE.read_bytes())
    assert set(decoded.evaluations) == {"quarter"}, "Bind the scenario without running it."


def test_SingletonHistoricalModelDoesNotInferDefaults():
    """Keep exact historical coefficients and require explicit project selection."""

    historical = json.loads((_FIXTURES / "valid-historical-scale.json").read_bytes())
    document = {"kind": "project", "schemaVersion": 1, "models": {"legacy": historical}}
    decoded = DecodeProject(json.dumps(document).encode())
    model = decoded.models["legacy"]

    assert decoded.defaults is None, "A singleton must not become an implicit default."
    assert isinstance(model, _ScaleModel), "Allow a scale-only model inside a project."
    scale = next(iter(model.scales.values()))
    assert tuple(term.name for term in scale.scale.terms) == ("Min", "Low", "Med", "High", "Max"), (
        "Preserve historical term order in a project."
    )
    minimum = scale.scale.terms[0].fuzzySet.membershipFunction
    assert isinstance(minimum, MembershipFunction), "Retain the allowlisted analytical source."
    assert minimum.parameters == {"scale": 8.0, "exponent": 20.0, "cutoff": 0.0}, "Retain historical Min coefficients."


def test_PreservesSignedZeroAndExactLabelSpelling():
    """Keep binary64 signed zero and display text independent of model settings."""

    document = json.loads(_PROJECT_FIXTURE.read_bytes())
    document["evaluations"]["quarter"]["inputs"]["risk"] = -0.0
    title = "  Cafe\u0301  "
    document["presentation"]["plots"]["risk"]["title"] = title
    decoded = DecodeProject(json.dumps(document).encode())
    assert math.copysign(1, decoded.evaluations["quarter"].inputs["risk"]) == -1, "Keep negative zero."
    assert decoded.plots["risk"].title == title, "Never trim or normalize labels."


@pytest.mark.parametrize(
    ("mutation", "category", "pointer"),
    [
        ("unknown-model-default", "unresolved-reference", "/defaults/model"),
        ("unknown-plot-default", "unresolved-reference", "/defaults/plot"),
        ("unknown-evaluation-default", "unresolved-reference", "/defaults/evaluation"),
        ("wrong-plot-default", "invalid-relationship", "/defaults/plot"),
        ("wrong-evaluation-default", "invalid-relationship", "/defaults/evaluation"),
        ("unknown-scenario-model", "unresolved-reference", "/evaluations/quarter/model"),
        ("scale-only-scenario", "invalid-relationship", "/evaluations/quarter/model"),
        ("unknown-scenario-input", "unresolved-reference", "/evaluations/quarter/inputs/second"),
        ("missing-scenario-input", "invalid-value", "/evaluations/quarter/inputs/second"),
        ("outside-scenario-input", "invalid-value", "/evaluations/quarter/inputs/risk"),
        ("unknown-plot-model", "unresolved-reference", "/presentation/plots/risk/model"),
        ("unknown-plot-scale", "unresolved-reference", "/presentation/plots/risk/scale"),
        ("unknown-color-term", "unresolved-reference", "/presentation/plots/risk/termColors/central"),
        ("blank-title", "invalid-value", "/presentation/plots/risk/title"),
        ("blank-axis-label", "invalid-value", "/presentation/plots/risk/xLabel"),
        ("unknown-units-model", "unresolved-reference", "/presentation/units/Weighted"),
        ("unknown-units-universe", "unresolved-reference", "/presentation/units/weighted/Normalized"),
        ("blank-unit", "invalid-value", "/presentation/units/weighted/normalized"),
        ("bad-inline-inference", "unresolved-reference", "/models/centroid/inference/rules/0/consequent"),
        ("bad-inline-definitions", "unresolved-reference", "/models/weighted/scales/risk/universe"),
        ("evaluation-before-model", "invalid-value", "/evaluations/quarter/inputs/risk"),
    ],
)
def test_ReportsExactProjectSemanticPointers(mutation, category, pointer):
    """Identify original wire fields for invalid references, inputs and labels."""

    document = json.loads(_PROJECT_FIXTURE.read_bytes())
    defaults = document["defaults"]
    plot = document["presentation"]["plots"]["risk"]
    units = document["presentation"]["units"]
    evaluation = document["evaluations"]["quarter"]
    weighted = document["models"]["weighted"]

    match mutation:
        case "unknown-model-default":
            defaults.pop("plot")
            defaults.pop("evaluation")
            defaults["model"] = "Weighted"
        case "unknown-plot-default":
            defaults["plot"] = "Risk"
        case "unknown-evaluation-default":
            defaults["evaluation"] = "Quarter"
        case "wrong-plot-default":
            plot["model"] = "centroid"
        case "wrong-evaluation-default":
            evaluation["model"] = "centroid"
        case "unknown-scenario-model":
            defaults.pop("evaluation")
            evaluation["model"] = "Weighted"
        case "scale-only-scenario":
            del weighted["inference"]
        case "unknown-scenario-input":
            evaluation["inputs"]["second"] = 0.25
        case "missing-scenario-input":
            weighted["inference"]["inputs"].append({"id": "second", "name": "Second", "scale": "risk"})
        case "outside-scenario-input":
            weighted["universes"]["normalized"]["leftClosed"] = False
            evaluation["inputs"]["risk"] = 0
        case "unknown-plot-model":
            defaults.pop("plot")
            plot["model"] = "Weighted"
        case "unknown-plot-scale":
            plot["scale"] = "response"
        case "unknown-color-term":
            plot["termColors"]["central"] = "#AABBCC"
        case "blank-title":
            plot["title"] = "  "
        case "blank-axis-label":
            plot["xLabel"] = "\t"
        case "unknown-units-model":
            units["Weighted"] = units.pop("weighted")
        case "unknown-units-universe":
            units["weighted"]["Normalized"] = units["weighted"].pop("normalized")
        case "blank-unit":
            units["weighted"]["normalized"] = "  "
        case "bad-inline-inference":
            document["models"]["centroid"]["inference"]["rules"][0]["consequent"] = "Central"
        case "bad-inline-definitions":
            weighted["scales"]["risk"]["universe"] = "Normalized"
        case "evaluation-before-model":
            document["models"]["centroid"]["inference"]["rules"][0]["consequent"] = "Central"
            evaluation["inputs"]["risk"] = 2

    with pytest.raises(ScaleModelDecodeError) as failure:
        DecodeProject(json.dumps(document).encode())

    assert failure.value.category == category, "Preserve the actionable project diagnostic category."
    assert failure.value.pointer == pointer, "Point at the original invalid project field."


def test_ProjectDispatchRejectsUnsupportedInlineVersions():
    """Reject an unsupported inline version before binding project semantics."""

    document = json.loads(_PROJECT_FIXTURE.read_bytes())
    document["models"]["weighted"]["schemaVersion"] = 2
    document["defaults"]["plot"] = "absent"

    with pytest.raises(ConfigEnvelopeError) as failure:
        DecodeProject(json.dumps(document).encode())

    assert failure.value.category == "unsupported-version", "Dispatch failures must precede semantic validation."
    assert failure.value.pointer == "/models/weighted/schemaVersion", "Keep the inline envelope pointer."

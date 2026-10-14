# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Optional scope and independent report failures for the neural CI workflow."""

import json
import math
from pathlib import Path

import pytest

from tools.neural_ci import SelectScope, ValidateReport

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("full, selected, training, plots", [
    (True, [], True, True),
    (False, [], False, False),
    (False, ["tests/test_neural_example.py"], True, False),
    (False, ["tests/test_neural_figures.py"], False, True),
    (False, ["tests/test_neural_example.py", "tests/test_neural_figures.py"], True, True),
    (False, ["tests/test_neural_workflow.py", "tests/test_ci_policy.py"], False, False),
    (False, ["tests/test_numpy_membership.py"], False, False),
    (False, ["tests/test_differentiable_sugeno.py"], True, False),
    (False, ["tests/test_sugeno_research.py"], True, False),
    (False, ["tests/test_sugeno_research_figures.py"], False, True),
])
def test_NeuralScopeRespectsReviewedFeatureSelection(full, selected, training, plots):
    """An unrelated update cannot install Torch or silently expand to the whole suite."""

    scope = SelectScope({"full": full, "tests": selected})
    assert scope["training"] is training
    assert scope["plots"] is plots
    assert scope["active"] is (training or plots)
    assert bool(scope["trainingTests"]) is training
    assert bool(scope["plotTests"]) is plots


@pytest.mark.parametrize("policy", [{}, {"full": "false", "tests": []}, {"full": False, "tests": "tests/test_neural_example.py"}, {"full": False, "tests": [None]}])
def test_NeuralScopeRejectsUnvalidatedPolicy(policy):
    """Malformed policy data is a failure, never an implicit skip or full request."""

    with pytest.raises(TypeError):
        SelectScope(policy)


def test_ResearchAndNeuralActionsAreIndependentlySelected():
    """Selecting a research test does not rerun neural training or unrelated figures."""

    research = SelectScope({"full": False, "tests": ["tests/test_sugeno_research.py"]})
    assert research["research"] and not research["neural"]
    assert research["trainingTests"] == ["tests/test_sugeno_research.py"]
    assert not research["plots"]
    figures = SelectScope({"full": False, "tests": ["tests/test_sugeno_research_figures.py"]})
    assert figures["researchPlots"] and not figures["neuralPlots"]
    assert not figures["training"]
    full = SelectScope({"full": True, "tests": []})
    assert all(full[name] for name in ("research", "neural", "researchPlots", "neuralPlots"))


def Reference():
    """Read measured evidence without importing Torch or running a network."""

    return json.loads((PROJECT_ROOT / "examples/neural/reference.json").read_text())


def test_NeuralSmokeOracleAcceptsMeasuredEvidence():
    """Recompute data, splits, centroid targets and metric arithmetic independently."""

    report = Reference()
    verified = ValidateReport(report, expectedVersion=report["environment"]["fuzzyroutines"], epochs=400, samples=600)
    assert verified["verified"] is True
    assert verified["heldOut"] == 120


@pytest.mark.parametrize("defect", ["metric", "labels", "target", "baseline", "split", "source", "package", "nan", "gradeShape", "clipping", "budget"])
def test_NeuralSmokeOracleRejectsContradictoryEvidence(defect):
    """Corrupt distinct externally meaningful report guarantees, not trainer internals."""

    report = Reference()
    expectedVersion = report["environment"]["fuzzyroutines"]

    if defect == "metric":
        report["scalarAblations"]["raw"]["heldOut"]["centroidRmse"] = 0

    elif defect == "labels":
        report["scalarAblations"]["centroid"]["heldOut"]["labelAccuracy"] = 0

    elif defect == "target":
        report["heldOutTargets"][0] = 0.5

    elif defect == "baseline":
        report["baseline"]["meanTrainingTarget"] = 0

    elif defect == "split":
        report["splits"]["heldOut"][0] = report["splits"]["train"][0]

    elif defect == "source":
        report["exampleSha256"] = "stale"

    elif defect == "package":
        report["environment"]["fuzzyroutines"] = "wrong-version"

    elif defect == "nan":
        report["gradeHead"]["heldOutGradeRmse"] = math.nan

    elif defect == "gradeShape":
        report["gradeHead"]["weakCoverageProbe"]["predictedGrades"].pop()

    elif defect == "clipping":
        report["outOfDomainExamples"][0]["value"] = 0

    elif defect == "budget":
        report["configuration"]["epochs"] = 500

    with pytest.raises(ValueError):
        ValidateReport(report, expectedVersion=expectedVersion, epochs=400, samples=600)


def test_NeuralWorkflowKeepsCpuDependenciesAndInstalledEvidenceScoped():
    """Guard execution policy, wheel isolation and bounded training at the workflow boundary."""

    workflow = (PROJECT_ROOT / ".github/workflows/neural-examples.yml").read_text()
    assert "  pull_request:" in workflow and "  workflow_dispatch:" in workflow
    assert "  push:" not in workflow and "pull_request_target" not in workflow
    assert "uses: ./.github/actions/ci-policy" in workflow
    assert "fetch-depth: 0" in workflow and "cancel-in-progress: true" in workflow
    assert 'python-version: ["3.13", "3.14"]' in workflow
    assert "--index-url https://download.pytorch.org/whl/cpu -r examples/neural/requirements.txt" in workflow
    assert "--verify-installed --epochs 30 --samples 90" in workflow
    assert '"$NEURAL_PYTHON" -I "$GITHUB_WORKSPACE/examples/neural/run.py"' in workflow
    assert '"$NEURAL_PYTHON" -I "$GITHUB_WORKSPACE/tools/neural_ci.py" verify-report' in workflow
    assert "python -m build --wheel --no-isolation" in workflow
    assert "sha256sum --check" in workflow and "git rev-parse HEAD" in workflow

    for name in ("Install the optional pinned CPU framework", "Run only selected neural source feature tests"):
        step = workflow.split(f"      - name: {name}\n", 1)[1].split("      - name:", 1)[0]
        assert "if: steps.neural.outputs.training == 'true'" in step

    for name in ("Install plotting dependencies without requiring Torch", "Run only selected figure evidence tests"):
        step = workflow.split(f"      - name: {name}\n", 1)[1].split("      - name:", 1)[0]
        assert "if: steps.neural.outputs.plots == 'true'" in step

    for name, scope in (("Smoke the installed wheel with a bounded CPU experiment", "neural"),
                        ("Smoke research Sugeno against the installed candidate", "research"),
                        ("Verify recorded figures against the installed scalar API", "neuralPlots"),
                        ("Verify recorded Sugeno figures and installed source provenance", "researchPlots")):
        step = workflow.split(f"      - name: {name}\n", 1)[1].split("      - name:", 1)[0]
        assert f"if: steps.neural.outputs.{scope} == 'true'" in step

    assert '"$NEURAL_PYTHON" -I "$GITHUB_WORKSPACE/tools/research_ci.py" smoke' in workflow
    assert '"$NEURAL_PYTHON" -I "$GITHUB_WORKSPACE/tools/research_ci.py" figures' in workflow
    assert "--measure-dependencies" not in workflow

    documentation = (PROJECT_ROOT / ".github/workflows/documentation-gates.yml").read_text()
    assert "tests/test_neural_example.py" not in documentation
    assert "examples/neural/run.py" not in documentation
    assert "-r examples/neural/requirements.txt" not in documentation

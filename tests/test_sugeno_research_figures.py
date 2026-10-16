# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Independent checks of recorded research metrics and the actual plot artists."""

import hashlib
import json
import math
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")

from tools.generate_sugeno_research_figures import (
    MODEL_NAMES,
    REPORT,
    BuildFigures,
    ConfigureStyle,
    RenderSvg,
    plt,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module", name="researchFigures")
def ResearchFigures():
    """Build plots once from the recorded evidence, with no Torch import or fit."""

    ConfigureStyle()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    figures = BuildFigures(report)

    yield report, figures

    for figure in figures.values():
        plt.close(figure)


def test_EvidenceMetricsAndSourceFingerprintsRemainHonest(researchFigures):
    """Recalculate held-out errors and require the actual recorded source bytes."""

    report, _ = researchFigures

    for source, digest in report["sourceSha256"].items():
        assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == digest, "Regenerate research evidence when its recorded calculation source changes"

    targets = report["heldOutTargets"]

    for model in report["models"].values():
        predictions = model["heldOutPredictions"]
        expected = math.sqrt(math.fsum((actual - target)**2 for actual, target in zip(predictions, targets, strict=True)) / len(targets))
        assert expected == pytest.approx(model["heldOut"]["centroidRmse"], rel=0, abs=1e-15), "Recorded RMSE must equal the independent error formula over held-out predictions"
        assert sum(not 0 <= value <= 1 for value in predictions) == model["heldOut"]["outOfDomainCount"], "The evidence must expose invalid predictions without clipping"

    assert report["datasetSha256"] == "269ecf533ab25d3371f2b0b208173adb6d2655eb1c30ba51c7776e37d5f000d2", "The reported run must retain the frozen common #328 synthetic dataset"
    assert report["models"]["firstOrder"]["heldOut"]["outOfDomainCount"] == 2, "The negative output-domain finding must remain visible"


def test_MembershipAndLearningArtistsUseRecordedValues(researchFigures):
    """Check membership curves analytically and losses against raw training logs."""

    report, figures = researchFigures
    axes = figures["sugeno-research-learning"].axes

    for dimension in range(2):
        for term in range(2):
            for phaseIndex, phase in enumerate(("initial", "selected")):
                snapshot = report["models"]["firstOrder"][phase]
                line = axes[dimension].lines[2 * term + phaseIndex]
                center, width = snapshot["centers"][dimension][term], snapshot["widths"][dimension][term]
                expected = [math.exp(-(value - center)**2 / (2 * width**2)) for value in line.get_xdata()]
                assert list(line.get_ydata()) == pytest.approx(expected, rel=0, abs=1e-14), "Membership artist must represent the recorded constrained Gaussian parameters"

    for line, name in zip(axes[2].lines, MODEL_NAMES[1:], strict=True):
        assert list(line.get_ydata()) == [math.sqrt(item["validationMse"]) for item in report["models"][name]["history"]], "Learning curves must show validation RMSE rather than training or held-out error"
        lower, upper = axes[2].get_ylim()
        assert all(lower <= value <= upper for value in line.get_ydata()), "Learning-axis limits must not hide recorded training behavior"

    assert [bar.get_width() for bar in axes[3].patches] == [report["models"][name]["heldOut"]["centroidRmse"] for name in MODEL_NAMES], "Comparison bars must show exact held-out errors in declared model order"


def test_PredictionArtistsKeepFailuresAndDeterministicSvg(researchFigures):
    """Retain all 120 predictions, the two failures and byte-identical SVG output."""

    report, figures = researchFigures
    axes = figures["sugeno-research-predictions"].axes
    assert list(axes[0].lines[0].get_ydata()) == report["slice"]["targets"], "Target slice must use recorded historical label centroids"

    for line, name in zip(axes[0].lines[1:], MODEL_NAMES[1:], strict=True):
        assert list(line.get_ydata()) == report["models"][name]["slicePredictions"], "Prediction curves must preserve actual model outputs"

    assert [len(collection.get_offsets()) for collection in axes[1].collections] == [118, 2], "The held-out scatter must visibly retain both invalid first-order predictions"
    directory = ROOT / "docs/site/content/en/assets/figures"

    for name, figure in figures.items():
        assert RenderSvg(figure, name) == (directory / f"{name}.svg").read_bytes(), "Research SVG must be regenerated after its evidence or plot code changes"

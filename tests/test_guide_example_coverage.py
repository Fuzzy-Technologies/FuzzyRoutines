# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Require observable guide usage, canonical alias identity and clean profiling."""

import json
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COVERAGE = runpy.run_path(str(PROJECT_ROOT / "tools/guide_example_coverage.py"))


def test_ImportsAloneCannotEstablishPublicExampleCoverage():
    """Reject unused imports even though the snippet itself executes successfully."""

    from fuzzyroutines import Triangle

    report = COVERAGE["BuildReport"]({"unused": "from fuzzyroutines import Triangle"}, {"fuzzyroutines.Triangle": Triangle})

    assert report["missing"] == ["fuzzyroutines.Triangle"]


def test_ConstructorsMethodsAndPropertiesAreObservedFromRealCalls():
    """Record generated constructor code, method execution and property reads."""

    from fuzzyroutines import ContinuousUniverse

    targets = {
        "fuzzyroutines.ContinuousUniverse": ContinuousUniverse,
        "fuzzyroutines.domain.ContinuousUniverse.Contains": ContinuousUniverse.Contains,
        "fuzzyroutines.domain.ContinuousUniverse.isBounded": ContinuousUniverse.isBounded,
    }
    snippet = "from fuzzyroutines import ContinuousUniverse\nu = ContinuousUniverse(0, 1)\nassert u.isBounded and u.Contains(0.5)"
    report = COVERAGE["BuildReport"]({"called": snippet}, targets)

    assert not report["missing"] and all(names == ["called"] for names in report["coverage"].values())


def test_AnAnnotationExercisesATypeContractOnBothSupportedPythons():
    """Handle eager 3.13 and deferred 3.14 module annotation dictionaries."""

    from fuzzyroutines import MembershipCallable

    report = COVERAGE["BuildReport"](
        {"typed": "from fuzzyroutines import MembershipCallable\ncallback: MembershipCallable = lambda x: x"},
        {"fuzzyroutines.MembershipCallable": MembershipCallable},
    )

    assert not report["missing"]


def test_ProfileIsRestoredWhenAnExampleFails():
    """An invalid published example must fail without leaving a profiler installed."""

    previous = sys.getprofile()

    with pytest.raises(ValueError, match="example failure"):
        COVERAGE["BuildReport"]({"broken": "raise ValueError('example failure')"}, {})

    assert sys.getprofile() is previous


def test_AntecedentTypeContractRequiresAnExecutedAnnotation():
    """Treat the rule type alias as a used contract, never as an imported name."""

    from fuzzyroutines.inference import Antecedent

    targets = {"fuzzyroutines.inference.Antecedent": Antecedent}
    imported = "from fuzzyroutines.inference import Antecedent, TermCondition"
    unused = COVERAGE["BuildReport"]({"unused": imported}, targets)
    assert unused["missing"] == list(targets)
    used = COVERAGE["BuildReport"](
        {"typed": imported + '\ncondition: Antecedent = TermCondition("risk", "low")'}, targets,
    )
    assert not used["missing"]


def test_CanonicalRootExportsCannotSilentlyChangeTheirTarget(monkeypatch):
    """Reject a root name that no longer resolves to its declared module object."""

    import fuzzyroutines

    monkeypatch.setattr(fuzzyroutines, "Triangle", object())

    with pytest.raises(RuntimeError, match="canonical root alias: Triangle"):
        COVERAGE["PublicTargets"]()


def test_BuiltinExceptionCategoriesRequireConstructedInstances():
    """An imported exception class is insufficient; a retained concrete value counts."""

    from fuzzyroutines.exceptions import InvalidDomainError

    target = {"fuzzyroutines.exceptions.InvalidDomainError": InvalidDomainError}
    report = COVERAGE["BuildReport"]({"used": "from fuzzyroutines.exceptions import InvalidDomainError\nerror = InvalidDomainError('domain')"}, target)

    assert not report["missing"]


def test_AllPublishedPublicExamplesAndTheirIndexAreCurrent():
    """Validate core usage and its index rows while reporting optional omissions."""

    report = COVERAGE["BuildReport"]()

    assert report["symbolCount"] >= 190 and not report["missing"]
    COVERAGE["ValidateIndex"](report, COVERAGE["INDEX_PATH"].read_text())
    assert report["omittedOptionalPages"] == ["guides/numpy-batches.md"]


def test_OptionalScopesAreReportedAndCannotProduceAFullIndex():
    """Separate unexecuted optional symbols from genuine missing core examples."""

    from fuzzyroutines import Triangle
    from fuzzyroutines.batches import EvaluateMembershipBatch

    report = COVERAGE["BuildReport"](
        {"called": "from fuzzyroutines import Triangle\nTriangle(0, 1, 2)"},
        {"fuzzyroutines.Triangle": Triangle, "fuzzyroutines.batches.EvaluateMembershipBatch": EvaluateMembershipBatch},
    )
    assert not report["missing"]
    assert report["omittedOptionalSymbols"] == ["fuzzyroutines.batches.EvaluateMembershipBatch"]
    assert report["symbolCount"] == 1

    with pytest.raises(RuntimeError, match="every declared optional extra"):
        COVERAGE["RenderIndex"](report)

    with pytest.raises(ValueError, match="Unknown guide extras"):
        COVERAGE["BuildReport"]({}, {}, extras=("unknown",))


def test_CoreIndexValidationRejectsMissingChangedAndDuplicateRows():
    """Validate actual core links without asserting optional example execution."""

    report = {
        "missing": [], "symbolCount": 1, "exampleCount": 1,
        "coverage": {"fuzzyroutines.Triangle": ["canonical-guides-temperature-1"]},
        "omittedOptionalPages": [], "omittedOptionalSymbols": [],
    }
    index = COVERAGE["RenderIndex"](report)
    scopedReport = dict(report, omittedOptionalPages=["guides/numpy-batches.md"])
    COVERAGE["ValidateIndex"](scopedReport, index)
    sharedIndex = index.replace("[temperature, block 1](temperature.md)",
                                "[temperature, block 1](temperature.md); [numpy-batches, block 1](numpy-batches.md)")
    COVERAGE["ValidateIndex"](scopedReport, sharedIndex)

    for invalidIndex in (index.replace("`fuzzyroutines.Triangle`", "`fuzzyroutines.Gone`"),
                         index.replace("block 1", "block 9"), index + index):
        with pytest.raises(RuntimeError):
            COVERAGE["ValidateIndex"](scopedReport, invalidIndex)


def test_OptionalCoverageCliWritesFullEvidenceAndValidatesCoreSubset(tmpPath):
    """Exercise JSON stdout and file outputs without requiring an optional backend."""

    projectRoot = tmpPath / "fixture"
    files = {
        "fuzzyroutines/__init__.py": 'from fuzzyroutines.membership import Triangle\n__all__ = ["Triangle"]\n',
        "fuzzyroutines/membership.py": 'def Triangle():\n    return 1\n',
        "fuzzyroutines/batches.py": 'def Batch():\n    return 2\n',
        "docs/site/content/en/guides/core.md": '```python\nfrom fuzzyroutines import Triangle\nassert Triangle() == 1\n```\n',
        "docs/site/content/en/guides/numpy-batches.md": '```python\nfrom fuzzyroutines.batches import Batch\nassert Batch() == 2\n```\n',
        "docs/site/api-coverage.toml": '''schemaVersion = 1
[[surfaces]]
module = "fuzzyroutines"
[[surfaces]]
module = "fuzzyroutines.membership"
[[surfaces]]
module = "fuzzyroutines.batches"
[[optionalExamples]]
extra = "numpy"
pages = ["guides/numpy-batches.md"]
modules = ["fuzzyroutines.batches"]
''',
        "docs/i18n/units.toml": '''[[units]]
kind = "symbol"
id = "symbol:fuzzyroutines.Triangle"
[[units]]
kind = "symbol"
id = "symbol:fuzzyroutines.membership.Triangle"
[[units]]
kind = "symbol"
id = "symbol:fuzzyroutines.batches.Batch"
''',
    }

    for relativePath, text in files.items():
        path = projectRoot / relativePath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    toolRoot = projectRoot / "tools"
    toolRoot.mkdir()

    for name in ("guide_example_coverage.py", "verify_installed_executables.py"):
        shutil.copyfile(PROJECT_ROOT / "tools" / name, toolRoot / name)

    environment = dict(os.environ, PYTHONPATH=str(projectRoot))
    command = [sys.executable, str(toolRoot / "guide_example_coverage.py")]

    for mode, arguments in (("full", ["--extra", "numpy", "--write-index"]), ("core", ["--check-index"])):
        reportPath = tmpPath / f"{mode}.json"
        stdoutPath = tmpPath / f"{mode}-stdout.json"

        with stdoutPath.open("w", encoding="utf-8") as stdout:
            result = subprocess.run(command + arguments + ["--output", str(reportPath)], cwd=tmpPath,
                                    env=environment, stdout=stdout, stderr=subprocess.PIPE, text=True, check=False)

        assert result.returncode == 0, result.stderr
        summary = json.loads(stdoutPath.read_text(encoding="utf-8"))
        report = json.loads(reportPath.read_text(encoding="utf-8"))
        assert not summary["missing"] and report["schemaVersion"] == 2
        assert summary["symbolCount"] == (3 if mode == "full" else 2)
        assert summary["omittedOptionalSymbols"] == ([] if mode == "full" else ["fuzzyroutines.batches.Batch"])

    denied = subprocess.run(command + ["--write-index"], cwd=tmpPath, env=environment,
                            capture_output=True, text=True, check=False)
    assert denied.returncode != 0 and "every declared optional extra" in denied.stderr


def test_TheReaderIndexCannotConcealAnUnexplainedGap():
    """Refuse to render apparent completeness when any public symbol lacks usage."""

    with pytest.raises(RuntimeError, match="incomplete public example index"):
        COVERAGE["RenderIndex"]({"missing": ["fuzzyroutines.NewFunction"]})

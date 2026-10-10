# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Require observable guide usage, canonical alias identity and clean profiling."""

import runpy
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
    """Validate complete canonical symbol usage and the actual reader-facing links."""

    report = COVERAGE["BuildReport"]()

    assert report["symbolCount"] >= 190 and not report["missing"]
    assert COVERAGE["INDEX_PATH"].read_text() == COVERAGE["RenderIndex"](report)


def test_TheReaderIndexCannotConcealAnUnexplainedGap():
    """Refuse to render apparent completeness when any public symbol lacks usage."""

    with pytest.raises(RuntimeError, match="incomplete public example index"):
        COVERAGE["RenderIndex"]({"missing": ["fuzzyroutines.NewFunction"]})

# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2019-2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0


"""Historical facade ownership, consumer, state, and serialization contracts."""

import ast
import base64
import importlib
import math
import pickle
import subprocess
import sys
from pathlib import Path

import pytest

import fuzzyroutines.FuzzyRoutines as legacy
from fuzzyroutines import ContinuousUniverse, DeriveProperties, Height, ScalarFuzzySet
from fuzzyroutines.membership import Triangle

PROJECT_ROOT = Path(__file__).parents[1]
HISTORICAL_SYMBOLS = (
    "DiapasonParser", "IsNumber", "IsCorrectFuzzyNumberValue", "FuzzyNOT",
    "FuzzyNOTParabolic", "FuzzyAND", "FuzzyOR", "TNorm", "TNormCompose",
    "SCoNorm", "SCoNormCompose", "MFunction", "FuzzySet", "FuzzyScale",
    "UniversalFuzzyScale",
)
# CPython protocol 4 fixture created before facade extraction at develop 42b0d217.
# Contains all four historical classes, defaults, lookup aliases and bound methods.
BASELINE_PICKLE_BASE64 = (
    "gASVSw0AAAAAAAAojBtmdXp6eXJvdXRpbmVzLkZ1enp5Um91dGluZXOUjAlNRnVuY3Rpb26Uk5QpgZR9lCiMCGFjY3VyYWN5lE3o"
    "A4wKX2Z1bmN0aW9uc5R9lCiMCmh5cGVyYm9saWOUjAhidWlsdGluc5SMB2dldGF0dHKUk5RoA4wKSHlwZXJib2xpY5SGlFKUjARi"
    "ZWxslGgLaAOMBEJlbGyUhpRSlIwJcGFyYWJvbGljlGgLaAOMCVBhcmFib2xpY5SGlFKUjAlzU2hvdWxkZXKUaAtoA2gUhpRSlIwI"
    "dHJpYW5nbGWUaAtoA4wIVHJpYW5nbGWUhpRSlIwJdHJhcGV6aXVtlGgLaAOMCVRyYXBleml1bZSGlFKUjAtleHBvbmVudGlhbJRo"
    "C2gDjAtFeHBvbmVudGlhbJSGlFKUjAhnYXVzc2lhbpRoC2gDaCOGlFKUjAlzaWdtb2lkYWyUaAtoA4wJU2lnbW9pZGFslIaUUpSM"
    "CGxvZ2lzdGljlGgLaANoKoaUUpSMDGRlc2lyYWJpbGl0eZRoC2gDjAxEZXNpcmFiaWxpdHmUhpRSlIwWaGFycmluZ3RvbkRlc2ly"
    "YWJpbGl0eZRoC2gDaDGGlFKUdYwDbWp1lGgdjAtfcGFyYW1ldGVyc5R9lCiMAWGUSwCMAWKUSwKMAWOUSwF1dWJoAIwIRnV6enlT"
    "ZXSUk5QpgZR9lCiMBV9uYW1llGg9jApfbUZ1bmN0aW9ulGgCKYGUfZQoaAVN6ANoBn2UKGgIaAtoQ2gMhpRSlGgPaAtoQ2gQhpRS"
    "lGgTaAtoQ2gUhpRSlGgXaAtoQ2gUhpRSlGgaaAtoQ2gbhpRSlGgeaAtoQ2gfhpRSlGgiaAtoQ2gjhpRSlGgmaAtoQ2gjhpRSlGgp"
    "aAtoQ2gqhpRSlGgtaAtoQ2gqhpRSlGgwaAtoQ2gxhpRSlGg0aAtoQ2gxhpRSlHVoN2hVaDh9lChoOksAaDtLAXV1YowSX2ludGVn"
    "cmF0aW9uRG9tYWlulIwUZnV6enlyb3V0aW5lcy5kb21haW6UjBFJbnRlZ3JhdGlvbkRvbWFpbpSTlCmBlF2UKEcAAAAAAAAAAEc/"
    "8AAAAAAAAGVijAtfZGVmdXpWYWx1ZZROdWJoAIwKRnV6enlTY2FsZZSTlCmBlH2UKGhBjAxEZWZhdWx0U2NhbGWUjAdfbGV2ZWxz"
    "lF2UKH2UKIwEbmFtZZSMA01pbpSMBGZTZXSUaD4pgZR9lChoQYwHTWluaW11bZRoQmgCKYGUfZQoaAVN6ANoBn2UKGgIaAtodGgM"
    "hpRSlGgPaAtodGgQhpRSlGgTaAtodGgUhpRSlGgXaAtodGgUhpRSlGgaaAtodGgbhpRSlGgeaAtodGgfhpRSlGgiaAtodGgjhpRS"
    "lGgmaAtodGgjhpRSlGgpaAtodGgqhpRSlGgtaAtodGgqhpRSlGgwaAtodGgxhpRSlGg0aAtodGgxhpRSlHVoN2h4aDh9lChoOksH"
    "aDtLBGg8SwB1dWJoX2hiKYGUXZQoRwAAAAAAAAAARz/wAAAAAAAAZWJoZU51YnV9lChobowDTWVklGhwaD4pgZR9lChoQYwGTWVk"
    "aXVtlGhCaAIpgZR9lChoBU3oA2gGfZQoaAhoC2iXaAyGlFKUaA9oC2iXaBCGlFKUaBNoC2iXaBSGlFKUaBdoC2iXaBSGlFKUaBpo"
    "C2iXaBuGlFKUaB5oC2iXaB+GlFKUaCJoC2iXaCOGlFKUaCZoC2iXaCOGlFKUaCloC2iXaCqGlFKUaC1oC2iXaCqGlFKUaDBoC2iX"
    "aDGGlFKUaDRoC2iXaDGGlFKUdWg3aJ1oOH2UKGg6Rz/WZmZmZmZmaDtHP+AAAAAAAABoPEc/4zMzMzMzM3V1YmhfaGIpgZRdlChH"
    "AAAAAAAAAABHP/AAAAAAAABlYmhlTnVidX2UKGhujARIaWdolGhwaD4pgZR9lChoQWi2aEJoAimBlH2UKGgFTegDaAZ9lChoCGgL"
    "aLloDIaUUpRoD2gLaLloEIaUUpRoE2gLaLloFIaUUpRoF2gLaLloFIaUUpRoGmgLaLloG4aUUpRoHmgLaLloH4aUUpRoImgLaLlo"
    "I4aUUpRoJmgLaLloI4aUUpRoKWgLaLloKoaUUpRoLWgLaLloKoaUUpRoMGgLaLloMYaUUpRoNGgLaLloMYaUUpR1aDdoxWg4fZQo"
    "aDpHP+ZmZmZmZmZoO0sBaDxLAXV1YmhfaGIpgZRdlChHAAAAAAAAAABHP/AAAAAAAABlYmhlTnVidWWMDF9sZXZlbHNOYW1lc5R9"
    "lChob2htaJNokmi2aLV1jBFfbGV2ZWxzTmFtZXNVcHBlcpR9lCiMA01JTpRobYwDTUVElGiSjARISUdIlGi1dXViaACME1VuaXZl"
    "cnNhbEZ1enp5U2NhbGWUk5QpgZR9lChoQWhmaGtdlCh9lChobmhvaHBoPimBlH2UKGhBaG9oQmgCKYGUfZQoaAVN6ANoBn2UKGgI"
    "aAto5mgMhpRSlGgPaAto5mgQhpRSlGgTaAto5mgUhpRSlGgXaAto5mgUhpRSlGgaaAto5mgbhpRSlGgeaAto5mgfhpRSlGgiaAto"
    "5mgjhpRSlGgmaAto5mgjhpRSlGgpaAto5mgqhpRSlGgtaAto5mgqhpRSlGgwaAto5mgxhpRSlGg0aAto5mgxhpRSlHVoN2jqaDh9"
    "lChoOksIaDtLFGg8SwB1dWJoX2hiKYGUXZQoRwAAAAAAAAAARz/NcKPXCj1xZWJoZU51YnV9lChobowDTG93lGhwaD4pgZR9lCho"
    "QWoFAQAAaEJoAimBlH2UKGgFTegDaAZ9lChoCGgLaggBAABoDIaUUpRoD2gLaggBAABoEIaUUpRoE2gLaggBAABoFIaUUpRoF2gL"
    "aggBAABoFIaUUpRoGmgLaggBAABoG4aUUpRoHmgLaggBAABoH4aUUpRoImgLaggBAABoI4aUUpRoJmgLaggBAABoI4aUUpRoKWgL"
    "aggBAABoKoaUUpRoLWgLaggBAABoKoaUUpRoMGgLaggBAABoMYaUUpRoNGgLaggBAABoMYaUUpR1aDdqDgEAAGg4fZQoaDpHP8XC"
    "j1wo9cNoO0c/zXCj1wo9cWg8Rz/Vwo9cKPXDdXViaF9oYimBlF2UKEc/xcKPXCj1w0c/2ZmZmZmZmmViaGVOdWJ1fZQoaG5ok2hw"
    "aD4pgZR9lChoQWiTaEJoAimBlH2UKGgFTegDaAZ9lChoCGgLaikBAABoDIaUUpRoD2gLaikBAABoEIaUUpRoE2gLaikBAABoFIaU"
    "UpRoF2gLaikBAABoFIaUUpRoGmgLaikBAABoG4aUUpRoHmgLaikBAABoH4aUUpRoImgLaikBAABoI4aUUpRoJmgLaikBAABoI4aU"
    "UpRoKWgLaikBAABoKoaUUpRoLWgLaikBAABoKoaUUpRoMGgLaikBAABoMYaUUpRoNGgLaikBAABoMYaUUpR1aDdqLwEAAGg4fZQo"
    "aDpHP9XCj1wo9cNoO0c/2ZmZmZmZmmg8Rz/jMzMzMzMzdXViaF9oYimBlF2UKEc/1cKPXCj1w0c/5R64UeuFH2ViaGVOdWJ1fZQo"
    "aG5otmhwaD4pgZR9lChoQWi2aEJoAimBlH2UKGgFTegDaAZ9lChoCGgLakoBAABoDIaUUpRoD2gLakoBAABoEIaUUpRoE2gLakoB"
    "AABoFIaUUpRoF2gLakoBAABoFIaUUpRoGmgLakoBAABoG4aUUpRoHmgLakoBAABoH4aUUpRoImgLakoBAABoI4aUUpRoJmgLakoB"
    "AABoI4aUUpRoKWgLakoBAABoKoaUUpRoLWgLakoBAABoKoaUUpRoMGgLakoBAABoMYaUUpRoNGgLakoBAABoMYaUUpR1aDdqUAEA"
    "AGg4fZQoaDpHP+MzMzMzMzNoO0c/5R64UeuFH2g8Rz/oo9cKPXCkdXViaF9oYimBlF2UKEc/4zMzMzMzM0c/6o9cKPXCj2ViaGVO"
    "dWJ1fZQoaG6MA01heJRocGg+KYGUfZQoaEFqaQEAAGhCaAIpgZR9lChoBU3oA2gGfZQoaAhoC2psAQAAaAyGlFKUaA9oC2psAQAA"
    "aBCGlFKUaBNoC2psAQAAaBSGlFKUaBdoC2psAQAAaBSGlFKUaBpoC2psAQAAaBuGlFKUaB5oC2psAQAAaB+GlFKUaCJoC2psAQAA"
    "aCOGlFKUaCZoC2psAQAAaCOGlFKUaCloC2psAQAAaCqGlFKUaC1oC2psAQAAaCqGlFKUaDBoC2psAQAAaDGGlFKUaDRoC2psAQAA"
    "aDGGlFKUdWg3anQBAABoOH2UKGg6Rz/oo9cKPXCkaDtHP+5mZmZmZmZ1dWJoX2hiKYGUXZQoRz/oo9cKPXCkRz/wAAAAAAAAZWJo"
    "ZU51YnVlaNd9lChob2jjagUBAABqBAEAAGiTaiYBAABotmpHAQAAamkBAABqaAEAAHVo2X2UKIwDTUlOlGjjjANMT1eUagQBAACM"
    "A01FRJRqJgEAAIwESElHSJRqRwEAAIwDTUFYlGpoAQAAdXVidJQu"
)


def test_FacadeContainsOnlyExplicitAdaptersAndHistoricalMetadata():
    """Prevent formulas and class bodies from migrating back into the facade."""

    syntax = ast.parse((PROJECT_ROOT / "fuzzyroutines" / "FuzzyRoutines.py").read_text())

    assert not any(isinstance(node, (ast.FunctionDef, ast.ClassDef)) for node in ast.walk(syntax))
    adapter_imports = [node for node in syntax.body if isinstance(node, ast.ImportFrom)]
    assert adapter_imports
    assert all(node.module.startswith("fuzzyroutines._legacy.") for node in adapter_imports)

    for name in HISTORICAL_SYMBOLS:
        assert getattr(legacy, name).__module__ == "fuzzyroutines.FuzzyRoutines"


@pytest.mark.parametrize("protocol", [0, 4, pickle.HIGHEST_PROTOCOL])
def test_NewPicklesResolveTheProtectedNamesAndBoundRegistry(protocol):
    """Protect historical callable identity across supported pickle encodings."""

    for name in HISTORICAL_SYMBOLS:
        historical_symbol = getattr(legacy, name)
        assert pickle.loads(pickle.dumps(historical_symbol, protocol=protocol)) is historical_symbol

    function = legacy.MFunction("triangle", a=0, b=2, c=1)
    restored = pickle.loads(pickle.dumps(function, protocol=protocol))
    assert type(restored) is legacy.MFunction
    assert restored.mju.__self__ is restored
    assert restored._functions["triangle"] == restored.mju
    assert restored.mju(0.5) == 0.5
    assert DeriveProperties(restored, ContinuousUniverse()).height == 1


def test_PreExtractionPickleRestoresOriginalMutableGraphAndClassIdentities():
    """Load the old implementation's bytes rather than only testing self-roundtrip."""

    function, fuzzy_set, scale, universal = pickle.loads(base64.b64decode(BASELINE_PICKLE_BASE64))

    assert tuple(type(value) for value in (function, fuzzy_set, scale, universal)) == (
        legacy.MFunction, legacy.FuzzySet, legacy.FuzzyScale, legacy.UniversalFuzzyScale,
    )
    assert function.mju.__self__ is function
    assert function.mju(0.5) == 0.5
    assert fuzzy_set.supportSet == (0.0, 1.0)
    expected_centroid = (1 - math.exp(-0.5)) / (math.sqrt(math.pi / 2) * math.erf(1 / math.sqrt(2)))
    assert fuzzy_set.Defuz() == pytest.approx(expected_centroid)
    assert scale.Fuzzy(1.0) is scale.levels[-1]
    assert universal.Fuzzy(1.0) is universal.levels[-1]
    assert universal.levelsNames["Med"] is universal.levels[2]
    assert universal.levelsNamesUpper["MED"] is universal.levels[2]
    assert universal.GetLevelByName("med", False) is universal.levels[2]
    function.parameters["c"] = 0.5
    assert function.mju(0.5) == 1
    assert Height(ScalarFuzzySet(ContinuousUniverse(), function.mju)) == 1


def test_FacadeMembershipDelegatesToTheCanonicalKernel(monkeypatch):
    """Prove the mutable adapter and modern function use one mathematical owner."""

    canonical = importlib.import_module("fuzzyroutines.membership")
    original = canonical._Triangle
    calls = []

    def RecordedTriangle(parameters, coordinate):
        """Record validated evaluations while retaining the canonical result."""

        calls.append((dict(parameters), coordinate))

        return original(parameters, coordinate)

    assert canonical._FORMULAS["Triangle"] is original
    monkeypatch.setattr(canonical, "_Triangle", RecordedTriangle)
    monkeypatch.setitem(canonical._FORMULAS, "Triangle", RecordedTriangle)
    modern = Triangle(0, 1, 2)
    historical = legacy.MFunction("triangle", a=0, b=2, c=1)
    assert modern(0.5) == historical.mju(0.5) == 0.5
    assert len(calls) == 2
    assert calls[0] == calls[1]


def test_CompatibilityScalePreservesZeroCoverageTiesAndMutableReturnIdentity():
    """Retain last-wins compatibility selection without modern no-match conversion."""

    scale = legacy.FuzzyScale()
    levels = [
        {"name": name, "fSet": legacy.FuzzySet(legacy.MFunction("triangle", a=0, b=2, c=1))}
        for name in ("first", "last")
    ]
    scale.levels = levels

    assert scale.Fuzzy(100) is levels[-1]
    assert scale.Fuzzy(1) is levels[-1]
    assert scale.GetLevelByName("LAST", False) is levels[-1]
    levels[-1]["fSet"].mFunction.parameters["c"] = 0.5
    assert scale.Fuzzy(1) is levels[0]


@pytest.mark.parametrize("coordinate", [True, math.nan, math.inf, "0.5"])
def test_CompatibilityAdapterRetainsBuiltinFiniteInputErrors(coordinate):
    """Reject malformed input before it reaches canonical membership mathematics."""

    with pytest.raises(ValueError):
        legacy.MFunction("triangle", a=0, b=2, c=1).mju(coordinate)


def test_BroadHistoricalConsumerStillRunsThroughTheFacade():
    """Execute the existing in-package consumer with its historical wildcard import."""

    completed = subprocess.run(
        [sys.executable, "-m", "fuzzyroutines.Examples"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Universal Fuzzy Scale" in completed.stdout


def test_ModernOperationsNeverLoadFacadeOrPrivateCompatibilityAdapters():
    """Block every compatibility entry point in a clean modern-core subprocess."""

    program = '''"""Exercise modern formula and numerical ownership with legacy imports blocked."""
import importlib.abc
import sys


class CompatibilityBlocker(importlib.abc.MetaPathFinder):
    """Reject facade and private compatibility adapter discovery."""

    def find_spec(self, fullname, path=None, target=None):
        """Leave unrelated imports untouched while enforcing dependency direction."""

        if fullname == "fuzzyroutines.FuzzyRoutines" or fullname.startswith("fuzzyroutines._legacy"):
            raise AssertionError("modern core must not load any compatibility adapter")

        return None


sys.meta_path.insert(0, CompatibilityBlocker())
from fuzzyroutines import Centroid, ContinuousUniverse, DeriveProperties, Height, IntegrationDomain, ScalarFuzzySet
from fuzzyroutines.membership import Triangle
from fuzzyroutines.operators import TNormPolicy
function = Triangle(0, 1, 2)
universe = ContinuousUniverse()
fuzzy_set = ScalarFuzzySet(universe, function)
assert Height(fuzzy_set) == DeriveProperties(function, universe).height == 1
assert Centroid(fuzzy_set, IntegrationDomain(0, 2)) == 1
assert TNormPolicy("algebraic").Evaluate(0.5, 0.5) == 0.25
'''
    completed = subprocess.run(
        [sys.executable, "-c", program],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr

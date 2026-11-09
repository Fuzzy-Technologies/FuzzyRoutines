# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Smoke-test verified wheel and sdist installs on the active OS and Python.

Each probe runs in a fresh virtual environment outside the checkout, with
spaces and non-ASCII characters in the artifact, interpreter and working paths.
The wheel and sdist are installed as an ordinary consumer would install them;
the NumPy extra gets its own environment. Usage after a reproducible build:

    python tools/verify_installed_platform.py --artifacts dist --output smoke.json
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import sysconfig
import tomllib
import venv
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory


def VerifiedArtifacts(directory, revision):
    """Require both distributions, the expected source revision and matching hashes."""

    if (directory / "source-revision.txt").read_text(encoding="utf-8").strip() != revision:
        raise ValueError("Distributions were built from a different Git revision")

    manifest = (directory / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    checksums = {name: digest for digest, name in (line.split("  ", 1) for line in manifest)}

    if len(manifest) != 2 or len(checksums) != 2:
        raise ValueError("Expected one checksum per distribution")

    artifacts = {}

    for kind, pattern in (("wheel", "*.whl"), ("sdist", "*.tar.gz")):
        paths = tuple(directory.glob(pattern))

        if len(paths) != 1:
            raise ValueError(f"Expected exactly one {kind} in {directory}")

        artifact = paths[0]
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()

        if checksums.get(artifact.name) != digest:
            raise ValueError(f"Distribution hash mismatch: {artifact.name}")

        artifacts[kind] = (artifact, digest)

    return artifacts


def ProbeHistoricalScale():
    """Check all five historical winners and the modern-to-legacy confidence parity."""

    from fuzzyroutines import CreateUniversalFuzzyScale, UniversalFuzzyScalePolicy
    from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale

    modern = CreateUniversalFuzzyScale()
    legacy = UniversalFuzzyScale()
    policy = UniversalFuzzyScalePolicy()
    winners = []

    references = ((0, "Min", 1), (0.2, "Low", 0.5), (0.5, "Med", 1), (0.7, "High", 1), (1, "Max", 1))

    for coordinate, term, confidence in references:
        result = modern.Fuzzify(coordinate, policy)
        winner = legacy.Fuzzy(coordinate)
        grade = winner["fSet"].mFunction.mju(coordinate)

        assert [item.name for item in result.selectedTerms] == [term], f"Modern historical winner changed at {coordinate}"
        assert winner["name"] == term, f"Legacy historical winner changed at {coordinate}"
        assert result.confidence == grade, f"Modern and legacy confidence differ at {coordinate}"
        assert math.isclose(result.confidence, confidence, rel_tol=0, abs_tol=1e-12), (
            f"Historical confidence changed at {coordinate}"
        )
        winners.append(term)

    return winners


def ProbeInference():
    """Evaluate the analytical two-rule examples from ADR-0017."""

    from fuzzyroutines import (
        ContinuousUniverse,
        IntegrationDomain,
        LinguisticTerm,
        NegationPolicy,
        ScalarFuzzySet,
        SNormPolicy,
        TNormPolicy,
    )
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

    def Low(coordinate):
        """Return the decreasing unit ramp."""

        return 1 - coordinate

    unit = ContinuousUniverse(0, 1, True, True)
    terms = (LinguisticTerm("low", ScalarFuzzySet(unit, Low)), LinguisticTerm("high", ScalarFuzzySet(unit, float)))
    inputs = (FuzzyVariable("risk", terms),)
    low, high = TermCondition("risk", "low"), TermCondition("risk", "high")
    conjunction, disjunction = TNormPolicy("logic"), SNormPolicy("logic")
    policy = InferencePolicy(conjunction, disjunction, NegationPolicy("standard"))
    coordinates = {"risk": 0.25}
    mamdani = MamdaniModel(inputs, FuzzyVariable("response", terms), (
        MamdaniRule("low", low, "low"), MamdaniRule("high", high, "high"),
    ), policy, conjunction, disjunction).Evaluate(coordinates, IntegrationDomain(0, 1))
    sugeno = SugenoModel(inputs, (
        SugenoRule("low", low, ConstantConsequent(0.2)), SugenoRule("high", high, ConstantConsequent(0.8)),
    ), policy, unit).Evaluate(coordinates)

    assert math.isclose(mamdani.value, 37 / 96, rel_tol=0, abs_tol=1e-12), (
        "Mamdani centroid differs from the analytical reference"
    )
    assert math.isclose(sugeno.value, 7 / 20, rel_tol=0, abs_tol=1e-12), (
        "Sugeno average differs from the analytical reference"
    )

    return {"mamdani": mamdani.value, "sugeno": sugeno.value}


def ProbeNumpy(expected):
    """Check optional imports, explicit missing-extra guidance and array execution."""

    from fuzzyroutines import CreateUniversalFuzzyScale, Gaussian
    from fuzzyroutines.batches import EvaluateMembershipBatch, FuzzifyBatch

    assert "numpy" not in sys.modules, "Importing the core or batch API eagerly imported NumPy"
    present = importlib.util.find_spec("numpy") is not None
    assert present == bool(expected), "NumPy availability disagrees with the requested installation"

    if not expected:
        operations = (
            (EvaluateMembershipBatch, Gaussian(0, 1), [0, 1]),
            (FuzzifyBatch, CreateUniversalFuzzyScale(), [0.2]),
        )

        for operation, membership, coordinates in operations:
            try:
                operation(membership, coordinates)

            except ImportError as error:
                assert "fuzzyroutines[numpy]" in str(error), "Missing NumPy error lacks extra installation guidance"

            else:
                raise AssertionError("Batch execution succeeded without NumPy")

        return None

    import numpy

    assert numpy.__version__ == expected, "The installed NumPy version differs from the requested baseline"
    grades = EvaluateMembershipBatch(Gaussian(0, 1), [0, 1])
    numpy.testing.assert_allclose(grades, [1, math.exp(-0.5)], rtol=0, atol=1e-12)
    scale = FuzzifyBatch(CreateUniversalFuzzyScale(), [0.2])
    assert scale.selected.tolist() == [[False, True, False, False, False]], "NumPy batch disagrees with the historical Low winner"

    return numpy.__version__


def Probe(expected, extra):
    """Prove consumer paths and installed origin before testing public behavior."""

    import fuzzyroutines

    workdir = Path.cwd()
    prefix = Path(sys.prefix).resolve()
    origin = Path(fuzzyroutines.__file__).resolve()
    purelib = Path(sysconfig.get_path("purelib")).resolve()
    assert " " in str(workdir) and not str(workdir).isascii(), "Consumer path must exercise spaces and Unicode"
    assert prefix == (workdir / "venv").resolve(), "Consumer is not using the fresh virtual environment"
    assert origin.is_relative_to(purelib) and purelib.is_relative_to(prefix), (
        "Core import escaped the installed site-packages"
    )
    assert version("fuzzyroutines") == expected, "Installed metadata differs from pyproject.toml"

    return {
        "working_directory": str(workdir),
        "package_origin": str(origin),
        "package_version": expected,
        "historical_winners": ProbeHistoricalScale(),
        "inference": ProbeInference(),
        "numpy": ProbeNumpy(extra),
    }


def InstallAndProbe(directory, artifact, release, extra=""):
    """Install a local distribution and execute the copied probe in isolated mode."""

    directory.mkdir()
    distribution = directory / artifact.name
    shutil.copyfile(artifact, distribution)
    probe = directory / "probe.py"
    shutil.copyfile(__file__, probe)
    environment = directory / "venv"
    venv.EnvBuilder(with_pip=True).create(environment)
    interpreter = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    requirements = [str(distribution)]

    if extra:
        constraints = directory / "constraints.txt"
        constraints.write_text(f"numpy=={extra}\n", encoding="utf-8")
        requirements = ["--constraint", str(constraints), "--only-binary=:all:", f"fuzzyroutines[numpy] @ {distribution.as_uri()}"]

    pip = [str(interpreter), "-I", "-m", "pip", "--disable-pip-version-check"]
    subprocess.run([*pip, "install", "--no-cache-dir", *requirements], cwd=directory, check=True)
    subprocess.run([*pip, "check"], cwd=directory, check=True)
    report = subprocess.check_output(
        [str(interpreter), "-I", str(probe), "--probe", release, extra],
        cwd=directory, encoding="utf-8",
    )

    return json.loads(report)


def Main():
    """Run the three consumer cases and write evidence only after all pass."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--numpy-version", default="2.3.5")
    parser.add_argument("--probe", nargs=2, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.probe:
        print(json.dumps(Probe(*args.probe)))

        return

    if args.artifacts is None or args.output is None or not args.numpy_version:
        parser.error("--artifacts, --output and a nonempty NumPy version are required")

    checkout = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, encoding="ascii").strip()
    artifacts = VerifiedArtifacts(args.artifacts.resolve(), revision)
    project = tomllib.loads((checkout / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    cases = {}

    with TemporaryDirectory(prefix="fuzzy install \N{GREEK CAPITAL LETTER OMEGA} ") as directory:
        consumer = Path(directory).resolve()

        if consumer.is_relative_to(checkout):
            raise ValueError("The temporary consumer directory must be outside the source checkout")

        scenarios = (("wheel", "wheel", ""), ("sdist", "sdist", ""), ("wheel-numpy", "wheel", args.numpy_version))

        for case, kind, extra in scenarios:
            artifact, digest = artifacts[kind]
            print(f"Installed distribution smoke: {case}", flush=True)
            result = InstallAndProbe(consumer / case, artifact, project["version"], extra)
            cases[case] = {"artifact": artifact.name, "sha256": digest, **result}

    report = json.dumps({
        "source_revision": revision, "platform": platform.platform(), "python": sys.version,
        "cases": cases,
    }, indent=2, sort_keys=True)
    args.output.write_text(report + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    Main()

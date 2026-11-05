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
        legacy_winner = legacy.Fuzzy(coordinate)
        legacy_grade = legacy_winner["fSet"].mFunction.mju(coordinate)

        assert [item.name for item in result.selectedTerms] == [term], f"Modern historical winner changed at {coordinate}"
        assert legacy_winner["name"] == term, f"Legacy historical winner changed at {coordinate}"
        assert result.confidence == legacy_grade, f"Modern and legacy confidence differ at {coordinate}"
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


def ProbeNumpy(expected_version):
    """Check optional imports, explicit missing-extra guidance and array execution."""

    from fuzzyroutines import CreateUniversalFuzzyScale, Gaussian
    from fuzzyroutines.batches import EvaluateMembershipBatch, FuzzifyBatch

    assert "numpy" not in sys.modules, "Importing the core or batch API eagerly imported NumPy"
    numpy_present = importlib.util.find_spec("numpy") is not None
    assert numpy_present == bool(expected_version), "NumPy availability disagrees with the requested installation"

    if not expected_version:
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

    assert numpy.__version__ == expected_version, "The installed NumPy version differs from the requested baseline"
    grades = EvaluateMembershipBatch(Gaussian(0, 1), [0, 1])
    numpy.testing.assert_allclose(grades, [1, math.exp(-0.5)], rtol=0, atol=1e-12)
    scale = FuzzifyBatch(CreateUniversalFuzzyScale(), [0.2])
    assert scale.selected.tolist() == [[False, True, False, False, False]], "NumPy batch disagrees with the historical Low winner"

    return numpy.__version__


def Probe(expected_version, numpy_version):
    """Prove consumer paths and installed origin before testing public behavior."""

    import fuzzyroutines

    work_path = Path.cwd()
    prefix = Path(sys.prefix).resolve()
    package_path = Path(fuzzyroutines.__file__).resolve()
    site_packages = Path(sysconfig.get_path("purelib")).resolve()
    assert " " in str(work_path) and not str(work_path).isascii(), "Consumer path must exercise spaces and Unicode"
    assert prefix == (work_path / "venv").resolve(), "Consumer is not using the fresh virtual environment"
    assert package_path.is_relative_to(site_packages) and site_packages.is_relative_to(prefix), (
        "Core import escaped the installed site-packages"
    )
    assert version("fuzzyroutines") == expected_version, "Installed metadata differs from pyproject.toml"

    return {
        "working_directory": str(work_path),
        "package_origin": str(package_path),
        "package_version": expected_version,
        "historical_winners": ProbeHistoricalScale(),
        "inference": ProbeInference(),
        "numpy": ProbeNumpy(numpy_version),
    }


def InstallAndProbe(case_path, artifact, package_version, numpy_version=""):
    """Install a local distribution and execute the copied probe in isolated mode."""

    case_path.mkdir()
    distribution = case_path / artifact.name
    shutil.copyfile(artifact, distribution)
    probe_path = case_path / "probe.py"
    shutil.copyfile(__file__, probe_path)
    environment = case_path / "venv"
    venv.EnvBuilder(with_pip=True).create(environment)
    interpreter = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    requirements = [str(distribution)]

    if numpy_version:
        constraints = case_path / "constraints.txt"
        constraints.write_text(f"numpy=={numpy_version}\n", encoding="utf-8")
        requirements = ["--constraint", str(constraints), "--only-binary=:all:", f"fuzzyroutines[numpy] @ {distribution.as_uri()}"]

    pip = [str(interpreter), "-I", "-m", "pip", "--disable-pip-version-check"]
    subprocess.run([*pip, "install", "--no-cache-dir", *requirements], cwd=case_path, check=True)
    subprocess.run([*pip, "check"], cwd=case_path, check=True)
    report = subprocess.check_output(
        [str(interpreter), "-I", str(probe_path), "--probe", package_version, numpy_version],
        cwd=case_path, encoding="utf-8",
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

    source_root = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source_root, encoding="ascii").strip()
    artifacts = VerifiedArtifacts(args.artifacts.resolve(), revision)
    project = tomllib.loads((source_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    cases = {}

    with TemporaryDirectory(prefix="fuzzy install \N{GREEK CAPITAL LETTER OMEGA} ") as directory:
        consumer_root = Path(directory).resolve()

        if consumer_root.is_relative_to(source_root):
            raise ValueError("The temporary consumer directory must be outside the source checkout")

        case_specs = (("wheel", "wheel", ""), ("sdist", "sdist", ""), ("wheel-numpy", "wheel", args.numpy_version))

        for case, kind, numpy_version in case_specs:
            artifact, digest = artifacts[kind]
            print(f"Installed distribution smoke: {case}", flush=True)
            result = InstallAndProbe(consumer_root / case, artifact, project["version"], numpy_version)
            cases[case] = {"artifact": artifact.name, "sha256": digest, **result}

    report = json.dumps({
        "source_revision": revision, "platform": platform.platform(), "python": sys.version,
        "cases": cases,
    }, indent=2, sort_keys=True)
    args.output.write_text(report + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    Main()

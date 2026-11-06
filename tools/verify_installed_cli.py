# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Probe the installed calculator from a temporary directory outside the checkout."""

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Sequence
from importlib.metadata import distribution
from pathlib import Path
from tempfile import TemporaryDirectory


def _Record(payload: bytes) -> dict[str, object]:
    """Require exactly one sorted JSON object followed by LF."""

    record = json.loads(payload)
    assert isinstance(record, dict), "The calculator must return an object."
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False)
    assert payload == (canonical + "\n").encode("utf-8"), "Machine output must be deterministic UTF-8."
    assert record.get("resultVersion") == 1, "The calculator must report the v1 result format."

    return record


def _CheckFailure(result: subprocess.CompletedProcess[bytes], code: int, category: str) -> dict[str, object]:
    """Require the declared diagnostic on stderr and no partial stdout."""

    assert (result.returncode, result.stdout) == (code, b""), (
        f"Expected {category} exit {code}, got {result.returncode}: {result.stdout!r} {result.stderr!r}"
    )
    error = _Record(result.stderr)["error"]
    assert isinstance(error, dict) and error.get("category") == category, "The diagnostic category must match its exit."

    return error


def Main(arguments: Sequence[str] | None = None) -> int:
    """Check one clean wheel environment, with or without the configuration extra."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expect-config", dest="expectConfig", action="store_true", help="exercise commands using the real validator",
    )
    options = parser.parse_args(arguments)

    installed = distribution("fuzzyroutines")
    installedRoot = Path(str(installed.locate_file(""))).resolve()
    assert installedRoot.is_relative_to(Path(sys.prefix).resolve()), "The distribution must be in the active environment."
    executable = Path(sys.executable).with_name("fuzzyroutines.exe" if os.name == "nt" else "fuzzyroutines")
    assert executable.is_file(), "The wheel must install the calculator entry point."
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONUTF8"] = "1"
    fixtureRoot = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "config-v1" / "fixtures"

    with TemporaryDirectory(prefix="fuzzyroutines-cli-") as directory:
        work = Path(directory)

        def Run(*command: str) -> subprocess.CompletedProcess[bytes]:
            """Invoke the console script without source import overrides."""

            return subprocess.run(
                (executable, *command), cwd=work, env=environment, capture_output=True, timeout=15, check=False,
            )

        helpResult = Run("--help")
        assert (helpResult.returncode, helpResult.stderr) == (0, b""), "Help must succeed without a diagnostic."
        assert b"usage: fuzzyroutines" in helpResult.stdout, "Help must describe the installed command."
        versionResult = Run("--version")
        assert (versionResult.returncode, versionResult.stdout, versionResult.stderr) == (
            0, f"fuzzyroutines {installed.version}\n".encode("ascii"), b"",
        ), "The console version must match the installed distribution."

        scalePath = work / "историческая шкала α.json"
        scalePath.write_bytes((fixtureRoot / "valid-historical-scale.json").read_bytes())

        if not options.expectConfig:
            error = _CheckFailure(Run("validate", "--project", scalePath.name), 6, "capability")
            assert "fuzzyroutines[config]" in str(error.get("message")), "Missing config must have installation guidance."

            return 0

        command = ("membership", "--project", scalePath.name, "--scale", "universal", "--term", "high", "--x", "0.75")
        result = Run(*command)
        assert (result.returncode, result.stderr) == (0, b""), f"Installed historical membership failed: {result.stderr!r}"
        assert _Record(result.stdout) == {
            "command": "membership",
            "result": {"coordinate": 0.75, "grade": 1.0, "scale": "universal", "term": "high"},
            "resultVersion": 1,
        }, "The historical fixture must retain its wire IDs and scalar grade."
        assert Run(*command).stdout == result.stdout, "Repeated invocations must produce the same bytes."

        model = json.loads((fixtureRoot / "valid-project.json").read_bytes())["models"]["weighted"]

        for rule in model["inference"]["rules"]:
            rule["weight"] = 0

        modelPath = work / "правила β.json"
        modelPath.write_text(json.dumps(model), encoding="utf-8")
        _CheckFailure(Run("infer", "--project", modelPath.name, "--input", "risk=0.25"), 4, "evaluation")

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())

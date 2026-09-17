"""Executable evidence for the historical-to-modern migration guide."""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECTROOT = Path(__file__).resolve().parents[1]
EXAMPLEROOT = PROJECTROOT / "examples" / "migration"


def _RunExample(exampleName, workingDirectory):
    """Run an example away from the source root through the active install."""

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    installedProbe = subprocess.run(
        [sys.executable, "-c", "import fuzzyroutines"],
        cwd=workingDirectory,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        env=environment,
    )

    # Package-build validation provides a clean installation. The source-tree
    # runner intentionally has no installation, so retain a deterministic
    # fallback without making the user examples modify sys.path themselves.
    if installedProbe.returncode != 0:
        environment["PYTHONPATH"] = str(PROJECTROOT)

    result = subprocess.run(
        [sys.executable, str(EXAMPLEROOT / exampleName)],
        cwd=workingDirectory,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        env=environment,
    )

    assert result.returncode == 0, (
        f"{exampleName} must run through the installed package.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    return json.loads(result.stdout)


def test_HistoricalCompatibilityExampleCoversEveryMigrationArea(tmp_path):
    """Keep all five protected historical paths executable together."""

    result = _RunExample("historical_compatibility.py", tmp_path)

    assert set(result) == {
        "defuzzification",
        "fuzzySet",
        "membership",
        "operator",
        "scale",
    }
    assert result["fuzzySet"] == {
        "name": "Medium",
        "supportSet": [0.0, 1.0],
    }
    assert result["membership"] == 1.0
    assert result["operator"] == 0.27999999999999997
    assert result["scale"] == "Med"
    assert abs(result["defuzzification"] - 0.5) < 1e-12


def test_ModernSupportedExampleDoesNotDependOnFutureApis(tmp_path):
    """Exercise only modern paths already exported by the installed package."""

    result = _RunExample("modern_supported.py", tmp_path)

    assert result == {
        "fuzzySet": 0.5,
        "integrationDomain": [0.0, 1.0],
        "membership": 1.0,
        "operator": 0.27999999999999997,
        "overlap": 0.5,
    }

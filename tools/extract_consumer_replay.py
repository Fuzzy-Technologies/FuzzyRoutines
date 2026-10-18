# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Extract pinned public consumer test literals without importing consumer code.

Both source files must match the recorded upstream bytes. Only ``ast.literal_eval``
reads test inputs and independent expected results. The small normalization step
below follows the pinned scalar consumer boundary; no trading engine runs.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests/fixtures/public_consumer_batches.json"
REVISION = "b963c54039f013d432220186ae35a22359c5a773"
SOURCE_SHA256 = "923981bb13302942c571c98133b50d97b2830b2fbdbb0873d64fc56cf951616e"
TEST_SHA256 = "69efddf14b3d3d7031aed90c6e6db0700fbc6c2796648ed3bb8818b12e64ddea"


def _VerifiedText(path, expected):
    """Reject a different upstream revision before interpreting any literals."""

    data = path.read_bytes()

    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"source bytes do not match the pinned consumer revision: {path}")

    return data.decode("utf-8")


def _RiskCoordinate(current, highest, lowest, direction):
    """Apply the pinned clipping, zero-width rule and directional distance."""

    if highest < lowest:
        raise ValueError("the positive replay cannot contain a reversed price range")

    current = min(highest, max(lowest, current))
    width = abs(highest - lowest) if highest != lowest else 1
    endpoint = lowest if direction == "long" else highest

    return abs(current - endpoint) / width


def BuildFixture(sourcePath, testPath):
    """Preserve ordered public inputs and expected labels/rounded percentages."""

    _VerifiedText(sourcePath, SOURCE_SHA256)
    module = ast.parse(_VerifiedText(testPath, TEST_SHA256))
    replays = []

    for direction, count in (("long", 17), ("short", 13)):
        function = "Risk" + direction.title()
        testName = f"test_{function}Positive"
        node = next(item for item in ast.walk(module) if isinstance(item, ast.FunctionDef) and item.name == testName)
        assignment = next(item for item in node.body if isinstance(item, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "testData" for target in item.targets
        ))
        data = ast.literal_eval(assignment.value)

        if len(data) != count:
            raise ValueError("the pinned public replay case count changed")

        coordinates = []
        cases = []

        for current, highest, lowest, expected in data:
            coordinate = _RiskCoordinate(current, highest, lowest, direction)

            if round(100 * coordinate, 4) != expected["riskPercent"]:
                raise ValueError("derived coordinate contradicts the upstream expected percentage")

            coordinates.append(coordinate)
            cases.append({"prices": {"current": current, "highest": highest, "lowest": lowest},
                          "expected_label": expected["riskFuzzy"],
                          "expected_percent_rounded_4": expected["riskPercent"]})

        replays.append({"name": f"tksbrokerapi_risk_{direction}", "function": function,
                        "test": testName, "test_lines": [node.lineno, node.end_lineno],
                        "coordinates": coordinates, "cases": cases})

    return {"schema_version": 1, "license": "SPDX-License-Identifier: Apache-2.0",
            "attribution": "Public TKSBrokerAPI test inputs and expected results by Timur Gilmullin; extracted and normalized for FuzzyRoutines replay, original order retained.",
            "source": {"repository": "Fuzzy-Technologies/TKSBrokerAPI", "revision": REVISION,
                       "source_path": "tksbrokerapi/TradeRoutines.py", "source_sha256": SOURCE_SHA256,
                       "source_git_blob": "012caf30a61daf79117f95ee880c4d224213e103",
                       "test_path": "tests/test_TradeRoutines.py", "test_sha256": TEST_SHA256,
                       "test_git_blob": "0a09fc3e30fe7182320fb776979d4b704e81fe0f",
                       "license_path": "LICENSE", "license_git_blob": "2bb9ad240fa04c8cf706a4901c4807878e90c2dc"},
            "scope": "Public positive-test replay groups, not observed production batches. Each original consumer invocation classifies one coordinate. Price normalization is performed before the timed fuzzy operation.",
            "replays": replays}


def Main(arguments=None):
    """Write or verify the reproducible fixture from two already-downloaded files."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--tests", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args(arguments)
    fixture = BuildFixture(options.source, options.tests)
    encoded = json.dumps(fixture, indent=2, sort_keys=True) + "\n"

    if options.check:
        if not options.output.is_file() or options.output.read_text(encoding="utf-8") != encoded:
            raise RuntimeError("public consumer replay fixture is stale or missing")

    else:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(encoded, encoding="utf-8")

    print(json.dumps({"checked": options.check, "cases": {case["name"]: len(case["coordinates"]) for case in fixture["replays"]}}))


if __name__ == "__main__":
    Main()

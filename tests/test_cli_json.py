# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Check the standalone calculator's wire IDs and command-line streams."""

import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from fuzzyroutines._cli import Main

_FIXTURES = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "config-v1" / "fixtures"


def _Run(*arguments: str) -> tuple[int, str, str]:
    """Capture the CLI's exit code and its independently routed streams."""

    stdout, stderr = StringIO(), StringIO()

    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = Main(arguments)

    return code, stdout.getvalue(), stderr.getvalue()


class StandaloneCalculatorTests(TestCase):
    """Exercise CLI orchestration around known codec fixtures and failures."""

    def test_HelpAndVersionArePlainTextWithoutConfiguration(self) -> None:
        """Keep plain text informational and free from required extras."""

        for option, prefix in (("--help", "usage: fuzzyroutines"), ("--version", "fuzzyroutines ")):
            code, stdout, stderr = _Run(option)
            self.assertEqual((code, stderr), (0, ""), "Informational commands must succeed silently on stderr.")
            self.assertTrue(stdout.startswith(prefix), "Informational output must be plain text.")

    def test_ValidationAndHistoricalScaleKeepWireIds(self) -> None:
        """Round-trip Unicode paths and historical term ordering through the CLI."""

        with TemporaryDirectory() as directory:
            path = Path(directory) / "шкала α.json"
            path.write_bytes((_FIXTURES / "valid-historical-scale.json").read_bytes())

            # Codec schema validation is independently tested with the optional
            # extra. This dispatch test retains real parsing and scalar evaluation.
            with patch("fuzzyroutines.configuration.CheckConfigStructure"):
                arguments = ("--project", str(path))
                code, stdout, stderr = _Run("validate", *arguments)
                self.assertEqual((code, stderr), (0, ""), "Valid standalone JSON must validate.")
                self.assertEqual(stdout, '{"command":"validate","result":{"kind":"model","schemaVersion":1},"resultVersion":1}\n')
                code, stdout, stderr = _Run(
                    "membership", *arguments, "--scale", "universal", "--term", "high", "--x", "0.75",
                )
                self.assertEqual((code, stderr), (0, ""), "Historical membership must evaluate.")
                self.assertEqual(json.loads(stdout)["result"], {
                    "coordinate": 0.75, "grade": 1.0, "scale": "universal", "term": "high",
                })
                code, stdout, stderr = _Run("fuzzify", *arguments, "--scale", "universal", "--x", "0.75")
                self.assertEqual((code, stderr), (0, ""), "Historical fuzzification must succeed.")
                result = json.loads(stdout)["result"]
                self.assertEqual([item["term"] for item in result["memberships"]], ["min", "low", "med", "high", "max"])
                self.assertEqual((result["match"], result["selectedTerms"]), (True, ["high"]))

    def test_StandaloneInferencePreservesTracesAndNoFiring(self) -> None:
        """Retain external IDs and report zero firing on the evaluation stream."""

        project = json.loads((_FIXTURES / "valid-project.json").read_bytes())

        with TemporaryDirectory() as directory, patch("fuzzyroutines.configuration.CheckConfigStructure"):
            for name, expected, ruleIds in (
                ("weighted", 0.296875, ["base", "increase"]), ("centroid", 0.5, ["respond"]),
            ):
                model = project["models"][name]
                path = Path(directory) / "model.json"
                path.write_text(json.dumps(model), encoding="utf-8")
                arguments = ("infer", "--project", str(path), "--input", "risk=0.25")
                code, stdout, stderr = _Run(*arguments, "--explain")
                self.assertEqual((code, stderr), (0, ""), "Both scalar rule engines must evaluate.")
                result = json.loads(stdout)["result"]
                self.assertAlmostEqual(result["value"], expected)
                self.assertEqual([row["rule"] for row in result["trace"]["rules"]], ruleIds)
                self.assertEqual(result["trace"]["inputGrades"][0]["input"], "risk")
                self.assertNotIn("trace", json.loads(_Run(*arguments)[1])["result"])

                for rule in model["inference"]["rules"]:
                    rule["weight"] = 0

                path.write_text(json.dumps(model), encoding="utf-8")
                code, stdout, stderr = _Run(*arguments)
                self.assertEqual((code, stdout), (4, ""), "Zero firing must not emit a partial result.")
                self.assertEqual(json.loads(stderr)["error"]["category"], "evaluation")

    def test_UsagePrecedesIoAndCodecErrorsKeepPointers(self) -> None:
        """Distinguish syntax, file access and malformed configuration failures."""

        for token in ("+1", "01", "1e-999", "1e999", "NaN", " 1"):
            code, stdout, stderr = _Run("membership", "--project", "absent.json", "--scale", "s", "--term", "t", "--x", token)
            self.assertEqual((code, stdout), (2, ""), f"{token!r} must fail before file access.")
            self.assertEqual(json.loads(stderr)["error"]["category"], "usage")

        code, stdout, stderr = _Run("fuzzify", "--project", "absent.json", "--scale", "s", "--x", "-1e-2")
        self.assertEqual((code, stdout), (5, ""), "A valid negative exponent must reach file access.")
        self.assertEqual(json.loads(stderr)["error"]["category"], "io")

        with TemporaryDirectory() as directory:
            path = Path(directory) / "malformed.json"
            path.write_bytes(b'{"kind":"model","kind":"model"}')
            code, stdout, stderr = _Run("validate", "--project", str(path))

        self.assertEqual((code, stdout), (3, ""), "Malformed JSON must report configuration failure.")
        error = json.loads(stderr)["error"]
        self.assertEqual((error["category"], error["detailCategory"], error["pointer"]),
                         ("configuration", "malformed-document", "/kind"))

    def test_OptionalCodecFailureIsReportedAsCapability(self) -> None:
        """Use a stable capability diagnostic when the lazy validator is absent."""

        with patch("fuzzyroutines._cli.LoadModel", side_effect=ImportError("Install fuzzyroutines[config].")):
            code, stdout, stderr = _Run("validate", "--project", str(_FIXTURES / "valid-historical-scale.json"))

        self.assertEqual((code, stdout), (6, ""), "Missing optional validation must not leak a traceback.")
        self.assertEqual(json.loads(stderr)["error"]["category"], "capability")

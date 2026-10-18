# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Render an explicitly unmeasured draft or verified comparison JSON to Markdown."""

import argparse
import importlib.util
import json
import math
from pathlib import Path


def LoadRunner():
    """Read plan/statistics helpers without importing any benchmark package."""

    spec = importlib.util.spec_from_file_location("comparison_runner", Path(__file__).resolve().parents[1] / "experiments/benchmark_installed_scalar.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)

    return runner


def Table(rows):
    """Align Markdown columns without changing their contents."""

    widths = [max(len(row[index]) for row in rows) for index in range(len(rows[0]))]
    formatted = ["| " + " | ".join(value.ljust(width) for value, width in zip(row, widths)) + " |" for row in rows]
    formatted.insert(1, "| " + " | ".join("-" * width for width in widths) + " |")

    return "\n".join(formatted)


def VerifyReport(report, runner):
    """Reject incomplete evidence or inconsistent derived timing statistics."""

    if report["kind"] != "installed-wheel-comparison" or not report["parity_passed"]:
        raise ValueError("require a successful installed-wheel parity report")

    if set(report["results"]) != set(runner.WorkloadNames()):
        raise ValueError("comparison workload set differs from the fixed plan")

    if len(report["rounds"]) != report["configuration"]["repeats"]:
        raise ValueError("raw paired-round count differs from the declared repeats")

    for name, result in report["results"].items():
        for label in runner.LABELS:
            values = result[label]["raw_samples"]

            if len(values) < 7 or len(values) != report["configuration"]["repeats"] or any(not math.isfinite(value) or value <= 0 for value in values):
                raise ValueError(f"invalid samples: {name}/{label}")

            observed = [item["artifacts"][label] for item in report["rounds"]]
            recorded = []

            for item in observed:
                if name in ("process_startup", "package_import"):
                    recorded.append(item[name + "_ns"])
                    continue

                operation = item["results"][name]
                elapsed = operation["raw_elapsed_ns"]
                iterations = operation["iterations"]
                units = operation["units_per_iteration"]

                if any(type(value) is not int or value <= 0 for value in (elapsed, iterations, units)):
                    raise ValueError(f"invalid positive elapsed time or operation counts: {name}/{label}")

                group = next((prefix + "_" + name.rsplit("_", 1)[1] for prefix in ("scale", "fuzzyset") if name.startswith(prefix + "_")), "scalar")
                expectedUnits = 100 if name.endswith("_lookup") else 1

                if iterations != report["configuration"]["iterations"][group] or units != expectedUnits:
                    raise ValueError(f"worker operation counts differ from the declared workload: {name}/{label}")

                rate = elapsed / iterations / units

                if operation["ns_per_unit"] != rate:
                    raise ValueError(f"worker rate differs from raw elapsed time and operation counts: {name}/{label}")

                recorded.append(rate)

            if values != recorded:
                raise ValueError(f"summary samples differ from the recorded worker results: {name}/{label}")

            if runner.Summary(values) != result[label]:
                raise ValueError(f"derived statistics differ from raw samples: {name}/{label}")

        ratio = result["baseline"]["median"] / result["candidate"]["median"]

        if ratio != result["baseline_over_candidate"]:
            raise ValueError(f"derived median ratio differs: {name}")


def Render(config, report, runner):
    """Keep artifacts, numerical gates, and operation classes explicit."""

    measured = report is not None
    artifacts = report["artifacts"] if measured else {label: config[label] for label in runner.LABELS}
    lines = ["<!--", "SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies", "SPDX-License-Identifier: Apache-2.0", "-->", "",
             "# Installed FuzzyRoutines comparison", "",
             "Measured installed-wheel evidence; independent parity passed." if measured else "DRAFT — NOT MEASURED. Artifact fields and all timing cells remain pending.", "",
             "Times are microseconds per operation (scale lookup: per single lookup). Each timing cell is median / minimum / IQR; ratio is baseline median divided by candidate median.", ""]

    for label in runner.LABELS:
        artifact = artifacts[label]
        lines.extend([f"- {label.title()}: version `{artifact['version'] or 'pending'}`; wheel SHA256 `{artifact['wheel_sha256'] or 'pending'}`; package source commit `{artifact['source_commit'] or 'pending'}`."])

    lines.extend([f"- Wrapper source commit: `{config['harness_commit'] or 'pending'}`; workload source commit: `{config['workload_commit']}`. Both are separate from installed package commits.",
                  f"- Samples: {config['repeats']} per artifact, alternating paired process order; warmups: {config['warmups']} per operation per worker.", ""])

    if measured:
        environment = report["environment"]
        lines.extend([f"Environment: {environment['python'].splitlines()[0]}; {environment['platform']}; {environment['processor']}.",
                      f"Runner SHA256: `{report['harness']['runner_sha256']}`; immutable harness snapshot dirty state: `{report['harness']['snapshot_dirty']}`.", ""])

    groups = [
        ("Process startup and package import", lambda name: name in ("process_startup", "package_import")),
        ("Membership evaluation", lambda name: name.startswith("membership_")),
        ("Operator evaluation", lambda name: name.startswith(("tnorm_", "sconorm_"))),
        ("Scale construction", lambda name: name.startswith("scale_") and name.endswith("_construction")),
        ("Scale lookup", lambda name: name.startswith("scale_") and name.endswith("_lookup")),
        ("Fuzzy-set construction", lambda name: name.startswith("fuzzyset_") and name.endswith("_construction")),
        ("Centroid recalculation", lambda name: name.endswith("_centroid")),
    ]

    for heading, selected in groups:
        rows = [["Workload", "2.0.0 median / min / IQR (µs)", "Candidate median / min / IQR (µs)", "Baseline / candidate"]]

        for name in filter(selected, runner.WorkloadNames()):
            if measured:
                result = report["results"][name]
                cells = [" / ".join(f"{result[label][statistic] / 1000:.6f}" for statistic in ("median", "minimum", "interquartile_range")) for label in runner.LABELS]
                rows.append([name, *cells, f"{result['baseline_over_candidate']:.3f}×"])

            else:
                rows.append([name, "not measured", "not measured", "not measured"])

        lines.extend(["## " + heading, "", Table(rows), ""])

    lines.extend(["Independent parity precedes timing: analytical membership/operator references (absolute 1e-12), exact scale term order and midpoint lookup, closed-form centroids over [0, 1] (absolute 1e-10), and cross-version observations. Relative tolerance is zero.", "",
                  "Interpretation is limited to these fixed workloads on this host. There is no timing pass/fail threshold. Imports use fresh processes but a warm filesystem cache; startup includes subprocess launch/teardown. Operation timings exclude tracemalloc. Scale lookup retains the existing counting instrumentation. Optional NumPy and other runtime extras are not installed.", ""])

    return "\n".join(lines)


def Main():
    """Generate no timing measurements; require one explicit report destination."""

    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--draft", type=Path, help="config JSON; all numbers remain explicitly unmeasured")
    source.add_argument("--input", type=Path, help="completed comparison.json")
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    runner = LoadRunner()
    report = json.loads(options.input.read_text()) if options.input else None

    if report:
        VerifyReport(report, runner)

    config = report["configuration"] if report else json.loads(options.draft.read_text())
    options.output.write_text(Render(config, report, runner), encoding="utf-8")


if __name__ == "__main__":
    Main()

# Project: FuzzyRoutines by Fuzzy Technologies
# Maintainer: Fuzzy Technologies contributors
# SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
# SPDX-License-Identifier: Apache-2.0

"""Render the exact representative-average versus aggregate-centroid example.

Requires docs/requirements-plots.txt and the candidate package. Writes a single
SVG to --output-directory; --check compares without writing. An optional
--preview-directory receives a PNG for visual review. No network is accessed.
"""

import argparse
import json
import math
import runpy
from pathlib import Path

from fuzzyroutines import (
    Centroid,
    ContinuousUniverse,
    FuzzificationPolicy,
    IntegrationDomain,
    LinguisticCodec,
    LinguisticScale,
    LinguisticTerm,
    ScalarFuzzySet,
    SNormPolicy,
    Triangle,
    Union,
)


def BuildFigure(plottingHelpers):
    """Draw API curves using sibling style helpers and independent triangle moments.

    Args:
        plottingHelpers: Namespace loaded from the sibling documentation plot
            script, without adding the checkout package to the import path.
    """

    universe = ContinuousUniverse(0, 6, leftClosed=True, rightClosed=True)
    small = ScalarFuzzySet(universe, Triangle(0, 1, 2))
    large = ScalarFuzzySet(universe, Triangle(2, 4, 6))
    codec = LinguisticCodec(
        LinguisticScale((LinguisticTerm("Small", small), LinguisticTerm("Large", large))),
        (IntegrationDomain(0, 2), IntegrationDomain(2, 6)),
        FuzzificationPolicy(),
    )
    average = codec.AverageRepresentatives((1, 1))
    aggregateCentroid = Centroid(Union(small, large, SNormPolicy("logic")), IntegrationDomain(0, 6))
    assert average == 2.5, "Equal-grade representative mean must equal (1 + 4) / 2."
    assert math.isclose(aggregateCentroid, 3, rel_tol=0, abs_tol=1e-10), (
        "The union centroid must equal (area 1 * centre 1 + area 2 * centre 4) / 3."
    )
    colors = plottingHelpers["COLORS"]
    figure, (axis,) = plottingHelpers["NewFigure"]("Representatives and areas carry different information")
    figure.set_size_inches(11.6, 5.7)
    coordinates = tuple(index / 100 for index in range(601))

    for fuzzySet, color, label in ((small, colors[0], "Small: area 1, centre 1"),
                                   (large, colors[1], "Large: area 2, centre 4")):
        grades = tuple(fuzzySet.Membership(coordinate) for coordinate in coordinates)
        axis.plot(coordinates, grades, color=color, linewidth=2.5, label=label)
        axis.fill_between(coordinates, grades, color=color, alpha=0.16)

    axis.axvline(average, color=colors[2], linestyle="--", linewidth=2)
    axis.axvline(float(aggregateCentroid), color=colors[3], linestyle=":", linewidth=2.5)
    axis.annotate("Representative mean = 2.5", (average, 0.36), xytext=(0.15, 0.45),
                  color=colors[2], fontsize=11,
                  arrowprops={"arrowstyle": "->", "color": colors[2]})
    axis.annotate("Union centroid = 3", (float(aggregateCentroid), 0.78), xytext=(3.6, 0.9),
                  color=colors[3], fontsize=11,
                  arrowprops={"arrowstyle": "->", "color": colors[3]})
    axis.set_xlim(0, 6)
    axis.set_xlabel("Output coordinate x  ·  both supplied grades equal 1")
    axis.legend(loc="upper center", bbox_to_anchor=(0.5, 1.17), ncol=2, frameon=False)

    return figure


def Main(arguments=None) -> int:
    """Write or compare the deterministic SVG and emit a compact JSON report.

    Args:
        arguments: Command arguments without the executable name; `None`
            reads the current process arguments.

    Returns:
        Zero after the requested SVG write or successful byte comparison.

    Raises:
        RuntimeError: The checked figure is missing or differs from the model.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", required=True, type=Path, dest="outputDirectory")
    parser.add_argument("--preview-directory", type=Path, dest="previewDirectory")
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args(arguments)
    plottingHelpers = runpy.run_path(str(Path(__file__).with_name("generate_guide_figures.py")))
    plottingHelpers["ConfigureStyle"]()
    figure = BuildFigure(plottingHelpers)
    rendered = plottingHelpers["RenderSvg"](figure, "linguistic-encoding")
    destination = options.outputDirectory / "linguistic-encoding.svg"

    if options.check:
        if not destination.is_file() or destination.read_bytes() != rendered:
            raise RuntimeError(f"stale or missing figure: {destination}")

    else:
        options.outputDirectory.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(rendered)

    if options.previewDirectory is not None:
        options.previewDirectory.mkdir(parents=True, exist_ok=True)
        figure.savefig(options.previewDirectory / "linguistic-encoding.png", dpi=120)

    plottingHelpers["plt"].close(figure)
    print(json.dumps({"checked": options.check, "svgBytes": len(rendered)}, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(Main())

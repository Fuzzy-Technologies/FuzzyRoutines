<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Scientific plot export {#scientific-plot-export}

Use the `plot` extra with a reviewed FuzzyRoutines 2.2 wheel that contains
`fuzzyroutines.plotting`. Set `FUZZYROUTINES_WHEEL` to its absolute path.
Ordinary scalar calculations use the base installation.

```bash
: "${FUZZYROUTINES_WHEEL:?Set the absolute path to the reviewed wheel}"
python -m pip install "${FUZZYROUTINES_WHEEL}[plot]"
```

Export a scale to SVG with an explicit dimensionless axis label. The temporary
directory makes the example safe to run again. A separate export demonstrates
how to inspect a failed sample.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from fuzzyroutines import CreateUniversalFuzzyScale, DiscreteUniverse, ScalarFuzzySet
from fuzzyroutines.plotting import ExportMembershipPlot, PlotSamplingError

def UnavailableGrade(coordinate):
    """Report an unavailable observation at the requested coordinate."""

    raise ValueError(f"No observation at {coordinate}")

scale = CreateUniversalFuzzyScale()
with TemporaryDirectory() as temporaryDirectory:
    folder = Path(temporaryDirectory)
    figure = ExportMembershipPlot(
        scale, folder / "membership.svg", coordinateLabel="Normalized coordinate x",
    )
    assert figure.read_bytes().startswith(b"<?xml")

    incomplete = ScalarFuzzySet(DiscreteUniverse((0, 1)), UnavailableGrade)
    failedFigure = folder / "missing.svg"
    try:
        ExportMembershipPlot(incomplete, failedFigure)
    except PlotSamplingError as error:
        sampleFailure = error
    else:
        raise AssertionError("An unavailable scalar sample must fail the export.")

    assert isinstance(sampleFailure.__cause__, ValueError) and not failedFigure.exists()
```

- Supply a finite `displayWindow=(left, right)` for an unbounded universe.
  A window controls what you see. Support and integration bounds retain their
  separate mathematical meanings.
- `sampleCount` sets the base grid per visible continuous segment. The exporter
  includes known knots and draws discrete values and custom functions of unknown
  continuity as unconnected markers. A finite grid gives display resolution.
- Use `.png` or `.svg` with `transparent=True` for a clear background. JPEG
  needs an opaque `background` such as `"#121829"`. SVG text stays editable by
  default. Use `svgTextAsPaths=True` to export glyph outlines.
- The parent directory must already exist. Set `overwrite=True` to replace an
  existing export after successful rendering. Choose a destination suffix and
  an optional `formatName` that agree.

See the [API reference](../api/modern/plotting.md) for the scalar failure contract.

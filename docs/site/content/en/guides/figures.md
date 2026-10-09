<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Figure provenance and reproduction

The ten checked-in SVGs are scientific teaching figures produced by
`tools/generate_guide_figures.py` from real scalar API evaluations. They are
not generated artwork. The generator first executes every assertion in the
eight worked scenarios, then draws the models and annotations. The scenario
code and numerical expectations are in `examples/guide.py`.

## One figure set for all languages

English, Russian, and Simplified Chinese documentation share these same SVGs.
Text inside the images stays English: titles, axes, legends, annotations, and
units. Translated pages explain those labels in localized captions, prose, and
descriptive image alternatives. No translated image variants are generated.

The canonical files are under `docs/site/content/en/assets/figures/`. Locale
builds may copy them for working relative links; the copies must preserve the
same bytes. Russian and Chinese pages still require their own language and
scientific review before publication. See the
[locale architecture](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/architecture/multilingual-documentation-pipeline.md) for
the documentation contracts.

## Reproduce the assets

From a checkout with FuzzyRoutines installed, use the pinned documentation
toolchain on CPython 3.14:

```bash
python -m pip install -r docs/requirements-plots.txt
python tools/generate_guide_figures.py --output-directory docs/site/content/en/assets/figures
python tools/generate_guide_figures.py --output-directory docs/site/content/en/assets/figures --check
```

`--check` compares every expected SVG byte for byte and writes no files. The
documentation CI runs it on Python 3.14 with this pinned toolchain. SVG IDs use
a fixed hash salt, metadata omits the generation date, and labels use a fixed
font family. Reproduction is scoped to that toolchain; byte identity across
different plotting-library or font versions is not promised.

For editorial review, an explicit `--preview-directory PATH` additionally
writes PNGs to the chosen directory. The default writes only SVGs below
`--output-directory`. No command accesses the network after dependencies have
been installed. A missing dependency, stale figure, failed scenario assertion,
or write failure produces a nonzero exit status.

Matplotlib and its dependencies, including NumPy, belong only to the
documentation toolchain. Installing or importing FuzzyRoutines does not require
them. The default example script imports neither.

## Verify scientific content independently

SVG byte comparison detects stale assets; it does not prove their mathematics.
`tests/test_guide_figures.py` independently checks all 401 coordinates of each
of the 26 plotted curves against elementary piecewise or exponential formulas.
It also checks scatter coordinates, six sensor bars, thresholds, the four-node
centroid calculation with exact rational arithmetic, and title/legend layout.
The reference calculations do not call the library's membership functions.
Documentation CI installs the plotting dependencies and runs these tests
against the installed scalar API before comparing the SVG files.

## Interpret the pictures correctly

- Continuous model lines use 401 display samples; they are illustrations, not
  proofs of exact geometry or a quadrature policy used by `Centroid`.
- Alpha-cut dots show the stated nine-point grid; outlined dots indicate the
  exhaustive five-point discrete universe's qualifying coordinates.
- Scale diagnosis uses eleven coordinates including endpoints. The plot's
  smooth curves and the diagnostic observations are different kinds of evidence.
- The normalization figure draws only discrete points, with no interpolating
  line or implied intermediate universe coordinates.
- The centroid picture contrasts analytical moments with a separate user-side
  four-point trapezoidal calculation. Neither the displayed line density nor
  that coarse calculation configures the library's adaptive integration.
- The operator picture fixes the second input grade at 0.6. Its horizontal
  axis varies the first grade; neither axis is a physical measurement.

Every image has a descriptive Markdown alternative and SVG title/description.
Its accompanying page gives the numerical result in text, so colour perception
or image availability is not required to understand the example. Model
parameters and labels are illustrative rather than empirical calibration data.

The plots use [Matplotlib's SVG backend](https://github.com/matplotlib/matplotlib/blob/main/lib/matplotlib/backends/backend_svg.py)
and [savefig metadata support](https://matplotlib.org/3.11.0/api/_as_gen/matplotlib.pyplot.savefig.html).

<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0022: Scientific plotting and export

- Status: Proposed
- Date: 2026-11-05
- Related Task: [#393](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/393)
- Related Feature: [#360](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/360)

## Context

The [guide generator](../../tools/generate_guide_figures.py) and
[agent recipe](../../examples/agent_recipe.py) plot scalar evaluations with the
same dark palette, 401 display samples and editable SVG labels. Their layouts
and metadata serve different documentation purposes. Their sampling loops
assume known curves; applying them unchanged to arbitrary models could connect
across a discontinuity or imply values between discrete coordinates.

The public renderer needs a shared presentation contract while keeping the
[universe, support and integration domain](0002-universe-support-semantics.md)
separate. Rendering is optional and must not affect evaluation or import of
the scalar API.

## Decision

### Evaluation and axes

- Render grades from the scalar evaluator used for calculations:
  `ScalarFuzzySet.Membership(x)` for sets and scale terms, or the public
  membership callable for a standalone function with an explicit universe.
  Use the evaluator's original coordinate types for declared knots, points
  and input values; convert for display only. Propagate invalid evaluations
  with series and coordinate context. A failed evaluation is never a zero grade.
- Use a linear coordinate axis with the supplied quantity and units, such as
  `Temperature (°C)`, or label a declared dimensionless input, such as
  `Normalized coordinate x`. A generic unlabeled input uses `Coordinate`.
  The vertical grade axis is dimensionless, with a fixed `[0, 1]` scale and
  ticks at `0, 0.25, 0.5, 0.75, 1`; an equivalent grade axis is horizontal
  for input membership bars. Padding for markers or labels has no data meaning.
  Titles and unit labels are display metadata. A normalization or conversion
  must be supplied by the caller and identified on the figure; no implicit
  rescaling, clipping of grades or inference of units.
- A finite, increasing display window defaults to the extent of bounded
  term universes (the span of declared coordinates for discrete terms).
  An unbounded universe requires a caller-supplied finite window. A
  discrete singleton may have padded axes without adding data coordinates.
  An overlay shares one coordinate axis and one unit; render each term only
  on its intersection with the window. Do not evaluate or draw zero outside
  a term's universe. A clipped or empty term keeps its legend identity; fail
  with a clear error if the window contains no renderable data for any term.
  The window is never an integration window or evidence of mathematical support.

### Sampling, knots and annotations

| Model or overlay | Rendering contract |
| --- | --- |
| Continuous with known geometry | Start with 401 evenly spaced display coordinates including both ends of each term's visible interval when they belong to the universe. Allow an explicit integer count of at least two. Assign endpoints directly, merge all visible known breakpoints and requested input coordinates, and deduplicate and sort before evaluation within each continuous segment. The count describes the base grid; extra samples are reported separately. |
| Explicit piecewise linear model | Include every visible knot and segment boundary, even when the base grid misses one. Connect samples only on declared linear segments. Take extrapolation and domain membership from the model contract; do not fit or extend a line past it. |
| Open endpoints, jumps and isolated values | Split artists at a known jump; no stroke or fill bridges it. Plot the evaluated value at an included jump or singleton as a filled marker. For an excluded endpoint or a one-sided limit, use an open marker only when the limit is known from the model's geometry and differs from any filled marker at that position. Include a representable interior sample near each visible open edge when the base grid does not reach it. A caller-supplied break coordinate splits the stroke even if exact one-sided limits are unavailable. |
| Custom callable with unknown continuity | Show sampled markers by default. A caller may declare continuous segments and breakpoints for lines, with that assumption recorded in the figure or accompanying evidence. The renderer does not infer continuity from apparent smoothness. |
| Discrete universe | Plot one marker per declared coordinate inside the window, including zero grades. Optional stems are vertical guides only. No joins, area fills, synthesized coordinates, interpolation or resampling. A continuous function evaluated on a discrete universe follows this rule. |

A finite grid is display resolution, not an error bound. Validate it before
evaluation and reject requests that cannot yield the required distinct display
coordinates for a visible continuous segment; do not shift a knot or input
coordinate to make a grid fit. Record the effective display window, base
sample count, added coordinates and any declared segmentation. Never round
grades before drawing or testing an annotation.

An input marker and its bars use an exact input evaluation, independent of
the nearest display sample. Use the ordered `LinguisticScale.Fuzzify` result
when displaying selection, with the actual policy and no-match state. Do not
classify an input that does not belong to every term universe. An alpha line
uses the requested dimensionless threshold. Highlight discrete cut points
using `AlphaCut` and its weak comparison (`grade >= alpha`). Continuous
cut observations must be labeled **sampled**, with their analysis domain and
resolution; use `SampleAlphaCut` when its domain is valid. Draw exact regions
only when the model supplies exact geometry. A line crossing the threshold
between plotted samples is not proof of an exact cut endpoint.

### Shared visual styles

Use the versioned corporate dark profile by default. It inherits the
existing guide and recipe's colors, with canvas and axes `#121829`,
foreground `#edf0f8`, tick labels `#c6cede`, and the `#8490ab` grid
at 20% opacity. Default single-panel and curve-plus-bars sizes are
`10.8 × 5.3 in` and `11.5 × 5.2 in`, respectively, at `160 dpi` for
rasters (`1728 × 848` and `1840 × 832` pixels). Allow explicit positive
finite size and resolution. Export the whole declared canvas with room for
labels and legends; tight cropping must not silently change dimensions.
SVG uses the same layout at 72 points per inch, independent of raster DPI
for vector geometry.

Use declared scale order in drawing, legends and bars. Assign the five
palette slots by declared position and retain the slot when a term is
hidden or clipped. For larger scales, repeat the color sequence with a
different line pattern or point symbol per cycle. Labels identify the
terms even when styles repeat. An explicit per-term style can customize a
user scale without changing its order or grades.

| Historical term | Corporate color | Unchanged model |
| --- | --- | --- |
| `Min` | `#a99aff` | `Hyperbolic(8, 20, 0)` |
| `Low` | `#4dd8d0` | `Bell(0.17, 0.23, 0.34)` |
| `Med` | `#ffd166` | `Bell(0.34, 0.40, 0.60)` |
| `High` | `#ff8c9d` | `Bell(0.60, 0.66, 0.77)` |
| `Max` | `#8cdb91` | `SShoulder(0.77, 0.95)` |

The historical Universal Fuzzy Scale uses the closed normalized `[0, 1]`
universe. Its Min tail and weak coverage around `x = 0.17` remain visible
in the numerical data; centroid windows must not clip any curve. Preserve
the historical last-exact-maximum policy where requested. Grades are not
probabilities and need not sum to one.

### Headless export

Use a local, noninteractive rendering context and release resources after
each export. In Matplotlib, use Agg for raster output and the SVG writer
for vectors. Import the optional backend only when requested. Preserve the
caller's selected backend, style and locale. Default to DejaVu Sans with
explicit font and label sizing (11 pt base, 18 pt title); require a
configured font that covers labels outside its repertoire rather than
silently substituting machine-specific glyphs.

| Format and filename suffix | Background and font behavior | Stable metadata |
| --- | --- | --- |
| PNG, `.png` | Opaque profile canvas by default; explicit transparency leaves the canvas and axes transparent while preserving artist alpha. Text is rasterized at the requested DPI. | Fixed software identifier and resolution; no timestamp or destination path. |
| JPEG, `.jpg` or `.jpeg` | Require an explicit opaque background color; reject a simultaneous transparency request. Composite both canvas and axes with the supplied background before RGB encoding. Use quality 95 and 4:4:4 chroma as defaults. | Fixed encoding settings and resolution; no generated timestamps, EXIF or destination path. |
| SVG, `.svg` | Opaque by default, with an explicit transparent option. Editable text is the default (`svg.fonttype = none`) and requires the font on the viewer's system. An opt-in path mode preserves glyph geometry without relying on the viewer's fonts and sacrifices selectable labels. | Fixed creator and description, caller title, versioned ID salt and no generated date; serialize as UTF-8 with LF line endings. |

Transparent exports leave foreground colors unchanged; the caller chooses
a contrasting background for the intended publication. Require an explicit
output filename, including its suffix. Infer format from the case-insensitive
suffix or check an explicitly supplied format agrees; reject unknown or
conflicting suffixes. Accept spaces and Unicode in paths as filesystem data.
The parent directory must exist. Reject an existing target unless overwrite
is explicitly requested, including a target created after validation; surface
file errors with their path. Evaluation or rendering failure must leave any
existing file intact.

With the same inputs, labels, style, renderer and encoder versions, font
files and platform, repeated exports must reproduce bytes independently of
the filename. Pin the toolchain used to compare committed documentation
figures via [requirements-plots.txt](../requirements-plots.txt).
Across environments require numerical and structural parity (formats,
dimensions, geometry, labels and colors); do not promise identical bytes
across different rasterizers, fonts or encoders.

## Output and consequences

This ADR specifies behavior without introducing an API, new dependency,
project-file schema or changes to existing generators. The implementation
in [#394](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/394)
owns the installed optional renderer and its API documentation;
[#395](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/395)
owns project-file plotting and its user workflow. Their EN/RU/zh-CN guides
should explain units, cut provenance, discrete markers, fonts and formats.

The [acceptance fixtures](evidence/0022-plotting-contract.md) separate
numeric and artist checks from file format checks for #394 and #395.
Existing documentation figures retain their current reproduction tests
and output bytes.

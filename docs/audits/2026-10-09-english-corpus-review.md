<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Canonical English corpus review — 2026-10-09

This final English example pass follows merged PR #301, squash commit
`518bc9dd5750afde569b1593e243490fc42ce658`. Its reviewed source is that baseline
plus the accompanying Task #294 PR. The final PR head and CI runs provide the
immutable revision evidence; `docs/i18n/units.toml` binds each canonical page
and public docstring to its SHA-256 source hash.

The review covers all 34 canonical English pages and all 193 inventoried public
symbol units, including their authored docstrings and alias relationships.
The [public example index](../site/content/en/guides/example-index.md) records
the per-symbol executable examples. These are AI-assisted engineering,
scientific, data-science and editorial passes, not independent human approval
or Russian/Chinese native-speaker approval. Task #298 still owns the independent
all-module mathematical and coverage audit.

## Engineering pass

Installation, the README and quick start agree on CPython 3.13/3.14 and the
current development package. Future stable PyPI installation is clearly
distinguished from today's available package. Eight standalone scenarios and
29 independent Python blocks exercise actual public behavior. The index gate
records function calls, constructors and property reads; imported-but-unused
names fail. Root aliases must be identical to canonical module objects.
Typing contracts require annotations; built-in exception constructors require
retained concrete instances. Private and generated dataclass helpers follow
the existing inventory exclusions.

The API navigation now leads to result reconstruction, error handling and
historical recipes. Three workflow diagrams show classification, set
composition/integration, sensor-grade combination and the compatibility
boundary. Clean wheel/sdist CI invokes the usage gate with `-I` and verifies
package origin; no checkout path is injected to satisfy an installed check.
Plotting remains a documentation-only dependency.

## Mathematical and scientific pass

The eight scenarios retain the independent calculations and limits recorded
in the [earlier guide review](2026-10-09-english-guide-review.md) and
[independent figure review](2026-10-09-figure-verification.md). The new operator
plot holds one grade at 0.6 and compares minimum/product conjunction and
maximum/algebraic disjunction; all four 401-point curves have independent
scalar references. All 26 plotted membership curves now have explicit reference
coverage, including an artist/reference-set equality check. Shared English
SVGs are regenerated deterministically; the prior nine are unchanged.

Result recipes distinguish continuous positive support from its closure,
discrete topology from intervals, weak alpha-cut boundaries from grid samples,
and observed height/partition quality from continuous proof. Manually rebuilt
records are not presented as independently validated mathematical evidence.
Convergence exhaustion is a real deliberately shallow integration, while the
category-hierarchy example explicitly constructs illustrative exceptions.

Corrections found during review:

- Historical `Trapezium` takes feet `a, b` and plateau bounds `c, d`; recipes
  preserve that order and explicitly distinguish modern geometric keywords.
- Historical `defuzValue` recomputes from the current model and integration
  window; the recipe does not describe it as a cached value.
- Hyperbolic scale is a distance multiplier; Gaussian scale is a standard
  deviation. Their docstrings now state the separate meanings.
- `HarringtonDesirability()` has no constructor parameters; its docstring no
  longer claims a parameter-validation failure for a nonexistent parameter.

No numerical formula or runtime statement is changed by this wave. The
mathematical model, migration contracts and performance records retain their
explicit domains, primary references, experimental evidence and unsupported
capability boundaries.

## Data-science pass

Membership is not probability. Confidence remains the maximum membership,
with abstention, ties and threshold boundaries explained. Sampled gap/overlap
fractions count grid observations rather than interval lengths. Diagnostics
are finite-grid evidence; no continuous partition certificate is inferred.
The new operator guide describes policy choice as modeling semantics, without
statistical independence or accuracy claims. Sensors retain separate physical
universes and combine dimensionless grades after evaluation.

Custom callbacks preserve application exceptions and must remain consistent
during integration. No inference engine, fuzzy-number arithmetic, automatic
NumPy backend or universal speed claim is introduced. Performance pages retain
the measured workload/environment scope and the optional prototype boundary.

## Reader and editorial pass

The reading route is quick start → workflow/scenarios → focused recipes →
API reference. Every inventoried function, constructor and behavior-bearing
method/property has a tested route in the index. Alias examples share canonical
objects. Result and historical recipes state expected values and practical
limits; examples do not require context from a previous code fence.

Formula notation follows the existing GitHub-compatible math contract. All
figures have meaningful alternatives and text explanations, and links open
the same SVG at full size. The new operator image was visually inspected for
legend/axis readability and clipping. Mermaid is configured through Material's
documented SuperFences route; strict rendered pages and anchors are checked by
PR CI. Final desktop/mobile review of all three languages belongs to #297.

The stale API-page statement that Task #95 typing coverage was still planned
was replaced with the implemented contract link. The properties-page grammar
and recipe navigation were corrected. README, changelog, figure counts and
executable-tool instructions agree with this corpus.

## Evidence and handoff

Affected local example/figure/coverage tests pass; complete regressions,
supported-runtime clean installs, strict documentation builds and packaging
run in PR CI. Their exact final-revision links belong in the accompanying PR,
not an assumed green status in this report.

The inventory now contains 227 units: 34 pages and 193 public symbol contracts.
Russian and Simplified Chinese translations remain missing, with no fabricated
approved reviews. Translate this finalized hash-bound source under #295/#296,
then enforce complete fresh reviews and rendered parity under #297. Task #280
remains open for its multilingual visual-documentation acceptance. Stable
publication, external publisher controls and final candidate approval remain
#299/#121; this English review does not approve or publish a release.

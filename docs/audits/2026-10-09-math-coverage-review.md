<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# All-module mathematical and test-evidence audit

Task #298 starts from `develop` commit
`80cda3dd4d19129ccff33de60e1beac33eb15e6d`, including the reviewed English
corpus in #302. This record accompanies the coverage/parity implementation;
final CI measurements and gap assessment are added after the first run.
It is not an assertion that unmeasured branches are sufficiently tested.

## Evidence boundary

The CI workflow `math-coverage.yml` measures every library source with line
and branch tracing on CPython 3.13 and 3.14, retaining JSON, JUnit and missing
branch coordinates. `Examples.py` is the sole source exclusion from the module
audit: it is a compatibility demonstration CLI, exercised by the installed
artifact verifier, rather than a mathematical implementation. Re-export and
exception modules remain included. No numerical source lines are suppressed.

The same workflow executes the process runner and compares each test identity
and outcome with the sequential run. Two equal totals with different test sets
fail. Duplicate executed tests fail; repeated collection-level skips alone
deduplicate. Serial-marker isolation, separate process identities, fail-fast
and timeouts retain executable fixture tests in `test_test_runner.py`.

## Finding resolved before measurement

The process runner previously summed collection-level module skips from both
its parallel and serial phases. Thus three optional module skips appeared as
six in the combined summary. Executed pass/failure counts were unaffected.
The runner now deduplicates these collection identities and retains phase XML
on explicit request. A real synthetic skipped module reproduces the defect and
checks the corrected summary against sequential execution. Existing evidence
directories are rejected rather than overwritten.

## Mathematical inventory

The contracts and independent-reference tests used for the review are recorded
below. Scientific acceptance requires reading the assumptions and unresolved
coverage gaps; a high percentage is not a replacement for a numerical oracle.

| Module group                | Contract and independent evidence                                                                                   |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `membership`                | Eight family formulas, geometry, endpoints, extreme finite values; independent scalar/reference and invariant tests |
| `numeric`                   | Finite non-Boolean real grades, exact rational ordering and deliberate float-only tie allowance                     |
| `domain`                    | Continuous endpoint closure, finite integration intervals, discrete exhaustive domains and equality contracts       |
| `operators`                 | Explicit negation/t-norm/s-norm families; truth boundaries, involution and algebraic invariants                     |
| `fuzzysets`                 | Equal-universe composition, directed difference and immutable wrappers; scalar operation references                 |
| `properties`                | Positive support versus closure, core/boundary/height, exact versus sampled provenance and analytical certificates  |
| `alphacuts`                 | Inclusive weak cut, exhaustive discrete results and declared finite sampling; analytic triangle checks              |
| `relations`                 | Explicit comparison coordinates, exact default and opt-in tolerance; no unproved continuous equality                |
| `defuzzification`           | Area/first moments, stable Gaussian tails and adaptive convergence; independent Decimal and rational references     |
| `linguistic`                | One evaluation per term, exact rational maxima, ties/abstention, sampled diagnostics and threshold semantics        |
| `_legacy.membership`        | Protected family aliases/parameter order, validation and shared reviewed scalar kernels                             |
| `_legacy.operators`         | Historical scalar/variadic calls; all norm families and independent algebraic invariants                            |
| `_legacy.sets`              | Current mutable model/window centroid, property recomputation and historical pickle identity                        |
| `_legacy.scales`            | Later-wins ties, complete-name lookup, level identity and universal preset behavior                                 |
| `_legacy.utilities`         | Numeric predicates and range parsing compatibility, including invalid-input boundaries                              |
| Exports and exceptions      | Root/facade alias identity, static typing and built-in exception catch compatibility                                |

Detailed mathematical contracts and primary-source references remain in the
[canonical model](../MATHEMATICAL_MODEL.md),
[source/algorithm invariants](../mathematics/source-algorithm-invariants.md),
[centroid derivation](../mathematics/centroid-defuzzification.md) and accepted
ADRs. Prior findings #282–285 have merged regression repairs; this audit
reassesses their evidence on the current source instead of treating old green
builds as final candidate acceptance.

## Pending measured assessment

Record per-module line/branch coverage, inspect every missing mathematical
branch, add meaningful targeted cases for unexplained gaps, and link final
supported-runtime CI and installed-example evidence before closing #298.
Complete local suites are not part of this task's development workflow.

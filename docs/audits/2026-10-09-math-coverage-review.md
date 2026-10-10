<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# All-module mathematical and test-evidence audit

Task #298 starts from `develop` commit
`80cda3dd4d19129ccff33de60e1beac33eb15e6d`, including the reviewed English
corpus in #302. The review combines source/contract inspection, independent
reference tests and actual supported-runtime CI. It is an AI-assisted
engineering/mathematical assessment, not a formal proof or a human release
approval. No new unresolved mathematical blocker was found in this scope.

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

## Independent evidence and new cases

The existing independent oracles remain authoritative: `test_defuzzification.py`
compares Gaussian tails with 60-digit Decimal references and checks affine
changes; `test_membership_function_contracts.py` checks family reference values,
monotonicity and symmetry; `test_operator_reference_contracts.py` and
`test_operator_algebraic_properties.py` cover norm/negation references and laws.
`test_derived_properties.py` distinguishes positive support from its closure,
supremum from attained core, and exact discrete evidence from sampling.
`test_linguistic_terms.py` checks exact Fraction maxima and explicit float-only
tie accommodation. `test_custom_membership_protocol.py` rejects borrowed
analytical certificates; `test_finite_number_policy.py` retains extreme finite
coordinate regressions. These directly cover the repaired #282–285 contracts.

The initial coverage run exposed missing public reconstruction and negative-input
cases. `test_result_record_boundaries.py` adds 88 focused cases: contradictory
regions, grids, grades, provenance and scale identities; invalid operation and
policy inputs; historical mutation and representation; and normalization after
continuous/discrete universe changes. Gaussian integration over an extreme
finite half-window is checked against the independent half-normal mean
`-sigma * sqrt(2 / pi)`, including an overflowed standardized endpoint. A remote
underflowed Gaussian window must fail instead of inventing a centroid. These
cases exercise externally meaningful contracts, rather than duplicating the
implementation as the only oracle. No production mathematical formula changed.

## Measured coverage and execution parity

The [supported-runtime audit run](https://github.com/Fuzzy-Technologies/FuzzyRoutines/actions/runs/37964924270)
measured test-source commit
[`63ce20d`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/commit/63ce20d6be6e674da84712815354c17393151c18).
Both CPython 3.13 and 3.14 reported **1202 passed, 3 collection skips** in each
execution mode. Exact test identities and outcomes matched; there were no
failures, process errors or timeouts. The three optional modules are measured
separately by the optional-prototype workflow, not claimed as executed here.
All nine workflows at that revision passed, including installed wheel/sdist
examples and documentation figure regeneration. CI durations here include
coverage instrumentation and are not a scalar/parallel performance benchmark.

The following values are the CPython 3.14 measurements. CPython 3.13 reports the
same missing source lines and branches; minor percentage differences in three
dataclass modules reflect its executable-line inventory. `n/a` means no branch
sites, not omitted coverage.

| Module                                | Lines (%) | Branches (%) |
| ------------------------------------- | --------- | ------------ |
| `fuzzyroutines/FuzzyRoutines.py`      | 100.00    | 100.00       |
| `fuzzyroutines/__init__.py`           | 100.00    | n/a          |
| `fuzzyroutines/_legacy/__init__.py`   | 100.00    | n/a          |
| `fuzzyroutines/_legacy/membership.py` | 98.33     | 83.33        |
| `fuzzyroutines/_legacy/operators.py`  | 100.00    | 100.00       |
| `fuzzyroutines/_legacy/scales.py`     | 100.00    | 100.00       |
| `fuzzyroutines/_legacy/sets.py`       | 100.00    | 100.00       |
| `fuzzyroutines/_legacy/utilities.py`  | 100.00    | 100.00       |
| `fuzzyroutines/alphacuts.py`          | 100.00    | 100.00       |
| `fuzzyroutines/defuzzification.py`    | 98.39     | 95.16        |
| `fuzzyroutines/domain.py`             | 100.00    | 100.00       |
| `fuzzyroutines/exceptions.py`         | 100.00    | n/a          |
| `fuzzyroutines/fuzzysets.py`          | 100.00    | 100.00       |
| `fuzzyroutines/linguistic.py`         | 99.59     | 99.14        |
| `fuzzyroutines/membership.py`         | 97.89     | 98.08        |
| `fuzzyroutines/numeric.py`            | 100.00    | 100.00       |
| `fuzzyroutines/operators.py`          | 100.00    | 100.00       |
| `fuzzyroutines/properties.py`         | 99.66     | 99.31        |
| `fuzzyroutines/relations.py`          | 100.00    | 100.00       |

## Remaining-gap assessment

- `_legacy.membership:76` is a defensive private snapshot guard. Public
  analytical dispatch checks `_HasAnalyticalEvaluator()` before requesting a
  snapshot. Overridden public callbacks and inherited-certificate rejection
  have explicit regression tests; invoking private internals just to increase
  a percentage adds no public-contract evidence.
- `membership:392` and `properties:623` reject unknown internal analytical
  families after the validated factory/registry boundary. Public unknown-family
  rejection is tested. `membership:514,519,525` are private adapter protocol
  stubs. `membership:570` accepts a bound method of the private frozen source;
  normal public modern and historical evaluator paths are covered. These are
  retained defensive/protocol paths, not omitted supported formulas.
- `defuzzification:267,456,464` are numerical postcondition guards for invalid
  analytical moments and non-finite final moments/centroids. Tested public
  fallback triggers include cancellation, precision insufficiency, underflow
  and exhausted adaptive depth. The unhit guards remain fail-closed insurance
  against arithmetic states rejected earlier by current inputs; this audit
  does not claim all possible floating-point combinations were enumerated.
- `linguistic:36` in the table is the non-real diagnostics partition-tolerance
  guard. The final follow-up adds an explicit Boolean `partitionTolerance`
  rejection (88 focused cases pass locally), after the measured commit above.
  PR CI verifies the final test revision again.

No executable mathematical source is hidden using `pragma: no cover`. Every
module has an assessed contract and evidence; remaining gaps are explicit
defensive/private paths rather than unexplained public calculation branches.
Branch coverage is considered adequate for the declared scalar release scope,
subject to maintainer review and the final candidate CI. It does not establish
arbitrary callback convergence, unsampled continuous equality/convexity, or
free-threaded Python support.

## Plan and release boundary

The audit retains ADR-0001 compatibility, ADR-0002 universe/support separation,
ADR-0003/0004 explicit family contracts, ADR-0005 fail-closed integration,
ADR-0007 process isolation, ADR-0008 directed difference, ADR-0009 evidence
limits, ADR-0013 exact/tolerant selection and ADR-0014 sampled diagnostics.
ADR-0015 still leaves NumPy experimental and opt-in; there is no automatic
backend selection or shared mutable numerical policy. Independent Python
processes have independent state. Caller-owned mutable callbacks and legacy
objects require caller coordination when shared between threads.

The 29 installed documentation blocks cover all 193 public symbol units and
include eight end-to-end scenarios. Their figures and expected intermediates
are checked by the separate installed-artifact documentation gate. The report
supports #298 and [release readiness](../release-readiness.md); translated
documentation and actual PyPI publication remain separate #295–299/#121 gates.
All final required checks must rerun on the approved release candidate.
Only affected tests and source/style checks ran locally; complete regressions,
coverage and the Python matrix ran in CI.

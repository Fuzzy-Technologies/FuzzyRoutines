<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0013: Linguistic Fuzzification Classification Policy

- Status: Accepted on merge
- Date: 2026-09-28
- Related planning task: #84
- Related amendment task: [#281](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/281)
- Related Feature: #27

## Context

An ordered linguistic scale evaluates several membership functions at one
coordinate. Returning only a winning label hides the membership evidence and
leaves equal maxima, zero coverage, near-zero coverage, and ordering semantics
implicit. The historical `FuzzyScale.Fuzzy()` method must remain callable and
continues to select the later level when grades are equal, but that mutable
dictionary API is not the architectural model for new code.

## Decision

The modern `LinguisticScale.Fuzzify()` operation returns immutable evidence for
every declared term and applies an explicit `FuzzificationPolicy`.

For ordered terms $L_i$ and a coordinate $x$, the operation records

$$
s_i=\mu_{L_i}(x), \qquad c=\max_i s_i.
$$

The complete ordered score tuple is always returned, and confidence is the
maximum membership $c$. Classification has no match when

$$
c \leq c_{\min},
$$

where $c_{\min}\in[0,1]$ is the explicit minimum-confidence threshold. The
default $c_{\min}=0$ rejects only zero coverage. A caller may use a positive
threshold to reject near-zero coverage.

When a match exists, the default zero tie tolerance requires equality of the
validated grade and $c$, without converting either value to a float. Distinct
rational grades must remain distinct even if float conversion would round
them to the same value.

A positive tie tolerance uses the inclusive absolute-distance comparison
$c-s_i\leq\tau$, where $\tau$ is the explicit tolerance. Rational grades and
mixed rational/float grades use their exact represented values for this
comparison; they receive no additional boundary allowance.

For the established positive float-only policy, where the grade, confidence,
and tolerance are all Python `float` values, retain the existing binary64
boundary accommodation. With `difference = confidence - grade`, a grade is
also tied when `math.isclose(difference, tolerance, rel_tol=1e-12, abs_tol=0)`
is true. Equivalently, after binary64 subtraction, the additional comparison is

$$
|\mathrm{difference}-\tau|
\leq 10^{-12}\max(|\mathrm{difference}|, |\tau|).
$$

This accommodation applies only to an explicitly positive float tolerance;
it never changes the zero default or rational/mixed comparisons. It preserves
existing decimal-boundary behavior, such as grades `0.7` and `0.75` under
tolerance `0.05`. The factor is a compatibility rule, not a proved subtraction
error bound, a global epsilon, or a general approximation policy.

The policy then selects the first tied term, the last tied
term, or every tied term. Scale order is therefore relevant only through the
chosen tie policy and is never an undocumented fallback.

Every membership function is evaluated exactly once. The coordinate must
belong to every term universe so the result cannot present a partial score
vector as a complete classification.

## Consequences

- Callers can inspect all membership scores, confidence, tied maxima, and final
  selections without reevaluating membership functions.
- The default modern tie rule is `first`; callers requiring historical
  later-winner semantics can request `last` explicitly.
- `all` preserves ambiguity instead of discarding tied candidates.
- `confidence` is a membership maximum, not a calibrated probability.
- No-match results contain the full score tuple but no tied or selected terms.
- The historical `FuzzyScale.Fuzzy()` signature and return type remain
  unchanged under ADR-0001.

## Rejected alternatives

- **Always select one term:** rejected because zero or negligible coverage is
  meaningful evidence and must not be converted into false certainty.
- **Hide all non-winning scores:** rejected because it prevents confidence,
  ambiguity, overlap, and future diagnostic analysis.
- **Use an implicit epsilon or change the zero default:** rejected because
  numerical tolerance is a caller policy, not a global constant. The retained
  positive float-only boundary accommodation above is a documented
  compatibility convention and does not add tolerance to exact evidence.
- **Change historical `Fuzzy()` defaults:** rejected because ADR-0001 protects
  its callable compatibility surface and existing later-winner behavior.

## Acceptance and supersession

This ADR is **Accepted** on merge. Changing the meaning of confidence,
no-match comparison, tie tolerance, or ordered selection requires a
superseding decision with compatibility evidence.

### Amendment: explicit positive float boundary convention — 2026-10-05

[Task #281](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/281)
records this proposed clarification; it becomes accepted with the implementing
PR's human review and merge. The audit found that the established
`math.isclose` boundary behavior was absent from the literal absolute-only
statement. This amendment makes that existing float-only convention explicit
while retaining the default policy and runtime behavior. It does not infer a
mathematical error bound or introduce a new global tolerance.

[Task #283](https://github.com/Fuzzy-Technologies/FuzzyRoutines/issues/283)
separately repairs lossy rational comparisons and confines the compatibility
allowance to its declared positive float-only scope. The
[linguistic tests](../../tests/test_linguistic_terms.py) and
[mathematical guide](../mathematics/linguistic-term-model.md) supply the affected
boundary examples; their implementation fix remains a separate review
candidate.

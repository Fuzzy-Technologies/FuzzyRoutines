<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# ADR-0013: Linguistic Fuzzification Classification Policy

- Status: Accepted on merge
- Date: 2026-09-28
- Related planning task: #84
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

When a match exists, a term is tied for the maximum when its absolute grade
difference from $c$ does not exceed the explicit tie tolerance. The default
tolerance is zero. The policy then selects the first tied term, the last tied
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
- **Use an implicit epsilon:** rejected because numerical tolerance is a caller
  policy, not a global constant.
- **Change historical `Fuzzy()` defaults:** rejected because ADR-0001 protects
  its callable compatibility surface and existing later-winner behavior.

## Acceptance and supersession

This ADR is **Accepted** on merge. Changing the meaning of confidence,
no-match comparison, tie tolerance, or ordered selection requires a
superseding decision with compatibility evidence.

<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Typed Linguistic-Term Representation

## Scope

The modern API represents one linguistic term as an immutable association:

```text
LinguisticTerm(name, fuzzySet)
```

`name` is a non-empty string preserved exactly as declared. `fuzzySet` is a
modern `ScalarFuzzySet`; the representation does not silently adapt the
historical mutable `FuzzySet` class.

An ordered scale is represented by:

```text
LinguisticScale((term1, term2, ...))
```

The explicit tuple is retained without sorting or normalization. It must be
non-empty, contain only `LinguisticTerm` values, and use names that are unique
under Unicode case-insensitive comparison. Case-distinct declarations such as
`Low` and `LOW` are rejected because they make case-insensitive lookup
ambiguous.

`GetTermByName(termName, exactMatching=True)` performs complete-name lookup.
The default mode compares names exactly, including case. Passing
`exactMatching=False` compares Unicode case-folded names. Both modes return the
original declared `LinguisticTerm` object or `None`; neither performs substring,
prefix, approximate, or membership-based matching.

## Fuzzification and confidence

`Fuzzify(coordinate, policy)` evaluates every term exactly once and returns a
`FuzzificationResult`. Its ordered `memberships` tuple preserves every term and
grade, while `confidence` is the maximum grade rather than a probability.

`FuzzificationPolicy` makes both uncertain cases explicit:

- `minimumConfidence` rejects a classification when the maximum grade is less
  than or equal to the threshold; its zero default rejects zero coverage, and a
  positive value also rejects near-zero coverage;
- `tieTolerance` defines the absolute distance from the maximum treated as a
  tie;
- `tiePolicy` selects the `first`, `last`, or `all` tied terms in declared scale
  order.

Zero tie tolerance compares the validated grades directly. Distinct `Fraction`
grades remain distinct even when converting them to `float` would produce the
same value. A positive tolerance uses an inclusive distance comparison;
rational grades and mixed rational/float grades retain their exact represented
values during that comparison. The values recorded in the result and policy
are never converted.

When both grades and the explicitly positive tolerance are floats, the
existing boundary-rounding rule also accepts a distance relatively close to
the tolerance (`rel_tol=1e-12`, `abs_tol=0`). For example, grades `0.7` and `0.75`
are tied under tolerance `0.05` despite subtraction rounding. This rule does
not apply to zero tolerance or rational evidence.

The complete membership tuple remains available even for no-match results.
The coordinate must belong to every term universe; partial score vectors fail
closed. These semantics are fixed by
[ADR-0013](../adr/0013-linguistic-fuzzification-policy.md).

## Sampled scale diagnostics

`Diagnose(analysisDomain, policy)` evaluates an explicit endpoint-preserving
grid across a finite `IntegrationDomain`. Every term must use a
`ContinuousUniverse` containing the complete analysis domain. For each sampled
coordinate $x_j$, the result records all ordered memberships and

$$
c_j=\max_i\mu_{L_i}(x_j).
$$

With explicit activity threshold $\tau$, a term is active only when
$\mu_{L_i}(x_j)>\tau$. A sampled point is a gap when no term is active and an
overlap when at least two terms are active. Partition-quality evidence uses

$$
e_j=\left|\sum_i\mu_{L_i}(x_j)-1\right|.
$$

`ScaleDiagnosticsResult` exposes every sampled point plus coverage extrema and
mean, gap and overlap fractions, maximum simultaneous active-term count, and
mean and maximum partition error. `partitionTolerance` determines whether all
sampled errors are accepted. These observations are reproducible for the
declared domain, grid size, and tolerances, but they do not prove a continuous
property between grid coordinates. [ADR-0014](../adr/0014-sampled-scale-diagnostics.md)
fixes the complete evidence boundary.

## Compatibility

The historical `fuzzyroutines.FuzzyRoutines.FuzzyScale` remains available.
Its `levels` property continues to expose and accept the original mutable list
of dictionaries with both required `name` and `fSet` keys. Its protected
`GetLevelByName(levelName, exactMatching=True)` call shape remains available:
the default performs exact complete-name lookup, while `False` performs
case-insensitive complete-name lookup through the historical uppercase map.
Names that collide ignoring case are rejected so this lookup remains
unambiguous. The modern types are additions; they do not replace the mutable
dictionary compatibility facade. Historical `Fuzzy()` continues selecting the
later level on an exact tie. The modern equivalent is an explicit
`FuzzificationPolicy(tiePolicy="last")` rather than a hidden default.

## Example

```python
from fuzzyroutines import (
    ContinuousUniverse,
    FuzzificationPolicy,
    IntegrationDomain,
    LinguisticScale,
    LinguisticTerm,
    ScaleDiagnosticsPolicy,
    ScalarFuzzySet,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
low = LinguisticTerm("Low", ScalarFuzzySet(universe, lambda value: 1.0 - value))
high = LinguisticTerm("High", ScalarFuzzySet(universe, lambda value: value))
scale = LinguisticScale((low, high))
assert scale.GetTermByName("Low") is low
assert scale.GetTermByName("high", exactMatching=False) is high
result = scale.Fuzzify(
    0.5,
    FuzzificationPolicy(tiePolicy="all", minimumConfidence=0.1),
)
assert result.confidence == 0.5
assert result.selectedTerms == (low, high)

diagnostics = scale.Diagnose(
    IntegrationDomain(0.0, 1.0),
    ScaleDiagnosticsPolicy(sampleCount=101),
)
assert diagnostics.minimumCoverage == 0.5
assert diagnostics.gapPoints == ()
```

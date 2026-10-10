<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Audit a linguistic scale

**Question:** can a scale produce ties, weak matches, or no coverage? Diagnose
the design before choosing an operational label-selection policy.

```python
from fuzzyroutines import (
    ContinuousUniverse, FuzzificationPolicy, IntegrationDomain, LinguisticScale,
    LinguisticTerm, ScalarFuzzySet, ScaleDiagnosticsPolicy, Triangle,
)

universe = ContinuousUniverse(0, 10, leftClosed=True, rightClosed=True)
scale = LinguisticScale((
    LinguisticTerm("Low", ScalarFuzzySet(universe, Triangle(0, 2, 6))),
    LinguisticTerm("High", ScalarFuzzySet(universe, Triangle(4, 8, 10))),
))
tied = scale.Fuzzify(5, FuzzificationPolicy(tiePolicy="all"))
assert tied.isTie and tied.confidence == 0.25
assert tuple(term.name for term in tied.selectedTerms) == ("Low", "High")
assert scale.Fuzzify(5).selectedTerms[0].name == "Low"
assert not scale.Fuzzify(5, FuzzificationPolicy(minimumConfidence=0.3)).isMatch

gappyScale = LinguisticScale((
    LinguisticTerm("Low", ScalarFuzzySet(universe, Triangle(0, 2, 4))),
    LinguisticTerm("High", ScalarFuzzySet(universe, Triangle(6, 8, 10))),
))
audit = gappyScale.Diagnose(IntegrationDomain(0, 10), ScaleDiagnosticsPolicy(sampleCount=11))
assert tuple(point.coordinate for point in audit.gapPoints) == (0, 4, 5, 6, 10)
assert audit.gapFraction == 5 / 11
assert not gappyScale.Fuzzify(5).isMatch
print(audit.gapFraction, audit.maximumPartitionError)
```

[![Overlapping scale on the left and sampled coverage gaps on the right](../assets/figures/scale-audit.svg)](../assets/figures/scale-audit.svg)

At score 5, the first scale has two grades of 0.25. `tiePolicy="all"` keeps
both. The default first-term policy chooses *Low*; `"last"` would choose
*High*. A minimum confidence of 0.3 declines this weak tie. Ordering is therefore
part of a first/last policy's model contract.

The second scale has zero membership for both terms at five of the eleven
audit coordinates: 0, 4, 5, 6, and 10. Thus the **sampled** gap fraction is
$5/11\approx0.454545$. This is a fraction of inspected coordinates, not
the continuous fraction of interval length. Endpoints count in this grid.

The default membership threshold is zero: a grade must be strictly positive
to be active. `membershipThreshold` changes that criterion; it does not alter
the model itself. Partition error measures how far the sum of grades is from
one, not an accuracy error against labelled observations. The examples are
deliberately not a partition of unity.

**Use in your project:** inspect individual diagnostic points, not only
aggregate fractions. Sample known transition boundaries and meaningful physical
settings in addition to a uniform grid. Grid diagnostics cannot establish
global continuous coverage or exclude narrow gaps between observations.

```bash
python -I examples/guide.py --scenario scale-audit
```

Continue with [a custom quality model](custom.md).

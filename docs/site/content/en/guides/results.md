<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Inspect and reconstruct result records

Result records preserve the evidence behind a calculation. Prefer the producer
function for ordinary use. Explicit constructors are useful when passing an
already verified record between components; constructor validation checks its
documented consistency rules, not an independent proof of the mathematics.
Modern records are immutable. Keep units and model assumptions with them in
your application. Every block below runs independently.

## Exact continuous and discrete geometry

```python
from fuzzyroutines import (
    ContinuousFuzzyProperties, ContinuousUniverse, DeriveProperties,
    DiscreteFuzzyProperties, DiscreteUniverse, Triangle,
)

model = Triangle(0, 1, 2)
continuous = DeriveProperties(model, ContinuousUniverse(0, 2, leftClosed=True, rightClosed=True))
continuousCopy = ContinuousFuzzyProperties(
    continuous.universe, continuous.positiveSupport, continuous.supportClosure,
    continuous.core, continuous.boundary, continuous.height,
)
assert continuousCopy == continuous and continuousCopy.isExact
discrete = DeriveProperties(model, DiscreteUniverse((0, 0.5, 1, 1.5, 2)))
discreteCopy = DiscreteFuzzyProperties(
    discrete.universe, discrete.positiveSupport, discrete.supportClosure,
    discrete.core, discrete.boundary, discrete.height,
)
assert discreteCopy == discrete and discreteCopy.isExact
assert discrete.core.Contains(1) and not discrete.positiveSupport.Contains(0)
assert discrete.boundary.points == (0.5, 1.5) and discrete.height == 1
print(continuous.height, discrete.positiveSupport.points, discrete.boundary.points)
```

The continuous positive support is the open interval (0, 2); its closure is
[0, 2]. On the discrete universe the positive support is the three points
{0.5, 1, 1.5}, and its closure is the same set. Both cores are {1}. A grade-zero
endpoint belongs to the continuous support closure without belonging to the
positive support. Discrete topology gives a different closure.

## Sampled properties retain their grid

```python
from fuzzyroutines import IntegrationDomain, SampledFuzzyProperties, SampleProperties, Triangle

sampled = SampleProperties(Triangle(0, 1, 2), IntegrationDomain(0, 2), sampleCount=5)
copy = SampledFuzzyProperties(
    sampled.analysisDomain, sampled.sampleCount, sampled.coordinates, sampled.grades,
    sampled.positiveSupportSamples, sampled.coreSamples, sampled.boundarySamples,
    sampled.heightEstimate, sampled.method,
)
assert copy == sampled and not copy.isExact
assert copy.coordinates == (0, 0.5, 1, 1.5, 2)
assert copy.grades == (0, 0.5, 1, 0.5, 0)
assert copy.coreSamples.points == (1,) and copy.heightEstimate == 1
print(copy.coordinates, copy.grades, copy.method)
```

The grid happens to hit this peak. A different grid could miss a narrow peak,
so `heightEstimate` is an observation rather than an exact supremum. Direct
construction checks ordering, endpoints, region subsets and the observed
maximum; it does not recompute all region classifications or prove equal grid
spacing. Prefer `SampleProperties` when creating new evidence.

## A sampled alpha-cut is a table, not an interval solution

```python
from fuzzyroutines import (
    ContinuousUniverse, IntegrationDomain, SampleAlphaCut,
    SampledAlphaCut, ScalarFuzzySet, Triangle,
)

fuzzySet = ScalarFuzzySet(ContinuousUniverse(0, 2, leftClosed=True, rightClosed=True), Triangle(0, 1, 2))
cut = SampleAlphaCut(fuzzySet, 0.5, IntegrationDomain(0, 2), sampleCount=5)
copy = SampledAlphaCut(
    cut.alpha, cut.analysisDomain, cut.sampleCount, cut.coordinates,
    cut.grades, cut.cutSamples, cut.method,
)
assert copy == cut and not copy.isExact
assert copy.cutSamples.points == (0.5, 1, 1.5)
print(copy.alpha, copy.cutSamples.points)
```

The weak boundary includes grade 0.5. The analytical interval for this triangle
is [0.5, 1.5], but `SampleAlphaCut` returns only qualifying grid coordinates.
Its constructor checks the cut against all supplied grades. The provenance
label does not independently establish equal spacing for a manually supplied
table. See [alpha cuts](alpha-cuts.md).

## A classification keeps all grades and its selection policy

```python
from fuzzyroutines import (
    DiscreteUniverse, FuzzificationPolicy, FuzzificationResult,
    LinguisticScale, LinguisticTerm, ScalarFuzzySet, TermMembership, Triangle,
)

term = LinguisticTerm("Preferred", ScalarFuzzySet(DiscreteUniverse((0, 1, 2)), Triangle(0, 1, 2)))
scale = LinguisticScale((term,))
assert scale.GetTermByName("Preferred") is term
assert scale.GetTermByName("PREFERRED", exactMatching=False) is term
assert scale.GetTermByName("Missing") is None
policy = FuzzificationPolicy(tiePolicy="all")
result = scale.Fuzzify(1, policy)
copy = FuzzificationResult((TermMembership(term, 1),), 1, policy, (term,), (term,))
assert copy == result and copy.isMatch and not copy.isTie
assert copy.memberships[0].grade == copy.confidence == 1
print(copy.selectedTerms[0].name, copy.confidence)
```

`memberships` retains the ordered complete term vector; `tiedTerms` and
`selectedTerms` explain which maxima were retained and selected. Confidence is
the greatest membership, not a probability. With the default threshold zero,
zero coverage produces no match. A grade equal to `minimumConfidence` also
produces no match. See [risk and abstention](risk.md) and [ties](scale-audit.md).

## Read every scale diagnostic with its sampling limits

```python
from math import isclose
from fuzzyroutines import (
    ContinuousUniverse, IntegrationDomain, LinguisticScale, LinguisticTerm,
    ScalarFuzzySet, ScaleDiagnosticPoint, ScaleDiagnosticsPolicy,
    ScaleDiagnosticsResult, TermMembership, Triangle,
)

universe = ContinuousUniverse(0, 2, leftClosed=True, rightClosed=True)
first = LinguisticTerm("Preferred A", ScalarFuzzySet(universe, Triangle(0, 1, 2)))
second = LinguisticTerm("Preferred B", ScalarFuzzySet(universe, Triangle(0, 1, 2)))
scale = LinguisticScale((first, second))
report = scale.Diagnose(IntegrationDomain(0, 2), ScaleDiagnosticsPolicy(sampleCount=3))
point = ScaleDiagnosticPoint(1, (TermMembership(first, 1), TermMembership(second, 1)), 0)
assert point == report.points[1]
assert point.maximumMembership == 1 and point.membershipSum == 2
assert point.activeTerms == (first, second) and point.isOverlap and not point.isGap
assert point.partitionError == 1
copy = ScaleDiagnosticsResult(report.analysisDomain, report.policy, report.points)
assert copy == report
assert tuple(point.coordinate for point in copy.gapPoints) == (0, 2)
assert tuple(point.coordinate for point in copy.overlapPoints) == (1,)
assert isclose(copy.gapFraction, 2 / 3) and isclose(copy.overlapFraction, 1 / 3)
assert copy.minimumCoverage == 0 and copy.maximumCoverage == 1
assert isclose(copy.meanCoverage, 1 / 3) and copy.maximumActiveTermCount == 2
assert copy.meanPartitionError == copy.maximumPartitionError == 1
assert not copy.isPartitionWithinTolerance
print(copy.gapFraction, copy.overlapFraction, copy.meanCoverage)
```

The deliberately duplicated triangles make the middle observation an overlap
and the two feet gaps. Coverage means the maximum grade at a coordinate; it is
distinct from the sum of all grades. Partition error is the absolute difference
between that sum and one. The fractions and means count the three observations,
not interval lengths or continuous integrals. A term is active only above the
policy's `membershipThreshold`; equality is inactive. No global coverage or
partition proof follows from this table.

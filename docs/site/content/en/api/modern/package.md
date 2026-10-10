<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Package exports

The root package re-exports the following modern API names. Each link resolves
to the object's canonical module-owned documentation so the reference does not
duplicate API contracts or create competing anchors. The literal root `__all__`
is the authoritative wildcard surface. Membership factories and typing contracts
are available directly from the root; imported modules, private helpers, and
historical mutable classes are outside that surface.

The historical wildcard entry point remains
`from fuzzyroutines.FuzzyRoutines import *`. Its explicit `__all__` contains
only the fifteen supported compatibility symbols; historical helper leaks
`math` and `copy` are no longer imported. Use Python's `math` and `copy` modules
directly if your application previously obtained them through the facade.

| Export                      | Canonical API object                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------ |
| `AlphaCut`                  | [`AlphaCut`][fuzzyroutines.alphacuts.AlphaCut]                                       |
| `Bell`                      | [`Bell`][fuzzyroutines.membership.Bell]                                              |
| `Centroid`                  | [`Centroid`][fuzzyroutines.defuzzification.Centroid]                                 |
| `CentroidConvergenceError`  | [`CentroidConvergenceError`][fuzzyroutines.defuzzification.CentroidConvergenceError] |
| `CentroidPolicy`            | [`CentroidPolicy`][fuzzyroutines.defuzzification.CentroidPolicy]                     |
| `ComparisonDomain`          | [`ComparisonDomain`][fuzzyroutines.relations.ComparisonDomain]                       |
| `ComparisonPolicy`          | [`ComparisonPolicy`][fuzzyroutines.relations.ComparisonPolicy]                       |
| `Complement`                | [`Complement`][fuzzyroutines.fuzzysets.Complement]                                   |
| `ContinuousFuzzyProperties` | [`ContinuousFuzzyProperties`][fuzzyroutines.properties.ContinuousFuzzyProperties]    |
| `ContinuousInterval`        | [`ContinuousInterval`][fuzzyroutines.properties.ContinuousInterval]                  |
| `ContinuousRegion`          | [`ContinuousRegion`][fuzzyroutines.properties.ContinuousRegion]                      |
| `ContinuousUniverse`        | [`ContinuousUniverse`][fuzzyroutines.domain.ContinuousUniverse]                      |
| `DeriveProperties`          | [`DeriveProperties`][fuzzyroutines.properties.DeriveProperties]                      |
| `Difference`                | [`Difference`][fuzzyroutines.fuzzysets.Difference]                                   |
| `DiscreteFuzzyProperties`   | [`DiscreteFuzzyProperties`][fuzzyroutines.properties.DiscreteFuzzyProperties]        |
| `DiscreteRegion`            | [`DiscreteRegion`][fuzzyroutines.properties.DiscreteRegion]                          |
| `DiscreteUniverse`          | [`DiscreteUniverse`][fuzzyroutines.domain.DiscreteUniverse]                          |
| `EqualOnDomain`             | [`EqualOnDomain`][fuzzyroutines.relations.EqualOnDomain]                             |
| `FuzzificationPolicy`       | [`FuzzificationPolicy`][fuzzyroutines.linguistic.FuzzificationPolicy]                |
| `FuzzificationResult`       | [`FuzzificationResult`][fuzzyroutines.linguistic.FuzzificationResult]                |
| `Gaussian`                  | [`Gaussian`][fuzzyroutines.membership.Gaussian]                                      |
| `HarringtonDesirability`    | [`HarringtonDesirability`][fuzzyroutines.membership.HarringtonDesirability]          |
| `Height`                    | [`Height`][fuzzyroutines.fuzzysets.Height]                                           |
| `Hyperbolic`                | [`Hyperbolic`][fuzzyroutines.membership.Hyperbolic]                                  |
| `IncludedOnDomain`          | [`IncludedOnDomain`][fuzzyroutines.relations.IncludedOnDomain]                       |
| `IntegrationDomain`         | [`IntegrationDomain`][fuzzyroutines.domain.IntegrationDomain]                        |
| `Intersection`              | [`Intersection`][fuzzyroutines.fuzzysets.Intersection]                               |
| `IsNormal`                  | [`IsNormal`][fuzzyroutines.fuzzysets.IsNormal]                                       |
| `LinguisticScale`           | [`LinguisticScale`][fuzzyroutines.linguistic.LinguisticScale]                        |
| `LinguisticTerm`            | [`LinguisticTerm`][fuzzyroutines.linguistic.LinguisticTerm]                          |
| `Logistic`                  | [`Logistic`][fuzzyroutines.membership.Logistic]                                      |
| `MembershipCallable`        | [`MembershipCallable`][fuzzyroutines.membership.MembershipCallable]                  |
| `MembershipFunction`        | [`MembershipFunction`][fuzzyroutines.membership.MembershipFunction]                  |
| `MembershipScalar`          | [`MembershipScalar`][fuzzyroutines.membership.MembershipScalar]                      |
| `NegationPolicy`            | [`NegationPolicy`][fuzzyroutines.operators.NegationPolicy]                           |
| `Normalize`                 | [`Normalize`][fuzzyroutines.fuzzysets.Normalize]                                     |
| `SNormPolicy`               | [`SNormPolicy`][fuzzyroutines.operators.SNormPolicy]                                 |
| `SShoulder`                 | [`SShoulder`][fuzzyroutines.membership.SShoulder]                                    |
| `SampleAlphaCut`            | [`SampleAlphaCut`][fuzzyroutines.alphacuts.SampleAlphaCut]                           |
| `SampleProperties`          | [`SampleProperties`][fuzzyroutines.properties.SampleProperties]                      |
| `SampledAlphaCut`           | [`SampledAlphaCut`][fuzzyroutines.alphacuts.SampledAlphaCut]                         |
| `SampledFuzzyProperties`    | [`SampledFuzzyProperties`][fuzzyroutines.properties.SampledFuzzyProperties]          |
| `ScalarFuzzySet`            | [`ScalarFuzzySet`][fuzzyroutines.fuzzysets.ScalarFuzzySet]                           |
| `ScaleDiagnosticPoint`      | [`ScaleDiagnosticPoint`][fuzzyroutines.linguistic.ScaleDiagnosticPoint]              |
| `ScaleDiagnosticsPolicy`    | [`ScaleDiagnosticsPolicy`][fuzzyroutines.linguistic.ScaleDiagnosticsPolicy]          |
| `ScaleDiagnosticsResult`    | [`ScaleDiagnosticsResult`][fuzzyroutines.linguistic.ScaleDiagnosticsResult]          |
| `TNormPolicy`               | [`TNormPolicy`][fuzzyroutines.operators.TNormPolicy]                                 |
| `TermMembership`            | [`TermMembership`][fuzzyroutines.linguistic.TermMembership]                          |
| `Trapezoid`                 | [`Trapezoid`][fuzzyroutines.membership.Trapezoid]                                    |
| `Triangle`                  | [`Triangle`][fuzzyroutines.membership.Triangle]                                      |
| `Union`                     | [`Union`][fuzzyroutines.fuzzysets.Union]                                             |

::: fuzzyroutines
    options:
      members: false

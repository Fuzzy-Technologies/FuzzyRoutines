<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Public API example index

All 193 inventoried public symbols are linked to executed examples (31 standalone Python blocks). Root exports are verified aliases of the corresponding module objects.

Functions, constructors, methods and properties require actual execution; imports alone do not count. Result constructors also run when their producer returns them; see [result records](results.md) for explicit reconstruction. The two typing contracts require a real annotation, and exception classes require constructed instances. Private helpers and generated dataclass methods remain outside the authored public inventory.

This index establishes example availability, not independent proof of every mathematical branch. Review the linked explanations, limits and assertions. CI regenerates the evidence against an installed package and rejects stale index content. At most two examples per symbol are shown.

| Public symbol                                                                | Executable examples                                                                                                |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `fuzzyroutines.AlphaCut`                                                     | [alpha-cuts, block 1](alpha-cuts.md)                                                                               |
| `fuzzyroutines.Bell`                                                         | [membership-families, block 1](membership-families.md); [universal-fuzzy-scale, block 2](universal-fuzzy-scale.md) |
| `fuzzyroutines.Centroid`                                                     | [membership, block 1](../api/modern/membership.md); [api-recipes, block 5](api-recipes.md)                         |
| `fuzzyroutines.CentroidConvergenceError`                                     | [errors, block 1](errors.md)                                                                                       |
| `fuzzyroutines.CentroidPolicy`                                               | [membership, block 1](../api/modern/membership.md); [api-recipes, block 5](api-recipes.md)                         |
| `fuzzyroutines.ComparisonDomain`                                             | [api-recipes, block 4](api-recipes.md)                                                                             |
| `fuzzyroutines.ComparisonPolicy`                                             | [api-recipes, block 4](api-recipes.md); [custom, block 1](custom.md)                                               |
| `fuzzyroutines.Complement`                                                   | [alarm, block 1](alarm.md)                                                                                         |
| `fuzzyroutines.ContinuousFuzzyProperties`                                    | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.ContinuousInterval`                                           | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.ContinuousRegion`                                             | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.ContinuousUniverse`                                           | [membership, block 1](../api/modern/membership.md); [alarm, block 1](alarm.md)                                     |
| `fuzzyroutines.DeriveProperties`                                             | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.Difference`                                                   | [alarm, block 1](alarm.md)                                                                                         |
| `fuzzyroutines.DiscreteFuzzyProperties`                                      | [results, block 1](results.md)                                                                                     |
| `fuzzyroutines.DiscreteRegion`                                               | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.DiscreteUniverse`                                             | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 1](api-recipes.md)                                       |
| `fuzzyroutines.EqualOnDomain`                                                | [api-recipes, block 4](api-recipes.md); [custom, block 1](custom.md)                                               |
| `fuzzyroutines.FuzzificationPolicy`                                          | [results, block 4](results.md); [risk, block 1](risk.md)                                                           |
| `fuzzyroutines.FuzzificationResult`                                          | [results, block 4](results.md); [risk, block 1](risk.md)                                                           |
| `fuzzyroutines.FuzzyRoutines.DiapasonParser`                                 | [historical-recipes, block 1](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzyAND`                                       | [historical-recipes, block 2](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzyNOT`                                       | [historical-recipes, block 2](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzyNOTParabolic`                              | [historical-recipes, block 2](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzyOR`                                        | [historical-recipes, block 2](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale`                                     | [historical-recipes, block 5](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.Fuzzy`                               | [historical-recipes, block 5](historical-recipes.md); [universal-fuzzy-scale, block 1](universal-fuzzy-scale.md)   |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.GetLevelByName`                      | [historical-recipes, block 5](historical-recipes.md); [universal-fuzzy-scale, block 1](universal-fuzzy-scale.md)   |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.levels`                              | [historical-recipes, block 5](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.name`                                | [historical-recipes, block 5](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzySet`                                       | [historical-recipes, block 4](historical-recipes.md); [historical-recipes, block 5](historical-recipes.md)         |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.Defuz`                                 | [historical-recipes, block 4](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.defuzValue`                            | [historical-recipes, block 4](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.mFunction`                             | [historical-recipes, block 4](historical-recipes.md); [historical-recipes, block 5](historical-recipes.md)         |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.name`                                  | [historical-recipes, block 4](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.supportSet`                            | [historical-recipes, block 4](historical-recipes.md); [universal-fuzzy-scale, block 1](universal-fuzzy-scale.md)   |
| `fuzzyroutines.FuzzyRoutines.IsCorrectFuzzyNumberValue`                      | [historical-recipes, block 1](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.IsNumber`                                       | [historical-recipes, block 1](historical-recipes.md); [historical-recipes, block 2](historical-recipes.md)         |
| `fuzzyroutines.FuzzyRoutines.MFunction`                                      | [historical-recipes, block 3](historical-recipes.md); [historical-recipes, block 4](historical-recipes.md)         |
| `fuzzyroutines.FuzzyRoutines.MFunction.Bell`                                 | [historical-recipes, block 3](historical-recipes.md); [historical-recipes, block 5](historical-recipes.md)         |
| `fuzzyroutines.FuzzyRoutines.MFunction.Desirability`                         | [historical-recipes, block 3](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.MFunction.Exponential`                          | [historical-recipes, block 3](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.MFunction.Hyperbolic`                           | [historical-recipes, block 3](historical-recipes.md); [historical-recipes, block 5](historical-recipes.md)         |
| `fuzzyroutines.FuzzyRoutines.MFunction.Parabolic`                            | [historical-recipes, block 3](historical-recipes.md); [historical-recipes, block 5](historical-recipes.md)         |
| `fuzzyroutines.FuzzyRoutines.MFunction.Sigmoidal`                            | [historical-recipes, block 3](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.MFunction.Trapezium`                            | [historical-recipes, block 3](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.MFunction.Triangle`                             | [historical-recipes, block 3](historical-recipes.md); [historical-recipes, block 5](historical-recipes.md)         |
| `fuzzyroutines.FuzzyRoutines.MFunction.name`                                 | [historical-recipes, block 3](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.MFunction.parameters`                           | [historical-recipes, block 3](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.SCoNorm`                                        | [historical-recipes, block 2](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.SCoNormCompose`                                 | [historical-recipes, block 2](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.TNorm`                                          | [historical-recipes, block 2](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.TNormCompose`                                   | [historical-recipes, block 2](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale`                            | [historical-recipes, block 5](historical-recipes.md); [universal-fuzzy-scale, block 1](universal-fuzzy-scale.md)   |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levels`                     | [historical-recipes, block 5](historical-recipes.md); [universal-fuzzy-scale, block 1](universal-fuzzy-scale.md)   |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levelsNames`                | [historical-recipes, block 5](historical-recipes.md)                                                               |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levelsNamesUpper`           | [historical-recipes, block 5](historical-recipes.md)                                                               |
| `fuzzyroutines.Gaussian`                                                     | [membership-families, block 1](membership-families.md)                                                             |
| `fuzzyroutines.HarringtonDesirability`                                       | [membership-families, block 1](membership-families.md)                                                             |
| `fuzzyroutines.Height`                                                       | [api-recipes, block 2](api-recipes.md); [custom, block 1](custom.md)                                               |
| `fuzzyroutines.Hyperbolic`                                                   | [membership-families, block 1](membership-families.md); [universal-fuzzy-scale, block 2](universal-fuzzy-scale.md) |
| `fuzzyroutines.IncludedOnDomain`                                             | [api-recipes, block 4](api-recipes.md); [custom, block 1](custom.md)                                               |
| `fuzzyroutines.IntegrationDomain`                                            | [exceptions, block 1](../api/modern/exceptions.md); [membership, block 1](../api/modern/membership.md)             |
| `fuzzyroutines.Intersection`                                                 | [alarm, block 1](alarm.md)                                                                                         |
| `fuzzyroutines.IsNormal`                                                     | [api-recipes, block 2](api-recipes.md)                                                                             |
| `fuzzyroutines.LinguisticScale`                                              | [results, block 4](results.md); [results, block 5](results.md)                                                     |
| `fuzzyroutines.LinguisticTerm`                                               | [results, block 4](results.md); [results, block 5](results.md)                                                     |
| `fuzzyroutines.Logistic`                                                     | [membership-families, block 1](membership-families.md)                                                             |
| `fuzzyroutines.MembershipCallable`                                           | [membership, block 1](../api/modern/membership.md); [custom, block 1](custom.md)                                   |
| `fuzzyroutines.MembershipFunction`                                           | [alarm, block 1](alarm.md); [alpha-cuts, block 1](alpha-cuts.md)                                                   |
| `fuzzyroutines.MembershipScalar`                                             | [membership, block 1](../api/modern/membership.md); [alarm, block 1](alarm.md)                                     |
| `fuzzyroutines.NegationPolicy`                                               | [alarm, block 1](alarm.md); [api-recipes, block 3](api-recipes.md)                                                 |
| `fuzzyroutines.Normalize`                                                    | [custom, block 1](custom.md)                                                                                       |
| `fuzzyroutines.SNormPolicy`                                                  | [alarm, block 1](alarm.md); [api-recipes, block 3](api-recipes.md)                                                 |
| `fuzzyroutines.SShoulder`                                                    | [alarm, block 1](alarm.md); [membership-families, block 1](membership-families.md)                                 |
| `fuzzyroutines.SampleAlphaCut`                                               | [alpha-cuts, block 1](alpha-cuts.md); [results, block 3](results.md)                                               |
| `fuzzyroutines.SampleProperties`                                             | [api-recipes, block 2](api-recipes.md); [results, block 2](results.md)                                             |
| `fuzzyroutines.SampledAlphaCut`                                              | [alpha-cuts, block 1](alpha-cuts.md); [results, block 3](results.md)                                               |
| `fuzzyroutines.SampledFuzzyProperties`                                       | [api-recipes, block 2](api-recipes.md); [results, block 2](results.md)                                             |
| `fuzzyroutines.ScalarFuzzySet`                                               | [membership, block 1](../api/modern/membership.md); [alarm, block 1](alarm.md)                                     |
| `fuzzyroutines.ScaleDiagnosticPoint`                                         | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.ScaleDiagnosticsPolicy`                                       | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.ScaleDiagnosticsResult`                                       | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.TNormPolicy`                                                  | [alarm, block 1](alarm.md); [api-recipes, block 3](api-recipes.md)                                                 |
| `fuzzyroutines.TermMembership`                                               | [results, block 4](results.md); [results, block 5](results.md)                                                     |
| `fuzzyroutines.Trapezoid`                                                    | [membership-families, block 1](membership-families.md)                                                             |
| `fuzzyroutines.Triangle`                                                     | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.Union`                                                        | [alarm, block 1](alarm.md); [centroid, block 1](centroid.md)                                                       |
| `fuzzyroutines.alphacuts.AlphaCut`                                           | [alpha-cuts, block 1](alpha-cuts.md)                                                                               |
| `fuzzyroutines.alphacuts.SampleAlphaCut`                                     | [alpha-cuts, block 1](alpha-cuts.md); [results, block 3](results.md)                                               |
| `fuzzyroutines.alphacuts.SampledAlphaCut`                                    | [alpha-cuts, block 1](alpha-cuts.md); [results, block 3](results.md)                                               |
| `fuzzyroutines.alphacuts.SampledAlphaCut.isExact`                            | [alpha-cuts, block 1](alpha-cuts.md); [results, block 3](results.md)                                               |
| `fuzzyroutines.defuzzification.Centroid`                                     | [membership, block 1](../api/modern/membership.md); [api-recipes, block 5](api-recipes.md)                         |
| `fuzzyroutines.defuzzification.CentroidConvergenceError`                     | [errors, block 1](errors.md)                                                                                       |
| `fuzzyroutines.defuzzification.CentroidPolicy`                               | [membership, block 1](../api/modern/membership.md); [api-recipes, block 5](api-recipes.md)                         |
| `fuzzyroutines.domain.ContinuousUniverse`                                    | [membership, block 1](../api/modern/membership.md); [alarm, block 1](alarm.md)                                     |
| `fuzzyroutines.domain.ContinuousUniverse.Contains`                           | [membership, block 1](../api/modern/membership.md); [alarm, block 1](alarm.md)                                     |
| `fuzzyroutines.domain.ContinuousUniverse.isBounded`                          | [api-recipes, block 1](api-recipes.md)                                                                             |
| `fuzzyroutines.domain.DiscreteUniverse`                                      | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 1](api-recipes.md)                                       |
| `fuzzyroutines.domain.DiscreteUniverse.Contains`                             | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 1](api-recipes.md)                                       |
| `fuzzyroutines.domain.IntegrationDomain`                                     | [exceptions, block 1](../api/modern/exceptions.md); [membership, block 1](../api/modern/membership.md)             |
| `fuzzyroutines.domain.IntegrationDomain.Contains`                            | [api-recipes, block 1](api-recipes.md)                                                                             |
| `fuzzyroutines.domain.IntegrationDomain.FromLegacyInterval`                  | [api-recipes, block 1](api-recipes.md); [historical-recipes, block 4](historical-recipes.md)                       |
| `fuzzyroutines.domain.IntegrationDomain.ToLegacyInterval`                    | [api-recipes, block 1](api-recipes.md); [historical-recipes, block 4](historical-recipes.md)                       |
| `fuzzyroutines.domain.IntegrationDomain.ValidateWithin`                      | [membership, block 1](../api/modern/membership.md); [alpha-cuts, block 1](alpha-cuts.md)                           |
| `fuzzyroutines.exceptions.FuzzyRoutinesError`                                | [errors, block 1](errors.md)                                                                                       |
| `fuzzyroutines.exceptions.InvalidDomainError`                                | [errors, block 1](errors.md)                                                                                       |
| `fuzzyroutines.exceptions.InvalidParameterError`                             | [errors, block 1](errors.md)                                                                                       |
| `fuzzyroutines.exceptions.InvalidParameterTypeError`                         | [errors, block 1](errors.md)                                                                                       |
| `fuzzyroutines.exceptions.NumericalError`                                    | [errors, block 1](errors.md)                                                                                       |
| `fuzzyroutines.exceptions.UndefinedResultError`                              | [errors, block 1](errors.md)                                                                                       |
| `fuzzyroutines.fuzzysets.Complement`                                         | [alarm, block 1](alarm.md)                                                                                         |
| `fuzzyroutines.fuzzysets.Difference`                                         | [alarm, block 1](alarm.md)                                                                                         |
| `fuzzyroutines.fuzzysets.Height`                                             | [api-recipes, block 2](api-recipes.md); [custom, block 1](custom.md)                                               |
| `fuzzyroutines.fuzzysets.Intersection`                                       | [alarm, block 1](alarm.md)                                                                                         |
| `fuzzyroutines.fuzzysets.IsNormal`                                           | [api-recipes, block 2](api-recipes.md)                                                                             |
| `fuzzyroutines.fuzzysets.Normalize`                                          | [custom, block 1](custom.md)                                                                                       |
| `fuzzyroutines.fuzzysets.ScalarFuzzySet`                                     | [membership, block 1](../api/modern/membership.md); [alarm, block 1](alarm.md)                                     |
| `fuzzyroutines.fuzzysets.ScalarFuzzySet.Membership`                          | [membership, block 1](../api/modern/membership.md); [alarm, block 1](alarm.md)                                     |
| `fuzzyroutines.fuzzysets.Union`                                              | [alarm, block 1](alarm.md); [centroid, block 1](centroid.md)                                                       |
| `fuzzyroutines.linguistic.FuzzificationPolicy`                               | [results, block 4](results.md); [risk, block 1](risk.md)                                                           |
| `fuzzyroutines.linguistic.FuzzificationResult`                               | [results, block 4](results.md); [risk, block 1](risk.md)                                                           |
| `fuzzyroutines.linguistic.FuzzificationResult.isMatch`                       | [results, block 4](results.md); [risk, block 1](risk.md)                                                           |
| `fuzzyroutines.linguistic.FuzzificationResult.isTie`                         | [results, block 4](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.LinguisticScale`                                   | [results, block 4](results.md); [results, block 5](results.md)                                                     |
| `fuzzyroutines.linguistic.LinguisticScale.Diagnose`                          | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.LinguisticScale.Fuzzify`                           | [results, block 4](results.md); [risk, block 1](risk.md)                                                           |
| `fuzzyroutines.linguistic.LinguisticScale.GetTermByName`                     | [results, block 4](results.md)                                                                                     |
| `fuzzyroutines.linguistic.LinguisticTerm`                                    | [results, block 4](results.md); [results, block 5](results.md)                                                     |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint`                              | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.activeTerms`                  | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.isGap`                        | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.isOverlap`                    | [results, block 5](results.md)                                                                                     |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.maximumMembership`            | [results, block 5](results.md)                                                                                     |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.membershipSum`                | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.partitionError`               | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.ScaleDiagnosticsPolicy`                            | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult`                            | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.gapFraction`                | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.gapPoints`                  | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.isPartitionWithinTolerance` | [results, block 5](results.md)                                                                                     |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumActiveTermCount`     | [results, block 5](results.md)                                                                                     |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumCoverage`            | [results, block 5](results.md)                                                                                     |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumPartitionError`      | [results, block 5](results.md); [scale-audit, block 1](scale-audit.md)                                             |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.meanCoverage`               | [results, block 5](results.md)                                                                                     |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.meanPartitionError`         | [results, block 5](results.md)                                                                                     |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.minimumCoverage`            | [results, block 5](results.md)                                                                                     |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.overlapFraction`            | [results, block 5](results.md)                                                                                     |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.overlapPoints`              | [results, block 5](results.md)                                                                                     |
| `fuzzyroutines.linguistic.TermMembership`                                    | [results, block 4](results.md); [results, block 5](results.md)                                                     |
| `fuzzyroutines.membership.Bell`                                              | [membership-families, block 1](membership-families.md); [universal-fuzzy-scale, block 2](universal-fuzzy-scale.md) |
| `fuzzyroutines.membership.Gaussian`                                          | [membership-families, block 1](membership-families.md)                                                             |
| `fuzzyroutines.membership.HarringtonDesirability`                            | [membership-families, block 1](membership-families.md)                                                             |
| `fuzzyroutines.membership.Hyperbolic`                                        | [membership-families, block 1](membership-families.md); [universal-fuzzy-scale, block 2](universal-fuzzy-scale.md) |
| `fuzzyroutines.membership.Logistic`                                          | [membership-families, block 1](membership-families.md)                                                             |
| `fuzzyroutines.membership.MembershipCallable`                                | [membership, block 1](../api/modern/membership.md); [custom, block 1](custom.md)                                   |
| `fuzzyroutines.membership.MembershipFunction`                                | [alarm, block 1](alarm.md); [alpha-cuts, block 1](alpha-cuts.md)                                                   |
| `fuzzyroutines.membership.MembershipFunction.Evaluate`                       | [alarm, block 1](alarm.md); [alpha-cuts, block 1](alpha-cuts.md)                                                   |
| `fuzzyroutines.membership.MembershipFunction.parameters`                     | [membership-families, block 1](membership-families.md)                                                             |
| `fuzzyroutines.membership.MembershipScalar`                                  | [membership, block 1](../api/modern/membership.md); [alarm, block 1](alarm.md)                                     |
| `fuzzyroutines.membership.SShoulder`                                         | [alarm, block 1](alarm.md); [membership-families, block 1](membership-families.md)                                 |
| `fuzzyroutines.membership.Trapezoid`                                         | [membership-families, block 1](membership-families.md)                                                             |
| `fuzzyroutines.membership.Triangle`                                          | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.operators.NegationPolicy`                                     | [alarm, block 1](alarm.md); [api-recipes, block 3](api-recipes.md)                                                 |
| `fuzzyroutines.operators.NegationPolicy.Evaluate`                            | [alarm, block 1](alarm.md); [api-recipes, block 3](api-recipes.md)                                                 |
| `fuzzyroutines.operators.SNormPolicy`                                        | [alarm, block 1](alarm.md); [api-recipes, block 3](api-recipes.md)                                                 |
| `fuzzyroutines.operators.SNormPolicy.Evaluate`                               | [alarm, block 1](alarm.md); [api-recipes, block 3](api-recipes.md)                                                 |
| `fuzzyroutines.operators.TNormPolicy`                                        | [alarm, block 1](alarm.md); [api-recipes, block 3](api-recipes.md)                                                 |
| `fuzzyroutines.operators.TNormPolicy.Evaluate`                               | [alarm, block 1](alarm.md); [api-recipes, block 3](api-recipes.md)                                                 |
| `fuzzyroutines.properties.ContinuousFuzzyProperties`                         | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.properties.ContinuousFuzzyProperties.isExact`                 | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.properties.ContinuousInterval`                                | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.properties.ContinuousInterval.Contains`                       | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.properties.ContinuousInterval.isSingleton`                    | [api-recipes, block 2](api-recipes.md)                                                                             |
| `fuzzyroutines.properties.ContinuousRegion`                                  | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.properties.ContinuousRegion.Contains`                         | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.properties.ContinuousRegion.isEmpty`                          | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.properties.DeriveProperties`                                  | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.properties.DiscreteFuzzyProperties`                           | [results, block 1](results.md)                                                                                     |
| `fuzzyroutines.properties.DiscreteFuzzyProperties.isExact`                   | [results, block 1](results.md)                                                                                     |
| `fuzzyroutines.properties.DiscreteRegion`                                    | [alpha-cuts, block 1](alpha-cuts.md); [api-recipes, block 2](api-recipes.md)                                       |
| `fuzzyroutines.properties.DiscreteRegion.Contains`                           | [results, block 1](results.md)                                                                                     |
| `fuzzyroutines.properties.DiscreteRegion.isEmpty`                            | [api-recipes, block 2](api-recipes.md)                                                                             |
| `fuzzyroutines.properties.SampleProperties`                                  | [api-recipes, block 2](api-recipes.md); [results, block 2](results.md)                                             |
| `fuzzyroutines.properties.SampledFuzzyProperties`                            | [api-recipes, block 2](api-recipes.md); [results, block 2](results.md)                                             |
| `fuzzyroutines.properties.SampledFuzzyProperties.isExact`                    | [api-recipes, block 2](api-recipes.md); [results, block 2](results.md)                                             |
| `fuzzyroutines.relations.ComparisonDomain`                                   | [api-recipes, block 4](api-recipes.md)                                                                             |
| `fuzzyroutines.relations.ComparisonDomain.ValidateWithin`                    | [api-recipes, block 4](api-recipes.md)                                                                             |
| `fuzzyroutines.relations.ComparisonPolicy`                                   | [api-recipes, block 4](api-recipes.md); [custom, block 1](custom.md)                                               |
| `fuzzyroutines.relations.ComparisonPolicy.Equal`                             | [api-recipes, block 4](api-recipes.md); [custom, block 1](custom.md)                                               |
| `fuzzyroutines.relations.ComparisonPolicy.Included`                          | [api-recipes, block 4](api-recipes.md); [custom, block 1](custom.md)                                               |
| `fuzzyroutines.relations.EqualOnDomain`                                      | [api-recipes, block 4](api-recipes.md); [custom, block 1](custom.md)                                               |
| `fuzzyroutines.relations.IncludedOnDomain`                                   | [api-recipes, block 4](api-recipes.md); [custom, block 1](custom.md)                                               |

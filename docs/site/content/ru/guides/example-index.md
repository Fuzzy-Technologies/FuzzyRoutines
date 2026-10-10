<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Указатель примеров публичного API {#public-api-example-index}

Все 193 учтённых публичных символа связаны с выполненными примерами (31 самостоятельный блок Python). Корневые экспорты проверены как псевдонимы соответствующих объектов модулей.

Для функций, конструкторов, методов и свойств требуется настоящее выполнение: одного импорта недостаточно. Конструкторы результатов также выполняются при возврате из производящей функции; явное восстановление показано в [записях результатов](results.md). Два контракта типизации требуют настоящей аннотации, классы исключений — создания экземпляров. Закрытые вспомогательные объекты и автоматически созданные методы dataclass не входят в авторский публичный перечень.

Указатель подтверждает наличие примеров, но не является независимым доказательством каждой математической ветви. Читайте пояснения, ограничения и утверждения по ссылкам. CI заново получает доказательства на установленном пакете и отклоняет устаревшее содержимое канонического указателя. На символ показано не более двух примеров.

| Публичный символ                                                             | Исполняемые примеры                                                                                                |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `fuzzyroutines.AlphaCut`                                                     | [alpha-cuts, блок 1](alpha-cuts.md)                                                                                |
| `fuzzyroutines.Bell`                                                         | [membership-families, блок 1](membership-families.md); [universal-fuzzy-scale, блок 2](universal-fuzzy-scale.md)   |
| `fuzzyroutines.Centroid`                                                     | [membership, блок 1](../api/modern/membership.md); [api-recipes, блок 5](api-recipes.md)                           |
| `fuzzyroutines.CentroidConvergenceError`                                     | [errors, блок 1](errors.md)                                                                                        |
| `fuzzyroutines.CentroidPolicy`                                               | [membership, блок 1](../api/modern/membership.md); [api-recipes, блок 5](api-recipes.md)                           |
| `fuzzyroutines.ComparisonDomain`                                             | [api-recipes, блок 4](api-recipes.md)                                                                              |
| `fuzzyroutines.ComparisonPolicy`                                             | [api-recipes, блок 4](api-recipes.md); [custom, блок 1](custom.md)                                                 |
| `fuzzyroutines.Complement`                                                   | [alarm, блок 1](alarm.md)                                                                                          |
| `fuzzyroutines.ContinuousFuzzyProperties`                                    | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.ContinuousInterval`                                           | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.ContinuousRegion`                                             | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.ContinuousUniverse`                                           | [membership, блок 1](../api/modern/membership.md); [alarm, блок 1](alarm.md)                                       |
| `fuzzyroutines.DeriveProperties`                                             | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.Difference`                                                   | [alarm, блок 1](alarm.md)                                                                                          |
| `fuzzyroutines.DiscreteFuzzyProperties`                                      | [results, блок 1](results.md)                                                                                      |
| `fuzzyroutines.DiscreteRegion`                                               | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.DiscreteUniverse`                                             | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 1](api-recipes.md)                                         |
| `fuzzyroutines.EqualOnDomain`                                                | [api-recipes, блок 4](api-recipes.md); [custom, блок 1](custom.md)                                                 |
| `fuzzyroutines.FuzzificationPolicy`                                          | [results, блок 4](results.md); [risk, блок 1](risk.md)                                                             |
| `fuzzyroutines.FuzzificationResult`                                          | [results, блок 4](results.md); [risk, блок 1](risk.md)                                                             |
| `fuzzyroutines.FuzzyRoutines.DiapasonParser`                                 | [historical-recipes, блок 1](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzyAND`                                       | [historical-recipes, блок 2](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzyNOT`                                       | [historical-recipes, блок 2](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzyNOTParabolic`                              | [historical-recipes, блок 2](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzyOR`                                        | [historical-recipes, блок 2](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale`                                     | [historical-recipes, блок 5](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.Fuzzy`                               | [historical-recipes, блок 5](historical-recipes.md); [universal-fuzzy-scale, блок 1](universal-fuzzy-scale.md)     |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.GetLevelByName`                      | [historical-recipes, блок 5](historical-recipes.md); [universal-fuzzy-scale, блок 1](universal-fuzzy-scale.md)     |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.levels`                              | [historical-recipes, блок 5](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.name`                                | [historical-recipes, блок 5](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzySet`                                       | [historical-recipes, блок 4](historical-recipes.md); [historical-recipes, блок 5](historical-recipes.md)           |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.Defuz`                                 | [historical-recipes, блок 4](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.defuzValue`                            | [historical-recipes, блок 4](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.mFunction`                             | [historical-recipes, блок 4](historical-recipes.md); [historical-recipes, блок 5](historical-recipes.md)           |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.name`                                  | [historical-recipes, блок 4](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.supportSet`                            | [historical-recipes, блок 4](historical-recipes.md); [universal-fuzzy-scale, блок 1](universal-fuzzy-scale.md)     |
| `fuzzyroutines.FuzzyRoutines.IsCorrectFuzzyNumberValue`                      | [historical-recipes, блок 1](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.IsNumber`                                       | [historical-recipes, блок 1](historical-recipes.md); [historical-recipes, блок 2](historical-recipes.md)           |
| `fuzzyroutines.FuzzyRoutines.MFunction`                                      | [historical-recipes, блок 3](historical-recipes.md); [historical-recipes, блок 4](historical-recipes.md)           |
| `fuzzyroutines.FuzzyRoutines.MFunction.Bell`                                 | [historical-recipes, блок 3](historical-recipes.md); [historical-recipes, блок 5](historical-recipes.md)           |
| `fuzzyroutines.FuzzyRoutines.MFunction.Desirability`                         | [historical-recipes, блок 3](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.MFunction.Exponential`                          | [historical-recipes, блок 3](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.MFunction.Hyperbolic`                           | [historical-recipes, блок 3](historical-recipes.md); [historical-recipes, блок 5](historical-recipes.md)           |
| `fuzzyroutines.FuzzyRoutines.MFunction.Parabolic`                            | [historical-recipes, блок 3](historical-recipes.md); [historical-recipes, блок 5](historical-recipes.md)           |
| `fuzzyroutines.FuzzyRoutines.MFunction.Sigmoidal`                            | [historical-recipes, блок 3](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.MFunction.Trapezium`                            | [historical-recipes, блок 3](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.MFunction.Triangle`                             | [historical-recipes, блок 3](historical-recipes.md); [historical-recipes, блок 5](historical-recipes.md)           |
| `fuzzyroutines.FuzzyRoutines.MFunction.name`                                 | [historical-recipes, блок 3](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.MFunction.parameters`                           | [historical-recipes, блок 3](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.SCoNorm`                                        | [historical-recipes, блок 2](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.SCoNormCompose`                                 | [historical-recipes, блок 2](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.TNorm`                                          | [historical-recipes, блок 2](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.TNormCompose`                                   | [historical-recipes, блок 2](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale`                            | [historical-recipes, блок 5](historical-recipes.md); [universal-fuzzy-scale, блок 1](universal-fuzzy-scale.md)     |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levels`                     | [historical-recipes, блок 5](historical-recipes.md); [universal-fuzzy-scale, блок 1](universal-fuzzy-scale.md)     |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levelsNames`                | [historical-recipes, блок 5](historical-recipes.md)                                                                |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levelsNamesUpper`           | [historical-recipes, блок 5](historical-recipes.md)                                                                |
| `fuzzyroutines.Gaussian`                                                     | [membership-families, блок 1](membership-families.md)                                                              |
| `fuzzyroutines.HarringtonDesirability`                                       | [membership-families, блок 1](membership-families.md)                                                              |
| `fuzzyroutines.Height`                                                       | [api-recipes, блок 2](api-recipes.md); [custom, блок 1](custom.md)                                                 |
| `fuzzyroutines.Hyperbolic`                                                   | [membership-families, блок 1](membership-families.md); [universal-fuzzy-scale, блок 2](universal-fuzzy-scale.md)   |
| `fuzzyroutines.IncludedOnDomain`                                             | [api-recipes, блок 4](api-recipes.md); [custom, блок 1](custom.md)                                                 |
| `fuzzyroutines.IntegrationDomain`                                            | [exceptions, блок 1](../api/modern/exceptions.md); [membership, блок 1](../api/modern/membership.md)               |
| `fuzzyroutines.Intersection`                                                 | [alarm, блок 1](alarm.md)                                                                                          |
| `fuzzyroutines.IsNormal`                                                     | [api-recipes, блок 2](api-recipes.md)                                                                              |
| `fuzzyroutines.LinguisticScale`                                              | [results, блок 4](results.md); [results, блок 5](results.md)                                                       |
| `fuzzyroutines.LinguisticTerm`                                               | [results, блок 4](results.md); [results, блок 5](results.md)                                                       |
| `fuzzyroutines.Logistic`                                                     | [membership-families, блок 1](membership-families.md)                                                              |
| `fuzzyroutines.MembershipCallable`                                           | [membership, блок 1](../api/modern/membership.md); [custom, блок 1](custom.md)                                     |
| `fuzzyroutines.MembershipFunction`                                           | [alarm, блок 1](alarm.md); [alpha-cuts, блок 1](alpha-cuts.md)                                                     |
| `fuzzyroutines.MembershipScalar`                                             | [membership, блок 1](../api/modern/membership.md); [alarm, блок 1](alarm.md)                                       |
| `fuzzyroutines.NegationPolicy`                                               | [alarm, блок 1](alarm.md); [api-recipes, блок 3](api-recipes.md)                                                   |
| `fuzzyroutines.Normalize`                                                    | [custom, блок 1](custom.md)                                                                                        |
| `fuzzyroutines.SNormPolicy`                                                  | [alarm, блок 1](alarm.md); [api-recipes, блок 3](api-recipes.md)                                                   |
| `fuzzyroutines.SShoulder`                                                    | [alarm, блок 1](alarm.md); [membership-families, блок 1](membership-families.md)                                   |
| `fuzzyroutines.SampleAlphaCut`                                               | [alpha-cuts, блок 1](alpha-cuts.md); [results, блок 3](results.md)                                                 |
| `fuzzyroutines.SampleProperties`                                             | [api-recipes, блок 2](api-recipes.md); [results, блок 2](results.md)                                               |
| `fuzzyroutines.SampledAlphaCut`                                              | [alpha-cuts, блок 1](alpha-cuts.md); [results, блок 3](results.md)                                                 |
| `fuzzyroutines.SampledFuzzyProperties`                                       | [api-recipes, блок 2](api-recipes.md); [results, блок 2](results.md)                                               |
| `fuzzyroutines.ScalarFuzzySet`                                               | [membership, блок 1](../api/modern/membership.md); [alarm, блок 1](alarm.md)                                       |
| `fuzzyroutines.ScaleDiagnosticPoint`                                         | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.ScaleDiagnosticsPolicy`                                       | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.ScaleDiagnosticsResult`                                       | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.TNormPolicy`                                                  | [alarm, блок 1](alarm.md); [api-recipes, блок 3](api-recipes.md)                                                   |
| `fuzzyroutines.TermMembership`                                               | [results, блок 4](results.md); [results, блок 5](results.md)                                                       |
| `fuzzyroutines.Trapezoid`                                                    | [membership-families, блок 1](membership-families.md)                                                              |
| `fuzzyroutines.Triangle`                                                     | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.Union`                                                        | [alarm, блок 1](alarm.md); [centroid, блок 1](centroid.md)                                                         |
| `fuzzyroutines.alphacuts.AlphaCut`                                           | [alpha-cuts, блок 1](alpha-cuts.md)                                                                                |
| `fuzzyroutines.alphacuts.SampleAlphaCut`                                     | [alpha-cuts, блок 1](alpha-cuts.md); [results, блок 3](results.md)                                                 |
| `fuzzyroutines.alphacuts.SampledAlphaCut`                                    | [alpha-cuts, блок 1](alpha-cuts.md); [results, блок 3](results.md)                                                 |
| `fuzzyroutines.alphacuts.SampledAlphaCut.isExact`                            | [alpha-cuts, блок 1](alpha-cuts.md); [results, блок 3](results.md)                                                 |
| `fuzzyroutines.defuzzification.Centroid`                                     | [membership, блок 1](../api/modern/membership.md); [api-recipes, блок 5](api-recipes.md)                           |
| `fuzzyroutines.defuzzification.CentroidConvergenceError`                     | [errors, блок 1](errors.md)                                                                                        |
| `fuzzyroutines.defuzzification.CentroidPolicy`                               | [membership, блок 1](../api/modern/membership.md); [api-recipes, блок 5](api-recipes.md)                           |
| `fuzzyroutines.domain.ContinuousUniverse`                                    | [membership, блок 1](../api/modern/membership.md); [alarm, блок 1](alarm.md)                                       |
| `fuzzyroutines.domain.ContinuousUniverse.Contains`                           | [membership, блок 1](../api/modern/membership.md); [alarm, блок 1](alarm.md)                                       |
| `fuzzyroutines.domain.ContinuousUniverse.isBounded`                          | [api-recipes, блок 1](api-recipes.md)                                                                              |
| `fuzzyroutines.domain.DiscreteUniverse`                                      | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 1](api-recipes.md)                                         |
| `fuzzyroutines.domain.DiscreteUniverse.Contains`                             | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 1](api-recipes.md)                                         |
| `fuzzyroutines.domain.IntegrationDomain`                                     | [exceptions, блок 1](../api/modern/exceptions.md); [membership, блок 1](../api/modern/membership.md)               |
| `fuzzyroutines.domain.IntegrationDomain.Contains`                            | [api-recipes, блок 1](api-recipes.md)                                                                              |
| `fuzzyroutines.domain.IntegrationDomain.FromLegacyInterval`                  | [api-recipes, блок 1](api-recipes.md); [historical-recipes, блок 4](historical-recipes.md)                         |
| `fuzzyroutines.domain.IntegrationDomain.ToLegacyInterval`                    | [api-recipes, блок 1](api-recipes.md); [historical-recipes, блок 4](historical-recipes.md)                         |
| `fuzzyroutines.domain.IntegrationDomain.ValidateWithin`                      | [membership, блок 1](../api/modern/membership.md); [alpha-cuts, блок 1](alpha-cuts.md)                             |
| `fuzzyroutines.exceptions.FuzzyRoutinesError`                                | [errors, блок 1](errors.md)                                                                                        |
| `fuzzyroutines.exceptions.InvalidDomainError`                                | [errors, блок 1](errors.md)                                                                                        |
| `fuzzyroutines.exceptions.InvalidParameterError`                             | [errors, блок 1](errors.md)                                                                                        |
| `fuzzyroutines.exceptions.InvalidParameterTypeError`                         | [errors, блок 1](errors.md)                                                                                        |
| `fuzzyroutines.exceptions.NumericalError`                                    | [errors, блок 1](errors.md)                                                                                        |
| `fuzzyroutines.exceptions.UndefinedResultError`                              | [errors, блок 1](errors.md)                                                                                        |
| `fuzzyroutines.fuzzysets.Complement`                                         | [alarm, блок 1](alarm.md)                                                                                          |
| `fuzzyroutines.fuzzysets.Difference`                                         | [alarm, блок 1](alarm.md)                                                                                          |
| `fuzzyroutines.fuzzysets.Height`                                             | [api-recipes, блок 2](api-recipes.md); [custom, блок 1](custom.md)                                                 |
| `fuzzyroutines.fuzzysets.Intersection`                                       | [alarm, блок 1](alarm.md)                                                                                          |
| `fuzzyroutines.fuzzysets.IsNormal`                                           | [api-recipes, блок 2](api-recipes.md)                                                                              |
| `fuzzyroutines.fuzzysets.Normalize`                                          | [custom, блок 1](custom.md)                                                                                        |
| `fuzzyroutines.fuzzysets.ScalarFuzzySet`                                     | [membership, блок 1](../api/modern/membership.md); [alarm, блок 1](alarm.md)                                       |
| `fuzzyroutines.fuzzysets.ScalarFuzzySet.Membership`                          | [membership, блок 1](../api/modern/membership.md); [alarm, блок 1](alarm.md)                                       |
| `fuzzyroutines.fuzzysets.Union`                                              | [alarm, блок 1](alarm.md); [centroid, блок 1](centroid.md)                                                         |
| `fuzzyroutines.linguistic.FuzzificationPolicy`                               | [results, блок 4](results.md); [risk, блок 1](risk.md)                                                             |
| `fuzzyroutines.linguistic.FuzzificationResult`                               | [results, блок 4](results.md); [risk, блок 1](risk.md)                                                             |
| `fuzzyroutines.linguistic.FuzzificationResult.isMatch`                       | [results, блок 4](results.md); [risk, блок 1](risk.md)                                                             |
| `fuzzyroutines.linguistic.FuzzificationResult.isTie`                         | [results, блок 4](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.LinguisticScale`                                   | [results, блок 4](results.md); [results, блок 5](results.md)                                                       |
| `fuzzyroutines.linguistic.LinguisticScale.Diagnose`                          | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.LinguisticScale.Fuzzify`                           | [results, блок 4](results.md); [risk, блок 1](risk.md)                                                             |
| `fuzzyroutines.linguistic.LinguisticScale.GetTermByName`                     | [results, блок 4](results.md)                                                                                      |
| `fuzzyroutines.linguistic.LinguisticTerm`                                    | [results, блок 4](results.md); [results, блок 5](results.md)                                                       |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint`                              | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.activeTerms`                  | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.isGap`                        | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.isOverlap`                    | [results, блок 5](results.md)                                                                                      |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.maximumMembership`            | [results, блок 5](results.md)                                                                                      |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.membershipSum`                | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.partitionError`               | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.ScaleDiagnosticsPolicy`                            | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult`                            | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.gapFraction`                | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.gapPoints`                  | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.isPartitionWithinTolerance` | [results, блок 5](results.md)                                                                                      |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumActiveTermCount`     | [results, блок 5](results.md)                                                                                      |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumCoverage`            | [results, блок 5](results.md)                                                                                      |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumPartitionError`      | [results, блок 5](results.md); [scale-audit, блок 1](scale-audit.md)                                               |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.meanCoverage`               | [results, блок 5](results.md)                                                                                      |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.meanPartitionError`         | [results, блок 5](results.md)                                                                                      |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.minimumCoverage`            | [results, блок 5](results.md)                                                                                      |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.overlapFraction`            | [results, блок 5](results.md)                                                                                      |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.overlapPoints`              | [results, блок 5](results.md)                                                                                      |
| `fuzzyroutines.linguistic.TermMembership`                                    | [results, блок 4](results.md); [results, блок 5](results.md)                                                       |
| `fuzzyroutines.membership.Bell`                                              | [membership-families, блок 1](membership-families.md); [universal-fuzzy-scale, блок 2](universal-fuzzy-scale.md)   |
| `fuzzyroutines.membership.Gaussian`                                          | [membership-families, блок 1](membership-families.md)                                                              |
| `fuzzyroutines.membership.HarringtonDesirability`                            | [membership-families, блок 1](membership-families.md)                                                              |
| `fuzzyroutines.membership.Hyperbolic`                                        | [membership-families, блок 1](membership-families.md); [universal-fuzzy-scale, блок 2](universal-fuzzy-scale.md)   |
| `fuzzyroutines.membership.Logistic`                                          | [membership-families, блок 1](membership-families.md)                                                              |
| `fuzzyroutines.membership.MembershipCallable`                                | [membership, блок 1](../api/modern/membership.md); [custom, блок 1](custom.md)                                     |
| `fuzzyroutines.membership.MembershipFunction`                                | [alarm, блок 1](alarm.md); [alpha-cuts, блок 1](alpha-cuts.md)                                                     |
| `fuzzyroutines.membership.MembershipFunction.Evaluate`                       | [alarm, блок 1](alarm.md); [alpha-cuts, блок 1](alpha-cuts.md)                                                     |
| `fuzzyroutines.membership.MembershipFunction.parameters`                     | [membership-families, блок 1](membership-families.md)                                                              |
| `fuzzyroutines.membership.MembershipScalar`                                  | [membership, блок 1](../api/modern/membership.md); [alarm, блок 1](alarm.md)                                       |
| `fuzzyroutines.membership.SShoulder`                                         | [alarm, блок 1](alarm.md); [membership-families, блок 1](membership-families.md)                                   |
| `fuzzyroutines.membership.Trapezoid`                                         | [membership-families, блок 1](membership-families.md)                                                              |
| `fuzzyroutines.membership.Triangle`                                          | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.operators.NegationPolicy`                                     | [alarm, блок 1](alarm.md); [api-recipes, блок 3](api-recipes.md)                                                   |
| `fuzzyroutines.operators.NegationPolicy.Evaluate`                            | [alarm, блок 1](alarm.md); [api-recipes, блок 3](api-recipes.md)                                                   |
| `fuzzyroutines.operators.SNormPolicy`                                        | [alarm, блок 1](alarm.md); [api-recipes, блок 3](api-recipes.md)                                                   |
| `fuzzyroutines.operators.SNormPolicy.Evaluate`                               | [alarm, блок 1](alarm.md); [api-recipes, блок 3](api-recipes.md)                                                   |
| `fuzzyroutines.operators.TNormPolicy`                                        | [alarm, блок 1](alarm.md); [api-recipes, блок 3](api-recipes.md)                                                   |
| `fuzzyroutines.operators.TNormPolicy.Evaluate`                               | [alarm, блок 1](alarm.md); [api-recipes, блок 3](api-recipes.md)                                                   |
| `fuzzyroutines.properties.ContinuousFuzzyProperties`                         | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.properties.ContinuousFuzzyProperties.isExact`                 | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.properties.ContinuousInterval`                                | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.properties.ContinuousInterval.Contains`                       | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.properties.ContinuousInterval.isSingleton`                    | [api-recipes, блок 2](api-recipes.md)                                                                              |
| `fuzzyroutines.properties.ContinuousRegion`                                  | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.properties.ContinuousRegion.Contains`                         | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.properties.ContinuousRegion.isEmpty`                          | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.properties.DeriveProperties`                                  | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.properties.DiscreteFuzzyProperties`                           | [results, блок 1](results.md)                                                                                      |
| `fuzzyroutines.properties.DiscreteFuzzyProperties.isExact`                   | [results, блок 1](results.md)                                                                                      |
| `fuzzyroutines.properties.DiscreteRegion`                                    | [alpha-cuts, блок 1](alpha-cuts.md); [api-recipes, блок 2](api-recipes.md)                                         |
| `fuzzyroutines.properties.DiscreteRegion.Contains`                           | [results, блок 1](results.md)                                                                                      |
| `fuzzyroutines.properties.DiscreteRegion.isEmpty`                            | [api-recipes, блок 2](api-recipes.md)                                                                              |
| `fuzzyroutines.properties.SampleProperties`                                  | [api-recipes, блок 2](api-recipes.md); [results, блок 2](results.md)                                               |
| `fuzzyroutines.properties.SampledFuzzyProperties`                            | [api-recipes, блок 2](api-recipes.md); [results, блок 2](results.md)                                               |
| `fuzzyroutines.properties.SampledFuzzyProperties.isExact`                    | [api-recipes, блок 2](api-recipes.md); [results, блок 2](results.md)                                               |
| `fuzzyroutines.relations.ComparisonDomain`                                   | [api-recipes, блок 4](api-recipes.md)                                                                              |
| `fuzzyroutines.relations.ComparisonDomain.ValidateWithin`                    | [api-recipes, блок 4](api-recipes.md)                                                                              |
| `fuzzyroutines.relations.ComparisonPolicy`                                   | [api-recipes, блок 4](api-recipes.md); [custom, блок 1](custom.md)                                                 |
| `fuzzyroutines.relations.ComparisonPolicy.Equal`                             | [api-recipes, блок 4](api-recipes.md); [custom, блок 1](custom.md)                                                 |
| `fuzzyroutines.relations.ComparisonPolicy.Included`                          | [api-recipes, блок 4](api-recipes.md); [custom, блок 1](custom.md)                                                 |
| `fuzzyroutines.relations.EqualOnDomain`                                      | [api-recipes, блок 4](api-recipes.md); [custom, блок 1](custom.md)                                                 |
| `fuzzyroutines.relations.IncludedOnDomain`                                   | [api-recipes, блок 4](api-recipes.md); [custom, блок 1](custom.md)                                                 |

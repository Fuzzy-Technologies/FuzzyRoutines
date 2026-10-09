<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 公共 API 示例索引 {#public-api-example-index}

全部 193 个已登记公共符号都链接到已执行的示例，共有 29 个独立 Python 代码块。根导出经过验证，确实是相应模块对象的别名。

函数、构造函数、方法和属性要求真实执行，仅导入不算。产生结果的函数返回对象时，也会运行结果构造函数；显式重建见[结果记录](results.md)。两个类型约定要求真实注解，异常类要求构造实例。私有辅助对象和自动生成的 dataclass 方法不属于手写公共清单。

该索引确立示例的可用性，不独立证明每个数学分支。应阅读链接中的解释、限制和断言。CI 针对已安装软件包重新生成证据，并拒绝过期的规范索引内容。每个符号最多显示两个示例。

| 公共符号                                                                         | 可执行示例                                                                                                      |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `fuzzyroutines.AlphaCut`                                                     | [alpha-cuts，代码块 1](alpha-cuts.md)                                                                          |
| `fuzzyroutines.Bell`                                                         | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.Centroid`                                                     | [membership，代码块 1](../api/modern/membership.md); [api-recipes，代码块 5](api-recipes.md)                       |
| `fuzzyroutines.CentroidConvergenceError`                                     | [errors，代码块 1](errors.md)                                                                                  |
| `fuzzyroutines.CentroidPolicy`                                               | [membership，代码块 1](../api/modern/membership.md); [api-recipes，代码块 5](api-recipes.md)                       |
| `fuzzyroutines.ComparisonDomain`                                             | [api-recipes，代码块 4](api-recipes.md)                                                                        |
| `fuzzyroutines.ComparisonPolicy`                                             | [api-recipes，代码块 4](api-recipes.md); [custom，代码块 1](custom.md)                                             |
| `fuzzyroutines.Complement`                                                   | [alarm，代码块 1](alarm.md)                                                                                    |
| `fuzzyroutines.ContinuousFuzzyProperties`                                    | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.ContinuousInterval`                                           | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.ContinuousRegion`                                             | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.ContinuousUniverse`                                           | [membership，代码块 1](../api/modern/membership.md); [alarm，代码块 1](alarm.md)                                   |
| `fuzzyroutines.DeriveProperties`                                             | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.Difference`                                                   | [alarm，代码块 1](alarm.md)                                                                                    |
| `fuzzyroutines.DiscreteFuzzyProperties`                                      | [results，代码块 1](results.md)                                                                                |
| `fuzzyroutines.DiscreteRegion`                                               | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.DiscreteUniverse`                                             | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 1](api-recipes.md)                                     |
| `fuzzyroutines.EqualOnDomain`                                                | [api-recipes，代码块 4](api-recipes.md); [custom，代码块 1](custom.md)                                             |
| `fuzzyroutines.FuzzificationPolicy`                                          | [results，代码块 4](results.md); [risk，代码块 1](risk.md)                                                         |
| `fuzzyroutines.FuzzificationResult`                                          | [results，代码块 4](results.md); [risk，代码块 1](risk.md)                                                         |
| `fuzzyroutines.FuzzyRoutines.DiapasonParser`                                 | [historical-recipes，代码块 1](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzyAND`                                       | [historical-recipes，代码块 2](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzyNOT`                                       | [historical-recipes，代码块 2](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzyNOTParabolic`                              | [historical-recipes，代码块 2](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzyOR`                                        | [historical-recipes，代码块 2](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale`                                     | [historical-recipes，代码块 5](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.Fuzzy`                               | [historical-recipes，代码块 5](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.GetLevelByName`                      | [historical-recipes，代码块 5](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.levels`                              | [historical-recipes，代码块 5](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzyScale.name`                                | [historical-recipes，代码块 5](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzySet`                                       | [historical-recipes，代码块 4](historical-recipes.md); [historical-recipes，代码块 5](historical-recipes.md)       |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.Defuz`                                 | [historical-recipes，代码块 4](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.defuzValue`                            | [historical-recipes，代码块 4](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.mFunction`                             | [historical-recipes，代码块 4](historical-recipes.md); [historical-recipes，代码块 5](historical-recipes.md)       |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.name`                                  | [historical-recipes，代码块 4](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.FuzzySet.supportSet`                            | [historical-recipes，代码块 4](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.IsCorrectFuzzyNumberValue`                      | [historical-recipes，代码块 1](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.IsNumber`                                       | [historical-recipes，代码块 1](historical-recipes.md); [historical-recipes，代码块 2](historical-recipes.md)       |
| `fuzzyroutines.FuzzyRoutines.MFunction`                                      | [historical-recipes，代码块 3](historical-recipes.md); [historical-recipes，代码块 4](historical-recipes.md)       |
| `fuzzyroutines.FuzzyRoutines.MFunction.Bell`                                 | [historical-recipes，代码块 3](historical-recipes.md); [historical-recipes，代码块 5](historical-recipes.md)       |
| `fuzzyroutines.FuzzyRoutines.MFunction.Desirability`                         | [historical-recipes，代码块 3](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.MFunction.Exponential`                          | [historical-recipes，代码块 3](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.MFunction.Hyperbolic`                           | [historical-recipes，代码块 3](historical-recipes.md); [historical-recipes，代码块 5](historical-recipes.md)       |
| `fuzzyroutines.FuzzyRoutines.MFunction.Parabolic`                            | [historical-recipes，代码块 3](historical-recipes.md); [historical-recipes，代码块 5](historical-recipes.md)       |
| `fuzzyroutines.FuzzyRoutines.MFunction.Sigmoidal`                            | [historical-recipes，代码块 3](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.MFunction.Trapezium`                            | [historical-recipes，代码块 3](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.MFunction.Triangle`                             | [historical-recipes，代码块 3](historical-recipes.md); [historical-recipes，代码块 5](historical-recipes.md)       |
| `fuzzyroutines.FuzzyRoutines.MFunction.name`                                 | [historical-recipes，代码块 3](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.MFunction.parameters`                           | [historical-recipes，代码块 3](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.SCoNorm`                                        | [historical-recipes，代码块 2](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.SCoNormCompose`                                 | [historical-recipes，代码块 2](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.TNorm`                                          | [historical-recipes，代码块 2](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.TNormCompose`                                   | [historical-recipes，代码块 2](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale`                            | [historical-recipes，代码块 5](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levels`                     | [historical-recipes，代码块 5](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levelsNames`                | [historical-recipes，代码块 5](historical-recipes.md)                                                          |
| `fuzzyroutines.FuzzyRoutines.UniversalFuzzyScale.levelsNamesUpper`           | [historical-recipes，代码块 5](historical-recipes.md)                                                          |
| `fuzzyroutines.Gaussian`                                                     | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.HarringtonDesirability`                                       | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.Height`                                                       | [api-recipes，代码块 2](api-recipes.md); [custom，代码块 1](custom.md)                                             |
| `fuzzyroutines.Hyperbolic`                                                   | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.IncludedOnDomain`                                             | [api-recipes，代码块 4](api-recipes.md); [custom，代码块 1](custom.md)                                             |
| `fuzzyroutines.IntegrationDomain`                                            | [exceptions，代码块 1](../api/modern/exceptions.md); [membership，代码块 1](../api/modern/membership.md)           |
| `fuzzyroutines.Intersection`                                                 | [alarm，代码块 1](alarm.md)                                                                                    |
| `fuzzyroutines.IsNormal`                                                     | [api-recipes，代码块 2](api-recipes.md)                                                                        |
| `fuzzyroutines.LinguisticScale`                                              | [results，代码块 4](results.md); [results，代码块 5](results.md)                                                   |
| `fuzzyroutines.LinguisticTerm`                                               | [results，代码块 4](results.md); [results，代码块 5](results.md)                                                   |
| `fuzzyroutines.Logistic`                                                     | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.MembershipCallable`                                           | [membership，代码块 1](../api/modern/membership.md); [custom，代码块 1](custom.md)                                 |
| `fuzzyroutines.MembershipFunction`                                           | [alarm，代码块 1](alarm.md); [alpha-cuts，代码块 1](alpha-cuts.md)                                                 |
| `fuzzyroutines.MembershipScalar`                                             | [membership，代码块 1](../api/modern/membership.md); [alarm，代码块 1](alarm.md)                                   |
| `fuzzyroutines.NegationPolicy`                                               | [alarm，代码块 1](alarm.md); [api-recipes，代码块 3](api-recipes.md)                                               |
| `fuzzyroutines.Normalize`                                                    | [custom，代码块 1](custom.md)                                                                                  |
| `fuzzyroutines.SNormPolicy`                                                  | [alarm，代码块 1](alarm.md); [api-recipes，代码块 3](api-recipes.md)                                               |
| `fuzzyroutines.SShoulder`                                                    | [alarm，代码块 1](alarm.md); [membership-families，代码块 1](membership-families.md)                               |
| `fuzzyroutines.SampleAlphaCut`                                               | [alpha-cuts，代码块 1](alpha-cuts.md); [results，代码块 3](results.md)                                             |
| `fuzzyroutines.SampleProperties`                                             | [api-recipes，代码块 2](api-recipes.md); [results，代码块 2](results.md)                                           |
| `fuzzyroutines.SampledAlphaCut`                                              | [alpha-cuts，代码块 1](alpha-cuts.md); [results，代码块 3](results.md)                                             |
| `fuzzyroutines.SampledFuzzyProperties`                                       | [api-recipes，代码块 2](api-recipes.md); [results，代码块 2](results.md)                                           |
| `fuzzyroutines.ScalarFuzzySet`                                               | [membership，代码块 1](../api/modern/membership.md); [alarm，代码块 1](alarm.md)                                   |
| `fuzzyroutines.ScaleDiagnosticPoint`                                         | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.ScaleDiagnosticsPolicy`                                       | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.ScaleDiagnosticsResult`                                       | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.TNormPolicy`                                                  | [alarm，代码块 1](alarm.md); [api-recipes，代码块 3](api-recipes.md)                                               |
| `fuzzyroutines.TermMembership`                                               | [results，代码块 4](results.md); [results，代码块 5](results.md)                                                   |
| `fuzzyroutines.Trapezoid`                                                    | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.Triangle`                                                     | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.Union`                                                        | [alarm，代码块 1](alarm.md); [centroid，代码块 1](centroid.md)                                                     |
| `fuzzyroutines.alphacuts.AlphaCut`                                           | [alpha-cuts，代码块 1](alpha-cuts.md)                                                                          |
| `fuzzyroutines.alphacuts.SampleAlphaCut`                                     | [alpha-cuts，代码块 1](alpha-cuts.md); [results，代码块 3](results.md)                                             |
| `fuzzyroutines.alphacuts.SampledAlphaCut`                                    | [alpha-cuts，代码块 1](alpha-cuts.md); [results，代码块 3](results.md)                                             |
| `fuzzyroutines.alphacuts.SampledAlphaCut.isExact`                            | [alpha-cuts，代码块 1](alpha-cuts.md); [results，代码块 3](results.md)                                             |
| `fuzzyroutines.defuzzification.Centroid`                                     | [membership，代码块 1](../api/modern/membership.md); [api-recipes，代码块 5](api-recipes.md)                       |
| `fuzzyroutines.defuzzification.CentroidConvergenceError`                     | [errors，代码块 1](errors.md)                                                                                  |
| `fuzzyroutines.defuzzification.CentroidPolicy`                               | [membership，代码块 1](../api/modern/membership.md); [api-recipes，代码块 5](api-recipes.md)                       |
| `fuzzyroutines.domain.ContinuousUniverse`                                    | [membership，代码块 1](../api/modern/membership.md); [alarm，代码块 1](alarm.md)                                   |
| `fuzzyroutines.domain.ContinuousUniverse.Contains`                           | [membership，代码块 1](../api/modern/membership.md); [alarm，代码块 1](alarm.md)                                   |
| `fuzzyroutines.domain.ContinuousUniverse.isBounded`                          | [api-recipes，代码块 1](api-recipes.md)                                                                        |
| `fuzzyroutines.domain.DiscreteUniverse`                                      | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 1](api-recipes.md)                                     |
| `fuzzyroutines.domain.DiscreteUniverse.Contains`                             | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 1](api-recipes.md)                                     |
| `fuzzyroutines.domain.IntegrationDomain`                                     | [exceptions，代码块 1](../api/modern/exceptions.md); [membership，代码块 1](../api/modern/membership.md)           |
| `fuzzyroutines.domain.IntegrationDomain.Contains`                            | [api-recipes，代码块 1](api-recipes.md)                                                                        |
| `fuzzyroutines.domain.IntegrationDomain.FromLegacyInterval`                  | [api-recipes，代码块 1](api-recipes.md); [historical-recipes，代码块 4](historical-recipes.md)                     |
| `fuzzyroutines.domain.IntegrationDomain.ToLegacyInterval`                    | [api-recipes，代码块 1](api-recipes.md); [historical-recipes，代码块 4](historical-recipes.md)                     |
| `fuzzyroutines.domain.IntegrationDomain.ValidateWithin`                      | [membership，代码块 1](../api/modern/membership.md); [alpha-cuts，代码块 1](alpha-cuts.md)                         |
| `fuzzyroutines.exceptions.FuzzyRoutinesError`                                | [errors，代码块 1](errors.md)                                                                                  |
| `fuzzyroutines.exceptions.InvalidDomainError`                                | [errors，代码块 1](errors.md)                                                                                  |
| `fuzzyroutines.exceptions.InvalidParameterError`                             | [errors，代码块 1](errors.md)                                                                                  |
| `fuzzyroutines.exceptions.InvalidParameterTypeError`                         | [errors，代码块 1](errors.md)                                                                                  |
| `fuzzyroutines.exceptions.NumericalError`                                    | [errors，代码块 1](errors.md)                                                                                  |
| `fuzzyroutines.exceptions.UndefinedResultError`                              | [errors，代码块 1](errors.md)                                                                                  |
| `fuzzyroutines.fuzzysets.Complement`                                         | [alarm，代码块 1](alarm.md)                                                                                    |
| `fuzzyroutines.fuzzysets.Difference`                                         | [alarm，代码块 1](alarm.md)                                                                                    |
| `fuzzyroutines.fuzzysets.Height`                                             | [api-recipes，代码块 2](api-recipes.md); [custom，代码块 1](custom.md)                                             |
| `fuzzyroutines.fuzzysets.Intersection`                                       | [alarm，代码块 1](alarm.md)                                                                                    |
| `fuzzyroutines.fuzzysets.IsNormal`                                           | [api-recipes，代码块 2](api-recipes.md)                                                                        |
| `fuzzyroutines.fuzzysets.Normalize`                                          | [custom，代码块 1](custom.md)                                                                                  |
| `fuzzyroutines.fuzzysets.ScalarFuzzySet`                                     | [membership，代码块 1](../api/modern/membership.md); [alarm，代码块 1](alarm.md)                                   |
| `fuzzyroutines.fuzzysets.ScalarFuzzySet.Membership`                          | [membership，代码块 1](../api/modern/membership.md); [alarm，代码块 1](alarm.md)                                   |
| `fuzzyroutines.fuzzysets.Union`                                              | [alarm，代码块 1](alarm.md); [centroid，代码块 1](centroid.md)                                                     |
| `fuzzyroutines.linguistic.FuzzificationPolicy`                               | [results，代码块 4](results.md); [risk，代码块 1](risk.md)                                                         |
| `fuzzyroutines.linguistic.FuzzificationResult`                               | [results，代码块 4](results.md); [risk，代码块 1](risk.md)                                                         |
| `fuzzyroutines.linguistic.FuzzificationResult.isMatch`                       | [results，代码块 4](results.md); [risk，代码块 1](risk.md)                                                         |
| `fuzzyroutines.linguistic.FuzzificationResult.isTie`                         | [results，代码块 4](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.LinguisticScale`                                   | [results，代码块 4](results.md); [results，代码块 5](results.md)                                                   |
| `fuzzyroutines.linguistic.LinguisticScale.Diagnose`                          | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.LinguisticScale.Fuzzify`                           | [results，代码块 4](results.md); [risk，代码块 1](risk.md)                                                         |
| `fuzzyroutines.linguistic.LinguisticScale.GetTermByName`                     | [results，代码块 4](results.md)                                                                                |
| `fuzzyroutines.linguistic.LinguisticTerm`                                    | [results，代码块 4](results.md); [results，代码块 5](results.md)                                                   |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint`                              | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.activeTerms`                  | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.isGap`                        | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.isOverlap`                    | [results，代码块 5](results.md)                                                                                |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.maximumMembership`            | [results，代码块 5](results.md)                                                                                |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.membershipSum`                | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.ScaleDiagnosticPoint.partitionError`               | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.ScaleDiagnosticsPolicy`                            | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult`                            | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.gapFraction`                | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.gapPoints`                  | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.isPartitionWithinTolerance` | [results，代码块 5](results.md)                                                                                |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumActiveTermCount`     | [results，代码块 5](results.md)                                                                                |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumCoverage`            | [results，代码块 5](results.md)                                                                                |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.maximumPartitionError`      | [results，代码块 5](results.md); [scale-audit，代码块 1](scale-audit.md)                                           |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.meanCoverage`               | [results，代码块 5](results.md)                                                                                |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.meanPartitionError`         | [results，代码块 5](results.md)                                                                                |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.minimumCoverage`            | [results，代码块 5](results.md)                                                                                |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.overlapFraction`            | [results，代码块 5](results.md)                                                                                |
| `fuzzyroutines.linguistic.ScaleDiagnosticsResult.overlapPoints`              | [results，代码块 5](results.md)                                                                                |
| `fuzzyroutines.linguistic.TermMembership`                                    | [results，代码块 4](results.md); [results，代码块 5](results.md)                                                   |
| `fuzzyroutines.membership.Bell`                                              | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.membership.Gaussian`                                          | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.membership.HarringtonDesirability`                            | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.membership.Hyperbolic`                                        | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.membership.Logistic`                                          | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.membership.MembershipCallable`                                | [membership，代码块 1](../api/modern/membership.md); [custom，代码块 1](custom.md)                                 |
| `fuzzyroutines.membership.MembershipFunction`                                | [alarm，代码块 1](alarm.md); [alpha-cuts，代码块 1](alpha-cuts.md)                                                 |
| `fuzzyroutines.membership.MembershipFunction.Evaluate`                       | [alarm，代码块 1](alarm.md); [alpha-cuts，代码块 1](alpha-cuts.md)                                                 |
| `fuzzyroutines.membership.MembershipFunction.parameters`                     | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.membership.MembershipScalar`                                  | [membership，代码块 1](../api/modern/membership.md); [alarm，代码块 1](alarm.md)                                   |
| `fuzzyroutines.membership.SShoulder`                                         | [alarm，代码块 1](alarm.md); [membership-families，代码块 1](membership-families.md)                               |
| `fuzzyroutines.membership.Trapezoid`                                         | [membership-families，代码块 1](membership-families.md)                                                        |
| `fuzzyroutines.membership.Triangle`                                          | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.operators.NegationPolicy`                                     | [alarm，代码块 1](alarm.md); [api-recipes，代码块 3](api-recipes.md)                                               |
| `fuzzyroutines.operators.NegationPolicy.Evaluate`                            | [alarm，代码块 1](alarm.md); [api-recipes，代码块 3](api-recipes.md)                                               |
| `fuzzyroutines.operators.SNormPolicy`                                        | [alarm，代码块 1](alarm.md); [api-recipes，代码块 3](api-recipes.md)                                               |
| `fuzzyroutines.operators.SNormPolicy.Evaluate`                               | [alarm，代码块 1](alarm.md); [api-recipes，代码块 3](api-recipes.md)                                               |
| `fuzzyroutines.operators.TNormPolicy`                                        | [alarm，代码块 1](alarm.md); [api-recipes，代码块 3](api-recipes.md)                                               |
| `fuzzyroutines.operators.TNormPolicy.Evaluate`                               | [alarm，代码块 1](alarm.md); [api-recipes，代码块 3](api-recipes.md)                                               |
| `fuzzyroutines.properties.ContinuousFuzzyProperties`                         | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.properties.ContinuousFuzzyProperties.isExact`                 | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.properties.ContinuousInterval`                                | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.properties.ContinuousInterval.Contains`                       | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.properties.ContinuousInterval.isSingleton`                    | [api-recipes，代码块 2](api-recipes.md)                                                                        |
| `fuzzyroutines.properties.ContinuousRegion`                                  | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.properties.ContinuousRegion.Contains`                         | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.properties.ContinuousRegion.isEmpty`                          | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.properties.DeriveProperties`                                  | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.properties.DiscreteFuzzyProperties`                           | [results，代码块 1](results.md)                                                                                |
| `fuzzyroutines.properties.DiscreteFuzzyProperties.isExact`                   | [results，代码块 1](results.md)                                                                                |
| `fuzzyroutines.properties.DiscreteRegion`                                    | [alpha-cuts，代码块 1](alpha-cuts.md); [api-recipes，代码块 2](api-recipes.md)                                     |
| `fuzzyroutines.properties.DiscreteRegion.Contains`                           | [results，代码块 1](results.md)                                                                                |
| `fuzzyroutines.properties.DiscreteRegion.isEmpty`                            | [api-recipes，代码块 2](api-recipes.md)                                                                        |
| `fuzzyroutines.properties.SampleProperties`                                  | [api-recipes，代码块 2](api-recipes.md); [results，代码块 2](results.md)                                           |
| `fuzzyroutines.properties.SampledFuzzyProperties`                            | [api-recipes，代码块 2](api-recipes.md); [results，代码块 2](results.md)                                           |
| `fuzzyroutines.properties.SampledFuzzyProperties.isExact`                    | [api-recipes，代码块 2](api-recipes.md); [results，代码块 2](results.md)                                           |
| `fuzzyroutines.relations.ComparisonDomain`                                   | [api-recipes，代码块 4](api-recipes.md)                                                                        |
| `fuzzyroutines.relations.ComparisonDomain.ValidateWithin`                    | [api-recipes，代码块 4](api-recipes.md)                                                                        |
| `fuzzyroutines.relations.ComparisonPolicy`                                   | [api-recipes，代码块 4](api-recipes.md); [custom，代码块 1](custom.md)                                             |
| `fuzzyroutines.relations.ComparisonPolicy.Equal`                             | [api-recipes，代码块 4](api-recipes.md); [custom，代码块 1](custom.md)                                             |
| `fuzzyroutines.relations.ComparisonPolicy.Included`                          | [api-recipes，代码块 4](api-recipes.md); [custom，代码块 1](custom.md)                                             |
| `fuzzyroutines.relations.EqualOnDomain`                                      | [api-recipes，代码块 4](api-recipes.md); [custom，代码块 1](custom.md)                                             |
| `fuzzyroutines.relations.IncludedOnDomain`                                   | [api-recipes，代码块 4](api-recipes.md); [custom，代码块 1](custom.md)                                             |

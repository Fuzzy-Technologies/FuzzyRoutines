<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# 包导出 {#package-exports}

根包重新导出以下现代 API 名称。每个链接指向对象所属模块的规范文档，避免重复 API 约定或建立互相竞争的锚点。字面量根 `__all__` 是通配符导入的权威接口。隶属函数工厂和类型约定可以直接从根导入；导入的模块、私有辅助对象和历史可变类不属于该接口。

历史通配符入口仍是 `from fuzzyroutines.FuzzyRoutines import *`。其显式 `__all__` 只包含十五个受支持的兼容符号；历史上意外泄露的辅助名称 `math` 和 `copy` 不再导入。如果应用曾通过兼容入口获取它们，应直接使用 Python 的 `math` 和 `copy` 模块。

| 导出名称                        | 规范 API 对象                                                                            |
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

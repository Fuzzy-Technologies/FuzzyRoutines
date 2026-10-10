<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Экспорты пакета {#package-exports}

Корневой пакет повторно экспортирует следующие имена современного API. Каждая ссылка ведёт к канонической документации объекта в его модуле; справочник не дублирует контракты и не создаёт конкурирующие якоря. Литеральный корневой `__all__` — канонический набор для импорта со звёздочкой. Фабрики принадлежности и контракты типов доступны из корня напрямую; импортированные модули, закрытые вспомогательные объекты и исторические изменяемые классы в этот набор не входят.

Исторический вход для импорта со звёздочкой остаётся `from fuzzyroutines.FuzzyRoutines import *`. Его явный `__all__` содержит только пятнадцать поддерживаемых символов совместимости; прежние случайные экспорты `math` и `copy` больше не импортируются. Если приложение получало их через фасад, используйте модули Python `math` и `copy` напрямую.

| Экспорт                     | Канонический объект API                                                              |
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

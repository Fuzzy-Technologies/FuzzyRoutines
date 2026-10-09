<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Проверка и восстановление записей результатов {#inspect-and-reconstruct-result-records}

Записи результатов сохраняют основания расчёта. При обычном использовании предпочитайте функцию, которая производит результат. Явные конструкторы полезны при передаче уже проверенной записи между компонентами; валидация проверяет описанные правила согласованности, а не независимо доказывает математику. Современные записи неизменяемы. В приложении сохраняйте вместе с ними единицы и предположения модели. Все блоки ниже запускаются независимо.

## Точная непрерывная и дискретная геометрия {#exact-continuous-and-discrete-geometry}

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


Непрерывное множество поддержки — открытый интервал (0, 2), его замыкание — [0, 2]. На дискретном универсальном множестве поддержка состоит из трёх точек {0.5, 1, 1.5}, и замыкание совпадает с ней. Оба ядра равны {1}. Граничная точка с нулевой степенью входит в непрерывное замыкание поддержки, но не в саму поддержку. Дискретная топология даёт другое замыкание.

## Выборочные свойства сохраняют свою сетку {#sampled-properties-retain-their-grid}

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


Здесь сетка попала в вершину. Другая сетка может пропустить узкую вершину, поэтому `heightEstimate` — наблюдение, а не точная верхняя грань. Прямой конструктор проверяет порядок, границы, подмножества регионов и наблюдаемый максимум; он не пересчитывает все классификации регионов и не доказывает равномерность сетки. Для создания новых данных используйте `SampleProperties`.

## Выборочный альфа-срез — таблица, а не решение для интервала {#a-sampled-alpha-cut-is-a-table-not-an-interval-solution}

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


Слабая граница включает степень 0.5. Аналитический интервал этого треугольника равен [0.5, 1.5], но `SampleAlphaCut` возвращает только подходящие координаты сетки. Конструктор проверяет срез по всем переданным степеням. Метка происхождения сама по себе не устанавливает равномерность вручную переданной таблицы. См. [альфа-срезы](alpha-cuts.md).

## Классификация сохраняет все степени и политику выбора {#a-classification-keeps-all-grades-and-its-selection-policy}

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


`memberships` сохраняет полный упорядоченный вектор термов; `tiedTerms` и `selectedTerms` объясняют, какие максимумы сохранены и выбраны. Уверенность — наибольшая принадлежность, а не вероятность. При нулевом пороге по умолчанию отсутствие покрытия даёт отсутствие совпадения. Степень, равная `minimumConfidence`, также не выбирается. См. [серьёзность и отказ](risk.md) и [равные максимумы](scale-audit.md).

## Диагностика шкалы с учётом ограничений выборки {#read-every-scale-diagnostic-with-its-sampling-limits}

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


Намеренно совпадающие треугольники дают перекрытие в среднем наблюдении и пробелы в двух опорных точках. Покрытие — максимальная степень в координате; оно отличается от суммы всех степеней. Ошибка разбиения — абсолютное отклонение этой суммы от единицы. Доли и средние учитывают три наблюдения, а не длины интервалов или непрерывные интегралы. Терм активен только выше `membershipThreshold`; равенство означает неактивность. Таблица не доказывает глобальное покрытие или разбиение.

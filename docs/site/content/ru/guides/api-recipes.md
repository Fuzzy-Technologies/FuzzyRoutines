<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Практические рецепты API {#practical-api-recipes}

[Практические сценарии](index.md) объясняют полные расчёты. Здесь собраны более короткие примеры проверки областей, выборочных свойств, альтернативных операторов, конечных сравнений и обработки ошибок. Каждый блок Python самостоятелен и выполняется в CI с установленными артефактами wheel и sdist.

## Проверка области перед интегрированием {#validate-a-domain-before-integration}

```python
from fuzzyroutines import ContinuousUniverse, DiscreteUniverse, IntegrationDomain

universe = ContinuousUniverse(0, 10, leftClosed=True, rightClosed=True)
domain = IntegrationDomain.FromLegacyInterval((2, 8)).ValidateWithin(universe)
assert universe.isBounded and universe.Contains(0)
assert domain.Contains(2) and domain.ToLegacyInterval() == (2, 8)
discrete = DiscreteUniverse((1, 3, 5))
assert discrete.Contains(3) and not discrete.Contains(2)
print(domain.ToLegacyInterval(), discrete.points)
```


Окно интегрирования — конечный замкнутый интервал, а не математическое множество поддержки. Универсальное множество может быть неограниченным или иметь открытые границы; запрошенное окно интегрирования обязано учитывать эти ограничения.

## Чтение точных и выборочных свойств {#read-exact-and-sampled-properties}

```python
from fuzzyroutines import (
    ContinuousInterval, ContinuousRegion, ContinuousUniverse, DeriveProperties,
    DiscreteRegion, IntegrationDomain, IsNormal, SampleProperties,
    ScalarFuzzySet, Triangle,
)

model = Triangle(0, 2, 4)
universe = ContinuousUniverse(0, 4, leftClosed=True, rightClosed=True)
properties = DeriveProperties(model, universe)
sampled = SampleProperties(model, IntegrationDomain(0, 4), sampleCount=5)
assert properties.isExact and properties.height == 1
assert properties.core.Contains(2) and not properties.positiveSupport.Contains(0)
assert not sampled.isExact and sampled.heightEstimate == 1
assert sampled.coreSamples.points == (2,)
assert IsNormal(ScalarFuzzySet(universe, model))
interval = ContinuousInterval(1, 3, leftClosed=True, rightClosed=False)
region = ContinuousRegion((interval,))
assert region.Contains(1) and not region.Contains(3) and not region.isEmpty
assert not interval.isSingleton and not DiscreteRegion((1, 3)).isEmpty
print(properties.height, sampled.coordinates)
```


Для встроенных аналитических семейств `DeriveProperties` вычисляет точную геометрию с ограничением на универсальное множество. `SampleProperties` сообщает наблюдаемые поддержку, ядро, границу и оценку высоты на заданной сетке. В этом примере попадание в вершину даёт оценку один; в другой модели сетка может пропустить узкую вершину и занизить высоту. Точная высота произвольной непрерывной модели из выборки не выводится. `IsNormal` использует точную высоту и явный допуск, по умолчанию $10^{-12}$.

## Осознанный выбор семейств скалярных операторов {#choose-scalar-operator-families-deliberately}

```python
from math import isclose
from fuzzyroutines import NegationPolicy, SNormPolicy, TNormPolicy

expectedAnd = {"logic": 0.4, "algebraic": 0.28, "boundary": 0.1, "drastic": 0}
expectedOr = {"logic": 0.7, "algebraic": 0.82, "boundary": 1, "drastic": 1}
for family in expectedAnd:
    assert isclose(TNormPolicy(family).Evaluate(0.4, 0.7), expectedAnd[family], abs_tol=1e-12)
    assert isclose(SNormPolicy(family).Evaluate(0.4, 0.7), expectedOr[family], abs_tol=1e-12)
assert NegationPolicy("standard").Evaluate(0.4) == 0.6
assert NegationPolicy("parametric", alpha=0.5).Evaluate(0.5) == 0.5
assert NegationPolicy("parabolic", alpha=0.5).Evaluate(0.5) == 0.5
print(expectedAnd, expectedOr)
```


Параметрическое отрицание требует $0<\alpha<1$, параболическое — $1/4\leq\alpha\leq3/4$. Здесь альфа — параметр отрицания, а не порог альфа-среза. Граничная и радикальная политики — явные альтернативы; резкое поведение на границах может влиять на модель.

## Сравнение непрерывных моделей в явных координатах {#compare-continuous-models-at-explicit-coordinates}

```python
from fuzzyroutines import (
    ComparisonDomain, ComparisonPolicy, ContinuousUniverse,
    EqualOnDomain, IncludedOnDomain, ScalarFuzzySet, Triangle,
)

universe = ContinuousUniverse(0, 4, leftClosed=True, rightClosed=True)
left = ScalarFuzzySet(universe, Triangle(0, 2, 4))
right = ScalarFuzzySet(universe, Triangle(0, 2, 4))
coordinates = ComparisonDomain((0, 1, 2, 3, 4)).ValidateWithin(universe)
policy = ComparisonPolicy("tolerance", absoluteTolerance=1e-12, relativeTolerance=1e-10)
assert policy.Equal(0.5, 0.5 + 1e-13)
assert policy.Included(0.4, 0.5)
assert EqualOnDomain(left, right, policy, coordinates)
assert IncludedOnDomain(left, right, policy, coordinates)
print(coordinates.points)
```


Результат подтверждает соотношение лишь в пяти объявленных наблюдениях. Это не доказательство глобальной эквивалентности непрерывных моделей, даже если отдельное аналитическое рассуждение устанавливает тождественность именно этих определений.

## Обработка математически неопределённого результата {#handle-a-mathematically-undefined-result}

```python
from fuzzyroutines import (
    Centroid, CentroidPolicy, ContinuousUniverse, IntegrationDomain,
    MembershipScalar, ScalarFuzzySet,
)
from fuzzyroutines.exceptions import UndefinedResultError


def ZeroGrade(coordinate: MembershipScalar) -> MembershipScalar:
    """Return zero area on every allowed coordinate."""

    return 0


empty = ScalarFuzzySet(
    ContinuousUniverse(0, 1, leftClosed=True, rightClosed=True), ZeroGrade,
)
try:
    Centroid(empty, IntegrationDomain(0, 1), CentroidPolicy(maximumDepth=20))
except UndefinedResultError:
    print("No centroid: the membership area is zero")
else:
    raise AssertionError("zero-area membership unexpectedly had a centroid")
```


Выберите запасное поведение, подходящее предметной области, или передайте ошибку выше. Молчаливый возврат нуля выдумал бы представительную координату. Недопустимые типы, параметры и области имеют отдельные описанные категории исключений; исчерпание адаптации обозначает `CentroidConvergenceError`. Перехватывайте конкретную категорию, которую приложение умеет обработать, вместо подавления всех ошибок.

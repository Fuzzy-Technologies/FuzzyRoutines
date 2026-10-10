<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Пользовательская модель качества {#a-custom-quality-model}

**Вопрос:** может ли предметная скалярная функция участвовать в интегрировании и нормализации на конечном универсальном множестве без создания подкласса?

```python
from math import isclose
from fuzzyroutines import (
    Centroid, ComparisonPolicy, ContinuousUniverse, DiscreteUniverse,
    EqualOnDomain, Height, IncludedOnDomain, IntegrationDomain,
    MembershipCallable, MembershipScalar, Normalize, ScalarFuzzySet,
)


def RisingQuality(coordinate: MembershipScalar) -> MembershipScalar:
    """Map a declared score in [0, 100] to its linear membership grade."""

    return coordinate / 100


callback: MembershipCallable = RisingQuality
continuous = ScalarFuzzySet(
    ContinuousUniverse(0, 100, leftClosed=True, rightClosed=True), callback,
)
centroid = Centroid(continuous, IntegrationDomain(0, 100))
assert isclose(centroid, 200 / 3, abs_tol=1e-9)
discrete = ScalarFuzzySet(DiscreteUniverse((0, 25, 50)), RisingQuality)
normalized = Normalize(discrete)
assert Height(discrete) == 0.5 and Height(normalized) == 1
assert tuple(normalized.Membership(coordinate) for coordinate in discrete.universe.points) == (0, 0.5, 1)
policy = ComparisonPolicy("exact")
assert IncludedOnDomain(discrete, normalized, policy)
assert not EqualOnDomain(discrete, normalized, policy)
print(centroid, Height(discrete), Height(normalized))
```


Контракт вызываемой функции принимает одну конечную вещественную координату, отличную от логического значения, и возвращает конечную степень в $[0,1]$. `MembershipScalar` описывает более широкий поддерживаемый тип скалярного входа. При создании проверяется возможность вызова; при вычислении — координата и возвращённая степень. Сохраняйте согласованность степеней между вызовами: библиотека не фиксирует снимок изменяемого состояния, захваченного произвольной функцией.

У функции $x/100$ площадь на $[0,100]$ равна 50, а первый момент — $10000/3$. Поэтому центроид равен $200/3\approx66.666667$, что совпадает с адаптивным расчётом. Встроенные средства аналитической геометрии не могут доказать точную высоту или множество поддержки произвольной непрерывной вызываемой функции. Выборка описывает наблюдения, но не даёт такого доказательства.

[![Исходные и нормализованные степени в трёх объявленных дискретных координатах](../../en/assets/figures/custom.svg)](../../en/assets/figures/custom.svg)

На дискретном универсальном множестве $\{0,25,50\}$ полный перебор доказывает высоту 0.5. `Normalize` делит каждую степень на эту высоту и возвращает новое множество; исходное не меняется. На графике намеренно изображены только точки: промежуточных координат в объявленном универсальном множестве нет.

Точное сравнение устанавливает включение **во всех трёх объявленных точках**. Для непрерывных моделей `EqualOnDomain` и `IncludedOnDomain` требуют явного конечного `ComparisonDomain` и доказывают соотношение лишь в этих наблюдениях, а не на всём интервале. При сравнении с допуском нужно явно задать абсолютный и относительный допуски.

**Применение в проекте:** оберните устойчивую калибровочную функцию объявленным универсальным множеством, сохраните единицы и предположения валидации и проверьте независимые интегралы для характерных случаев. Нормализуйте только тогда, когда приведение максимальной степени к единице соответствует смыслу задачи.

```bash
python -I examples/guide.py --scenario custom
```


Далее — [галерея функций принадлежности](membership-families.md) или [полный справочник API](../api/index.md).

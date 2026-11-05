<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Функции принадлежности по заданным точкам {#membership-from-explicit-points}

При калибровке получены степени принадлежности для координат 10, 13 и 21.
Если этими тремя значениями исчерпывается модель, используйте дискретную
таблицу. Если между результатами измерений нужны степени принадлежности,
которые меняются по прямой, выберите кусочно-линейную функцию.

```python
from fuzzyroutines import ContinuousUniverse, ScalarFuzzySet
from fuzzyroutines.point_membership import (
    DiscreteMembershipTable,
    PiecewiseLinearMembership,
)

points = ((10, 0.25), (13, 0.75), (21, 0.5))
table = DiscreteMembershipTable(points)
curve = PiecewiseLinearMembership(points, boundary="zero")
discrete = ScalarFuzzySet(table.universe, table)
continuous = ScalarFuzzySet(ContinuousUniverse(), curve)

assert discrete.Membership(13) == continuous.Membership(13) == 0.75
assert continuous.Membership(11.5) == 0.5
assert continuous.Membership(17) == 0.625
assert continuous.Membership(22) == 0
```

В таблице для координаты 17 степень не задана: этой координаты нет в её
универсальном множестве. На кривой степень равна 0,625: координата 17 находится
ровно посередине между 13 и 21, где степени равны 0,75 и 0,5. Первый интервал
имеет длину три единицы, второй — восемь; для каждого отрезка используется
его фактическая длина.

## Справочник API {#api-reference}

`DiscreteMembershipTable(points)` принимает непустой кортеж пар
`(координата, степень)`. Доступные только для чтения атрибуты `points` и
`universe` содержат данные и соответствующий `DiscreteUniverse`. Таблица
проверяет и хранит все степени при создании. Связка `DiscreteUniverse` с
вызываемой функцией задаёт координаты и передаёт вычисление степеней этой
функции. Вызов таблицы с незаданной координатой приводит к
`InvalidDomainError`. Координаты сравниваются точно, без допуска.

`PiecewiseLinearMembership(knots, boundary="error")` принимает не менее двух
пар в том же формате. Атрибуты `knots` и `boundary` доступны только для чтения.
В узле возвращается сохранённая степень. Для соседних узлов
$(x_i,g_i)$ и $(x_{i+1},g_{i+1})$ положим $t=(x-x_i)/(x_{i+1}-x_i)$.
В точке $x$ между ними степень равна $(1-t)g_i+tg_{i+1}$. Если все участвующие
в интерполяции числа представлены целыми или рациональными типами,
возвращается `Fraction`; при участии числа с плавающей точкой — Python float.

Вне замкнутого интервала узлов:

- `"error"` приводит к `InvalidDomainError` (по умолчанию).
- `"zero"` возвращает 0. Если степень в крайнем узле ненулевая, в нём возникает разрыв.
- `"clamp"` возвращает степень в ближайшем крайнем узле.

Разрыв внутри интервала задать нельзя. Повтор координаты для его задания
приводит к `InvalidDomainError`.

Оба объекта принимают один позиционный аргумент `MembershipScalar`.
Координаты в исходных данных должны быть конечными и строго возрастать;
степени должны быть конечными и лежать в $[0,1]$. Логические и другие
невещественные значения приводят к `InvalidParameterTypeError`.
Неконечные координаты, неконечные или выходящие за допустимый диапазон
степени и неизвестные строки режима приводят к `InvalidParameterError`.
Данные не сортируются и не нормируются.

Политика за границами узлов не переопределяет универсальное множество
`ScalarFuzzySet`. Скалярный протокол вызова не регистрирует кривую для
вывода точных непрерывных свойств или аналитического вычисления центроида.
См. [ADR-0024](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/adr/0024-point-membership-contracts.md)
и [справочник аналитических функций принадлежности](membership.md).

::: fuzzyroutines.point_membership
    options:
      members:
        - DiscreteMembershipTable
        - PiecewiseLinearMembership

<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Равенство и включение нечётких множеств {#fuzzy-set-equality-and-inclusion}

- Статус: исполняемый контракт задачи #73
- Публичный модуль: `fuzzyroutines.relations`

## Математические отношения {#mathematical-relations}

Для нечётких множеств `A` и `B` на одном универсальном множестве `X`
поточечное равенство и включение определяются как

```text
A = B  iff  for every x in X: mu_A(x) = mu_B(x)
A <= B iff  for every x in X: mu_A(x) <= mu_B(x)
```

Публичный API никогда не сравнивает идентичность объектов функций принадлежности.
Поэтому разные Python-вычислители могут представлять одинаковое поведение принадлежности.
Оба отношения требуют точного равенства универсальных множеств до вычисления любой степени.
Равенство Python-объектов `ScalarFuzzySet` остаётся проверкой идентичности и не является
математическим отношением; необходимо вызывать явные функции отношений.

## Полный перебор и выборочная область {#exhaustive-and-sampled-scope}

`DiscreteUniverse` конечно, поэтому `EqualOnDomain` и `IncludedOnDomain` вычисляют каждую
объявленную точку. Нельзя передать частичную область сравнения и случайно выдать такой
результат за равенство на всём универсальном множестве.

В общем случае конечным числом вычислений нельзя доказать глобальное равенство произвольного
Python-вычислителя на `ContinuousUniverse` другому вычислителю. Поэтому непрерывные отношения
требуют явный `ComparisonDomain` с конечными упорядоченными точками внутри универсального множества.
Булев результат действителен только в этих объявленных точках; он не доказывает равенство
функций или включение между точками.

Это намеренная граница. Аналитические доказательства отношений известных семейств функций
принадлежности потребовали бы отдельного символьного представления и контракта.

## Точный режим и режим с допуском {#exact-and-tolerance-modes}

Каждое отношение требует `ComparisonPolicy`:

- `ComparisonPolicy("exact")` использует точное численное равенство степеней принадлежности
  и точный поточечный порядок;
- `ComparisonPolicy("tolerance", absoluteTolerance=..., relativeTolerance=...)` использует
  `math.isclose` для равенства и допускает нарушение включения только при близости
  двух степеней по этим явным допускам.

Режим с допуском требует оба поля допуска; хотя бы одно должно быть положительным.
Точный режим отклоняет аргументы допусков. Нет общего для библиотеки или неявного epsilon.

Близость с допуском в общем случае нетранзитивна. Её нельзя использовать как отношение
эквивалентности для хеширования, канонизации или идентичности.

## Примеры {#examples}

Полное дискретное сравнение:

```python
from fuzzyroutines import (
    ComparisonPolicy,
    DiscreteUniverse,
    EqualOnDomain,
    IncludedOnDomain,
    ScalarFuzzySet,
)

universe = DiscreteUniverse((0.0, 0.5, 1.0))
leftSet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
rightSet = ScalarFuzzySet(universe, lambda coordinate: coordinate**1)
policy = ComparisonPolicy("exact")

assert EqualOnDomain(leftSet, rightSet, policy)
assert IncludedOnDomain(leftSet, rightSet, policy)
```

Явное выборочное сравнение непрерывных множеств:

```python
from fuzzyroutines import ComparisonDomain, ContinuousUniverse

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
leftSet = ScalarFuzzySet(universe, lambda coordinate: coordinate * coordinate)
rightSet = ScalarFuzzySet(universe, lambda coordinate: coordinate**2)
samplePoints = ComparisonDomain((0.0, 0.25, 0.5, 0.75, 1.0))

assert EqualOnDomain(leftSet, rightSet, policy, samplePoints)
```

## Проверенные свойства {#verified-properties}

Исполняемые тесты покрывают:

- полное дискретное равенство и включение;
- равенство разных по идентичности вызываемых представлений;
- рефлексивность и точную антисимметричность;
- явное поведение абсолютного и относительного допусков;
- обязательность области непрерывного сравнения;
- отклонение частичных дискретных областей;
- отклонение несовместимых универсальных множеств и недопустимых точек выборки.

## Источники {#references}

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>
- G. J. Klir and B. Yuan, *Fuzzy Sets and Fuzzy Logic: Theory and
  Applications*, Prentice Hall, 1995. ISBN 978-0-13-101171-7.

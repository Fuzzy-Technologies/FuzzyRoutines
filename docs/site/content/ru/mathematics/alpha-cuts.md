<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Контракт альфа-срезов {#alpha-cut-contract}

## Определение и соглашение о границе {#definition-and-boundary-convention}

Для скалярного нечёткого множества $A$ на универсальном множестве $X$
FuzzyRoutines определяет нестрогий альфа-срез как

$$
A_\alpha = \{x \in X \mid \mu_A(x) \ge \alpha\},
\qquad \alpha \in [0, 1].
$$

Сравнение — точно `>=`. Координата с принадлежностью, равной порогу, входит в срез.
API не подменяет его неявно строгим срезом $\{x \mid \mu_A(x) > \alpha\}$
и не применяет численный допуск.

Поведение на концах диапазона непосредственно следует из определения:

- $A_0 = X$, поскольку каждая допустимая степень принадлежности лежит в $[0, 1]$;
- $A_1 = \{x \in X \mid \mu_A(x) = 1\}$ — ядро множества $A$.

При любых $0 \le \alpha \le \beta \le 1$ срезы вложены:

$$
A_\beta \subseteq A_\alpha.
$$

## Точная дискретная операция {#exact-discrete-operation}

`AlphaCut(fuzzySet, alpha)` полностью вычисляет каждую координату `DiscreteUniverse`
и возвращает `DiscreteRegion`. Поэтому результат — точный срез относительно объявленного
конечного универсального множества.

```python
from fuzzyroutines import AlphaCut, DiscreteUniverse, ScalarFuzzySet

universe = DiscreteUniverse((0.0, 0.5, 1.0))
fuzzySet = ScalarFuzzySet(universe, lambda coordinate: coordinate)

assert AlphaCut(fuzzySet, 0.5).points == (0.5, 1.0)
assert AlphaCut(fuzzySet, 0.0).points == universe.points
assert AlphaCut(fuzzySet, 1.0).points == (1.0,)
```

Операция вычисляет через `ScalarFuzzySet.Membership`, поэтому неконечные,
невещественные степени принадлежности и значения вне диапазона приводят к явной ошибке.

## Явно выборочная непрерывная операция {#explicitly-sampled-continuous-operation}

Для произвольного Python-вычислителя на `ContinuousUniverse` нет общего аналитического
обращения. Конечное сканирование не доказывает его непрерывный альфа-срез.
Поэтому `AlphaCut` отклоняет непрерывные нечёткие множества, не выдавая точки выборки за точную геометрию.

`SampleAlphaCut(fuzzySet, alpha, analysisDomain, sampleCount)` — явная численная
альтернатива. Она вычисляет равномерную конечную сетку на `IntegrationDomain`,
содержащейся в универсальном множестве исходного множества, и возвращает `SampledAlphaCut`.
Результат записывает:

- `alpha` и нестрогий отбор `>= alpha`;
- `analysisDomain`, `sampleCount` и все вычисленные `coordinates`;
- каждую проверенную степень принадлежности в `grades`;
- выбранные `cutSamples` как `DiscreteRegion`;
- `method == "uniform-grid"` и `isExact == False`.

```python
from fuzzyroutines import (
    ContinuousUniverse,
    IntegrationDomain,
    SampleAlphaCut,
    ScalarFuzzySet,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, lambda coordinate: coordinate)
sampledCut = SampleAlphaCut(
    fuzzySet,
    0.5,
    IntegrationDomain(0.0, 1.0),
    sampleCount=5,
)

assert sampledCut.cutSamples.points == (0.5, 0.75, 1.0)
assert sampledCut.isExact is False
```

При `alpha=0` поле `cutSamples` содержит всю объявленную сетку, а не материализованное
непрерывное универсальное множество. При `alpha=1` оно содержит только точки выборки
с принадлежностью ровно один; это не доказательство полного непрерывного ядра.
Инвариант вложенности гарантируется, когда срезы используют одно нечёткое множество,
одну область анализа и одно разрешение сетки.

## Источники {#references}

- L. A. Zadeh, “Fuzzy Sets,” *Information and Control*, 8(3), 338–353,
  1965. <https://doi.org/10.1016/S0019-9958(65)90241-X>

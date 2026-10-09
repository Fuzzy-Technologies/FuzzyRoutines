<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Альфа-срезы качества {#quality-alpha-cuts}

**Вопрос:** какие объявленные оценки качества достигают порога принадлежности 0.5? Треугольная модель допуска имеет полную принадлежность при 12 и нулевую при 10 и 14. Слабый срез включает равенство порогу.

```python
from fuzzyroutines import (
    AlphaCut, ContinuousUniverse, DeriveProperties, DiscreteUniverse,
    IntegrationDomain, SampleAlphaCut, ScalarFuzzySet, Triangle,
)

model = Triangle(10, 12, 14)
discrete = ScalarFuzzySet(DiscreteUniverse((10, 11, 12, 13, 14)), model)
assert AlphaCut(discrete, 0.5).points == (11, 12, 13)
assert AlphaCut(discrete, 0).points == (10, 11, 12, 13, 14)
assert AlphaCut(discrete, 1).points == (12,)
universe = ContinuousUniverse(10, 14, leftClosed=True, rightClosed=True)
continuous = ScalarFuzzySet(universe, model)
sampled = SampleAlphaCut(continuous, 0.5, IntegrationDomain(10, 14), sampleCount=9)
properties = DeriveProperties(model, universe)
assert sampled.cutSamples.points == (11, 11.5, 12, 12.5, 13)
assert not sampled.isExact and properties.isExact
assert not properties.positiveSupport.Contains(10)
assert properties.supportClosure.Contains(10)
assert properties.core.Contains(12)
print(sampled.cutSamples.points)
```


[![Непрерывный треугольник, девять наблюдений на сетке и точки точного дискретного среза](../../en/assets/figures/alpha-cuts.svg)](../../en/assets/figures/alpha-cuts.svg)

Точный **дискретный** срез равен $\{11,12,13\}$: проверена каждая координата объявленного дискретного универсального множества. При нулевом альфа он содержит все объявленные точки, включая точки с нулевой принадлежностью.

Непрерывный пример проверяет девять координат с шагом 0.5. Он возвращает пять подходящих наблюдений и `isExact=False`; эти наблюдения не являются точной непрерывной областью. Для конкретного известного треугольника независимое решение двух линейных неравенств даёт непрерывный срез $[11,13]$. `SampleAlphaCut` не выполняет такое символьное решение.

`DeriveProperties` использует известное аналитическое семейство: множество поддержки — $(10,14)$, его замыкание — $[10,14]$, ядро — $\{12\}$. Обратите внимание, почему множество поддержки и его замыкание по-разному включают границы.

**Применение в проекте:** для конечного набора допустимых настроек используйте точный дискретный срез. Для исследования непрерывной модели подходит выборочный результат; сохраняйте в отчёте область и число узлов сетки. Более плотная сетка увеличивает число наблюдений, но не доказывает отсутствие особенностей между ними.

```bash
python -I examples/guide.py --scenario alpha-cuts
```


Далее — [центроиды и численная точность](centroid.md).

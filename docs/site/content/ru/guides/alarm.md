<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Зоны предупреждения для обслуживания {#maintenance-warning-zones}

**Вопрос:** насколько температура принадлежит зоне предупреждения и одновременно не принадлежит критической зоне? Обе модели описывают одно универсальное множество 40–120 °C, поэтому их можно комбинировать как нечёткие множества.

```python
from fuzzyroutines import (
    Complement, ContinuousUniverse, Difference, Intersection, NegationPolicy,
    ScalarFuzzySet, SNormPolicy, SShoulder, TNormPolicy, Union,
)

universe = ContinuousUniverse(40, 120, leftClosed=True, rightClosed=True)
warning = ScalarFuzzySet(universe, SShoulder(60, 100))
critical = ScalarFuzzySet(universe, SShoulder(90, 110))
negation = NegationPolicy("standard")
conjunction = TNormPolicy("logic")
warningWithoutCritical = Difference(warning, critical, conjunction, negation)
noncritical = Complement(critical, negation)
both = Intersection(warning, critical, conjunction)
either = Union(warning, critical, SNormPolicy("logic"))
assert warning.Membership(100) == 1
assert critical.Membership(100) == 0.5
assert warningWithoutCritical.Membership(100) == 0.5
assert noncritical.Membership(100) == both.Membership(100) == 0.5
assert either.Membership(100) == 1
print(warningWithoutCritical.Membership(100))
```


[![Предупреждение, критическая зона и направленная нечёткая разность по температуре](../../en/assets/figures/alarm.svg)](../../en/assets/figures/alarm.svg)

При стандартном отрицании и конъюнкции по минимуму

$$
\mu_{W\setminus C}(x)=\min\{\mu_W(x),1-\mu_C(x)\}.
$$


При 100 °C получаем $\min(1,1-0.5)=0.5$. Разность **направленная**: перестановка зоны предупреждения и критической зоны меняет смысл. Это не обычное вычитание и не арифметика нечётких чисел. Результат композиции снижается до нуля, когда критическая принадлежность достигает единицы.

**Применение в проекте:** сохраняйте степени предупреждения и критичности вместе с составным результатом, чтобы панель наблюдения могла объяснить решение. Прежде чем применять демонстрационные пороги в работе, проверьте их для конкретного приложения.

```bash
python -I examples/guide.py --scenario alarm
```


Далее — [альфа-срезы качества](alpha-cuts.md).

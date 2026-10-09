<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Метки серьёзности и отказ от классификации {#severity-labels-and-abstention}

**Вопрос:** стоит ли присваивать метку оценке серьёзности 65, если наибольшая степень принадлежности равна всего 0.4? Оценка — иллюстративный инженерный индекс от 0 до 100, а не вероятность события или медицински валидированная оценка риска.

```python
from math import isclose
from fuzzyroutines import (
    ContinuousUniverse, FuzzificationPolicy, LinguisticScale,
    LinguisticTerm, ScalarFuzzySet, SShoulder, Triangle,
)

universe = ContinuousUniverse(0, 100, leftClosed=True, rightClosed=True)
scale = LinguisticScale((
    LinguisticTerm("Low", ScalarFuzzySet(universe, Triangle(0, 20, 50))),
    LinguisticTerm("Moderate", ScalarFuzzySet(universe, Triangle(25, 50, 75))),
    LinguisticTerm("High", ScalarFuzzySet(universe, SShoulder(50, 90))),
))
result = scale.Fuzzify(65)
cautious = scale.Fuzzify(65, FuzzificationPolicy(minimumConfidence=0.45))
grades = {item.term.name: item.grade for item in result.memberships}
assert isclose(grades["Moderate"], 0.4)
assert grades["High"] == 0.28125
assert result.selectedTerms[0].name == "Moderate"
assert not cautious.isMatch
print(grades, cautious.isMatch)
```


[![Кривые серьёзности и порог выбора 0.45](../../en/assets/figures/risk.svg)](../../en/assets/figures/risk.svg)

По умолчанию выбирается *Moderate*. Нисходящая сторона его треугольника даёт

$$
\mu_{\mathrm{Moderate}}(65)=\frac{75-65}{75-50}=0.4.
$$


Восходящее плечо даёт $2(15/40)^2=0.28125$ для *High*. Степень *Low* равна нулю. Поле `confidence` содержит максимальную принадлежность, а не калиброванную статистическую уверенность. При `minimumConfidence=0.45` выбор отклоняется, но все степени сохраняются. Степень, **равная** порогу, тоже приводит к отказу: для выбора требуется строго большее значение.

**Применение в проекте:** направляйте наблюдения без выбранного терма на проверку или в предусмотренную ветку обработки. Выбирайте порог по требованиям приложения и проверяйте его на репрезентативных наблюдениях. FuzzyRoutines не оценивает и не валидирует этот порог вместо вас.

```bash
python -I examples/guide.py --scenario risk
```


Далее — [объединение критериев датчиков](sensors.md).

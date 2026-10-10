<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Аудит лингвистической шкалы {#audit-a-linguistic-scale}

**Вопрос:** может ли шкала давать равные максимумы, слабое соответствие или отсутствие покрытия? Проверьте её устройство до выбора рабочей политики присвоения меток.

```python
from fuzzyroutines import (
    ContinuousUniverse, FuzzificationPolicy, IntegrationDomain, LinguisticScale,
    LinguisticTerm, ScalarFuzzySet, ScaleDiagnosticsPolicy, Triangle,
)

universe = ContinuousUniverse(0, 10, leftClosed=True, rightClosed=True)
scale = LinguisticScale((
    LinguisticTerm("Low", ScalarFuzzySet(universe, Triangle(0, 2, 6))),
    LinguisticTerm("High", ScalarFuzzySet(universe, Triangle(4, 8, 10))),
))
tied = scale.Fuzzify(5, FuzzificationPolicy(tiePolicy="all"))
assert tied.isTie and tied.confidence == 0.25
assert tuple(term.name for term in tied.selectedTerms) == ("Low", "High")
assert scale.Fuzzify(5).selectedTerms[0].name == "Low"
assert not scale.Fuzzify(5, FuzzificationPolicy(minimumConfidence=0.3)).isMatch

gappyScale = LinguisticScale((
    LinguisticTerm("Low", ScalarFuzzySet(universe, Triangle(0, 2, 4))),
    LinguisticTerm("High", ScalarFuzzySet(universe, Triangle(6, 8, 10))),
))
audit = gappyScale.Diagnose(IntegrationDomain(0, 10), ScaleDiagnosticsPolicy(sampleCount=11))
assert tuple(point.coordinate for point in audit.gapPoints) == (0, 4, 5, 6, 10)
assert audit.gapFraction == 5 / 11
assert not gappyScale.Fuzzify(5).isMatch
print(audit.gapFraction, audit.maximumPartitionError)
```


[![Перекрывающаяся шкала слева и обнаруженные на сетке пробелы покрытия справа](../../en/assets/figures/scale-audit.svg)](../../en/assets/figures/scale-audit.svg)

При оценке 5 первая шкала даёт две степени 0.25. `tiePolicy="all"` сохраняет оба терма. Политика первого терма по умолчанию выбирает *Low*, а `"last"` выбрала бы *High*. При пороге уверенности 0.3 ни один из этих термов не выбирается. Поэтому порядок термов входит в контракт модели при политике first/last.

У второй шкалы оба терма имеют нулевую принадлежность в пяти из одиннадцати проверяемых координат: 0, 4, 5, 6 и 10. **Выборочная** доля пробелов равна $5/11\approx0.454545$. Это доля проверенных координат, а не непрерывная доля длины интервала. В данной сетке границы учитываются.

По умолчанию порог принадлежности нулевой: активной считается строго положительная степень. `membershipThreshold` меняет критерий активности, но не саму модель. Ошибка разбиения показывает отклонение суммы степеней от единицы, а не ошибку точности относительно размеченных наблюдений. Примеры намеренно не образуют разбиение единицы.

**Применение в проекте:** изучайте отдельные диагностические точки, а не только итоговые доли. Помимо равномерной сетки проверяйте известные границы переходов и физически значимые режимы. Диагностика на сетке не устанавливает глобальное непрерывное покрытие и не исключает узких пробелов между наблюдениями.

```bash
python -I examples/guide.py --scenario scale-audit
```


Далее — [пользовательская модель качества](custom.md).

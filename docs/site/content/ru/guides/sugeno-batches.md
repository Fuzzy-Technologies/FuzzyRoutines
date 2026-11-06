<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Пакетный вывод Сугено

Установите `fuzzyroutines[numpy]` и импортируйте `EvaluateSugenoBatch`, чтобы обработать таблицу наблюдений одной моделью Сугено со встроенными функциями. В одной модели могут сочетаться правила нулевого и первого порядков. Для пользовательских функций и моделей Мамдани используйте [скалярный вывод](inference.md).

В примере мониторинга столбец нагрузки идёт перед столбцом риска. Передайте этот порядок в `featureNames`. Результат сохраняет порядок строк, а столбцы трассировки идут в порядке объявления модели. Для допустимого наблюдения взвешенные силы срабатывания равны 0,375 и 0,25. После нормировки веса равны 0,6 и 0,4, поэтому среднее значений консеквентов 0,25 и 0,625 равно 0,4.

```python
import math

from fuzzyroutines import ContinuousUniverse, LinguisticTerm, ScalarFuzzySet, Triangle
from fuzzyroutines import NegationPolicy, SNormPolicy, TNormPolicy
from fuzzyroutines.inference import (
    AffineConsequent, ConstantConsequent, FuzzyVariable, InferencePolicy,
    SugenoModel, SugenoRule, TermCondition,
)
from fuzzyroutines.sugeno_batches import EvaluateSugenoBatch

universe = ContinuousUniverse(0, 1, True, True)
low = LinguisticTerm("low", ScalarFuzzySet(universe, Triangle(-1, 0, 1)))
high = LinguisticTerm("high", ScalarFuzzySet(universe, Triangle(0, 1, 1)))
model = SugenoModel(
    (FuzzyVariable("risk", (low, high)), FuzzyVariable("load", (low, high))),
    (
        SugenoRule("base response", TermCondition("risk", "low"), ConstantConsequent(0.25), weight=0.5),
        SugenoRule("risk response", TermCondition("risk", "high"), AffineConsequent(0.5, (("risk", 0.5),))),
    ),
    InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard")),
    universe,
)

result = EvaluateSugenoBatch(
    model,
    [[0.5, 0.25], [1.2, 0.25]],
    featureNames=("load", "risk"),
    backend="numpy",
    onError="mask",
    trace="full",
    chunkSize=1,
)
assert result.featureNames == ("risk", "load")
assert result.status.tolist() == [0, 2]
assert result.validMask.tolist() == [True, False]
assert math.isclose(result.values[0], 0.4, rel_tol=0, abs_tol=1e-12)
assert math.isnan(result.values[1])
assert result.trace.firedRuleCount.tolist() == [2, -1]
assert result.trace.full.firings[0].tolist() == [0.375, 0.25]
```

Обычный вещественный массив должен иметь форму `(rows, features)`. Подойдёт и прямоугольный список или кортеж. Пустой пакет передайте как пустой список или массив формы `(0, features)`. Столбец нужен для каждой объявленной входной переменной, в том числе для нагрузки.

При `onError="mask"` отбирайте допустимые прогнозы по `validMask`. Код 0 означает успех, 1 — неконечную координату (в том числе при переполнении преобразования), 2 — выход входа за область определения, 3 — нулевое срабатывание, 4 — выход за область значений, 5 — численную ошибку. При `onError="raise"` сообщается первая ошибочная строка в исходном порядке. Некорректная форма, неверные имена и неподдерживаемая модель прерывают вызов в обоих режимах.

С `trace="off"` доступны значения, статусы и метаданные модели. Режим `"summary"` добавляет число сработавших правил и максимальную силу срабатывания, а `"full"` — степени принадлежности, срабатывания и вклады правил. `chunkSize` ограничивает размер блока вычислений. Полная трассировка хранит данные всех возвращённых строк, поэтому её объём растёт с числом наблюдений.

См. [API пакетного вывода Сугено](../api/modern/sugeno-batches.md).

<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# От нечётких правил к численному отклику

Пусть система мониторинга получила нормированную оценку риска $x=0.25$.
Нужно выбрать интенсивность реакции от нуля до единицы. Зададим два правила:
**если риск низкий, реакция слабая**; **если риск высокий, реакция сильная**.
Оба правила могут сработать одновременно, но с разной степенью.

В системе Мамдани каждое правило формирует **нечёткое множество выходных
значений**. Мы объединяем эти множества и находим центр тяжести полученной
фигуры. В системе Сугено каждое правило даёт **число** — постоянное или
вычисляемое по входным данным. Итогом становится среднее этих чисел с весами,
зависящими от степени срабатывания правил. Входная логика может быть одинаковой,
а способ формирования выхода — разным.

Для наглядности возьмём две линейные функции принадлежности на $[0,1]$:
$\mu_L(x)=1-x$ и $\mu_H(x)=x$. При $x=0.25$ получаем $(0.75,0.25)$.
Это степени принадлежности, а не вероятности событий. Здесь используется
учебная шкала из двух термов; историческая
[Универсальная нечёткая шкала](universal-fuzzy-scale.md) остаётся отдельной моделью.

## Мамдани: объединяем множества и находим центр тяжести

![Четыре этапа нечёткого вывода Мамдани](../../en/assets/figures/inference-mamdani.svg)

Вес каждого правила равен единице, поэтому степени срабатывания совпадают
со степенями принадлежности входа. Активация через минимум ограничивает высоту
выходных функций на уровнях $0.75$ и $0.25$. Агрегация через максимум выбирает
верхнюю огибающую:

$$
\alpha_i=w_i A_i(\mathbf{x}),\qquad
\mu_{\mathrm{out}}(y)=\max_i\min(\alpha_i,\mu_{B_i}(y)).
$$

Численный отклик — центр тяжести площади под этой огибающей на явно заданном
интервале $D$:

$$
y^*=\frac{\int_D y\mu_{\mathrm{out}}(y)\,\mathrm{d}y}
{\int_D\mu_{\mathrm{out}}(y)\,\mathrm{d}y}.
$$

При $x=0.25$ огибающая равна $0.75$ до $y=0.25$, затем $1-y$ до $y=0.75$,
затем $0.25$. Площадь составляет $1/2$, первый момент — $37/192$.
Получаем $y^*=37/96\approx0.385417$. Это интенсивность реакции, а не
вероятность того, что тревога обоснованна.

```python
from fuzzyroutines import (
    ContinuousUniverse, IntegrationDomain, LinguisticTerm, NegationPolicy,
    ScalarFuzzySet, SNormPolicy, TNormPolicy,
)
from fuzzyroutines.inference import (
    FuzzyVariable, InferencePolicy, MamdaniModel, MamdaniRule, TermCondition,
)

universe = ContinuousUniverse(0, 1, True, True)
terms = (
    LinguisticTerm("low", ScalarFuzzySet(universe, lambda x: 1 - x)),
    LinguisticTerm("high", ScalarFuzzySet(universe, lambda x: x)),
)
policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
model = MamdaniModel(
    (FuzzyVariable("risk", terms),), FuzzyVariable("response", terms),
    (
        MamdaniRule("low response", TermCondition("risk", "low"), "low"),
        MamdaniRule("high response", TermCondition("risk", "high"), "high"),
    ),
    policy, TNormPolicy("logic"), SNormPolicy("logic"),
)
result = model.Evaluate({"risk": 0.25}, IntegrationDomain(0, 1))
print(round(result.value, 6))  # 0.385417
print(tuple(rule.firingStrength for rule in result.rules))  # (0.75, 0.25)
```

Если не передать `IntegrationDomain`, метод `Evaluate` вернёт агрегированное
множество и вклады правил без вычисления центра тяжести. Функции принадлежности
`result.rules[i].activatedSet` и `result.outputSet` можно вывести на график для
объяснения результата. Выражения И, ИЛИ и НЕ задаются через `AllOf`, `AnyOf` и
`NotCondition`. Конъюнкция в условии, активация заключения и агрегация выходов
настраиваются независимо.

## Сугено: усредняем численные заключения

![Вклады правил Сугено нулевого и первого порядка](../../en/assets/figures/inference-sugeno.svg)

Правила Сугено нулевого порядка возвращают постоянные, например $(0.2,0.8)$.
У правил первого порядка заключения — аффинные функции, например
$(x/2,0.5+x/2)$:

$$
z_i=b_i+\sum_j a_{ij}x_j,\qquad
\bar\alpha_i=\frac{\alpha_i}{\sum_k\alpha_k},\qquad
z=\sum_i\bar\alpha_i z_i.
$$

При тех же входе и степенях срабатывания постоянные заключения дают
$0.75\cdot0.2+0.25\cdot0.8=0.35$, а аффинные —
$0.75\cdot0.125+0.25\cdot0.625=0.25$. Контурные столбцы показывают значения
заключений, закрашенные — их взвешенные вклады. Сумма вкладов и есть результат.
Центр тяжести площади здесь не вычисляется.

В `SugenoRule` передают `ConstantConsequent(value)` или
`AffineConsequent(intercept, ((inputName, coefficient), ...))`.
Для `SugenoModel` обязательно задаётся `outputUniverse`.
В трассировке каждого правила доступны `consequentValue`,
`normalizedStrength` и `contribution`.

Полный [пример мониторинга](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/examples/inference.py)
запускается после установки версии-кандидата, содержащей этот API:

```bash
python examples/inference.py
```

Он проверяет три независимо рассчитанных эталонных значения и печатает JSON
с входами, степенями срабатывания, заключениями и вкладами. Графический интерфейс
и библиотеки визуализации для запуска примера не нужны. Графики воспроизводятся
командой `python -m tools.generate_inference_figures --output-directory docs/site/content/en/assets/figures`;
флаг `--check` проверяет совпадение файлов с сохранёнными версиями.
Для генерации нужны зависимости из `docs/requirements-plots.txt`.

## Составные условия и веса правил

Этот самостоятельный пример объединяет риск и нагрузку с помощью И, ИЛИ и НЕ.
При `risk=0.25` и `load=0.75` степени истинности условий равны `(0.75, 0.25)`.
Вес первого правила `0.5` меняет степени срабатывания на `(0.375, 0.25)`;
после нормировки получаются `(0.6, 0.4)`. Постоянное и аффинное заключения
дают `(0.2, 0.625)`, поэтому отклик равен `0.37`. Правила выбраны для разбора
вычислений и не являются откалиброванной политикой мониторинга.

```python
import math

from fuzzyroutines import (
    ContinuousUniverse, LinguisticTerm, NegationPolicy,
    ScalarFuzzySet, SNormPolicy, TNormPolicy,
)
from fuzzyroutines.inference import (
    AffineConsequent, AllOf, Antecedent, AnyOf, ConstantConsequent,
    FuzzyVariable, InferencePolicy, NotCondition,
    SugenoModel, SugenoRule, TermCondition,
)

universe = ContinuousUniverse(0, 1, True, True)
terms = (
    LinguisticTerm("low", ScalarFuzzySet(universe, lambda x: 1 - x)),
    LinguisticTerm("high", ScalarFuzzySet(universe, lambda x: x)),
)
inputs = (FuzzyVariable("risk", terms), FuzzyVariable("load", terms))
policy = InferencePolicy(TNormPolicy("logic"), SNormPolicy("logic"), NegationPolicy("standard"))
busy = TermCondition("load", "high")
condition: Antecedent = AllOf((TermCondition("risk", "low"), busy))
model = SugenoModel(inputs, (
    SugenoRule("low risk and busy", condition, ConstantConsequent(0.2), weight=0.5),
    SugenoRule("risk or spare capacity", AnyOf((TermCondition("risk", "high"), NotCondition(busy))),
               AffineConsequent(0.5, (("risk", 0.5),))),
), policy, universe)
result = model.Evaluate({"risk": 0.25, "load": 0.75})
assert tuple(rule.antecedentGrade for rule in result.rules) == (0.75, 0.25)
assert tuple(rule.firingStrength for rule in result.rules) == (0.375, 0.25)
assert tuple(rule.consequentValue for rule in result.rules) == (0.2, 0.625)
assert math.isclose(result.value, 0.6 * 0.2 + 0.4 * 0.625, rel_tol=0, abs_tol=1e-15)
assert len(result.inputGrades) == 4
print(round(result.value, 2))  # 0.37
```

## Что учитывать в приложении

Модель имеет именованные скалярные входы и один скалярный выход. Нужно передать
ровно объявленные имена и конечные координаты из соответствующих универсальных
множеств. Если ни одно правило не сработало, возникает `UndefinedResultError`.
Предыдущий результат или условный отклик по умолчанию не подставляется.
Множество Мамдани с нулевой площадью нельзя дефаззифицировать.
Интегрирование составной функции выполняется численно с настройками
`CentroidPolicy`; при недостаточной сходимости возникает `CentroidConvergenceError`.
Выборочные вычисления произвольной функции не гарантируют обнаружения узких
особенностей между проверенными координатами.

Каждое заключение Сугено, в том числе у неактивного правила, должно быть конечным
и принадлежать выходному универсальному множеству. Переполнение вызывает
`NumericalError`; автоматического ограничения значений нет. Неизменяемые
контейнеры модели хранят ссылки на пользовательские функции принадлежности.
Для воспроизводимого результата эти функции должны быть чистыми.

Эти модели используют фиксированные правила: они не обучают параметры и не
сохраняют граф автоматического дифференцирования. Обучаемая нейронечёткая система
требует отдельной модели. Полные контракты приведены в
[справочнике API](../api/modern/inference.md).

## Источники

- Mamdani, E. H.; Assilian, S. (1975). [An experiment in linguistic synthesis with a fuzzy logic controller](https://doi.org/10.1016/S0020-7373(75)80002-2).
- Takagi, T.; Sugeno, M. (1985). [Fuzzy identification of systems and its applications to modeling and control](https://doi.org/10.1109/TSMC.1985.6313399).

Учебная модель мониторинга и её численные примеры разработаны независимо;
они не воспроизводят экспериментальные установки из этих работ.

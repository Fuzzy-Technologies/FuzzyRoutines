<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Примеры миграции с исторического API на современный {#historical-to-modern-api-migration-examples}

- Статус: текущая граница реализации `develop`
- Связанная задача: #99
- Каноническая отправная точка: [совместимость и миграция](../../../../COMPATIBILITY.md)
- Решение о совместимости: [ADR-0001](../../../../adr/0001-backward-compatibility-contract.md)
- Точная граница реализации: [текущий статус](../../../../current-status.md)

## Правило миграции {#migration-rule}

Исторические имена поддерживаются. Существующим пользователям не требуется переименовывать
`MFunction`, `FuzzySet`, `FuzzyScale`, `UniversalFuzzyScale`, `Defuz` или скалярные
операторы только ради перехода на версию 2. Переносите по одной области за раз,
когда специализированный API уже предоставляет нужное приложению поведение.

Текущий современный API покрывает явные области, неизменяемые скалярные нечёткие множества,
алгебру множеств, отношения, вычисляемые свойства, альфа-срезы, нормализацию с точной высотой,
типизированные лингвистические термы и упорядоченные шкалы. Неизменяемые фабрики функций
принадлежности доступны через `fuzzyroutines.membership`. Доступны точный и регистронезависимый
Unicode-поиск по типизированной шкале, явные политики фаззификации и диагностика покрытия,
перекрытий, пробелов и разбиения на явной сетке без изменения коэффициентов принадлежности.
Современная центроидная дефаззификация использует явную область интегрирования и численную
политику. Примеры ниже явно обозначают оставшиеся ограничения и используют только доступные формы вызова.

| Область                | Поддерживаемый исторический API                                             | Предпочтительный путь, доступный сейчас                                                                      |
| ---------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Операторы              | `FuzzyNOT`, `TNorm`, `SCoNorm` и функции композиции                         | `NegationPolicy`, `TNormPolicy` и `SNormPolicy`; операции множеств требуют явных политик                     |
| Функции принадлежности | `MFunction` и каждый защищённый исторический идентификатор                  | Неизменяемые вызываемые фабрики `fuzzyroutines.membership`, включая обычный порядок `Triangle` и `Trapezoid` |
| Нечёткие множества     | Изменяемый `FuzzySet` с историческим интервалом интегрирования `supportSet` | Неизменяемый `ScalarFuzzySet` с явным `ContinuousUniverse` или `DiscreteUniverse`                            |
| Шкалы                  | `FuzzyScale` и `UniversalFuzzyScale`                                        | Типизированное представление, поиск, фаззификация и выборочная диагностика через `LinguisticScale`           |
| Производные операции   | Нет эквивалентного единого современного интерфейса                          | `DeriveProperties`, `AlphaCut`, `SampleAlphaCut`, `Height` и `Normalize` сохраняют явные границы точности    |
| Дефаззификация         | `FuzzySet.Defuz()` и `defuzValue`                                           | `Centroid()` с явными `ScalarFuzzySet`, `IntegrationDomain` и необязательной `CentroidPolicy`                |

## Операторы {#operators}

Исторические скалярные вызовы выбирают семейство строкой:

```python
from fuzzyroutines.FuzzyRoutines import FuzzyNOT, SCoNorm, TNorm

conjunction = TNorm(0.4, 0.7, normType="algebraic")
disjunction = SCoNorm(0.4, 0.7, normType="logic")
negated = FuzzyNOT(0.4)
```

Современные скалярные операции и операции над множествами делают выбранную политику
неизменяемым значением:

```python
from fuzzyroutines import NegationPolicy, SNormPolicy, TNormPolicy

conjunction = TNormPolicy("algebraic").Evaluate(0.4, 0.7)
disjunction = SNormPolicy("logic").Evaluate(0.4, 0.7)
negated = NegationPolicy("standard").Evaluate(0.4)
```

У `TNormCompose` и `SCoNormCompose` пока нет специализированных современных аналогов.
Сохраняйте эти исторические имена для n-арной композиции; не заменяйте их недокументированным API.

## Функции принадлежности {#membership-functions}

Историческая фабрика и соглашения о параметрах остаются исполняемым API:

```python
from fuzzyroutines.FuzzyRoutines import MFunction

# Historical order is preserved: a = left foot, c = apex, b = right foot.
membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
grade = membershipFunction.mju(0.25)
```

В новом коде используйте неизменяемый современный вычислитель напрямую:

```python
from fuzzyroutines import ContinuousUniverse, ScalarFuzzySet
from fuzzyroutines.membership import Triangle

membershipFunction = Triangle(left=0.0, peak=0.5, right=1.0)
universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
fuzzySet = ScalarFuzzySet(universe, membershipFunction)
```

Дополнительные имена реестра `gaussian`, `logistic`, `sShoulder` и `harringtonDesirability`
доступны, но миграция не требует переименования `exponential`, `sigmoidal`, `parabolic`
или `desirability`. До смены идентификатора прочитайте
[контракт функций принадлежности](../../../../mathematics/membership-function-contracts.md):
некоторые исторические порядки параметров намеренно сохранены.

Современный контракт `Triangle(left, peak, right)` намеренно отличается от исторического
`MFunction("triangle", a=left, b=right, c=peak)`. Аналогично,
`Trapezoid(left, plateauStart, plateauEnd, right)` отличается от исторического
соответствия ключевых аргументов `trapezium`. Не переносите позиционный кортеж между API
без явного преобразования. Общие скалярные формулы сохраняют принятые исторические
границы, включая `peak == right` для существующего верхнего треугольного терма.

Ранние снимки разработки v2 называли аргументы плато `plateau_start` и `plateau_end`.
Теперь канонические имена — `plateauStart` и `plateauEnd` в `Bell`, `Trapezoid`
и доступной только для чтения таблице параметров `MembershipFunction`.
Конструкторы и прямое создание семейства по-прежнему принимают старые ключевые имена
во время выполнения; одновременное указание псевдонима и канонического имени отклоняется.
Позиционный порядок, смысл параметров и численные результаты не изменились.
Новый код и статическая типизация используют канонические имена camelCase.

## Нечёткие множества {#fuzzy-sets}

Историческое создание объединяет объект принадлежности, изменяемое имя
и кортеж с историческим названием `supportSet`:

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = FuzzySet(
    membershipFunction,
    supportSet=(0.0, 1.0),
    linguisticName="Medium",
)
```

Для новой алгебры множеств объявляйте универсальное множество отдельно и передавайте
вызываемый объект принадлежности:

```python
from fuzzyroutines import (
    Complement,
    ContinuousUniverse,
    NegationPolicy,
    ScalarFuzzySet,
)

universe = ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True)
membershipFunction = Triangle(left=0.0, peak=0.5, right=1.0)
fuzzySet = ScalarFuzzySet(universe, membershipFunction)
complement = Complement(fuzzySet, NegationPolicy("standard"))

assert complement.Membership(0.25) == 0.5
```

У `ScalarFuzzySet` нет поля лингвистического имени и численного интервала интегрирования.
`IntegrationDomain` — отдельное рабочее значение, не математическое множество поддержки.

## Шкалы {#scales}

Продолжайте использовать защищённые исторические классы:

```python
from fuzzyroutines.FuzzyRoutines import UniversalFuzzyScale

scale = UniversalFuzzyScale()
level = scale.Fuzzy(0.5)
assert level["name"] == "Med"
```

Современный API представляет имена, нечёткие множества и явный порядок термов,
не наследуя историческую форму словаря неявно:

```python
from fuzzyroutines import FuzzificationPolicy, LinguisticScale, LinguisticTerm

modernScale = LinguisticScale((LinguisticTerm("Medium", fuzzySet),))
term = modernScale.GetTermByName("medium", exactMatching=False)
result = modernScale.Fuzzify(
    0.5,
    FuzzificationPolicy(tiePolicy="last", minimumConfidence=0.05),
)
```

Современный поиск сопоставляет только полные имена. По умолчанию сравнение точное
и учитывает регистр; `exactMatching=False` использует регистронезависимое сравнение Unicode.
Поиск не является нечётким, префиксным или поиском по подстроке.
Современный `Fuzzify()` возвращает все упорядоченные степени принадлежности и максимум
как уверенность. Политика явно задаёт порог отсутствия совпадения, допуск равенства
и выбор `first`, `last` или `all`. Исторические пользователи могут сохранить `FuzzyScale`
или `UniversalFuzzyScale`; `tiePolicy="last"` даёт современный эквивалент правила
победы более позднего терма, не меняя `Fuzzy()`.

## Дефаззификация {#defuzzification}

Существующий код может продолжать использовать пересчитывающую точку совместимости:

```python
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

membershipFunction = MFunction("triangle", a=0.0, b=1.0, c=0.5)
fuzzySet = FuzzySet(membershipFunction, supportSet=(0.0, 1.0))
centroid = fuzzySet.Defuz()
```

`Defuz()` теперь использует современную аналитическую/адаптивную стратегию и игнорирует
сохранённый атрибут совместимости `MFunction.accuracy`. Исторический кортеж `supportSet`
задаёт конечный интервал численного интегрирования, не точное множество поддержки.
Новый код может явно выразить ту же операцию:

```python
from fuzzyroutines import Centroid, ContinuousUniverse, IntegrationDomain, ScalarFuzzySet

integrationDomain = IntegrationDomain.FromLegacyInterval(fuzzySet.supportSet)
modernSet = ScalarFuzzySet(ContinuousUniverse(), membershipFunction.mju)
centroid = Centroid(modernSet, integrationDomain)
```

Об аналитических семействах, адаптивных допусках, нулевой площади и ошибке сходимости
см. [центроидную дефаззификацию](../../../../mathematics/centroid-defuzzification.md).

## Исполняемые примеры {#executable-examples}

Оба примера импортируют только публичные точки входа пакета и не изменяют пути дерева исходного кода:

```bash
python examples/migration/historical_compatibility.py
python examples/migration/modern_supported.py
```

- [`historical_compatibility.py`](../../../../../examples/migration/historical_compatibility.py)
  проверяет все пять исторических областей.
- [`modern_supported.py`](../../../../../examples/migration/modern_supported.py) проверяет явные
  политики операторов и неизменяемые нечёткие множества, используя специализированную
  неизменяемую фабрику принадлежности без импорта исторического модуля.

Тесты примеров запускают каждый скрипт из временного рабочего каталога.
Workflow пакета независимо устанавливает wheel и исходный дистрибутив, убирает
`PYTHONPATH`, подтверждает происхождение импорта внутри чистого окружения и запускает
те же скрипты через доступные оболочке точки входа. Полный контракт артефактов и кодов
завершения см. в [«Исполняемые тесты, инструменты, бенчмарки и примеры»](../../../../executable-tests-tools-and-examples.md).

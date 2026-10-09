<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Сопровождение исторических интеграций {#maintain-historical-integrations}

Эти рецепты предназначены для существующих потребителей 1.x. Исторический фасад — `fuzzyroutines.FuzzyRoutines`; новые интеграции стоит начинать с неизменяемого [современного API](../api/modern/index.md). Поддерживаются Python 3.13 и 3.14. Совместимость сохраняет проверенные вызовы и имена, а [заметки о миграции](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/migration/1.0.3-to-2.0.0.md) объясняют математические исправления и удалённые импорты вспомогательных объектов. Каждый блок самостоятелен и тестируется на установленных дистрибутивах.

## Разбор диапазонов и проверка исторических скаляров {#parse-ranges-and-validate-historical-scalar-values}

```python
from fuzzyroutines.FuzzyRoutines import DiapasonParser, IsCorrectFuzzyNumberValue, IsNumber

assert DiapasonParser("1-3,5,3") == [1, 2, 3, 5]
assert IsNumber(0.5) and not IsNumber(True)
assert IsCorrectFuzzyNumberValue(0.5) and not IsCorrectFuzzyNumberValue(1.5)
print(DiapasonParser("1-3,5,3"))
```


Исторические скалярные предикаты принимают встроенные `int` и `float`, исключая логические значения. `IsNumber` проверяет тип, но не гарантирует конечность. Для ошибочного текста парсер сохраняет историческое поведение: диагностическое сообщение и пустой список. Проверяйте результат, если пустой диапазон недопустим в проекте.

## Объединение исторических степеней {#combine-historical-grades}

```python
from math import isclose
from fuzzyroutines.FuzzyRoutines import (
    FuzzyAND, FuzzyNOT, FuzzyNOTParabolic, FuzzyOR,
    SCoNorm, SCoNormCompose, TNorm, TNormCompose,
)

assert FuzzyAND(0.4, 0.7) == 0.4 and FuzzyOR(0.4, 0.7) == 0.7
assert isclose(FuzzyNOT(0.4), 0.6) and isclose(FuzzyNOTParabolic(0.4), 0.6)
expectedAnd = {"logic": 0.4, "algebraic": 0.28, "boundary": 0.1, "drastic": 0}
expectedOr = {"logic": 0.7, "algebraic": 0.82, "boundary": 1, "drastic": 1}
for family in expectedAnd:
    assert isclose(TNorm(0.4, 0.7, normType=family), expectedAnd[family], abs_tol=1e-12)
    assert isclose(SCoNorm(0.4, 0.7, normType=family), expectedOr[family], abs_tol=1e-12)
assert isclose(TNormCompose(0.4, 0.7, 0.9, normType="algebraic"), 0.252)
assert isclose(SCoNormCompose(0.4, 0.7, 0.9, normType="algebraic"), 0.982)
print(TNormCompose(0.4, 0.7, 0.9, normType="algebraic"))
```


Композиция сворачивается слева направо. Один допустимый операнд возвращается сам; отсутствие операндов вызывает ошибку. Все операнды и политика проверяются, включая унарный случай. `FuzzyNOT` — историческое параметрическое отрицание; при альфа 0.5 по умолчанию оно сводится к стандартному дополнению. Параболический адаптер сохраняет `epsilon` как проверяемый аргумент совместимости, но он не меняет точность результата.

## Все исторические семейства и псевдонимы {#evaluate-all-historical-membership-families-and-aliases}

```python
from math import exp, isclose
from fuzzyroutines.FuzzyRoutines import MFunction

cases = (
    ("hyperbolic", {"a": 1, "b": 2, "c": 0}, 1),
    ("bell", {"a": -2, "b": -1, "c": 1}, 1),
    ("parabolic", {"a": -2, "b": 2}, 0.5),
    ("triangle", {"a": -2, "b": 2, "c": 0}, 1),
    ("trapezium", {"a": -2, "b": 2, "c": -1, "d": 1}, 1),
    ("exponential", {"a": 0, "b": 1}, 1),
    ("sigmoidal", {"a": 2, "b": 0}, 0.5),
    ("desirability", {}, exp(-1)),
)
for family, parameters, expected in cases:
    model = MFunction(family, **parameters)
    assert isclose(model.mju(0), expected)
    assert model.name == model.mju.__name__ and model.parameters == parameters
for alias, canonical, parameters in (
    ("sShoulder", "parabolic", {"a": -2, "b": 2}),
    ("gaussian", "exponential", {"a": 0, "b": 1}),
    ("logistic", "sigmoidal", {"a": 2, "b": 0}),
    ("harringtonDesirability", "desirability", {}),
):
    assert MFunction(alias, **parameters).mju(0) == MFunction(canonical, **parameters).mju(0)
triangle = MFunction("triangle", a=0, b=2, c=1)
triangle.parameters = {"a": 0, "b": 4, "c": 2}
assert triangle.mju(2) == 1
print(triangle.name, triangle.parameters)
```


`mju` связывается с выбранным публичным методом семейства: `Hyperbolic`, `Bell`, `Parabolic`, `Triangle`, `Trapezium`, `Exponential`, `Sigmoidal` или `Desirability`. Передавайте одну координату. Псевдонимы выбирают те же методы и не задают новую математику. Исторический порядок треугольника: **a = левая опорная точка, b = правая опорная точка, c = вершина**; современный `Triangle` использует **left, peak, right**. Историческая трапеция: **a = левая опорная точка, b = правая опорная точка, c = начало плато, d = конец плато**; современный `Trapezoid` использует геометрический порядок слева направо. Изменяемый сеттер параметров повторно проверяет весь словарь. После замены `mju` нельзя ожидать применимости стандартных аналитических сертификатов.

## Пересчёт изменяемого множества после смены модели или окна {#recompute-a-mutable-set-after-changing-its-model-or-window}

```python
from math import isclose
from fuzzyroutines.FuzzyRoutines import FuzzySet, MFunction

model = MFunction("triangle", a=0, b=2, c=1)
fuzzySet = FuzzySet(model, supportSet=(0, 2), linguisticName="Preferred")
assert fuzzySet.name == "Preferred" and fuzzySet.mFunction is model
assert fuzzySet.supportSet == (0, 2)
assert isclose(fuzzySet.Defuz(), 1) and isclose(fuzzySet.defuzValue, 1)
replacement = MFunction("triangle", a=0, b=4, c=2)
fuzzySet.name = "Updated preference"
fuzzySet.mFunction = replacement
fuzzySet.supportSet = (0, 4)
assert fuzzySet.mFunction is replacement and fuzzySet.name == "Updated preference"
assert isclose(fuzzySet.Defuz(), 2) and isclose(fuzzySet.defuzValue, 2)
print(fuzzySet.name, fuzzySet.Defuz())
```


Несмотря на историческое имя, `supportSet` — конечное **окно интегрирования**, а не аналитическое множество поддержки. `Defuz()` заново вычисляет центроид с проверенной современной численной политикой. Чтение `defuzValue` также пересчитывает текущий результат; оба пути учитывают изменения модели и окна. `MFunction.accuracy` сохранён для совместимости и не настраивает современную квадратуру центроида.

## Осознанное чтение и замена уровней шкалы {#read-and-replace-scale-levels-deliberately}

```python
from fuzzyroutines.FuzzyRoutines import FuzzyScale, FuzzySet, MFunction, UniversalFuzzyScale

first = FuzzySet(MFunction("triangle", a=0, b=2, c=1), supportSet=(0, 2))
second = FuzzySet(MFunction("triangle", a=0, b=2, c=1), supportSet=(0, 2))
scale = FuzzyScale()
scale.name = "Two identical preferences"
scale.levels = [{"name": "First", "fSet": first}, {"name": "Second", "fSet": second}]
assert scale.name == "Two identical preferences" and len(scale.levels) == 2
assert scale.Fuzzy(1)["name"] == "Second"
assert scale.GetLevelByName("First")["fSet"] is first
assert scale.GetLevelByName("SECOND", exactMatching=False)["fSet"] is second
universal = UniversalFuzzyScale()
assert len(universal.levels) == len(universal.levelsNames) == len(universal.levelsNamesUpper)
assert universal.Fuzzy(0.5)["name"] in universal.levelsNames
assert {name.upper() for name in universal.levelsNames} == set(universal.levelsNamesUpper)
print(scale.Fuzzy(1)["name"], tuple(universal.levelsNames))
```


Историческое равенство разрешается в пользу **более позднего** уровня; современная политика по умолчанию выбирает первый терм, альтернативы задаются явно. Историческая шкала всегда возвращает победителя, даже при нулевом покрытии; современный результат допускает отказ. Универсальная предустановка сохраняет историческую геометрию и известные ограничения покрытия. Проверяйте новую рабочую шкалу, а не считайте название предустановки доказательством полноты покрытия.

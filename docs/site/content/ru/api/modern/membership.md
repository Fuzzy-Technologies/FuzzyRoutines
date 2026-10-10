<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Функции принадлежности {#membership-functions}

Модуль функций принадлежности владеет скалярными аналитическими формулами. Его неизменяемые вызываемые определения можно передавать прямо в `ScalarFuzzySet`. `Triangle` использует обычный порядок left, peak, right; `Trapezoid` — left, plateau start, plateau end, right. Исторические идентификаторы `MFunction` сохраняют свои соглашения о параметрах через явные адаптеры.

## Пользовательские скалярные вычислители {#custom-scalar-evaluators}

`MembershipCallable` — типизированный структурный контракт для пользовательских функций, лямбд, связанных методов и вызываемых объектов. Наследование, обёртка и регистрация не нужны. Вычислитель принимает одну позиционную конечную координату `numbers.Real` и возвращает конечную вещественную степень в `[0, 1]`; логические значения исключены с обеих сторон контракта.

В аннотациях `MembershipScalar` явно включает `float | numbers.Real`; статические анализаторы также принимают встроенные целые числа через числовое продвижение к `float`. Это не смешивает регистрацию типа во время выполнения со статическим наследованием: одного `numbers.Real` недостаточно для обычных значений `float` в распространённых анализаторах типов. Пользовательская функция с аннотацией только `float -> float` сужает более широкий контракт и не обещает поддержку каждого вещественного скаляра. Используйте `MembershipScalar` на входе, а на выходе — этот псевдоним либо `float`.

Конструктор `ScalarFuzzySet` проверяет возможность вызова, не выполняя функцию. `Membership` до вызова проверяет координату относительно объявленного универсального множества, затем проверяет возвращённую степень без приведения или ограничения диапазона. Неверная сигнатура обнаруживается при вызове; пользовательские исключения передаются выше. Протокол не выполняет проверку значений во время выполнения и не инспектирует сигнатуру. Прямой вызов пользовательской функции следует её собственным правилам проверки.

```python
from fuzzyroutines.defuzzification import Centroid
from fuzzyroutines.domain import ContinuousUniverse, IntegrationDomain
from fuzzyroutines.fuzzysets import ScalarFuzzySet
from fuzzyroutines.membership import MembershipCallable, MembershipScalar


def RisingGrade(coordinate: MembershipScalar) -> MembershipScalar:
    """Return a linear grade for coordinates in the closed unit interval."""

    return coordinate


membershipFunction: MembershipCallable = RisingGrade
fuzzySet = ScalarFuzzySet(
    ContinuousUniverse(0.0, 1.0, leftClosed=True, rightClosed=True),
    membershipFunction,
)
centroid = Centroid(fuzzySet, IntegrationDomain(0.0, 1.0))
assert abs(centroid - 2 / 3) < 1e-12
```


Центроид равен `2 / 3`; применяется адаптивное численное интегрирование на явно заданной ограниченной области. Протокол не наделяет произвольную функцию точными непрерывными поддержкой, ядром, высотой или аналитическими моментами. Функция должна быть достаточно регулярной для выбранной политики интегрирования, а степени — согласованными на протяжении вычисления. Изменяемый служебный учёт, например счётчик вызовов, допустим, если не меняет степени. Снимок вызываемого объекта автоматически не создаётся. См. исполняемый пример [`custom_membership.py`](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/examples/migration/custom_membership.py).

Изолированную статическую проверку потребителя можно воспроизвести с дополнительно установленным mypy:

```bash
python -m mypy --python-version 3.13 --strict --follow-imports silent --warn-unused-ignores tests/typing/custom_membership.py
```


Она проверяет вызовы с встроенными вещественными и целыми значениями, аналитические вычислители и связанные методы; отвергает суженные входы, нечисловые результаты и отсутствие позиционных аргументов. Диагностика импортированных модулей намеренно скрыта через `--follow-imports silent`: проверяется контракт потребителя. Более широкая проверка типов исходного и установленного пакета из задачи #95 описана в [контракте типизации](https://github.com/Fuzzy-Technologies/FuzzyRoutines/blob/develop/docs/public-typing.md). Эти аннотации не доказывают конечность значений, исключение логических значений и допустимый диапазон степеней во время выполнения.

## Практические примеры {#worked-examples}

[Галерея функций принадлежности](../../guides/membership-families.md) показывает все семейства; [пользовательская модель](../../guides/custom.md) использует типизированную вызываемую функцию.

::: fuzzyroutines.membership
    options:
      members:
        - MembershipCallable
        - MembershipScalar
        - MembershipFunction
        - Hyperbolic
        - Bell
        - SShoulder
        - Triangle
        - Trapezoid
        - Gaussian
        - Logistic
        - HarringtonDesirability

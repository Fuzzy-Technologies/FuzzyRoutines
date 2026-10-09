<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Представляет одно историческое семейство аналитических функций принадлежности.

Args:
    userFunc: Зарегистрированный идентификатор семейства. Псевдонимы совместимости включают
        `"gaussian"`, `"logistic"`, `"sShoulder"` и `"harringtonDesirability"`.
    **membershipFunctionParams: Точный набор параметров выбранного семейства. Каждое значение
        должно быть конечным числом встроенного типа `int` или `float`; `bool` исключён.

Raises:
    ValueError: Неверное семейство или набор его параметров.

Attributes:
    accuracy: Сохранённый изменяемый атрибут совместимости. Современная центроидная
        дефаззификация намеренно его игнорирует.
    mju: Связанный вычислитель выбранного семейства.

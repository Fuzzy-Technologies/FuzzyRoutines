<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Возвращает уровень с наибольшей принадлежностью в `realValue`.

При равенстве выбирается более поздний уровень в порядке шкалы.

Args:
    realValue: Конечная координата встроенного типа `int` или `float`, вычисляемая
        функцией принадлежности каждого уровня; `bool` исключён.

Returns:
    Изменяемый словарь выбранного уровня.

Raises:
    ValueError: `realValue` не является поддерживаемым конечным числом встроенного типа.

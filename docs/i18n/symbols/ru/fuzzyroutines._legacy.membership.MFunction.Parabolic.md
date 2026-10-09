<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Вычисляет возрастающее параболическое плечо в `x`.

Args:
    x: Конечная координата встроенного типа `int` или `float`; `bool` исключён.

Returns:
    Степень принадлежности из $[0, 1]$.

Raises:
    ValueError: `x` не является поддерживаемым конечным числом встроенного типа.
    OverflowError: Конечный ввод приводит к непредставимому промежуточному квадрату.

<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Возвращает максимум двух степеней принадлежности.

Args:
    aNumber: Левая степень принадлежности встроенного типа `int` или `float` из $[0, 1]$.
    bNumber: Правая степень принадлежности встроенного типа `int` или `float` из $[0, 1]$.

Returns:
    `max(aNumber, bNumber)`.

Raises:
    ValueError: Операнд имеет тип `bool` или другой неподдерживаемый тип, не конечен
        либо находится вне $[0, 1]$.

<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Возвращает допустимую ветвь уравнения $2a-x-y=(2a-1)(y-x)^2$.

Args:
    fuzzyNumber: Степень принадлежности встроенного типа `int` или `float` из $[0, 1]$;
        `bool` исключён.
    alpha: Неподвижная точка встроенного типа `int` или `float` из $[1/4, 3/4]$;
        `bool` исключён.
    epsilon: Устаревший аргумент совместимости; аналитическое решение намеренно его игнорирует.

Returns:
    Параболическое дополнение `fuzzyNumber`.

Raises:
    ValueError: `fuzzyNumber` или `alpha` имеет неподдерживаемый тип, не конечен
        либо находится вне допустимого диапазона.

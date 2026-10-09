<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Вычисляет историческое параметрическое нечёткое отрицание.

При `alpha=0.5` результат совпадает со стандартным дополнением $1 - fuzzyNumber$.

Args:
    fuzzyNumber: Степень принадлежности встроенного типа `int` или `float` из $[0, 1]$;
        `bool` исключён.
    alpha: Неподвижная точка встроенного типа `int` или `float` из $(0, 1)$;
        `bool` исключён.

Returns:
    Степень принадлежности дополнения.

Raises:
    ValueError: Аргумент имеет неподдерживаемый тип, не конечен или находится вне допустимого диапазона.

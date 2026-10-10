<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Вычисляет бинарную s-норму из исторического реестра семейств.

Args:
    aFuzzyNumber: Левая степень принадлежности встроенного типа `int` или `float` из $[0, 1]$.
    bFuzzyNumber: Правая степень принадлежности встроенного типа `int` или `float` из $[0, 1]$.
    normType: Одно из значений `"logic"`, `"algebraic"`, `"boundary"` или `"drastic"`.

Returns:
    Дизъюнкция двух степеней принадлежности по выбранному семейству.

Raises:
    ValueError: Операнд не является конечным поддерживаемым встроенным числом из $[0, 1]$
        либо семейство неизвестно.

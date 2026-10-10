<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Последовательно применяет одну t-норму к одной или нескольким степеням принадлежности.

Args:
    *fuzzyNumbers: Степени принадлежности встроенного типа `int` или `float` из $[0, 1]$;
        значения `bool` исключены.
    normType: Одно из значений `"logic"`, `"algebraic"`, `"boundary"` или `"drastic"`.

Returns:
    Конъюнкция всех операндов с группировкой слева.

Raises:
    ValueError: Операнды отсутствуют, один из них недопустим либо семейство неизвестно.

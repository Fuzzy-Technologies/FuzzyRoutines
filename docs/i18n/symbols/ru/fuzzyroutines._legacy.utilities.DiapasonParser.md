<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Разбирает целые числа и целочисленные диапазоны с включёнными границами, разделённые запятыми.

Args:
    diapason: Строка вида `"1,3-5"`.

Returns:
    Отсортированный список уникальных целых чисел. При неверном вводе печатает историческое
    диагностическое сообщение и возвращает пустой список.

Examples:
    ```python
    DiapasonParser("8-10, 1-3, 3")
    # [1, 2, 3, 8, 9, 10]
    ```

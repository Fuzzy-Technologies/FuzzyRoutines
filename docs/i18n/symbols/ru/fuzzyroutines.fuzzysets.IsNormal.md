<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Проверяет, равна ли точная высота нечёткого множества единице с учётом допуска.

Args:
    fuzzySet: Скалярное нечёткое множество с доказуемой точной высотой.
    tolerance: Неотрицательный абсолютный допуск сравнения.

Returns:
    Находится ли точная высота в пределах `tolerance` от единицы.

Raises:
    TypeError: `fuzzySet` не является скалярным нечётким множеством или `tolerance` не является вещественным скаляром.
    ValueError: `tolerance` отрицателен или точная высота недоступна.

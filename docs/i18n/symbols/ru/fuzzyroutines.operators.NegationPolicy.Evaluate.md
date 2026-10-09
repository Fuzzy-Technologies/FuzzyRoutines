<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Вычисляет выбранное отрицание одной степени принадлежности.

Args:
    grade: Конечная степень принадлежности в $[0, 1]$.

Returns:
    Дополненная степень принадлежности согласно политике.

Raises:
    TypeError: `grade` не является вещественным скаляром.
    ValueError: `grade` неконечна или вне $[0, 1]$.

<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Проверяет равенство двух степеней принадлежности согласно политике.

Args:
    leftGrade: Левая степень принадлежности в $[0, 1]$.
    rightGrade: Правая степень принадлежности в $[0, 1]$.

Returns:
    Точное равенство или `math.isclose` в зависимости от `mode`.

Raises:
    TypeError: Степень не является вещественным скаляром.
    ValueError: Степень неконечна или вне $[0, 1]$.

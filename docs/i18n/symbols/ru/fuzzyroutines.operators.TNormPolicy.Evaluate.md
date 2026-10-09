<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Вычисляет выбранную T-норму двух степеней принадлежности.

Args:
    leftGrade: Левая степень принадлежности в $[0, 1]$.
    rightGrade: Правая степень принадлежности в $[0, 1]$.

Returns:
    Конъюнкция согласно выбранному семейству.

Raises:
    TypeError: Операнд не является вещественным скаляром.
    ValueError: Операнд неконечен или вне $[0, 1]$.

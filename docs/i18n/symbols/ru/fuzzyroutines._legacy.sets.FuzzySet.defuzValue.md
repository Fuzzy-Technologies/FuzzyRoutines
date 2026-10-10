<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Вычисляет и возвращает текущее значение центра площади.

Raises:
    ValueError: Площадь под функцией принадлежности равна нулю или не конечна.
    CentroidConvergenceError: Адаптивное интегрирование не удовлетворяет явному допуску по умолчанию.

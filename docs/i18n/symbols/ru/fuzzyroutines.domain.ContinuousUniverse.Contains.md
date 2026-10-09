<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Проверяет принадлежность конечной скалярной координаты универсальному множеству.

Args:
    coordinate: Проверяемая конечная вещественная координата.

Returns:
    `True` тогда и только тогда, когда координата удовлетворяет правилам обеих границ.

Raises:
    TypeError: Координата не является вещественным скаляром.
    ValueError: Координата неконечна.

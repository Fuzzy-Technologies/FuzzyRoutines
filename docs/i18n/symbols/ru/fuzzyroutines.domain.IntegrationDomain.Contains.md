<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Проверяет, лежит ли конечная скалярная координата в этом замкнутом интервале.

Args:
    coordinate: Проверяемая конечная вещественная координата.

Returns:
    `True`, если `left <= coordinate <= right`.

Raises:
    TypeError: Координата не является вещественным скаляром.
    ValueError: Координата неконечна.

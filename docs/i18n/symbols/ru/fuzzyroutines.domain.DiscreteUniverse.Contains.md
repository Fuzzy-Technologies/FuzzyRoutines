<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Проверяет, объявлена ли конечная скалярная координата в универсальном множестве.

Args:
    coordinate: Проверяемая конечная вещественная координата.

Returns:
    `True`, если `coordinate` входит в объявленные точки.

Raises:
    TypeError: Координата не является вещественным скаляром.
    ValueError: Координата неконечна.

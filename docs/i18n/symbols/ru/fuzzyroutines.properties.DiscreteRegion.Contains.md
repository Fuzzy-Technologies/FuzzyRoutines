<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Проверяет, принадлежит ли конечная координата этой дискретной области.

Args:
    coordinate: Проверяемая конечная вещественная координата.

Returns:
    `True`, если `coordinate` входит в `points`.

Raises:
    TypeError: Координата не является вещественным скаляром.
    ValueError: Координата неконечна.

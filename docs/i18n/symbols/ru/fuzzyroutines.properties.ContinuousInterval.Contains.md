<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Проверяет, принадлежит ли конечная координата этому интервалу.

Args:
    coordinate: Проверяемая конечная вещественная координата.

Returns:
    `True` тогда и только тогда, когда граничные правила допускают координату.

Raises:
    TypeError: Координата не является вещественным скаляром.
    ValueError: Координата неконечна.

<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Проверяет, принадлежит ли конечная координата хотя бы одной компоненте.

Args:
    coordinate: Проверяемая конечная вещественная координата.

Returns:
    `True`, если хотя бы одна компонента содержит координату.

Raises:
    TypeError: Область непустая, а координата не является вещественным скаляром.
    ValueError: Область непустая, а координата неконечна.

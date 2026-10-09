<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Возвращает новое нечёткое множество с одной явно выбранной допустимой политикой отрицания.

Args:
    fuzzySet: Исходное скалярное нечёткое множество.
    negationPolicy: Явная семантика дополнения.

Returns:
    Неизменяемое множество с отложенным вычислением на прежнем универсальном множестве.

Raises:
    TypeError: Один из аргументов имеет неверный тип контракта.

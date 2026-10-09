<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Преобразует исторический двухэлементный кортеж `supportSet` без переосмысления.

Args:
    interval: Кортеж ровно из двух численных границ.

Returns:
    Проверенная замкнутая область интегрирования.

Raises:
    TypeError: `interval` не является кортежем или граница не является вещественным скаляром.
    ValueError: Неверны форма, конечность границ или порядок.

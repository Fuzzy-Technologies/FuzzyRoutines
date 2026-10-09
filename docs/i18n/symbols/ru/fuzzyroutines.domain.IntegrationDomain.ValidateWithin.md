<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Возвращает эту область после проверки её включения в непрерывное универсальное множество.

Args:
    universe: Непрерывное универсальное множество, которое должно содержать обе границы.

Returns:
    Эта же неизменённая область после успешной проверки.

Raises:
    TypeError: `universe` не является непрерывным.
    ValueError: Одна из границ лежит вне универсального множества.

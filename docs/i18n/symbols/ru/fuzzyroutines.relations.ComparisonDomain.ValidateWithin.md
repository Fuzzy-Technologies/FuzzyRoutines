<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Возвращает эту область после проверки принадлежности каждой точки универсальному множеству.

Args:
    universe: Непрерывное универсальное множество, которое должно содержать каждую точку.

Returns:
    Эта же неизменённая область сравнения после успешной проверки.

Raises:
    TypeError: `universe` не является непрерывным.
    ValueError: Точка сравнения лежит вне универсального множества.

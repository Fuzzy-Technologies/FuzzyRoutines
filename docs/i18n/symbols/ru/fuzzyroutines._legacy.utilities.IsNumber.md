<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Проверяет, является ли значение встроенным целым числом или числом с плавающей точкой, исключая булевы значения.

Args:
    value: Проверяемое значение.

Returns:
    `True` для значений `int` и `float`, кроме `bool`; иначе `False`.

<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Именованное правило с одним термом выходной переменной в заключении.

Attributes:
    name: Уникальный идентификатор правила; порядок сохраняется в результате.
    antecedent: Типизированное выражение над входными термами.
    consequent: Точный идентификатор выходного терма.
    weight: Конечная степень в $[0,1]$, умножаемая на степень истинности условия.

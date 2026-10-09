<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Проверяет включение одной степени в другую согласно политике.

Args:
    subsetGrade: Степень принадлежности кандидата на подмножество.
    supersetGrade: Степень принадлежности кандидата на надмножество.

Returns:
    Не превышает ли степень подмножества степень надмножества; близость допускается только в режиме tolerance.

Raises:
    TypeError: Степень не является вещественным скаляром.
    ValueError: Степень неконечна или вне $[0, 1]$.

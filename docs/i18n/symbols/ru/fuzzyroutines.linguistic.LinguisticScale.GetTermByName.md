<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Возвращает терм, полное имя которого совпадает с запросом.

Args:
    termName: Полное имя искомого терма.
    exactMatching: При `True` учитывать регистр; иначе сравнивать имена через Unicode case folding.

Returns:
    Объявленный объект терма либо `None`, если полного совпадения нет.

Raises:
    TypeError: `termName` не является строкой или `exactMatching` не является логическим значением.

Notes:
    Операция не ищет подстроки, префиксы, приближённые совпадения или совпадения по принадлежности.

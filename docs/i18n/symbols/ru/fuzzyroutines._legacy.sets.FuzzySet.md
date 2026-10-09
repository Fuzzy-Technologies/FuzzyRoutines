<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Представляет изменяемое историческое нечёткое множество и интервал интегрирования.

Args:
    membershipFunction: Настроенный [MFunction][fuzzyroutines.FuzzyRoutines.MFunction].
    supportSet: Кортеж из двух элементов, задающий численную область интегрирования.
    linguisticName: Человекочитаемое имя множества.

Raises:
    Exception: `linguisticName` не является строкой или `membershipFunction` не является `MFunction`.
    TypeError: `supportSet` не является кортежем либо содержит невещественные границы.
    ValueError: `supportSet` не содержит две конечные строго возрастающие границы.

Notes:
    Историческое имя `supportSet` обозначает границы интегрирования, а не точное математическое
    множество поддержки. В новом коде используйте [ScalarFuzzySet][fuzzyroutines.ScalarFuzzySet].

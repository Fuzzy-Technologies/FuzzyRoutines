<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Представляет изменяемую историческую лингвистическую шкалу из трёх уровней.

Каждый уровень — словарь с уникальной строкой `name` и полем `fSet`, содержащим
[FuzzySet][fuzzyroutines.FuzzyRoutines.FuzzySet]. Шкала по умолчанию содержит уровни `Min`, `Med` и `High`.

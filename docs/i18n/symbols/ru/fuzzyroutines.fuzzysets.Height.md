<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

Возвращает точную верхнюю грань степеней принадлежности, если она доказуема.

Дискретное универсальное множество перебирается полностью. Непрерывному нужны внутренне сохранённые точные сведения, современная аналитическая [MembershipFunction][fuzzyroutines.membership.MembershipFunction] или зарегистрированный исторический вычислитель [MFunction][fuzzyroutines.FuzzyRoutines.MFunction], поддерживаемый [DeriveProperties][fuzzyroutines.properties.DeriveProperties]. Функция никогда не выдаёт максимум конечной выборки за точную высоту.

Args:
    fuzzySet: Скалярное нечёткое множество, для которого запрашивается точная высота.

Returns:
    Точная верхняя грань степеней принадлежности.

Raises:
    TypeError: `fuzzySet` не является скалярным нечётким множеством.
    ValueError: Точная непрерывная высота недоступна.

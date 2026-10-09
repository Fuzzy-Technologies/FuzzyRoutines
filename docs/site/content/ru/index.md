<!--
SPDX-FileCopyrightText: 2026 Timur Gilmullin and Fuzzy Technologies
SPDX-License-Identifier: Apache-2.0
-->

# Документация FuzzyRoutines {#fuzzyroutines-documentation}

![Алиса и FuzzyRoutines в исследовательской лаборатории Fuzzy Technologies](../en/assets/brand/fuzzyroutines-alice.png){ .fr-project-art }

Начните с [быстрого старта](quick-start.md): установите библиотеку и классифицируйте физическое измерение. [Девять практических сценариев](guides/index.md) объясняют исходные данные, правила вычислений, ожидаемые результаты и графики. Выбрать форму кривой поможет [галерея функций принадлежности](guides/membership-families.md), а выполнить отдельную операцию — [практические рецепты API](guides/api-recipes.md).

В новом коде используйте [современный API](api/modern/index.md). [Исторический фасад совместимости](api/legacy/index.md) предназначен для сопровождения программ, написанных для FuzzyRoutines 1.0.3.

Современный API явно разделяет нечёткие множества, объявленные универсальные множества, альфа-срезы, вычисляемые свойства, лингвистические структуры и правила сравнения по отдельным модулям. Например, скалярное нечёткое множество задаётся на [`ContinuousUniverse`][fuzzyroutines.domain.ContinuousUniverse] или [`DiscreteUniverse`][fuzzyroutines.domain.DiscreteUniverse].

Направленная разность определяется формулой

$$
\mu_{A \setminus B}(x)
= T\left(\mu_A(x), N\left(\mu_B(x)\right)\right).
$$
